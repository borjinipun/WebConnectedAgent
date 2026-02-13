# Web Connected Agent

A Python-based research assistant for Dutch government organizations that leverages multiple data sources to answer questions about AI implementation policies and regulations.

## Overview

This project implements an intelligent agent that can:
- **Search a local AI implementation handbook** for policy questions
- **Fetch and analyze specific web pages** when provided with URLs
- **Perform web searches** on official Dutch government domains
- **Maintain conversation history** for multi-turn interactions
- **Provide structured answers** with citations and sources

The agent uses the Groq API with `llama-3.3-70b-versatile` model and supports structured JSON outputs via Pydantic models.

## Features

- 🤖 **Multi-tool Agent**: Dynamically chooses between handbook search, web page fetching, and web search
- 📚 **Local Handbook Support**: Integrates with [data/handbook.md](data/handbook.md) containing AI implementation guidelines for Dutch government
- 🔗 **Web Integration**: Fetches and converts web pages to markdown using Docling
- 📝 **Structured Responses**: Returns answers with citations and source attribution
- 💬 **Interactive Mode**: Run multi-turn conversations with conversation history
- 🔍 **Domain-Restricted Search**: Web searches limited to official government domains (`rijksoverheid.nl`, `tweedekamer.nl`, `cbs.nl`)

## Project Structure

```
.
├── main.py                      # Basic Groq API example
├── 1-get-single-page.py        # Web page fetching and summarization
├── 2-web-search.py             # Web search with citations
├── 3-search-handbook.py        # Handbook search with structured output
├── 4-search-agent.py           # Multi-tool search agent
├── 5-interactive-agent.py      # Interactive terminal agent
├── tools/
│   ├── __init__.py             # Package exports
│   ├── agent.py                # Main SearchAgent class
│   ├── models.py               # Pydantic data models (Citation, AgentAnswer)
│   ├── get_web_page.py         # Web page fetching utility
│   ├── search_handbook.py      # Handbook search utility
│   └── web_search.py           # Web search tool definition
├── data/
│   └── handbook.md             # AI implementation handbook content
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not committed)
└── .gitignore                  # Git ignore rules
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd WebConnectedAgent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
   Get your API key from [console.groq.com](https://console.groq.com)

## Usage

### Interactive Agent (Recommended)

Run the interactive terminal agent for multi-turn conversations:

```bash
python 5-interactive-agent.py
```

Features:
- Type your question and get answers with citations
- `quit` or `exit`: End conversation
- `reset`: Clear conversation history

Example queries:
- "What are the requirements for registering an AI system?"
- "What does the handbook say about human oversight?"
- "Search the web for current AI policies in Dutch government"

### Single Query Examples

**Example 1: Fetch and summarize a web page**
```bash
python 1-get-single-page.py
```

**Example 2: Web search with citations**
```bash
python 2-web-search.py
```

**Example 3: Search handbook only**
```bash
python 3-search-handbook.py
```

**Example 4: Multi-tool search agent**
```bash
python 4-search-agent.py
```

## Core Components

### [`tools/agent.py`](tools/agent.py) - SearchAgent Class

The main agent class that:
- Manages conversation history
- Dynamically calls appropriate tools
- Processes function calls and outputs
- Generates structured responses with citations

**Key methods:**
- `ask(query: str) -> AgentAnswer`: Ask a question and get a structured response
- `_call_function(name: str, args: dict) -> str`: Execute tool functions

### [`tools/models.py`](tools/models.py) - Data Models

Pydantic models for structured outputs:
- `Citation`: Text excerpt with URL or section reference
- `AgentAnswer`: Answer with list of citations

### [`tools/search_handbook.py`](tools/search_handbook.py) - Handbook Search

Searches the local [data/handbook.md](data/handbook.md) file for AI implementation policies.

### [`tools/get_web_page.py`](tools/get_web_page.py) - Web Page Fetching

Uses Docling library to fetch and convert web pages to markdown format.

### [`tools/web_search.py`](tools/web_search.py) - Web Search

Configures web search tool with domain restrictions for official government sources.

## Data Source

The [data/handbook.md](data/handbook.md) handbook covers:

- **General Principles**: Transparency, Accountability, Non-Discrimination, Privacy
- **Mandatory Steps**: Impact Assessment (IAMA), Algorithm Register, Security (BIO), Human Oversight
- **AI System Categories**: Low-risk, Medium-risk, High-risk classifications
- **Compliance**: Dutch Data Protection Authority (AP), Internal Audit
- **Best Practices**: Documentation, Training, Testing & Validation
- **Resources**: Contacts and useful links

## Requirements

See [requirements.txt](requirements.txt):

```
groq              # Groq API client
openai            # OpenAI API (fallback/comparison)
docling           # Web page to markdown conversion
pydantic          # Data validation and modeling
python-dotenv     # Environment variable management
transformers      # NLP transformers (optional)
```

## API Models Used

- **Primary**: `llama-3.3-70b-versatile` (Groq)
- **Fallback**: `gpt-4.1` (OpenAI) - optional

## Configuration

### System Prompt

Customize the agent's behavior by modifying the `DEFAULT_SYSTEM_PROMPT` in [`tools/agent.py`](tools/agent.py):

```python
DEFAULT_SYSTEM_PROMPT = """You are a research assistant for Dutch government organizations..."""
```

### Allowed Domains

Restrict web search to specific domains in [`tools/agent.py`](tools/agent.py):

```python
get_web_search_tool(
    allowed_domains=["rijksoverheid.nl", "tweedekamer.nl", "cbs.nl"]
)
```

## Examples

### Example 1: Direct Response (No Tool Call)

```
Query: What can you do?
Response: [Direct response without tool calls, no citations]
```

### Example 2: Handbook Search

```
Query: What are the requirements for registering an AI system in the Algorithm Register?
Response: [Handbook content retrieved, structured answer with citations from sections 2.2 and 3.x]
```

### Example 3: Web Page Fetch

```
Query: Can you fetch and summarize the EU AI Act?
Response: [Web page fetched and converted, summary provided with URL citation]
```

### Example 4: Web Search

```
Query: Find current AI policies on Dutch government websites
Response: [Web search executed on allowed domains, results synthesized with citations]
```

## Troubleshooting

### Common Issues

1. **"API key not found"**
   - Ensure `.env` file exists with `GROQ_API_KEY=your_key`
   - Check that key is valid at [console.groq.com](https://console.groq.com)

2. **"Handbook not found"**
   - Verify [data/handbook.md](data/handbook.md) exists
   - Check file path in [`tools/search_handbook.py`](tools/search_handbook.py)

3. **"Model not found" or API errors**
   - Verify model name: `llama-3.3-70b-versatile`
   - Check Groq API status and rate limits
   - Test with: `python main.py`

4. **Web page fetching fails**
   - Some sites may block automated access
   - Docling may not support certain formats
   - Try alternative URLs

## Future Enhancements

- [ ] Semantic search for handbook sections (RAG implementation)
- [ ] Support for additional government handbooks
- [ ] Conversation persistence (save/load history)
- [ ] Batch query processing
- [ ] Custom domain configuration UI
- [ ] Response caching
- [ ] Performance metrics and logging

## License

MIT License - see [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For questions about the handbook content, contact:
- **Bureau AI-Implementatie**: ai-implementatie@bzk.nl
- **Algorithm Register**: https://algoritmes.overheid.nl/
- **AP Oversight**: https://autoriteitpersoonsgegevens.nl/themas/algoritmes-ai

---

**Author**: Nipun Borji  
**Created**: 2025  
**Last Updated**: 2025