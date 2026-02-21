"""
CDCT Subject Models Configuration
Maps each subject model to its provider, endpoint, and authentication method
Based on DDFT's configuration-driven approach
"""

# Contestant Models for CDCT Evaluation
SUBJECT_MODELS_CONFIG = [
    # Azure OpenAI models (AZURE_OPENAI_API_ENDPOINT)
    {
        "model_name": "gpt-5",
        "deployment_name": "gpt-5",
        "provider": "azure_openai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "AZURE_OPENAI_API_ENDPOINT",
        "api_version": "2025-03-01-preview",
        "architecture": "reasoning-aligned",
        "params": "Undisclosed",
        "family": "OpenAI",
    },
    {
        "model_name": "gpt-5.1",
        "deployment_name": "gpt-5.1",
        "provider": "azure_openai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "AZURE_OPENAI_API_ENDPOINT",
        "api_version": "2025-03-01-preview",
        "architecture": "reasoning-aligned",
        "params": "Undisclosed",
        "family": "OpenAI",
    },
    {
        "model_name": "o3",
        "deployment_name": "o3",
        "provider": "azure_openai_bearer",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "AZURE_OPENAI_API_ENDPOINT",
        "api_version": "2025-01-01-preview",
        "architecture": "reasoning-aligned",
        "params": "Undisclosed",
        "family": "OpenAI",
    },
    {
        "model_name": "o4-mini",
        "deployment_name": "o4-mini",
        "provider": "azure_openai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "AZURE_OPENAI_API_ENDPOINT",
        "api_version": "2025-03-01-preview",
        "architecture": "reasoning-aligned",
        "params": "Undisclosed",
        "family": "OpenAI",
    },

    # Azure AI Foundry models (DDFT_MODELS_ENDPOINT)
    {
        "model_name": "DeepSeek-v3.1",
        "deployment_name": "DeepSeek-v3.1",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "DDFT_MODELS_ENDPOINT",
        "architecture": "mixture-of-experts",
        "params": "Undisclosed",
        "family": "DeepSeek",
    },
    {
        "model_name": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "deployment_name": "Llama-4-Maverick-17B-128E-Instruct-FP8",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "DDFT_MODELS_ENDPOINT",
        "architecture": "mixture-of-experts",
        "params": "17B (128 experts)",
        "family": "Meta",
    },
    {
        "model_name": "Phi-4",
        "deployment_name": "Phi-4",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "DDFT_MODELS_ENDPOINT",
        "architecture": "reasoning-aligned",
        "params": "14B",
        "family": "Microsoft",
    },
    {
        "model_name": "grok-4-fast-non-reasoning",
        "deployment_name": "grok-4-fast-non-reasoning",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "DDFT_MODELS_ENDPOINT",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "xAI",
    },
    {
        "model_name": "mistral-medium-2505",
        "deployment_name": "mistral-medium-2505",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "DDFT_MODELS_ENDPOINT",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "Mistral",
    },
    {
        "model_name": "gpt-oss-120b",
        "deployment_name": "gpt-oss-120b",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "DDFT_MODELS_ENDPOINT",
        "architecture": "dense",
        "params": "120B",
        "family": "OpenSource",
    },
    {
        "model_name": "Kimi-K2.5",
        "deployment_name": "Kimi-K2.5",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "DDFT_MODELS_ENDPOINT",
        "architecture": "dense",
        "params": "Undisclosed",
        "family": "Moonshot",
    },
]

# Jury Models
JURY_MODELS_CONFIG = [
    {
        "model_name": "gpt-5.2",
        "deployment_name": "gpt-5.2",
        "provider": "azure_openai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "AZURE_OPENAI_API_ENDPOINT",
        "api_version": "2025-03-01-preview",
    },
    {
        "model_name": "DeepSeek-v3.2",
        "deployment_name": "DeepSeek-v3.2",
        "provider": "azure_ai",
        "api_key_env_var": "AZURE_API_KEY",
        "endpoint_env_var": "DDFT_MODELS_ENDPOINT",
    },
]
