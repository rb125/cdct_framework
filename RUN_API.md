# CDCT API Server

This API serves CDCT (Compression-Decay Comprehension Test) scores and allows running new experiments via a REST interface.

## Prerequisites

- Python 3.12+
- Virtual environment (`.venv`) with dependencies installed:
  ```bash
  .venv/bin/pip install fastapi uvicorn
  ```
- Environment variables configured in a `.env` file or exported:
  - `AZURE_API_KEY`: Your Azure API key.
  - `AZURE_OPENAI_API_ENDPOINT`: Endpoint for OpenAI models (gpt-5, o3, etc.).
  - `DDFT_MODELS_ENDPOINT`: Endpoint for Azure AI Foundry models (Phi-4, DeepSeek, etc.).
  - `AZURE_ANTHROPIC_API_ENDPOINT`: Endpoint for Anthropic models.

## Running the Server

To start the API server on port 8001:

```bash
.venv/bin/uvicorn cdct_api:app --host 0.0.0.0 --port 8001
```

To run it in the background:

```bash
nohup .venv/bin/uvicorn cdct_api:app --host 0.0.0.0 --port 8001 > cdct_api.log 2>&1 &
```

## API Endpoints

### 1. Get Model Scores
**Endpoint:** `GET /score/{model_name}`

Retrieves the CDCT scores for a specific model. If no scores exist for a valid model, it automatically triggers a diagnostic battery in the background.

**Example:**
```bash
curl http://localhost:8001/score/gpt-5
```

**Response:**
Returns a JSON array of metrics for each concept tested.

### 2. Run Fresh Experiment
**Endpoint:** `POST /run_experiment`

Triggers a fresh diagnostic battery against a model.

**Payload:**
```json
{
  "model": "phi-4",
  "concepts": ["concepts/derivative.json"]
}
```
*(The `concepts` list is optional; if omitted, all available concepts are run.)*

**Example:**
```bash
curl -X POST http://localhost:8001/run_experiment 
     -H "Content-Type: application/json" 
     -d '{"model": "phi-4"}'
```

## Jury Configuration

The API uses a 2-judge jury system for evaluation:
1. **GPT-5.2**: Reasoning Stability
2. **DeepSeek-V3.2**: Logical Consistency

Results are stored in the `results_jury/` directory.
