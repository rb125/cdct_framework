"""
IFEval experiment pipeline for CDCT.
- LLM-based constraint-preserving compression
- Bedrock + Featherless agents
- IFEval heuristic verifier
- 3-model jury evaluation (CC/SA/FC)
- Experiment runner with resume
"""
import json
import os
import re
import time
from pathlib import Path
import requests

# ─── Configuration ───────────────────────────────────────────────────────────

RESULTS_DIR = Path("results_ifeval")
COMPRESSED_PROMPTS_FILE = Path("ifeval_compressed_200.json")
SAMPLE_FILE = Path("ifeval_sample_200.json")

COMPRESSION_LEVELS = [0.0, 0.25, 0.5, 0.75, 1.0]

SUBJECT_MODELS = [
    {"name": "claude-sonnet-4.6", "model_id": "us.anthropic.claude-sonnet-4-6", "provider": "bedrock"},
    {"name": "DeepSeek-V3.2", "model_id": "deepseek.v3.2", "provider": "bedrock"},
    {"name": "Llama-4-Maverick-17B", "model_id": "us.meta.llama4-maverick-17b-instruct-v1:0", "provider": "bedrock"},
    {"name": "nova-pro", "model_id": "amazon.nova-pro-v1:0", "provider": "bedrock"},
    {"name": "Mistral-Large-3", "model_id": "mistral.mistral-large-3-675b-instruct", "provider": "bedrock"},
    {"name": "Phi-4", "model_id": "microsoft/phi-4", "provider": "featherless"},
]

JURY_MODELS = [
    {"name": "Qwen3-32B", "model_id": "qwen.qwen3-32b-v1:0", "provider": "bedrock"},
    {"name": "GLM-5", "model_id": "zai.glm-5", "provider": "bedrock"},
    {"name": "Nemotron-Super-3-120B", "model_id": "nvidia.nemotron-super-3-120b", "provider": "bedrock"},
]

# ─── LLM-Based Constraint-Preserving Compression ────────────────────────────

COMPRESSION_AGENT_SYSTEM = """You are simulating how a human expert compresses instructions for another expert.

When an expert tells another expert "sort list", the receiver understands the full task — they don't need "given an array of integers, arrange them in ascending order using a comparison-based algorithm." Compression works because both parties share knowledge.

Your job: compress the given prompt to the target level AS AN EXPERT WOULD for another expert. The compressed version should be the minimal signal that a competent language model COULD reconstruct the full intent from — if it has the comprehension to do so.

RULES:
1. Compress by leveraging shared knowledge, not by paraphrasing.
2. At high compression, use domain shorthand an expert would use (e.g., "formal letter, no commas" instead of "write a formal letter to your friend without using any commas in your response").
3. Never use ALL-CAPS words in your output. Describe capitalization constraints in lowercase.
4. Output ONLY the compressed instruction. Nothing else."""

CL_TARGETS = {
    0.0: "Maximum compression: 2-3 words. The absolute minimal topic signal. Drop ALL constraints. An expert seeing this would only know the domain.",
    0.25: "High compression: 6-10 words. The task verb + subject + the single most unusual/specific constraint. Drop routine constraints.",
    0.5: "Medium compression: 12-20 words. Expert shorthand for the full task. All constraints mentioned but in compressed expert notation.",
    0.75: "Low compression: 25-40 words. All constraints present and unambiguous, but expressed concisely as an expert would brief a colleague.",
}

COMPRESSION_MODEL = {"name": "nova-micro", "model_id": "amazon.nova-micro-v1:0", "provider": "bedrock"}


