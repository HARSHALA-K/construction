import streamlit as st
import os
import asyncio
import pandas as pd
from datetime import datetime
from backend.router import route_query
# Import backend modules
from backend.calculators.tile import calculate_tiles
from backend.calculators.tile import extract_tile_inputs
from backend.calculators.material import calculate_bricks
from backend.calculators.material import extract_material_inputs
from backend.calculators.project_estimator import estimate_cost
from backend.calculators.project_estimator import extract_project_inputs
from backend.calculators.interior import estimate_interior
from backend.calculators.interior import extract_interior_inputs
from backend.intent_detector import detect_intent
from backend.utils import setup_logging
from backend.embedding import load_embedding_model
from backend.qdrant_db import connect_qdrant
from backend.llm import initialize_llm
from backend.rag import answer_question
# Import client functions
from mcp_client.client import get_tile_estimate
from mcp_client.client import get_material_estimate
from mcp_client.client import get_project_estimate
from mcp_client.client import get_interior_estimate
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
        @st.cache_resource
        def get_llm():
            return initialize_llm()

        @st.cache_resource
        def get_embedding():
            return load_embedding_model()

        @st.cache_resource
        def get_qdrant():
            return connect_qdrant()
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

if "tile_context" not in st.session_state:
    st.session_state.tile_context = {}

if "material_context" not in st.session_state:
    st.session_state.material_context = {}

if "project_context" not in st.session_state:
    st.session_state.project_context = {}

if "interior_context" not in st.session_state:
    st.session_state.interior_context = {}

if "pending_intent" not in st.session_state:
    st.session_state.pending_intent = None

if "pending_data" not in st.session_state:
    st.session_state.pending_data = {}

print("===== SESSION STATE CHECK =====")
print("Messages count:", len(st.session_state.messages))
print("Messages:", st.session_state.messages)
print("Pending intent:", st.session_state.pending_intent)
print("===============================")

# ==========================================
# Sidebar Navigation
# ==========================================
st.sidebar.image("assets/logo.png", use_container_width=True)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat", "Calculator", "Agents", "Feedback", "About"])

# ==========================================
# Page: Chat
# ==========================================

# -----------------------------------------
# Display previous conversation
# -----------------------------------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg.get("sources"):
            with st.expander("View Source Context"):
                for idx, src in enumerate(msg["sources"]):
                    st.markdown(
                        f"**Chunk ID:** {src.get('chunk_id', 'N/A')}"
                    )
                    st.markdown(
                        f"_{src.get('text', '')}_"
                    )
                    st.divider()

    # Chat Input
with st.form("chat_form", clear_on_submit=True):
    prompt = st.text_area(
        "Ask a construction question...",
        height=100,
        placeholder="Type your construction question here..."
    )

    submitted = st.form_submit_button("Send")

