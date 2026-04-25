"""
CDCT Subject Models Configuration
Maps each subject model to its provider, endpoint, and authentication method
"""

# Contestant Models for CDCT Evaluation
SUBJECT_MODELS_CONFIG = [
    # Azure OpenAI
    {
        "model_name": "gpt-5.4",
        "deployment_name": "gpt-5.4",
        "provider": "azure_openai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "AZURE_OPENAI_API_ENDPOINT",
        "api_version": "2025-03-01-preview",
        "architecture": "reasoning-aligned",
        "params": "Undisclosed",
        "family": "OpenAI",
    },
    # Azure AI Foundry
    {
        "model_name": "DeepSeek-V3.2",
        "deployment_name": "DeepSeek-V3.2",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "FOUNDRY_MODELS_ENDPOINT",
        "architecture": "mixture-of-experts",
        "params": "Undisclosed",
        "family": "DeepSeek",
    },
    {
        "model_name": "Mistral-Large-3",
        "deployment_name": "Mistral-Large-3",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "FOUNDRY_MODELS_ENDPOINT",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "Mistral",
    },
    {
        "model_name": "grok-4-20-reasoning",
        "deployment_name": "grok-4-20-reasoning",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "FOUNDRY_MODELS_ENDPOINT",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "xAI",
    },
    {
        "model_name": "Phi-4",
        "deployment_name": "Phi-4",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "FOUNDRY_MODELS_ENDPOINT",
        "architecture": "reasoning-aligned",
        "params": "14B",
        "family": "Microsoft",
    },
    {
        "model_name": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "deployment_name": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "FOUNDRY_MODELS_ENDPOINT",
        "architecture": "mixture-of-experts",
        "params": "17B (128 experts)",
        "family": "Meta",
    },
    {
        "model_name": "Kimi-K2.5",
        "deployment_name": "Kimi-K2.5",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "FOUNDRY_MODELS_ENDPOINT",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "Moonshot",
    },
    # Gemma via Modal
    {
        "model_name": "gemma-4-27b-it",
        "deployment_name": "google/gemma-4-26B-A4B-it",
        "provider": "azure_ai",
        "api_key_env_var": "GEMMA_API_KEY",
        "endpoint_env_var": "GEMMA_BASE_URL",
        "architecture": "mixture-of-experts",
        "params": "27B (4B active)",
        "family": "Google",
    },
    # AWS Bedrock (ABSK bearer token, direct HTTP)
    {
        "model_name": "nova-pro",
        "model_id": "amazon.nova-pro-v1:0",
        "provider": "bedrock",
        "region": "us-east-1",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "Amazon",
    },
    {
        "model_name": "claude-sonnet-4.6",
        "model_id": "us.anthropic.claude-sonnet-4-6",
        "provider": "bedrock",
        "region": "us-east-1",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "Anthropic",
    },
    {
        "model_name": "MiniMax-M2.5",
        "model_id": "minimax.minimax-m2.5",
        "provider": "bedrock",
        "region": "us-east-1",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "MiniMax",
    },
]

# Jury Models — zero family overlap with contestants
# Families: Alibaba (Qwen), Zhipu (GLM), NVIDIA (Nemotron)
JURY_MODELS_CONFIG = [
    {
        "model_name": "Qwen3-32B",
        "model_id": "qwen.qwen3-32b-v1:0",
        "provider": "bedrock",
        "region": "us-east-1",
    },
    {
        "model_name": "GLM-5",
        "model_id": "zai.glm-5",
        "provider": "bedrock",
        "region": "us-east-1",
    },
    {
        "model_name": "Nemotron-Super-3-120B",
        "model_id": "nvidia.nemotron-super-3-120b",
        "provider": "bedrock",
        "region": "us-east-1",
    },
]