def compress_with_agent(prompt, cl):
    """Use LLM agent to compress prompt while preserving constraints."""
    if cl == 1.0:
        return prompt
    target = CL_TARGETS[cl]
    user_msg = f"TARGET: {target}\n\nORIGINAL PROMPT:\n{prompt}"
    messages = [{"role": "user", "content": f"{COMPRESSION_AGENT_SYSTEM}\n\n{user_msg}"}]
    result = call_model(COMPRESSION_MODEL, messages, max_tokens=1024)
    # Strip leaked metadata
    result = re.sub(r'(?i)compression_level:\s*[\d.]+\s*', '', result)
    result = re.sub(r'(?i)TARGET:.*?\n', '', result)
    # Strip structural labels
    result = re.sub(r'(?i)^(Task|Task context|Constraint clauses?|Constraints?|Output)\s*:\s*', '', result)
    result = re.sub(r'(?i)\n(Constraint clauses?|Constraints?)\s*:\s*', '\n', result)
    # Force-lowercase any ALL-CAPS words (2+ chars, all alpha, all upper)
    def decaps(m):
        word = m.group(0)
        if len(word) >= 2 and word.isalpha() and word == word.upper():
            return word.lower()
        return word
    result = re.sub(r'\b[A-Z]{2,}\b', decaps, result)
    return result.strip().strip('"')


def build_compressed_prompts():
    """Compress all 200 prompts at 5 CLs using LLM agent. Saves incrementally. Enforces monotonicity."""
    if COMPRESSED_PROMPTS_FILE.exists():
        compressed = json.loads(COMPRESSED_PROMPTS_FILE.read_text())
        incomplete = [e for e in compressed if len(e["compressions"]) < len(COMPRESSION_LEVELS)]
        if not incomplete:
            print(f"✓ Compressed prompts already complete: {COMPRESSED_PROMPTS_FILE}")
            return compressed
        print(f"  Resuming compression: {len(incomplete)} prompts incomplete")
    else:
        with open(SAMPLE_FILE) as f:
            sample = json.load(f)
        compressed = []
        for p in sample:
            compressed.append({
                "key": p["key"],
                "instruction_id_list": p["instruction_id_list"],
                "kwargs": p["kwargs"],
                "original_prompt": p["prompt"],
                "compressions": {"1.0": p["prompt"]},
            })

    total_calls = sum(len(COMPRESSION_LEVELS) - len(e["compressions"]) for e in compressed)
    done = 0
    print(f"  Compressing {len(compressed)} prompts ({total_calls} LLM calls needed)...")

    for entry in compressed:
        for cl in COMPRESSION_LEVELS:
            cl_key = str(cl)
            if cl_key in entry["compressions"]:
                continue
            done += 1
            try:
                result = compress_with_agent(entry["original_prompt"], cl)
                entry["compressions"][cl_key] = result
                if done % 10 == 0:
                    print(f"    [{done}/{total_calls}] key={entry['key']} cl={cl}")
            except Exception as e:
                print(f"    ✗ key={entry['key']} cl={cl}: {e}")
                entry["compressions"][cl_key] = None

        # Monotonicity check: word count should increase with CL
        # If violated, retry the offending level (max 2 retries)
        for _retry in range(2):
            wcs = []
            for cl in COMPRESSION_LEVELS:
                v = entry["compressions"].get(str(cl))
                wcs.append(len(v.split()) if v else 0)
            monotonic = all(wcs[i] <= wcs[i+1] for i in range(len(wcs)-1))
            if monotonic:
                break
            # Find first violation and regenerate the LOWER CL (the one that's too long)
            for i in range(len(wcs)-1):
                if wcs[i] > wcs[i+1] and COMPRESSION_LEVELS[i] != 1.0:
                    cl_fix = COMPRESSION_LEVELS[i]
                    try:
                        entry["compressions"][str(cl_fix)] = compress_with_agent(entry["original_prompt"], cl_fix)
                        done += 1
                    except:
                        pass
                    break

        # Save after each prompt
        COMPRESSED_PROMPTS_FILE.write_text(json.dumps(compressed, indent=2))

    failures = sum(1 for e in compressed for v in e["compressions"].values() if v is None)
    print(f"✓ Compression complete. {done} calls made, {failures} failures → {COMPRESSED_PROMPTS_FILE}")
    return compressed


# ─── Agents ──────────────────────────────────────────────────────────────────

def _load_env():
    env = {}
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


ENV = _load_env()


