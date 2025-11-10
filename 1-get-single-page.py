import os
import json
from docling.document_converter import DocumentConverter
from groq import Groq
from pydantic import BaseModel, HttpUrl
from typing import Literal # Needed for the structured output type

# Ensure the GROQ_API_KEY is set in your environment
client = Groq(
    #api_key=os.getenv('GROQ_API_KEY')
)
converter = DocumentConverter()

# Using the correct, recommended model for Groq API
MODEL = "llama-3.3-70b-versatile"

# --------------------------------------------------------------
# Define the output model
# --------------------------------------------------------------

class Source(BaseModel):
    # HttpUrl is good practice for URL validation
    url: HttpUrl

class Summary(BaseModel):
    """A model to hold the summarized text."""
    # The field description is crucial for the LLM to understand
    summary: str

# --------------------------------------------------------------
# Extract content from a web page
# --------------------------------------------------------------

test_url = "https://www.europarl.europa.eu/topics/en/article/20230601STO93804/eu-ai-act-first-regulation-on-artificial-intelligence"

source = Source(url=test_url)
print(f"Fetching and converting content from: {source.url}")

try:
    # docling returns a Document object which has an export_to_markdown method
    page_content = converter.convert(str(source.url))
    markdown_content = page_content.document.export_to_markdown()
except Exception as e:
    print(f"Error converting document: {e}")
    # Use a placeholder or exit if content extraction fails
    markdown_content = "Failed to extract content."

# print(markdown_content) # Uncomment if you want to see the raw markdown

# --------------------------------------------------------------
# Generate summary using Groq Chat Completions API
# --------------------------------------------------------------

# Define the structured response schema based on the Pydantic model
summary_schema = Summary.model_json_schema()

# The system prompt sets the context and goal
SYSTEM_PROMPT = "You are an assistant that retrieves the content of a web page and provides a short, concise summary of it. Your output MUST be a valid JSON object that strictly follows the provided schema."

# The user message contains the content to be summarized
USER_MESSAGE = f"Please give a short summary of this website content, focusing on the key points of the EU AI Act:\n\n{markdown_content}"

print("\nGenerating summary via Groq API...")

try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_MESSAGE},
        ],
        # --- Crucial change for Pydantic/JSON output ---
        response_format={
            "type": "json_object",
            "schema": summary_schema
        },
        temperature=0.0 # Use low temperature for summarization tasks
    )

    # Extract the JSON string from the response
    json_string = response.choices[0].message.content
    
    # Parse the JSON string and validate it against the Pydantic model
    summary_data = json.loads(json_string)
    result = Summary.model_validate(summary_data)

    # --------------------------------------------------------------
    # Print the result
    # --------------------------------------------------------------

    print("\n✅ Summary Generated:")
    print("-" * 20)
    print(result.summary)

except Exception as e:
    print(f"\n❌ An error occurred during API call or parsing: {e}")
    print("Please ensure your GROQ_API_KEY is set and the model name is correct.")