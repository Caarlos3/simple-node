import logging
import json
import os

logger = logging.getLogger(__name__)

class SessionManager:
    """
    Handles persistence of chat sessions using local JSON files.
    Provides methods to load, save, and manage session history independently 
    from the workflow engine.
    """

    def __init__(self, storage_dir: str = "memory") -> None:
        """Initializes the manager with a specific directory for session files."""
        self.storage_dir = storage_dir
    
    def _get_path(self, session_id: str) -> str:
        """Constructs the full file path for a given session ID."""
        return f"{self.storage_dir}/{session_id}.json"
    
    def load_history(self, session_id: str) -> str:
        """
        Loads the conversation history from a JSON file.
        If the file is corrupted, it renames it to .corrupted and returns an empty list.
        """

        file_path = self._get_path(session_id)
        if os.path.exists(file_path):
            try:
                 with open (file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f'session loaded: {file_path} ({len(data)})')
                    return data
            
            except json.JSONDecodeError:
                corrupted_path = f'{file_path}.corrupted'
                logger.error(f'Corrupted JSON in {file_path}. Renaming to {corrupted_path}') 

                try:
                    os.rename(file_path, corrupted_path)
                except Exception as rename_error:
                    logger.error(f'Could not rename corrupted file: {rename_error}. Renaming to {corrupted_path}')
                return []
            
            except Exception as e:
                logger.error(f'Unexpected error: {e}')
                return []
            
        else:
             logger.info(f"Session not found: {file_path}")
             return []
    
    def save_history(self, session_id: str, history: list) -> None:
        """
        Saves the provided history list to a JSON file.
        Creates the storage directory if it does not exist.
        """

        file_path = self._get_path(session_id)
        temp_path = file_path + ".tmp"
        os.makedirs(self.storage_dir, exist_ok=True)
        with open (temp_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, file_path)
        logger.info(f"session saved: {file_path} ({len(history)} messages)")

        