def call_bedrock(model_id, messages, max_tokens=2048):
    url = f"https://bedrock-runtime.us-east-1.amazonaws.com/model/{model_id}/converse"
    # Bedrock Converse API: system prompt goes in separate 'system' field
    system_texts = []
    user_messages = []
    for m in messages:
        if m["role"] == "system":
            system_texts.append({"text": m["content"]})
        else:
            user_messages.append({"role": m["role"], "content": [{"text": m["content"]}]})

    body = {
        "messages": user_messages,
        "inferenceConfig": {"temperature": 0.0, "maxTokens": max_tokens},
    }
    if system_texts:
        body["system"] = system_texts

    for attempt in range(5):
        try:
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {ENV['AWS_BEARER_TOKEN_BEDROCK']}"},
                json=body, timeout=300,
            )
            if resp.status_code == 429:
                time.sleep(2 ** attempt * 5)
                continue
            resp.raise_for_status()
            content = resp.json()["output"]["message"]["content"]
            for block in content:
                if "text" in block:
                    return block["text"]
            return str(content)
        except Exception as e:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt * 2)
    raise RuntimeError(f"Bedrock call failed after 5 attempts: {model_id}")


def call_featherless(model_id, messages, max_tokens=2048):
    url = "https://api.featherless.ai/v1/chat/completions"
    body = {"model": model_id, "messages": messages, "temperature": 0.0, "max_tokens": max_tokens}
    for attempt in range(5):
        try:
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {ENV['FEATHERLESS_API_KEY']}"},
                json=body, timeout=300,
            )
            if resp.status_code == 429:
                time.sleep(2 ** attempt * 5)
                continue
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt * 2)
    raise RuntimeError(f"Featherless call failed after 5 attempts: {model_id}")


def call_model(model_config, messages, max_tokens=2048):
    if model_config["provider"] == "bedrock":
        return call_bedrock(model_config["model_id"], messages, max_tokens)
    elif model_config["provider"] == "featherless":
        return call_featherless(model_config["model_id"], messages, max_tokens)
    raise ValueError(f"Unknown provider: {model_config['provider']}")


# ─── IFEval Heuristic Verifier ───────────────────────────────────────────────

def verify_word_count(response, kwargs):
    words = len(response.split())
    relation = kwargs.get("relation", "at least")
    num_words = kwargs.get("num_words")
    if num_words is None:
        return None
    if relation == "at least":
        return words >= num_words
    elif relation == "less than":
        return words < num_words
    return None


def verify_sentence_count(response, kwargs):
    sents = len([s for s in re.split(r'[.!?]+', response) if s.strip()])
    relation = kwargs.get("relation", "at least")
    num = kwargs.get("num_sentences")
    if num is None:
        return None
    if "less than" in (relation or ""):
        return sents < num
    elif "at least" in (relation or ""):
        return sents >= num
    elif "at most" in (relation or ""):
        return sents <= num
    return sents == num


def verify_no_comma(response, _kwargs):
    return "," not in response


def verify_lowercase(response, _kwargs):
    return response == response.lower()


def verify_uppercase(response, _kwargs):
    alpha = "".join(c for c in response if c.isalpha())
    return alpha == alpha.upper() if alpha else True


def verify_capital_word_frequency(response, kwargs):
    relation = kwargs.get("capital_relation")
    frequency = kwargs.get("capital_frequency")
    if relation is None or frequency is None:
        return None
    all_caps = sum(1 for w in response.split() if len(w) >= 2 and w.isalpha() and w == w.upper())
    if "less than" in relation:
        return all_caps < frequency
    elif "at least" in relation:
        return all_caps >= frequency
    elif "at most" in relation:
        return all_caps <= frequency
    return None


def verify_json_format(response, _kwargs):
    text = re.sub(r'```(?:json|JSON)?\s*', '', response)
    text = re.sub(r'```', '', text).strip()
    try:
        json.loads(text)
        return True
    except:
        return False


def verify_keyword_existence(response, kwargs):
    keywords = kwargs.get("keywords")
    if not keywords:
        return None
    return all(kw.lower() in response.lower() for kw in keywords)


def verify_forbidden_words(response, kwargs):
    forbidden = kwargs.get("forbidden_words")
    if not forbidden:
        return None
    return all(fw.lower() not in response.lower() for fw in forbidden)


