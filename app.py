import streamlit as st
import os
import pandas as pd
from datetime import datetime

# Import backend modules
from backend.utils import setup_logging
from backend.embedding import load_embedding_model
from backend.qdrant_db import connect_qdrant
from backend.llm import initialize_llm
from backend.rag import answer_question

# ==========================================
# Application Setup & Styling
# ==========================================
st.set_page_config(page_title="Construction AI Assistant", page_icon="🏗️", layout="centered")

# Custom CSS for a professional, minimal, construction-themed look
st.markdown("""
<style>
    /* Primary buttons */
    .stButton>button {
        background-color: #2E4053; 
        color: white;
    }
    .stButton>button:hover {
        background-color: #1A252F;
        color: #F39C12; /* Subtle orange/gold accent */
    }
</style>
""", unsafe_allow_html=True)

# Initialize logging
if "logger_setup" not in st.session_state:
    setup_logging(log_dir="logs", log_file="app.log")
    st.session_state.logger_setup = True

import logging
logger = logging.getLogger(__name__)

# ==========================================
# Caching Heavy Initializations
# ==========================================
@st.cache_resource
def load_backend_resources():
    """Loads models and connects to services only once."""
    try:
        logger.info("Initializing backend resources from Streamlit...")
        load_embedding_model()
        connect_qdrant()
        initialize_llm()
        logger.info("Backend resources initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize backend: {e}")
        st.error(f"System Error: Could not connect to backend services. Details: {str(e)}")
        return False

is_backend_ready = load_backend_resources()

# ==========================================
# Session State Initialization
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# Sidebar Navigation
# ==========================================
st.sidebar.image("assets/logo.png", use_container_width=True)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat", "Feedback", "About"])

# ==========================================
# Page: Chat
# ==========================================
if page == "Chat":
    st.title("🏗️ Construction AI Assistant")
    st.markdown("Ask me questions about construction materials, costs, phases, and best practices.")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("View Source Context"):
                    for idx, src in enumerate(msg["sources"]):
                        st.markdown(f"**Chunk ID:** {src.get('chunk_id')}")
                        st.markdown(f"_{src.get('text')}_")
                        st.divider()

    # Chat Input
    if prompt := st.chat_input("Ask a construction question..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Generate assistant response
        with st.chat_message("assistant"):
            if not is_backend_ready:
                st.error("Backend services are not available. Please check configuration.")
            else:
                with st.spinner("Analyzing knowledge base..."):
                    try:
                        answer, sources = answer_question(prompt, backend="qdrant")
                        st.markdown(answer)
                        
                        if sources:
                            with st.expander("View Source Context"):
                                for idx, src in enumerate(sources):
                                    st.markdown(f"**Chunk ID:** {src.get('chunk_id')}")
                                    st.markdown(f"_{src.get('text')}_")
                                    st.divider()
                                    
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer,
                            "sources": sources
                        })
                    except Exception as e:
                        logger.error(f"Error answering question: {e}")
                        st.error("Sorry, an error occurred while processing your request.")

# ==========================================
# Page: Feedback
# ==========================================
elif page == "Feedback":
    st.title("📝 Feedback")
    st.markdown("Help us improve the assistant by providing your feedback on recent answers.")
    
    with st.form("feedback_form"):
        question = st.text_input("What was your question?")
        answer = st.text_area("What was the assistant's answer?")
        rating = st.radio("Was this helpful?", ["Yes", "No"])
        comments = st.text_area("Additional comments (optional)")
        
        submitted = st.form_submit_button("Submit Feedback")
        
        if submitted:
            feedback_dir = "feedback"
            os.makedirs(feedback_dir, exist_ok=True)
            feedback_file = os.path.join(feedback_dir, "feedback.csv")
            
            new_data = pd.DataFrame([{
                "timestamp": datetime.utcnow().isoformat(),
                "question": question,
                "answer": answer,
                "rating": rating,
                "comments": comments
            }])
            
            try:
                if os.path.exists(feedback_file):
                    existing_data = pd.read_csv(feedback_file)
                    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                else:
                    updated_data = new_data
                
                updated_data.to_csv(feedback_file, index=False)
                st.success("Thank you for your feedback!")
                logger.info("Feedback submitted successfully.")
            except Exception as e:
                logger.error(f"Failed to save feedback: {e}")
                st.error("Failed to save feedback. Please try again later.")

# ==========================================
# Page: About
# ==========================================
elif page == "About":
    st.title("ℹ️ About")
    
    st.markdown("""
    ### Purpose
    The Construction AI Assistant is a specialized Retrieval-Augmented Generation (RAG) system designed to answer complex construction domain questions using a vetted knowledge base.
    
    ### Current Capabilities
    - Audio transcription via **Whisper** (Backend utility)
    - Semantic search powered by **all-MiniLM-L6-v2** embeddings
    - Fast vector retrieval using **Qdrant**
    - High-quality reasoning and generation via **Groq Llama 3.3**
    
    ### Technology Stack
    - Frontend: Streamlit
    - LLM Provider: Groq
    - Embeddings: Sentence Transformers
    - Vector DB: Qdrant
    
    ### Future Roadmap
    The architecture is modularly designed to support an upcoming migration to an AWS-native stack without disrupting the user experience:
    - Whisper → **Amazon Transcribe**
    - all-MiniLM-L6-v2 → **Titan Embeddings**
    - Qdrant → **OpenSearch Serverless**
    - Groq → **Amazon Bedrock**
    """)
