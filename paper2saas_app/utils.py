import os
import logging
from agno.db.sqlite import SqliteDb

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

def validate_arxiv_id(arxiv_id: str) -> bool:
    """Validate arXiv ID format"""
    import re
    pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
    return bool(re.match(pattern, arxiv_id))

def run_team_with_error_handling(team, input_text: str, log_start_msg: str, log_success_msg: str) -> dict:
    """
    Generic wrapper for executing a team with error handling.
    
    Args:
        team: The team instance to run
        input_text: The input prompt for the team
        log_start_msg: Message to log at start
        log_success_msg: Message to log on success
        
    Returns:
        dict with status, result/error
    """
    logger.info(log_start_msg)
    
    try:
        result = team.run(input_text)
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
