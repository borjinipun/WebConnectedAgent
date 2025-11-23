import os
import json
from typing import List, Literal
from groq import Groq
from pydantic import BaseModel

from dotenv import load_dotenv


load_dotenv()
#print(os.getenv('GROQ_API_KEY'))
# Initialize the Groq client
client = Groq(
    api_key=os.getenv('GROQ_API_KEY'),)
# Using a commonly available Llama 3 model for Groq
MODEL = "llama-3.3-70b-versatile"
# --------------------------------------------------------------
# Define the output model (Pydantic)
# --------------------------------------------------------------

class Citation(BaseModel):
    """A specific text excerpt and its source URL."""
    text: str
    url: str

class SearchResult(BaseModel):
    """The final answer and a list of supporting citations."""
    answer: str
    citations: List[Citation]

# Generate the JSON schema from the Pydantic model
search_result_schema = SearchResult.model_json_schema()

# --------------------------------------------------------------
# Configure and Execute the Query
# --------------------------------------------------------------

query = "What are the current policies and regulations regarding AI implementation in Dutch government services, and what are the key requirements for public sector AI adoption? Use official Dutch government websites like rijksoverheid.nl, tweedekamer.nl, and cbs.nl as sources."

# The SYSTEM PROMPT is crucial for the LLM to understand its role and output format
SYSTEM_PROMPT = """You are a policy research assistant for Dutch governmental agencies. 
Your task is to answer the user's query and provide a list of citations.
Your answer MUST be a valid JSON object that strictly follows the provided schema.
For each piece of information in your answer, you MUST provide a corresponding citation (text excerpt and URL).
"""

print(f"Executing query using model: {MODEL}")

try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        # --- Crucial for structured Pydantic output ---
        response_format={
            "type": "json_object",
            "schema": search_result_schema
        },
        temperature=0.0 # Use low temperature for factual synthesis/summarization
    )

    # Extract the JSON string from the response
    json_string = response.choices[0].message.content
    
    # Parse the JSON string and validate it against the Pydantic model
    summary_data = json.loads(json_string)
    result = SearchResult.model_validate(summary_data)

    # --------------------------------------------------------------
    # Print the result
    # --------------------------------------------------------------

    print("\n✅ Search Result Generated:")
    print("-" * 30)
    print(result.model_dump_json(indent=2))

except Exception as e:
    print(f"\n❌ An error occurred during API call or parsing: {e}")
    print("Please ensure your GROQ_API_KEY is set and the model name is correct.")