import crewai.llms.cache as _crewai_cache

# Disable unsupported cache_breakpoint injection for Groq
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

import os
from importlib.metadata import version

print("LiteLLM version:", version("litellm"))
from crewai import Agent, Crew, Process, Task, LLM
from dotenv import load_dotenv

from backend.rag import answer_question


def get_rag_context(query: str):
    """
    Retrieve relevant construction knowledge using the existing
    Qdrant + RAG pipeline.
    """

    load_dotenv()

    try:

        answer, sources = answer_question(
            query,
            backend="qdrant",
            web_results=[],
            history=[]
        )

        context_parts = []

        # Add retrieved source chunks
        if sources:

            for idx, source in enumerate(sources, start=1):

                text = source.get("text", "")

                if text:
                    context_parts.append(
                        f"[Source {idx}]\n{text}"
                    )

        # If sources are unavailable, still provide the RAG answer
        if not context_parts and answer:

            context_parts.append(
                f"[RAG Answer]\n{answer}"
            )

        if context_parts:

            return "\n\n".join(context_parts)

        return "No relevant information was retrieved from the construction knowledge base."

    except Exception as e:

        print("RAG RETRIEVAL ERROR:", e)

        return (
            "No relevant information could be retrieved from "
            "the construction knowledge base."
        )

def create_construction_crew(query: str, rag_context: str):
    """
    Creates a CrewAI workflow for construction questions
    using Groq as the LLM provider.
    """

    # Use the same Groq API key already stored in .env
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    # IMPORTANT:
    # Replace this with the Groq model that is currently working
    # in your existing Construction AI Assistant.
    model_name = os.getenv(
        "CREWAI_MODEL",
        "groq/openai/gpt-oss-120b"
    )

    llm = LLM(
        model=model_name,
        api_key=groq_api_key,
        temperature=0.2,
    )

    researcher = Agent(
        role="Construction Researcher",
        goal=(
            "Research and identify the important construction information "
            "needed to answer the user's question."
        ),
        backstory=(
            "You are a construction-domain research assistant. "
            "You focus on materials, construction methods, quantities, "
            "costs, and project practices."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    analyst = Agent(
        role="Construction Analyst",
        goal=(
            "Analyze the research findings and produce a clear, practical, "
            "accurate construction answer."
            "When the user asks for a numerical estimate"
            " ALWAYS call the appropriate calculation tool."
            "NEVER perform the calculation yourself."
            "NEVER invent assumptions, quantities, prices, waste percentages, densities, or costs."
            "Use the EXACT value returned by the calculation tool."
            "Do not replace the tool result with your own calculation."
            " If required inputs are missing, ask the user for those inputs."
            "The calculation tool is the authoritative source for numerical results."
        ),
        backstory=(
            "You are a construction analyst who checks quantities, "
            "units, assumptions, and practical implications."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description=f"""
        Analyze the following construction question:

        {query}
        {rag_context}
         Use the retrieved knowledge as the primary source.
        Identify:
        1. What information is required.
        2. Important construction assumptions.
        3. Relevant materials, quantities, costs, or methods.
        4. Any missing information that would affect the answer.

        Do not invent project-specific information.
        """,
        expected_output=(
            "A concise research summary containing relevant construction "
            "facts, assumptions, and missing information."
        ),
        agent=researcher,
    )

    analysis_task = Task(
        description=f"""
        Using the researcher's findings, answer this construction question:

        {query}
        {rag_context}

        provide short answer dont include more detauls until said too
        Answer to the user question first and focus on whats asked
        keep the answer practical, accurate, and clear.
        Clearly state assumptions.
        Provide conciseand readable answers.
        Use appropriate construction units.
        If an exact calculation cannot be made because information is missing,
        clearly identify what is needed.
        """,
        expected_output=(
            "A clear construction answer to the user question "
            "give calculations where stated, and practical recommendations."
        ),
        agent=analyst,
        context=[research_task],
    )

    crew = Crew(
        agents=[researcher, analyst],
        tasks=[research_task, analysis_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew


def run_construction_crew(query: str):
    """Run the CrewAI construction workflow."""

    rag_context = get_rag_context(query)
    crew = create_construction_crew(query, rag_context)

    result = crew.kickoff()

    return str(result)


if __name__ == "__main__":
    question = input("Enter construction question: ")

    answer = run_construction_crew(question)

    print("\n========== CREWAI RESULT ==========\n")
    print(answer)
