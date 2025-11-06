# CDCT Usage Guide - Your Specific Setup

## Environment Setup

### 1. Set Environment Variables

```bash
# Add to your .bashrc, .zshrc, or .env file
export AZURE_API_KEY="your-azure-api-key"
export AZURE_OPENAI_API_ENDPOINT="https://your-openai-endpoint.openai.azure.com/"
export AZURE_API_ENDPOINT="https://your-ai-foundry-endpoint.models.ai.azure.com/"
```

### 2. Verify Configuration

```bash
python -c "import config; print('Azure OpenAI:', config.AZURE_OPENAI_SETTINGS['azure_endpoint']); print('Azure AI:', config.AZURE_AI_SETTINGS['azure_endpoint'])"
```

## Running Experiments

### OpenAI Models (GPT-4.1, GPT-5-mini)

These use Azure OpenAI endpoint:

```bash
# GPT-4.1
python main.py \
  --concept concepts/derivative.json \
  --model gpt-4.1 \
  --deployment "4.1"

# GPT-5-mini
python main.py \
  --concept concepts/derivative.json \
  --model gpt-5-mini \
  --deployment "gpt-5-mini-deployment-name"
```

### Azure AI Foundry Models

These use Azure AI endpoint (DeepSeek, Grok, Phi-4, GPT-OSS, Mistral):

```bash
# DeepSeek V3
python main.py \
  --concept concepts/derivative.json \
  --model deepseek-v3-0324 \
  --deployment "DeepSeek-V3-0324"

# Grok-4
python main.py \
  --concept concepts/derivative.json \
  --model grok-4-fast-reasoning \
  --deployment "grok-4-fast-reasoning"

# Phi-4 Mini
python main.py \
  --concept concepts/derivative.json \
  --model phi-4-mini-instruct \
  --deployment "Phi-4-mini-instruct"

# GPT-OSS-120B
python main.py \
  --concept concepts/derivative.json \
  --model gpt-oss-120b \
  --deployment "gpt-oss-120b"

# Mistral Medium 3
python main.py \
  --concept concepts/derivative.json \
  --model mistral-medium-3 \
  --deployment "Mistral-Medium-3"
```

## Advanced Options

### Compare Prompt Strategies

```bash
python main.py \
  --concept concepts/derivative.json \
  --model gpt-4.1 \
  --deployment "4.1" \
  --compare-strategies
```

This will test three strategies and show you which works best:
- `simple`: Basic prompting
- `compression_aware`: Explicit constraints (recommended)
- `few_shot`: Learning by example

### Use Different Evaluation Modes

```bash
# Strict mode (heavy hallucination penalty)
python main.py \
  --concept concepts/derivative.json \
  --model deepseek-v3-0324 \
  --deployment "DeepSeek-V3-0324" \
  --evaluation-mode strict

# Balanced mode (default)
python main.py \
  --concept concepts/derivative.json \
  --model gpt-4.1 \
  --deployment "4.1" \
  --evaluation-mode balanced

# Lenient mode (keyword-only, for comparison)
python main.py \
  --concept concepts/derivative.json \
  --model phi-4-mini-instruct \
  --deployment "Phi-4-mini-instruct" \
  --evaluation-mode lenient
```

### Validate Compression Protocol

Before running experiments, validate your concept JSON:

```bash
python main.py \
  --concept concepts/derivative.json \
  --validate-only
```

## Batch Benchmarking

### Run All Models on One Concept

```bash
# Create a batch script: run_all_models.sh

#!/bin/bash

CONCEPT="concepts/derivative.json"

# OpenAI models
python main.py --concept $CONCEPT --model gpt-4.1 --deployment "4.1"
python main.py --concept $CONCEPT --model gpt-5-mini --deployment "gpt-5-mini"

# Azure AI Foundry models
python main.py --concept $CONCEPT --model deepseek-v3-0324 --deployment "DeepSeek-V3-0324"
python main.py --concept $CONCEPT --model grok-4-fast-reasoning --deployment "grok-4-fast-reasoning"
python main.py --concept $CONCEPT --model phi-4-mini-instruct --deployment "Phi-4-mini-instruct"
python main.py --concept $CONCEPT --model gpt-oss-120b --deployment "gpt-oss-120b"
python main.py --concept $CONCEPT --model mistral-medium-3 --deployment "Mistral-Medium-3"

echo "Batch processing complete!"
```

Run it:
```bash
chmod +x run_all_models.sh
./run_all_models.sh
```

### Run One Model on All Concepts

