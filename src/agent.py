"""
Agent module - Handles different model endpoints
"""
from abc import ABC, abstractmethod
from openai import AzureOpenAI, OpenAI
from src.utils import io as config

class Agent(ABC):
    """Abstract base class for a model agent."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def query(self, prompt: str) -> str:
        """Sends a prompt to the model and returns the response."""
        pass


class AzureOpenAIAgent(Agent):
    """
    Agent for Azure OpenAI native models (GPT-4.1, GPT-5-mini).
    Uses AZURE_OPENAI_SETTINGS endpoint.
    """

    def __init__(self, model_name: str, deployment_name: str = None, 
                 azure_endpoint: str = None, azure_api_key: str = None):
        super().__init__(model_name)
        
        # Use provided credentials or fall back to config
        self.client = AzureOpenAI(
            api_key=azure_api_key or config.AZURE_OPENAI_SETTINGS["api_key"],
            azure_endpoint=azure_endpoint or config.AZURE_OPENAI_SETTINGS["azure_endpoint"],
            api_version=config.AZURE_OPENAI_SETTINGS["api_version"]
        )
        
        # Use provided deployment or fall back to config default
        self.deployment_name = deployment_name or config.AZURE_OPENAI_SETTINGS.get("deployment_name")

    def query(self, prompt: str) -> str:
        """Sends a prompt to Azure OpenAI and returns the response."""
        try:
            package = {}
            if self.deployment_name == "gpt-5-mini":
                package = { 
                    "model": self.deployment_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_completion_tokens": 16384
                }
            else: # default handling
                package = {
                    "model": self.deployment_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.0  # Deterministic for benchmarking
                }
            response = self.client.chat.completions.create(**package)
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error querying Azure OpenAI ({self.model_name}): {e}")
            return f"Error: {e}"


class AzureAIAgent(Agent):
    """
    Agent for Azure AI Foundry models (DeepSeek, Grok, Phi-4, GPT-OSS, Mistral).
    Uses AZURE_AI_SETTINGS endpoint.
    """

    def __init__(self, model_name: str, deployment_name: str,
                 azure_endpoint: str = None, azure_api_key: str = None):
        super().__init__(model_name)
        
        # Use Azure AI Foundry endpoint
        self.client = OpenAI(
            base_url=azure_endpoint or config.AZURE_AI_SETTINGS["azure_endpoint"],
            api_key=azure_api_key or config.AZURE_AI_SETTINGS["api_key"]
        )
        self.deployment_name = deployment_name

    def query(self, prompt: str) -> str:
        """Sends a prompt to Azure AI Foundry and returns the response."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0  # Deterministic for benchmarking
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error querying Azure AI Foundry ({self.model_name}): {e}")
            return f"Error: {e}"


# Factory function to create the right agent type
def create_agent(model_name: str, deployment_name: str = None,
                azure_endpoint: str = None, azure_api_key: str = None) -> Agent:
    """
    Factory function to create the appropriate agent based on model name.
    
    Args:
        model_name: Name of the model (e.g., "gpt-4.1", "deepseek-v3")
        deployment_name: Deployment name in Azure
        azure_endpoint: Optional endpoint override
        azure_api_key: Optional API key override
    
    Returns:
        Appropriate Agent instance
    """
    # Models on Azure OpenAI endpoint
    openai_models = ["gpt-4.1", "gpt-5-mini"]
    
    # Models on Azure AI Foundry endpoint
    ai_foundry_models = [
        "deepseek-v3", "deepseek-v3-0324",
        "grok-4", "grok-4-fast-reasoning",
        "phi-4", "phi-4-mini-instruct",
        "gpt-oss-120b",
        "mistral-medium-3"
    ]
    
    if model_name in openai_models:
        return AzureOpenAIAgent(
            model_name=model_name,
            deployment_name=deployment_name,
            azure_endpoint=azure_endpoint,
            azure_api_key=azure_api_key
        )
    elif model_name in ai_foundry_models:
        if not deployment_name:
            raise ValueError(f"deployment_name required for Azure AI Foundry model: {model_name}")
        return AzureAIAgent(
            model_name=deployment_name,
            deployment_name=deployment_name,
            azure_endpoint=azure_endpoint,
            azure_api_key=azure_api_key
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")