if submitted and prompt.strip():
        # -----------------------------------------
        # Add user message to chat history
        # -----------------------------------------
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "sources": []
        })
        print("===== AFTER USER MESSAGE =====")
        print("Added:", prompt)
        print("Messages count:", len(st.session_state.messages))
        print("Messages:", st.session_state.messages)
        print("==============================")

        with st.chat_message("user"):
            st.markdown(prompt)

        # -----------------------------------------
        # Generate assistant response
        # -----------------------------------------
        with st.chat_message("assistant"):

            if not is_backend_ready:
                st.error(
                    "Backend services are not available. "
                    "Please check configuration."
                )

            else:

                with st.spinner("Analyzing knowledge base..."):

                    try:

                        answer = ""
                        sources = []

                        # =====================================================
                        # 1. CHECK PREVIOUS/PENDING CALCULATOR
                        # =====================================================

                        pending_intent = st.session_state.get(
                            "pending_intent"
                        )

                        pending_data = st.session_state.get(
                            "pending_data",
                            {}
                        ).copy()

                        # =====================================================
                        # 2. DETECT INTENT
                        # =====================================================

                        intent = detect_intent(prompt)

                        print("=================================")
                        print("DEBUG PROMPT:", prompt)
                        print("DEBUG DETECTED INTENT:", intent)
                        print("DEBUG PENDING INTENT:", pending_intent)
                        print("=================================")

                        # =====================================================
                        # 3. IF WE ARE ALREADY IN A CALCULATOR CONVERSATION
                        # =====================================================

                        if pending_intent:

                            # Keep the previous calculator
                            intent = pending_intent

                            data = pending_data

                            print(
                                "DEBUG USING PENDING INTENT:",
                                intent
                            )

                        # =====================================================
                        # 4. TILE CALCULATOR
                        # =====================================================

                        if intent == "tile":

                            # -------------------------------------------------
                            # Keep previous data if this is a follow-up
                            # -------------------------------------------------

                            if pending_intent == "tile":
                                data = pending_data.copy()
                            else:
                                data = {}

                            # -------------------------------------------------
                            # Extract inputs using the existing tile extractor
                            # -------------------------------------------------

                            new_data = extract_tile_inputs(prompt)

                            print("DEBUG TILE EXTRACTED DATA:", new_data)

                            for key, value in new_data.items():

                                if key not in {
                                    "missing",
                                    "complete"
                                } and value is not None:

                                    data[key] = value

                            print("DEBUG TILE DATA AFTER EXTRACTION:", data)

                            # -------------------------------------------------
                            # Check missing values
                            # -------------------------------------------------

                            missing = []

                            if data.get("room_length") is None:
                                missing.append("room length")

                            if data.get("room_width") is None:
                                missing.append("room width")

                            if data.get("tile_length") is None:
                                missing.append("tile length")

                            if data.get("tile_width") is None:
                                missing.append("tile width")

                            print("DEBUG TILE FINAL DATA:", data)
                            print("DEBUG TILE MISSING:", missing)

                            # -------------------------------------------------
                            # Calculate only when ALL inputs exist
                            # -------------------------------------------------

                            if not missing:

                                result = get_tile_estimate(
                                    data["room_length"],
                                    data["room_width"],
                                    data["tile_length"],
                                    data["tile_width"]
                                )

                                answer = f"""
                        ### Tile Estimation

                        For a **{data["room_length"]:.0f} × {data["room_width"]:.0f} ft room**
                        using **{data["tile_length"]:.0f} × {data["tile_width"]:.0f} mm tiles**:

                        **Estimated tiles required: {result}**

                        Includes **10% wastage allowance**.
                        """

                                # Clear calculator conversation
                                st.session_state.pending_intent = None
                                st.session_state.pending_data = {}

                            # -------------------------------------------------
                            # Ask for missing information
                            # -------------------------------------------------

                            else:

                                st.session_state.pending_intent = "tile"
                                st.session_state.pending_data = data

                                answer = (
                                    "I need the following information:\n\n"
                                    + "\n".join(
                                        f"- {item.title()}"
                                        for item in missing
                                    )
                                )

                        # =====================================================
                        # 5. MATERIAL CALCULATOR
                        # =====================================================

                        elif intent == "material":

                            if pending_intent:
                                data = pending_data
                            else:
                                data = {}

                            new_data = extract_material_inputs(prompt)

                            print(
                                "DEBUG MATERIAL EXTRACTED DATA:",
                                new_data
                            )
                            # -------------------------------------------------
                            # FOLLOW-UP FALLBACK
                            # If we are already waiting for material data
                            #calculation_type is missing ask if its brickwork or concrete, if material_type is missing ask if its cement or sand,
                            #and take that answer and fill in as calculation_type or material_type respectively. If length, width, are present
                            # and thickness is the missing value,
                            # allow the user to reply with just a number.
                            # Example:
                            # Assistant: "What is the thickness?"
                            # User: "0.15"
                            # -------------------------------------------------

                            if pending_intent == "material":

                                previous_data = pending_data.copy()

                                thickness_missing = (
                                    previous_data.get("length") is not None
                                    and previous_data.get("width") is not None
                                    and previous_data.get("thickness") is None
                                )

                                if thickness_missing:

                                    import re

                                    number_match = re.fullmatch(
                                        r"\s*(\d+(?:\.\d+)?)\s*",
                                        prompt
                                    )

                                    if number_match:
                                        new_data["thickness"] = float(
                                            number_match.group(1)
                                        )

                            for key, value in new_data.items():

                                if key not in {
                                    "missing",
                                    "complete"
                                } and value is not None:

                                    data[key] = value

                            missing = []

                            if data.get("length") is None:
                                missing.append("length")

                            if data.get("width") is None:
                                missing.append("width")

                            if data.get("thickness") is None:
                                missing.append("thickness")

                            if data.get("material_type") is None:
                                missing.append("material type")

                            if data.get("calculation_type") is None:
                                missing.append("calculation type")

                            print(
                                "DEBUG MATERIAL FINAL DATA:",
                                data
                            )

                            if not missing:

                                result = get_material_estimate(
                                    data["length"],
                                    data["width"],
                                    data["thickness"],
                                    data.get("material_type"),
                                    data["calculation_type"]
                                )

                                answer = f"""
### Material Estimation

Estimated material requirement:

{result}
"""

                                st.session_state.pending_intent = None
                                st.session_state.pending_data = {}

                            else:

                                st.session_state.pending_intent = "material"
                                st.session_state.pending_data = data

                                answer = (
                                    "I need the following information:\n\n"
                                    + "\n".join(
                                        f"- {item.title()}"
                                        for item in missing
                                    )
                                )

                        # =====================================================
                        # 6. PROJECT COST ESTIMATOR
                        # =====================================================

                        elif intent == "project":

                            if pending_intent:
                                data = pending_data
                            else:
                                data = {}

                            new_data = extract_project_inputs(prompt)

                            print(
                                "DEBUG PROJECT EXTRACTED DATA:",
                                new_data
                            )

                            for key, value in new_data.items():

                                if key not in {
                                    "missing",
                                    "complete"
                                } and value is not None:

                                    data[key] = value

                            missing = []

                            if data.get("area_sqft") is None:
                                missing.append("area in sqft")

                            if data.get("cost_per_sqft") is None:
                                missing.append("cost per sqft")

                            print(
                                "DEBUG PROJECT FINAL DATA:",
                                data
                            )

                            if not missing:

                                result = get_project_estimate(
                                    data["area_sqft"],
                                    data["cost_per_sqft"]
                                )

                                answer = f"""
                                ### Project Cost Estimate

                                Construction Area: **{data["area_sqft"]:.0f} sqft**

                                Cost per sqft: **₹{data["cost_per_sqft"]:,.0f}**

                                ### Estimated Cost

                                **₹{result:,.0f}**
                                """

                                st.session_state.pending_intent = None
                                st.session_state.pending_data = {}

                            else:

                                st.session_state.pending_intent = "project"
                                st.session_state.pending_data = data

                                answer = (
                                    "I need the following information:\n\n"
                                    + "\n".join(
                                        f"- {item.title()}"
                                        for item in missing
                                    )
                                )

                        # =====================================================
                        # 7. INTERIOR ESTIMATOR
                        # =====================================================

                        elif intent == "interior":

                            if pending_intent:
                                data = pending_data
                            else:
                                data = {}

                            new_data = extract_interior_inputs(prompt)

                            print(
                                "DEBUG INTERIOR EXTRACTED DATA:",
                                new_data
                            )

                            for key, value in new_data.items():

                                if key not in {
                                    "missing",
                                    "complete"
                                } and value is not None:

                                    data[key] = value

                            missing = []

                            if data.get("area_sqft") is None:
                                missing.append("area in sqft")

                            print(
                                "DEBUG INTERIOR FINAL DATA:",
                                data
                            )

                            if not missing:

                                result = get_interior_estimate(
                                    data["area_sqft"]
                                )

                                answer = "### Interior Cost Estimate\n\n"

                                for name, value in result.items():

                                    answer += (
                                        f"**{name}:** "
                                        f"₹{value:,.0f}\n\n"
                                    )

                                st.session_state.pending_intent = None
                                st.session_state.pending_data = {}

                            else:

                                st.session_state.pending_intent = "interior"
                                st.session_state.pending_data = data

                                answer = (
                                    "I need the following information:\n\n"
                                    + "\n".join(
                                        f"- {item.title()}"
                                        for item in missing
                                    )
                                )   

                       
                        else:
                            web_results = []
                            answer, sources = answer_question(
                                prompt,
                                backend="qdrant",
                                web_results=web_results,
                                history=st.session_state.messages
                            )
                            print("debug rag used")
                            logger.info(
                                f"Detected new intent: {intent}"
                                    )
                    
                        st.markdown(answer)
                        st.session_state.messages.append({
                                                    "role": "assistant", 
                                                    "content": answer,
                                                    "sources": sources
                                                })
                        if sources:
                            with st.expander("View Source Context"):
                                for idx, src in enumerate(sources):
                                    st.markdown(f"**Chunk ID:** {src.get('chunk_id')}")
                                    st.markdown(f"_{src.get('text')}_")
                                    st.divider()
                                    
                        
                        print("===== AFTER ASSISTANT MESSAGE =====")
                        print("Messages count:", len(st.session_state.messages))
                        print("Messages:", st.session_state.messages)
                        print("====================================")
                    except Exception as e:
                        import traceback

                        st.error(str(e))
                        st.code(traceback.format_exc())

                        logger.error(traceback.format_exc())