```bash
#!/bin/bash

MODEL="gpt-4.1"
DEPLOYMENT="gpt-4.1"

for concept in concepts/*.json; do
    echo "Processing $concept..."
    python main.py \
      --concept "$concept" \
      --model "$MODEL" \
      --deployment "$DEPLOYMENT"
done
```

## Understanding Results

### Result File Location

Results are saved to: `results/results_{concept}_{model}_{strategy}_{evaluation_mode}.json`

Example: `results/results_derivative_gpt-4.1_compression_aware_balanced.json`

### Key Metrics

```json
{
  "analysis": {
    "CSI": 0.0825,              // Lower = better (0.08-0.12 is excellent)
    "C_h": 2,                   // Comprehension horizon (level where score < 0.70)
    "mean_score": 0.826,        // Average across all compression levels
    "decay_direction": "decay", // Should be "decay" (improvement means problems)
    "R_squared": 0.924          // How linear the decay is (>0.5 is good)
  }
}
```

### Expected CSI Values (from paper)

| Model | Expected CSI | Interpretation |
|-------|--------------|----------------|
| GPT-OSS-120B | 0.08 | Excellent |
| Phi-4-mini | 0.09 | Excellent |
| Mistral-Medium-3 | 0.12 | Good |
| DeepSeek-V3 | 0.14 | Good |
| Grok-4-Fast | 0.18 | Moderate |
| GPT-4.1 | 0.19 | Moderate |
| GPT-5-mini | 0.23 | Poor |

## Troubleshooting

### Issue: Authentication Error

```
Error: (Unauthorized) Access denied due to invalid subscription key
```

**Solution:** Check environment variables:
```bash
echo $AZURE_API_KEY
echo $AZURE_OPENAI_API_ENDPOINT
echo $AZURE_API_ENDPOINT
```

### Issue: All Scores are 1.0

**Problem:** Evaluation too lenient

**Solution:** Use stricter evaluation:
```bash
python main.py --concept concepts/derivative.json --model X --deployment Y \
  --evaluation-mode strict
```

### Issue: CSI = 0

**Problem:** No decay detected (flat performance)

**Solutions:**
1. Check if you're using the updated files (should show decay)
2. Try compression_aware strategy:
   ```bash
   --prompt-strategy compression_aware
   ```
3. Validate your concept JSON has proper compression ratios

### Issue: "improvement" instead of "decay"

**Problem:** Performance increases with compression (impossible for true comprehension)

**Explanation:** Model is ignoring compression constraints

**Solutions:**
1. Use `--prompt-strategy compression_aware`
2. Use `--evaluation-mode strict`
3. Check if your concept JSON has proper ordering (level 0 = most compressed)

## Quick Tests

### Test if Setup Works

```bash
# Quick test with default settings
python main.py \
  --concept concepts/derivative.json \
  --model gpt-4.1 \
  --deployment "4.1"

# Should see:
# - CSI between 0.08-0.25
# - Scores decreasing with compression
# - No warnings
```

### Compare Your Two Endpoints

```bash
# Test OpenAI endpoint
python main.py --concept concepts/derivative.json --model gpt-4.1 --deployment "4.1"

# Test AI Foundry endpoint
python main.py --concept concepts/derivative.json --model phi-4-mini-instruct --deployment "Phi-4-mini-instruct"
```

Both should work without errors!

## Model Deployment Names

Keep track of your deployment names in Azure:

| Model | Deployment Name (Example) |
|-------|---------------------------|
| GPT-4.1 | `4.1` |
| GPT-5-mini | `gpt-5-mini` |
| DeepSeek-V3-0324 | `DeepSeek-V3-0324` |
| Grok-4-Fast-Reasoning | `grok-4-fast-reasoning` |
| Phi-4-mini-instruct | `Phi-4-mini-instruct` |
| GPT-OSS-120B | `gpt-oss-120b` |
| Mistral-Medium-3 | `Mistral-Medium-3` |

**Note:** Your actual deployment names may differ. Check Azure Portal → AI Foundry / OpenAI → Deployments.

## Next Steps

1. **Run your first test:**
   ```bash
   python main.py --concept concepts/derivative.json --model gpt-4.1 --deployment "4.1"
   ```

2. **Compare with old results:**
   ```bash
   # Your old result
   cat results/results_derivative_gpt-4.1.json
   
   # New result
   cat results/results_derivative_gpt-4.1_compression_aware_balanced.json
   ```

3. **Create more concepts** for full benchmarking (8 domains × 3 concepts = 24 total)

4. **Run all 7 models** to reproduce paper Table 1

