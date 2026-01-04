import os
from agno.models.mistral import Mistral
from paper2saas_app.config import AgentConfig

# Instantiate Mistral model objects directly
# This avoids potential issues with string-based model resolution defaulting to OpenAI

def get_large_model():
    model_id = AgentConfig.LARGE_MODEL.split(":")[-1] if ":" in AgentConfig.LARGE_MODEL else AgentConfig.LARGE_MODEL
    return Mistral(id=model_id, api_key=os.getenv("MISTRAL_API_KEY"))

def get_small_model():
    model_id = AgentConfig.SMALL_MODEL.split(":")[-1] if ":" in AgentConfig.SMALL_MODEL else AgentConfig.SMALL_MODEL
    return Mistral(id=model_id, api_key=os.getenv("MISTRAL_API_KEY"))

# Specific agent model getters that respect the config overrides
def get_model(config_value, default_func):
    if config_value == AgentConfig.LARGE_MODEL:
        return get_large_model()
    elif config_value == AgentConfig.SMALL_MODEL:
        return get_small_model()
    else:
        # If it's a custom override string, try to parse it
        model_id = config_value.split(":")[-1] if ":" in config_value else config_value
        return Mistral(id=model_id, api_key=os.getenv("MISTRAL_API_KEY"))
