import os
import logging
import warnings
from agno.db.sqlite import SqliteDb
from agno.models.mistral import MistralChat

# Suppress annoying OpenAI API key warnings
# These occur because Agno might auto-initialize OpenAI client even when using Mistral
warnings.filterwarnings("ignore", message="The api_key client option must be set")

# Configure logging (only if enabled)
if os.getenv("ENABLE_LOGGING", "false").lower() == "true":
    log_handlers = [logging.StreamHandler()]
    if os.getenv("LOG_TO_FILE", "false").lower() == "true":
        log_handlers.append(logging.FileHandler('tmp/paper2saas.log'))
    
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=log_handlers
    )
    logger = logging.getLogger(__name__)
else:
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())

# Shared DB for persistence and context sharing
shared_db = SqliteDb(db_file="tmp/paper2saas.db")

def get_mistral_model(model_id: str):
    """Returns a MistralChat model instance with the given ID."""
    # Strip provider prefix if present (e.g. "mistral:mistral-large-latest" -> "mistral-large-latest")
    clean_id = model_id.split(":")[-1] if ":" in model_id else model_id
    return MistralChat(id=clean_id)

def validate_arxiv_id(arxiv_id: str) -> bool:
    """Validate arXiv ID format"""
    import re
    pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
    return bool(re.match(pattern, arxiv_id))

def run_team_with_error_handling(team, input_text: str, log_start_msg: str, log_success_msg: str, session_id: str = None) -> dict:
    """
    Generic wrapper for executing a team with error handling.
    
    Args:
        team: The team instance to run
        input_text: The input prompt for the team
        log_start_msg: Message to log at start
        log_success_msg: Message to log on success
        session_id: Optional session ID to ensure isolation
        
    Returns:
        dict with status, result/error
    """
    logger.info(log_start_msg)
    
    try:
        # Pass session_id if provided
        kwargs = {"session_id": session_id} if session_id else {}
        result = team.run(input_text, **kwargs)
        logger.info(log_success_msg)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
