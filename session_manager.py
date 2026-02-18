import logging
import json
import os

logger = logging.getLogger(__name__)

class SessionManager:

    def __init__(self, storage_dir: str = "memory") -> None:
        self.storage_dir = storage_dir
    
    def _get_path(self, session_id: str) -> str:
        return f"{self.storage_dir}/{session_id}.json"
    
    def load_history(self, session_id: str) -> str:

        file_path = self._get_path(session_id)
        if os.path.exists(file_path):
            try:
                 with open (file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f'session loaded: {file_path} ({len(data)})')
                    return data
            
            except json.JSONDecodeError:
                corrupted_path = f'{file_path}.corrupted'
                logger.error(f'Corrupted JSON in {file_path}') 

                try:
                    os.rename(file_path, corrupted_path)
                except Exception as rename_error:
                    logger.error(f'Could not rename corrupted file: {rename_error}. Renaming to {corrupted_path}')
                return []
            
            except Exception as e:
                logger.error(f'Unexpected error: {e}')
                return []
            
        else:
             logger.info("Session not found")
             return []
    
    def save_history(self, session_id: str, history: list) -> None:
        file_path = self._get_path(session_id)
        os.makedirs(self.storage_dir, exist_ok=True)
        with open (file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
  