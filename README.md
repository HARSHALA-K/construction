# Construction AI Assistant

A Retrieval-Augmented Generation (RAG) system for a Construction domain AI assistant. 
This application is built with a modular architecture to support multiple backend implementations (e.g., Qdrant, AWS).

## Setup Instructions

1. Clone the repository or navigate to this folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   Copy `.env.example` to `.env` and fill in your API keys and configuration.
   ```bash
   cp .env.example .env
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
