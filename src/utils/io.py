# API Keys and endpoints for different models
# It is recommended to load these from environment variables for security
import os
AZURE_OPENAI_SETTINGS = {
    "api_key": os.getenv("AZURE_API_KEY"),
    "azure_endpoint": os.getenv("AZURE_OPENAI_API_ENDPOINT"),
    "deployment_name": "4.1",
    "api_version": "2024-02-01" 
}
AZURE_AI_SETTINGS = { #for deepseek, phi-4, grok, gpt-oss-120b models 
    "api_key": os.getenv("AZURE_API_KEY"),
    "azure_endpoint": os.getenv("AZURE_API_ENDPOINT")
    
}
