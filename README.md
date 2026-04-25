# Compression Decay Comprehension Test (CDCT) Framework

This repository contains the source code and data for the research paper "The Compression Decay Comprehension Test (CDCT)." It measures how model comprehension decays under progressive information compression and aggregates results into CDCT metrics.

**Live results:** [rb125.github.io/cdct_framework](https://rb125.github.io/cdct_framework/)

## API (Vercel)

The Vercel deployment serves precomputed metrics from `results_jury/`.
*   `GET /score/{model_name}`: Return CDCT metrics for a model.
*   `POST /run_experiment`: Disabled on Vercel; run locally or on a worker, then commit results.

## Subject Models (11 Contestants)

| Model | Family | Provider |
|---|---|---|
| GPT-5.4 | OpenAI | Azure OpenAI |
| DeepSeek-V3.2 | DeepSeek | Azure AI Foundry |
| Mistral-Large-3 | Mistral | Azure AI Foundry |
| Grok-4-20-Reasoning | xAI | Azure AI Foundry |
| Phi-4 | Microsoft | Azure AI Foundry |
| Llama-4-Maverick-17B-128E | Meta | Azure AI Foundry |
| Kimi-K2.5 | Moonshot | Azure AI Foundry |
| Gemma-4-27B-IT | Google | Modal (vLLM) |
| Nova Pro | Amazon | AWS Bedrock |
| Claude Sonnet 4.6 | Anthropic | AWS Bedrock |
| MiniMax M2.5 | MiniMax | AWS Bedrock |

## Jury Models (3 Judges — Zero Family Overlap)

| Model | Family | Primary Axis |
|---|---|---|
| Qwen3-32B | Alibaba | SA (Semantic Accuracy) |
| GLM-5 | Zhipu AI | CC (Constraint Compliance) |
| Nemotron Super 3 120B | NVIDIA | FC (Functional Completeness) |

The jury evaluates each response on three orthogonal dimensions:
- **CC (Constraint Compliance):** Did the model follow length/content restrictions?
- **SA (Semantic Accuracy):** Is the content factually correct given the context?
- **FC (Functional Completeness):** Did it answer the question adequately?

## Ablation Study

The `no_helpfulness` ablation removes RLHF alignment cues from the prompt to test whether the CC dip at CL=0.50 is caused by learned helpfulness behavior or is an intrinsic compression boundary.

- **Baseline:** `results_jury/` — compression-aware prompts with level-specific constraints
- **Ablation:** `results_jury_ablation/` — minimal prompts stripped of social framing

## Project Structure

```
/
├── concepts/                  # JSON definitions for each concept (8 domains)
├── results_jury/              # Baseline jury evaluation results (88 files)
├── results_jury_ablation/     # RLHF ablation results (88 files)
├── src/
│   ├── agent.py               # Model agents (Azure OpenAI, Azure AI, Bedrock)
│   ├── llm_jury.py            # 3-model jury with weighted consensus
│   ├── experiment_jury.py     # Jury-based experiment pipeline
│   ├── prompting.py           # Prompt strategies (compression_aware, minimal)
│   ├── compression.py         # Compression algorithm
│   ├── retry_handler.py       # Exponential backoff with error classification
│   └── ...
├── main.py                    # Single experiment entry point
├── main_jury.py               # Jury evaluation entry point
├── run_all_jury.py            # Batch: all models × all concepts
├── run_all_jury_ablation.py   # Batch: ablation study
├── models_config.py           # Model registry and provider configuration
├── index.html                 # GitHub Pages results dashboard
└── README.md
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rb125/cdct_framework.git
    cd cdct_framework
    ```

2.  **Install dependencies:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure credentials** in `.env`:
    ```
    AZURE_API_KEY=<your-key>
    AZURE_OPENAI_API_ENDPOINT=https://<resource>.cognitiveservices.azure.com/
    FOUNDRY_MODELS_ENDPOINT=https://<resource>.services.ai.azure.com/openai/v1/
    AWS_BEARER_TOKEN_BEDROCK=<your-absk-token>
    GEMMA_BASE_URL=<your-modal-endpoint>
    GEMMA_API_KEY=not-needed
    ```

## Usage

### Run full evaluation battery

```bash
python3 run_all_jury.py            # 11 models × 8 concepts = 88 runs
python3 run_all_jury_ablation.py   # Same, with no_helpfulness ablation
```

### Run a single experiment

```bash
python3 main_jury.py --concept concepts/mathematics_derivative.json --model gpt-5.4
python3 main_jury.py --concept concepts/mathematics_derivative.json --model gpt-5.4 --ablation-type no_helpfulness --output-dir results_jury_ablation
```

### Analyze results

```bash
python3 analyze_jury_results.py
python3 calculate_cdct_metrics.py
```