def verify_quotation(response, _kwargs):
    stripped = response.strip()
    return stripped.startswith('"') and stripped.endswith('"')


def verify_postscript(response, kwargs):
    marker = kwargs.get("postscript_marker", "P.S.")
    return marker in response or "P.P.S" in response or "P.S." in response


VERIFIERS = {
    "length_constraints:number_words": verify_word_count,
    "length_constraints:number_sentences": verify_sentence_count,
    "punctuation:no_comma": verify_no_comma,
    "change_case:english_lowercase": verify_lowercase,
    "change_case:english_capital": verify_uppercase,
    "change_case:capital_word_frequency": verify_capital_word_frequency,
    "detectable_format:json_format": verify_json_format,
    "keywords:existence": verify_keyword_existence,
    "keywords:forbidden_words": verify_forbidden_words,
    "startend:quotation": verify_quotation,
    "detectable_content:postscript": verify_postscript,
}


def verify_constraints(response, instruction_id_list, kwargs_list):
    """Run all applicable heuristic verifiers. Keys on (iid, index) to handle duplicates."""
    results = {}
    for i, iid in enumerate(instruction_id_list):
        kw = kwargs_list[i] if i < len(kwargs_list) else {}
        verifier = VERIFIERS.get(iid)
        if verifier:
            try:
                results[f"{iid}_{i}"] = verifier(response, kw)
            except:
                results[f"{iid}_{i}"] = None
        else:
            results[f"{iid}_{i}"] = None
    return results


def compute_heuristic_cc(verification_results):
    """Compute CC score from heuristic verification (0-1)."""
    checked = [v for v in verification_results.values() if v is not None]
    if not checked:
        return None
    return sum(1 for v in checked if v) / len(checked)


# ─── Jury Evaluation ─────────────────────────────────────────────────────────

JURY_SYSTEM_PROMPT = """You are an expert evaluator for language model outputs. Score the response on three dimensions using a 0.0-1.0 scale.

CONTEXT:
- The model was given a compressed instruction prompt and produced a response.
- You must evaluate the response against the ORIGINAL (uncompressed) prompt's requirements.

DIMENSIONS:
1. CC (Constraint Compliance): Did the response follow the FORMATTING and STRUCTURAL constraints? (word count, case, punctuation, format requirements, number of sections, etc.)
   - Score CC based ONLY on format/structure rules, NOT on whether the content is correct.
   - 1.0 = all formatting constraints satisfied perfectly
   - 0.5 = some formatting constraints met, others violated
   - 0.0 = formatting constraints completely ignored

2. SA (Semantic Accuracy): Did the model correctly understand and execute the PRIMARY TASK? (correct answer, right topic, relevant content)
   - 1.0 = task fully understood and correctly executed
   - 0.5 = partially correct or partially relevant
   - 0.0 = wrong task, wrong answer, or irrelevant

3. FC (Functional Completeness): Is the response complete and useful as a whole?
   - 1.0 = fully complete, addresses all aspects
   - 0.5 = partially complete, missing key aspects
   - 0.0 = fails to address the task

OUTPUT FORMAT (strict JSON, nothing else):
{"CC": 0.0, "SA": 0.0, "FC": 0.0}"""


