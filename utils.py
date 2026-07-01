import os
import logging
from datetime import datetime

def setup_logging(log_dir: str = "logs", log_file: str = "app.log"):
    """
    Sets up python logging to output to both console and a log file.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_path = os.path.join(log_dir, log_file)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

def read_txt(file_path: str) -> str:
    """Reads and returns the contents of a text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def save_txt(text: str, file_path: str):
    """Saves text content to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

def chunk_text(text: str, delimiter: str = "Question:") -> list[str]:
    """
    Splits text by a delimiter and cleans up the chunks.
    Assumes the delimiter should be kept at the start of each chunk.
    """
    raw_chunks = text.split(delimiter)
    chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]
    
    # Prepend the delimiter back since split removes it
    # We only prepend if the original text had it, which this basic chunker assumes.
    return [f"{delimiter} {chunk}" for chunk in chunks]

def get_timestamp() -> str:
    """Returns the current timestamp in ISO format."""
    return datetime.utcnow().isoformat()
