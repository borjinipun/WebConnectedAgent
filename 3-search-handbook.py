import os
import json
from pathlib import Path
from typing import List
from groq import Groq
from pydantic import BaseModel, Field

# Ensure GROQ_API_KEY is set in your environment
client = Groq(
   # api_key=os.getenv('GROQ_API_KEY')
   )

# Use a standard, high-performing Groq model
MODEL = "llama-3.3-70b-versatile"
HANDBOOK_PATH = Path(__file__).parent / "data" / "handbook.md"


# --------------------------------------------------------------
# Define the output models (Pydantic)
# --------------------------------------------------------------


class Citation(BaseModel):
    """A specific text excerpt and the section it came from."""
    text: str = Field(description="A brief text excerpt from the handbook.")
    section: str = Field(description="The section number (e.g., '2.1', '3.2').")


class HandbookAnswer(BaseModel):
    """The final, comprehensive answer supported by citations."""
    answer: str = Field(description="The clear, comprehensive answer to the user's question.")
    citations: List[Citation] = Field(description="A list of 2-4 key citations from the handbook content.")


# Define the JSON schema for structured output
HANDBOOK_ANSWER_SCHEMA = HandbookAnswer.model_json_schema()


# --------------------------------------------------------------
# Handbook search function (called as a tool)
# ------------------------------------------------------------------------------------------------
def search_handbook(query: str) -> str:
    """Retrieve the full AI implementation handbook content for the agent to interpret.

    Note: The query parameter is accepted but not used - we return the full handbook.
    In a real RAG application, you would implement semantic search to retrieve only relevant sections.

    Args:
        query: The user's question, used for context.

    Returns: The full handbook content as a string, or an error message.
    """
    if not HANDBOOK_PATH.exists():
        return "ERROR: Handbook file not found at expected path."

    try:
        handbook_content = HANDBOOK_PATH.read_text(encoding="utf-8")
        return handbook_content
    except Exception as e:
        return f"ERROR: Could not read handbook file: {e}"


# --------------------------------------------------------------
# Define the tool metadata for the Groq API
# ------------------------------------------------------------------------------------------------

# Tools must be provided in the format expected by the Groq SDK
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_handbook",
            "description": "Retrieve the AI implementation handbook content. Use this when the user asks questions about AI implementation requirements, regulations, or procedures for Dutch government organizations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question or search query."
                    },
                },
                "required": ["query"],
            },
        }
    }
]


# Map the function name to the actual Python function
AVAILABLE_FUNCTIONS = {
    "search_handbook": search_handbook,
}


# --------------------------------------------------------------
# Agent function that uses tools dynamically
# ------------------------------------------------------------------------------------------------


def ask_agent(query: str) -> HandbookAnswer:
    """Ask the agent a question. It will decide whether to search the handbook."""
    
    # 1. Initial Prompt and Tool Check
    messages = [{"role": "user", "content": query}]
    SYSTEM_PROMPT = "You are a helpful assistant for Dutch government organizations. You can help answer questions about AI implementation policies and regulations by using the 'search_handbook' tool. If asked what you can do, simply explain your capabilities without searching the handbook. Your final output MUST be a JSON object conforming to the HandbookAnswer schema."

    initial_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto", # Let the model decide if it needs the tool
        system_prompt=SYSTEM_PROMPT,
    )

    # 2. Check for Tool Call
    response_message = initial_response.choices[0].message
    
    if response_message.tool_calls:
        print(f"Tool called: {response_message.tool_calls[0].function.name}")
        
        # 3. Process Tool Calls and Get Function Output
        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name in AVAILABLE_FUNCTIONS:
                # Call the local Python function
                function_to_call = AVAILABLE_FUNCTIONS[function_name]
                function_response_text = function_to_call(**function_args)
                print(f"Handbook retrieved ({len(function_response_text)} chars)")
                
                # Append the tool's output back to the messages list
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response_text,
                    }
                )
            else:
                raise ValueError(f"Unknown function: {function_name}")
        
        # 4. Final Generation with Tool Output and Structured Format
        print("Generating final structured answer...")
        
        final_completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            system_prompt=f"{SYSTEM_PROMPT} Use the retrieved handbook content to answer the question. Provide a clear, comprehensive answer. Include only the most important citations (2-4 maximum) that reference the primary sections where the key information comes from. Each citation should include a brief text excerpt and the section number (e.g., '2.1', '3.2'). Do not cite every detail - only cite the main sources.",
            response_format={
                "type": "json_object",
                "schema": HANDBOOK_ANSWER_SCHEMA
            },
            temperature=0.0 # Low temp for factual/structured response
        )
        
        # Extract and parse the structured JSON response
        json_string = final_completion.choices[0].message.content
        parsed_data = json.loads(json_string)
        return HandbookAnswer.model_validate(parsed_data)
        
    else:
        # 5. Direct Response (No tool needed)
        print("No tool call needed, responding directly\n")
        
        # Generate structured output even for direct answers
        direct_completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            system_prompt=f"{SYSTEM_PROMPT} Answer directly. Since you did not use the tool, return an empty list for 'citations'.",
            response_format={
                "type": "json_object",
                "schema": HANDBOOK_ANSWER_SCHEMA
            },
            temperature=0.0
        )
        json_string = direct_completion.choices[0].message.content
        parsed_data = json.loads(json_string)
        return HandbookAnswer.model_validate(parsed_data)


# --------------------------------------------------------------
# Example queries
# --------------------------------------------------------------

example_queries = [
    "What can you do?",
    "What are the requirements for registering an AI system in the Algorithm Register?",
    "Do I need to perform an IAMA for a chatbot that answers citizen questions?",
]

# Test with example queries
if __name__ == "__main__":
    for query in example_queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print(f"{'=' * 60}\n")
        
        try:
            result = ask_agent(query)
            print(f"Answer: {result.answer}\n")
            if result.citations:
                print("Citations:")
                for citation in result.citations:
                    print(f"  Section {citation.section}: {citation.text[:100]}...")
            else:
                print("Citations: None (Direct response or no relevant policy found)")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("Ensure the 'data/handbook.md' file exists and your GROQ_API_KEY is set.")
        print()