def evaluate_with_jury(original_prompt, compressed_prompt, response):
    """Run 3-model jury evaluation. Returns consensus scores + per-judge breakdown."""
    user_content = f"""ORIGINAL PROMPT:
{original_prompt}

COMPRESSED PROMPT GIVEN TO MODEL:
{compressed_prompt}

MODEL RESPONSE:
{response}

Score this response. Output ONLY the JSON: {{"CC": ..., "SA": ..., "FC": ...}}"""

    messages = [
        {"role": "system", "content": JURY_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    judges = {}
    for jury_model in JURY_MODELS:
        try:
            raw = call_model(jury_model, messages, max_tokens=200)
            # Parse JSON from response — handle partial/malformed
            match = re.search(r'\{\s*"CC"\s*:\s*([\d.]+)\s*,\s*"SA"\s*:\s*([\d.]+)\s*,\s*"FC"\s*:\s*([\d.]+)\s*\}', raw)
            if match:
                judges[jury_model["name"]] = {
                    "CC": float(match.group(1)),
                    "SA": float(match.group(2)),
                    "FC": float(match.group(3)),
                }
            else:
                # Try generic JSON parse
                jmatch = re.search(r'\{[^}]+\}', raw)
                if jmatch:
                    scores = json.loads(jmatch.group())
                    judges[jury_model["name"]] = {
                        "CC": float(scores.get("CC", 0)),
                        "SA": float(scores.get("SA", 0)),
                        "FC": float(scores.get("FC", 0)),
                    }
                else:
                    judges[jury_model["name"]] = {"CC": 0.0, "SA": 0.0, "FC": 0.0, "parse_error": raw[:200]}
        except Exception as e:
            judges[jury_model["name"]] = {"CC": 0.0, "SA": 0.0, "FC": 0.0, "error": str(e)}
        time.sleep(0.5)  # Throttle between jury calls

    # Compute consensus (mean of 3 judges)
    cc_scores = [j["CC"] for j in judges.values()]
    sa_scores = [j["SA"] for j in judges.values()]
    fc_scores = [j["FC"] for j in judges.values()]

    import numpy as np
    consensus = {
        "CC": float(np.mean(cc_scores)),
        "SA": float(np.mean(sa_scores)),
        "FC": float(np.mean(fc_scores)),
        "judge_variance_CC": float(np.std(cc_scores)),
        "judge_variance_SA": float(np.std(sa_scores)),
        "judge_variance_FC": float(np.std(fc_scores)),
    }

    return {"judges": judges, "consensus": consensus}


# ─── Experiment Runner with Resume ───────────────────────────────────────────

def result_path(prompt_key, model_name, cl):
    return RESULTS_DIR / f"{prompt_key}_{model_name}_{cl}.json"


def is_complete(rp):
    """Check if a result file exists and is not an error."""
    if not rp.exists():
        return False
    try:
        existing = json.loads(rp.read_text())
        return "error" not in existing
    except:
        return False


def run_experiment(prompts=None, models=None, cls=None, dry_run=False, with_jury=False):
    """Run the IFEval experiment with resume support."""
    RESULTS_DIR.mkdir(exist_ok=True)

    if prompts is None:
        prompts = build_compressed_prompts()
    if models is None:
        models = SUBJECT_MODELS
    if cls is None:
        cls = COMPRESSION_LEVELS

    total = len(prompts) * len(models) * len(cls)
    done = 0
    skipped = 0

    print(f"=== IFEval Experiment: {len(prompts)} prompts × {len(models)} models × {len(cls)} CLs = {total} conditions ===")
    if with_jury:
        print("  Jury evaluation: ENABLED (3 judges per condition)")

    for prompt_data in prompts:
        key = prompt_data["key"]
        for model in models:
            for cl in cls:
                rp = result_path(key, model["name"], cl)
                if is_complete(rp):
                    skipped += 1
                    continue

                done += 1
                compressed_prompt = prompt_data["compressions"].get(str(cl))
                if compressed_prompt is None:
                    continue  # Skip failed compressions

                if dry_run:
                    print(f"  [DRY] key={key} model={model['name']} cl={cl} | {len(compressed_prompt.split())}w")
                    continue

                print(f"  [{done}/{total-skipped}] key={key} model={model['name']} cl={cl}", end="", flush=True)

                try:
                    response = call_model(model, [{"role": "user", "content": compressed_prompt}])

                    # Heuristic verification
                    verification = verify_constraints(
                        response, prompt_data["instruction_id_list"], prompt_data["kwargs"]
                    )
                    heuristic_cc = compute_heuristic_cc(verification)

                    result = {
                        "key": key,
                        "model": model["name"],
                        "compression_level": cl,
                        "compressed_prompt": compressed_prompt,
                        "compressed_word_count": len(compressed_prompt.split()),
                        "response": response,
                        "response_word_count": len(response.split()),
                        "instruction_id_list": prompt_data["instruction_id_list"],
                        "heuristic_verification": verification,
                        "heuristic_cc": heuristic_cc,
                    }

                    # Jury evaluation (optional, expensive)
                    if with_jury:
                        jury_result = evaluate_with_jury(
                            prompt_data["original_prompt"], compressed_prompt, response
                        )
                        result["jury_evaluation"] = jury_result
                        jury_cc = jury_result["consensus"]["CC"]
                        print(f" ✓ hcc={heuristic_cc:.2f}" if heuristic_cc is not None else " ✓ hcc=N/A", end="")
                        print(f" jcc={jury_cc:.2f} ({len(response.split())}w)")
                    else:
                        status = f"hcc={heuristic_cc:.2f}" if heuristic_cc is not None else "hcc=N/A"
                        print(f" ✓ {status} ({len(response.split())}w)")

                    rp.write_text(json.dumps(result, indent=2))

                except Exception as e:
                    print(f" ✗ {e}")
                    error_result = {"key": key, "model": model["name"], "compression_level": cl, "error": str(e)}
                    rp.write_text(json.dumps(error_result, indent=2))

    print(f"\n=== Done. Completed: {done}, Skipped (already done): {skipped} ===")


def run_mini_experiment():
    """Run 5 prompts × 1 model × 5 CLs with jury to validate full pipeline."""
    prompts = build_compressed_prompts()[:5]
    models = [m for m in SUBJECT_MODELS if m["name"] == "nova-pro"]
    if not models:
        models = SUBJECT_MODELS[:1]
    print(f"\n=== MINI EXPERIMENT: 5 prompts × {models[0]['name']} × 5 CLs = 25 calls + jury ===\n")
    run_experiment(prompts=prompts, models=models, with_jury=True)

    # Print summary
    print("\n=== MINI EXPERIMENT RESULTS ===")
    results = []
    for f in RESULTS_DIR.glob("*.json"):
        r = json.loads(f.read_text())
        if "error" not in r:
            results.append(r)

    if not results:
        print("No successful results.")
        return

    by_cl = {}
    for r in results:
        cl = r["compression_level"]
        if cl not in by_cl:
            by_cl[cl] = {"hcc": [], "jcc": []}
        if r.get("heuristic_cc") is not None:
            by_cl[cl]["hcc"].append(r["heuristic_cc"])
        if r.get("jury_evaluation"):
            by_cl[cl]["jcc"].append(r["jury_evaluation"]["consensus"]["CC"])

    print(f"\n{'CL':<6} {'Heuristic CC':<15} {'Jury CC':<15}")
    print("-" * 36)
    for cl in sorted(by_cl.keys()):
        hcc = by_cl[cl]["hcc"]
        jcc = by_cl[cl]["jcc"]
        h_str = f"{sum(hcc)/len(hcc):.3f} (n={len(hcc)})" if hcc else "N/A"
        j_str = f"{sum(jcc)/len(jcc):.3f} (n={len(jcc)})" if jcc else "N/A"
        print(f"{cl:<6} {h_str:<15} {j_str:<15}")


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    
    # Parse --models flag
    model_filter = None
    for i, arg in enumerate(sys.argv):
        if arg == "--models" and i + 1 < len(sys.argv):
            model_filter = sys.argv[i + 1].split(",")

    def get_models(filter_list):
        if not filter_list:
            return SUBJECT_MODELS
        return [m for m in SUBJECT_MODELS if m["name"] in filter_list]

    if cmd == "mini":
        run_mini_experiment()
    elif cmd == "compress":
        build_compressed_prompts()
    elif cmd == "full":
        run_experiment(models=get_models(model_filter), with_jury=True)
    elif cmd == "full-nojury":
        run_experiment(models=get_models(model_filter), with_jury=False)
    else:
        names = ", ".join(m["name"] for m in SUBJECT_MODELS)
        print("Usage: python3 ifeval_experiment.py [mini|compress|full|full-nojury] [--models name1,name2]")
        print(f"  Available models: {names}")
        print("\nExamples:")
        print("  python3 ifeval_experiment.py full --models claude-sonnet-4.6,DeepSeek-V3.2,Llama-4-Maverick-17B,nova-pro,Mistral-Large-3")
        print("  python3 ifeval_experiment.py full --models Phi-4")
