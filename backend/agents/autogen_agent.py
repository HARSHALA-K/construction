import os
import asyncio

from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from backend.rag import answer_question

from backend.calculators.input_extractor import (
    extract_tile_inputs,
    extract_material_inputs,
    extract_project_inputs,
    extract_interior_inputs,
)

from mcp_client.client import (
    get_tile_estimate,
    get_material_estimate,
    get_project_estimate,
    get_interior_estimate,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# RAG / QDRANT
# ============================================================

def construction_rag(query: str) -> str:
    """
    Retrieve relevant construction knowledge from the
    existing Qdrant + RAG pipeline.
    """

    try:

        answer, sources = answer_question(
            query,
            backend="qdrant",
            web_results=[],
            history=[]
        )

        if not sources:
            return (
                "No relevant information was found in "
                "the construction knowledge base."
            )

        context = []

        for index, source in enumerate(
            sources,
            start=1
        ):

            text = source.get("text", "")

            if text:

                context.append(
                    f"[QDRANT SOURCE {index}]\n{text}"
                )

        if context:
            return "\n\n".join(context)

        return (
            "No relevant information was found in "
            "the construction knowledge base."
        )

    except Exception as e:

        print("RAG ERROR:", e)

        return (
            "Unable to retrieve information from "
            "the construction knowledge base."
        )


# ============================================================
# GROQ MODEL
# ============================================================

def create_model_client():

    groq_api_key = os.getenv(
        "GROQ_API_KEY"
    )

    if not groq_api_key:

        raise ValueError(
            "GROQ_API_KEY is not configured."
        )

    model_name = os.getenv(
        "AUTOGEN_MODEL",
        "openai/gpt-oss-120b"
    )

    model_client = OpenAIChatCompletionClient(

        model=model_name,

        api_key=groq_api_key,

        base_url="https://api.groq.com/openai/v1",

        temperature=0.2,

        model_info={

            "vision": False,

            "function_calling": True,

            "json_output": False,

            "structured_output": False,

            "family": "unknown",

        },

        parallel_tool_calls=False,
    )

    return model_client


# ============================================================
# CREATE AUTOGEN AGENT
# ============================================================

def create_construction_agent():

    model_client = create_model_client()

    # --------------------------------------------------------
    # TILE TOOL
    # --------------------------------------------------------

    def tile_tool(
        room_length: float,
        room_width: float,
        tile_length: float,
        tile_width: float
    ) -> str:

        result = get_tile_estimate(
            room_length,
            room_width,
            tile_length,
            tile_width
        )

        return str(result)

    # --------------------------------------------------------
    # MATERIAL TOOL
    # --------------------------------------------------------

    def material_tool(
    length: float,
    width: float,
    thickness: float,
    material_type: str,
    calculation_type: str
) -> str:

        result = get_material_estimate(
            length,
            width,
            thickness,
            material_type,
            calculation_type
        )

        return str(result)

    # --------------------------------------------------------
    # PROJECT TOOL
    # --------------------------------------------------------

    def project_tool(
        area_sqft: float,
        cost_per_sqft: float
    ) -> str:

        result = get_project_estimate(
            area_sqft,
            cost_per_sqft
        )

        return str(result)

    # --------------------------------------------------------
    # INTERIOR TOOL
    # --------------------------------------------------------

    def interior_tool(
        area_sqft: float
    ) -> str:

        result = get_interior_estimate(
            area_sqft
        )

        return str(result)

    # --------------------------------------------------------
    # AUTOGEN AGENT
    # --------------------------------------------------------

    agent = AssistantAgent(

        name="construction_agent",

        model_client=model_client,

        tools=[

            construction_rag,

            tile_tool,

            material_tool,

            project_tool,

            interior_tool,

        ],

        system_message="""

You are a Construction AI Assistant.

You answer construction questions using:

1. The company's construction knowledge base
   through Qdrant/RAG.

2. Construction calculation tools.

============================================================
KNOWLEDGE QUESTIONS
============================================================

For questions about:

- construction methods
- construction stages
- materials
- vendors
- raw materials
- construction practices
- timelines
- builder knowledge
- apartment construction
- why a material is preferred

use the construction_rag tool.

The construction_rag tool retrieves information from
the existing Qdrant construction knowledge base.

The retrieved text is SOURCE MATERIAL.

Do not dump the raw Qdrant chunks to the user.

Read the retrieved information and answer the
original question directly.
. Ask only the next necessary question instead of asking all questions at once.
6. Use previous conversation context when interpreting short follow-up answers.
7. A short answer such as "2", "rural", "yes", or "brick" should be interpreted according to the question currently being asked.
8. Maintain the context of the current task until the required information has been collected.
9. Once all required information is available, use the appropriate MCP tool or calculator.
10. Do not perform construction calculations yourself when an available calculator/MCP tool should be used.
============================================================
CALCULATION QUESTIONS
============================================================

For numerical construction questions, use the appropriate calculation tool.
NEVER invent assumptions, quantities, prices, waste percentages, densities, or costs.
Available calculation tools:

- tile_tool
- material_tool
- project_tool
- interior_tool

Use the correct tool when the required values are available.

Do NOT perform the calculation yourself.

The calculation tools are connected to the project's existing deterministic calculation functions.

The tool result is the authoritative numerical result.

============================================================
TILE CALCULATION
============================================================

For tile questions, the required values are:

- room_length
- room_width
- tile_length
- tile_width

Do not invent missing values.

============================================================
MATERIAL CALCULATION
============================================================

For material questions, the required values are:

- length
- width
- thickness
- material_type
- calculation_type
Use "brickwork" for brick/masonry calculations.

Use "concrete" for cement, sand, or aggregate requirements
related to concrete.

Do not invent or assume calculation_type when the user's
question is ambiguous. Ask for clarification if necessary.
Do not invent missing values.

============================================================
PROJECT COST CALCULATION
============================================================

For project cost questions, the required values are:

- area_sqft
- cost_per_sqft

Do not invent missing values.

============================================================
INTERIOR CALCULATION
============================================================

For interior estimation, the required value is:

- area_sqft

Do not invent missing values.

============================================================
IMPORTANT
============================================================

Never fabricate numerical values.

Never replace a calculator result with your own arithmetic.

Never change the values returned by a calculator.

Do not return raw Qdrant source chunks.

Use retrieved knowledge as context and formulate
a concise answer.

============================================================
ANSWER STYLE
============================================================

Answer the user's question FIRST.

Keep answers SHORT and direct.

Do not provide unnecessary explanations.

Only provide additional detail if the user asks.

Use appropriate construction units.

Mention assumptions when necessary.
For land-related questions, relevant follow-ups may include:
- Is the land rural or urban?
- Is it agricultural or non-agricultural?

If information is missing, clearly ask for it.

Never fabricate construction facts.

"""
    )

    return agent, model_client


# ============================================================
# AUTOGEN EXECUTION
# ============================================================

async def _run_autogen(query: str):

    agent, model_client = create_construction_agent()

    try:

        # ====================================================
        # TILE
        # ====================================================

        tile_data = extract_tile_inputs(query)

        if tile_data["complete"]:

            print(
                "DEBUG TILE INPUTS:",
                tile_data
            )

            result = get_tile_estimate(

                tile_data["room_length"],

                tile_data["room_width"],

                tile_data["tile_length"],

                tile_data["tile_width"]

            )

            return (
                "### Tile Estimation\n\n"
                f"For a **"
                f"{tile_data['room_length']:.0f} × "
                f"{tile_data['room_width']:.0f} ft room** "
                f"using **"
                f"{tile_data['tile_length']:.0f} × "
                f"{tile_data['tile_width']:.0f} mm tiles**:\n\n"
                f"**Tiles required: {result}**\n\n"
                "Includes 10% wastage."
            )

        # ====================================================
        # MATERIAL
        # ====================================================

        material_data = extract_material_inputs(query)

        if (
            material_data["complete"]
            and material_data["calculation_type"] in {
                "brickwork",
                "concrete"
            }
        ):

            print(
                "DEBUG MATERIAL INPUTS:",
                material_data
            )

            result = get_material_estimate(

                material_data["length"],

                material_data["width"],

                material_data["thickness"],

                material_data["material_type"],

                material_data["calculation_type"]

            )

            return (
                "### Material Estimation\n\n"
                f"{result}"
            )

        # ====================================================
        # PROJECT
        # ====================================================

        project_data = extract_project_inputs(query)

        if (
            project_data["complete"]
            and any(
                word in query.lower()
                for word in [
                    "project cost",
                    "construction cost",
                    "construction estimate",
                    "cost estimate",
                    "cost per sqft",
                    "cost per sq ft"
                ]
            )
        ):

            print(
                "DEBUG PROJECT INPUTS:",
                project_data
            )

            result = get_project_estimate(

                project_data["area_sqft"],

                project_data["cost_per_sqft"]

            )

            return (
                "### Project Cost Estimate\n\n"
                f"Estimated Cost: **₹{result:,.0f}**"
            )

        # ====================================================
        # INTERIOR
        # ====================================================

        interior_data = extract_interior_inputs(query)

        if (
            interior_data["complete"]
            and any(
                word in query.lower()
                for word in [
                    "interior",
                    "interiors",
                    "interior cost"
                ]
            )
        ):

            print(
                "DEBUG INTERIOR INPUTS:",
                interior_data
            )

            result = get_interior_estimate(

                interior_data["area_sqft"]

            )

            answer = "### Interior Cost Estimate\n\n"

            if isinstance(result, dict):

                for name, value in result.items():

                    answer += (
                        f"**{name}:** "
                        f"₹{value:,.0f}\n\n"
                    )

            else:

                answer += str(result)

            return answer

        # ====================================================
        # NORMAL AUTOGEN
        # ====================================================

        result = await agent.run(
            task=query
        )

        # ----------------------------------------------------
        # Find final assistant response
        # ----------------------------------------------------

        for message in reversed(
            result.messages
        ):

            if not hasattr(
                message,
                "content"
            ):
                continue

            content = message.content

            if (
                isinstance(content, str)
                and content.strip()
            ):

                if content.startswith(
                    "[QDRANT SOURCE"
                ):
                    continue

                return content

        return str(result)

    finally:

        await model_client.close()


# ============================================================
# SYNCHRONOUS ENTRY POINT
# ============================================================

def run_autogen_agent(query: str):

    return asyncio.run(
        _run_autogen(query)
    )


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    question = input(
        "Enter construction question: "
    )

    answer = run_autogen_agent(
        question
    )

    print(
        "\n========== AUTOGEN RESULT ==========\n"
    )

    print(answer)