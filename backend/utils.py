import os
import logging
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

def section_chunk(text):
    pattern = r'\n\d+\.\d+\s+'

    sections = re.split(pattern, text)

    chunks = []

    for section in sections:
        section = section.strip()

        if len(section) > 50:
            chunks.append(section)

    return chunks

def chunk_text(text: str) -> list[str]:
    # Extract headers and bodies using a regex that captures the section title
    pattern = r'\n(\d+\.\d+\s+[^\n]+)'
    parts = re.split(pattern, text)
    
    sections = []
    if parts[0].strip():
        sections.append( ("General", parts[0].strip()) )
        
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i+1].strip() if i+1 < len(parts) else ""
        sections.append( (header, body) )
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    final_chunks = []
    chunk_counter = 1
    for header, body in sections:
        if len(body) < 10:
            continue
        sub_chunks = splitter.split_text(body)
        for sub in sub_chunks:
            # Format exactly as requested by user
            chunk_str = f"Chunk {chunk_counter}:\nSection: {header}\n{sub}"
            final_chunks.append(chunk_str)
            chunk_counter += 1
            
    return final_chunks


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


def get_timestamp() -> str:
    """Returns the current timestamp in ISO format."""
    return datetime.utcnow().isoformat()