# ==========================================
# Page: Calculator
# ==========================================
elif page == "Calculator":
    st.title("🧮 Calculator")
    st.markdown("Use this calculator for quick construction-related calculations.")
    calculator_type = st.sidebar.radio(
        "Choose Calculator",
        [
            "Tile Calculator",
            "Material Calculator",
            "Project Estimator",
            "Interior Estimator",
        ]
    )
    if calculator_type == "Tile Calculator":
            st.subheader("🧱 Tile Calculator")

            room_length = st.number_input("Room Length (ft)", min_value=0.0)
            room_width = st.number_input("Room Width (ft)", min_value=0.0)

            tile_length = st.number_input("Tile Length (mm)", value=600)
            tile_width = st.number_input("Tile Width (mm)", value=600)

            if st.button("Calculate Tiles"):

                room_area_m2 = (room_length * 0.3048) * (room_width * 0.3048)

                tile_area = (
                    tile_length / 1000
                ) * (
                    tile_width / 1000
                )

                tiles_required = room_area_m2 / tile_area

                tiles_required = int(tiles_required * 1.10) + 1

                st.success(
                f"Tiles Required (including 10% wastage): {tiles_required}"
                )

    elif calculator_type == "Material Calculator":
        st.subheader("🏗️ Material Calculator")

        area = st.number_input(
            "Built-up Area (sq ft)",
            min_value=0.0
        )

        if st.button("Estimate Materials"):

            cement = area * 0.4
            sand = area * 0.6
            aggregate = area * 0.8
            steel = area * 0.004

            st.write(f"🧱 Cement Bags: {cement:.0f}")
            st.write(f"🏖️ Sand: {sand:.0f} cu.ft")
            st.write(f"🪨 Aggregate: {aggregate:.0f} cu.ft")
            st.write(f"🔩 Steel: {steel:.2f} tons")

    elif calculator_type == "Project Estimator":
            st.subheader("🏢 Project Cost Estimator")

            area = st.number_input(
                "Construction Area (sq ft)",
                min_value=0.0
            )

            quality = st.selectbox(
                "Construction Quality",
                [
                    "Economy",
                    "Standard",
                    "Premium",
                    "Luxury"
                ]
            )

            rates = {
                "Economy": 1800,
                "Standard": 2500,
                "Premium": 3500,
                "Luxury": 5000
            }

            if st.button("Estimate Project Cost"):

                cost = area * rates[quality]

                st.success(
                    f"Estimated Cost: ₹{cost:,.0f}"
                )

    elif calculator_type == "Interior Estimator":
            st.subheader("🎨 Interior Cost Estimator")

            bhk = st.selectbox(
                "Apartment Type",
                [
                    "1 BHK",
                    "2 BHK",
                    "3 BHK",
                    "4 BHK"
                ]
            )

            style = st.selectbox(
                "Interior Style",
                [
                    "Basic",
                    "Premium",
                    "Luxury"
                ]
            )

            pricing = {
                ("1 BHK", "Basic"): 400000,
                ("1 BHK", "Premium"): 700000,
                ("1 BHK", "Luxury"): 1200000,

                ("2 BHK", "Basic"): 600000,
                ("2 BHK", "Premium"): 1000000,
                ("2 BHK", "Luxury"): 1800000,

                ("3 BHK", "Basic"): 800000,
                ("3 BHK", "Premium"): 1500000,
                ("3 BHK", "Luxury"): 2500000,
            }

            if st.button("Estimate Interior Cost"):

                cost = pricing.get((bhk, style), 0)

                st.success(
                    f"Estimated Interior Cost: ₹{cost:,.0f}"
                )

#page:agents
elif page == "Agents":
    st.title("🤖 AI Agents")

    agent_type = st.selectbox(
        "Choose Agent Framework",
        ["CrewAI", "AutoGen"]
    )

    prompt = st.text_area(
        "Enter a construction question",
        placeholder="How many tiles are needed for a 10x12 ft room using 600x600 mm tiles?"
    )

    if st.button("Run Agent") and prompt:
        # call corresponding agent
         with st.spinner("Agent is thinking..."):

            try:

                # ==========================================
                # CrewAI
                # ==========================================

                if agent_type == "CrewAI":

                    from backend.agents.crewai_agent import run_construction_crew

                    result = run_construction_crew(prompt)

                    st.subheader("CrewAI Response")

                    st.markdown(result)

                # ==========================================
                # AutoGen
                # ==========================================

                elif agent_type == "AutoGen":

                    from backend.agents.autogen_agent import run_autogen_agent
                    answer = run_autogen_agent(
                        prompt
                    )
                    st.subheader("🤖 AutoGen Response")

                    st.markdown(answer)

            except Exception as e:

                st.error("Agent execution failed.")

                st.code(
                    str(e)
                )
        

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
