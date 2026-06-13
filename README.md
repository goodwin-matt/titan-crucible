# Titan Research Agent

An AI-powered research agent designed for financial and regulatory search, built using **PydanticAI** and **Groq**. The agent autonomously decides which tool(s) to query based on a user's natural language question, processes the results, and synthesizes a structured answer with verified citations.

## Architecture Overview and Key Design Decisions

- **Framework**: Built with [PydanticAI](https://pydantic.dev/pydantic-ai) for robust type-safety, structured LLM outputs, and clean developer APIs.
- **Model**: Utilizes Groq's `llama-3.3-70b-versatile` model for fast, accurate response generation and tool orchestration.
- **Modular Search Tools**:
  - The tools adhere to a consistent interface defined in [base.py](file:///Users/goodwin/Matt/SideProjects/titan/tools/base.py) via the `BaseResearchTool` abstract class and Pydantic models `ToolResult` / `ToolResultItem`.
  - **arXiv Tool**: Mock search for academic papers (e.g., Basel III, credit risk modeling).
  - **FRED Tool**: Mock search for Federal Reserve Economic Data series (e.g., Primary Credit Rate/discount window, bank capitalization rates).
- **Answer Synthesis**: Enforces a strict system prompt that instructs the LLM to:
  1. Directly address the question.
  2. Synthesize tool results using inline citations.
  3. Clearly separate retrieved facts from model reasoning and inferences.
  4. Format the final output in distinct sections (`Executive Summary`, `Key Findings`, `Analysis & Reasoning`, `Sources & Citations`).

## Setup and Run Instructions

### Prerequisites

- **Python**: `>=3.13` (managed by `uv`)
- **API Key**: A Groq API key (from [Groq Console](https://console.groq.com/))

### Installation

1. Make sure you have `uv` installed. If not, install it using:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Clone the repository and navigate into it:
   ```bash
   git clone <repo-url> titan
   cd titan
   ```
3. Install dependencies and set up the virtual environment:
   ```bash
   uv sync
   ```

### Configuration

Create a `.env` file in the root of the project and add your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```


### Running the Agent

You can run the agent from the command line using `uv run`:

```bash
uv run python agent.py "What is the Federal Reserve's discount window and how does it work?"
```

Or:

```bash
uv run python agent.py "What are the Basel III capital requirements for banks?"
```

### Running Tests

Run the test suite (which uses `pytest` and mocks out the LLM calls via PydanticAI's `TestModel`):

```bash
uv run pytest
```

## Agent Performance Summary and Honest Assessment of Limitations

- **Performance**:
  - The agent successfully matches the intent of the query to the correct search tool (arXiv for academic/regulatory theory, FRED for macroeconomic series/rates).
  - Answers are synthesized cleanly with specific, structured citations.
- **Limitations**:
  - **Mock Data**: Currently, the search tools return high-quality mock data instead of calling live external APIs.
  - **Context Limits**: Since it's a single-turn architecture, very large tool outputs could exhaust the context window if not truncated or summarized first.
  - **Sequential Search**: The current version performs tools calls sequentially. If multiple tool calls are required, it can introduce latency.

## What You Would Do Differently with More Time

1. **Live API Integration**:
   - Connect [arxiv.py](file:///Users/goodwin/Matt/SideProjects/titan/tools/arxiv.py) to the official ArXiv XML API.
   - Connect [fred.py](file:///Users/goodwin/Matt/SideProjects/titan/tools/fred.py) to the official FRED JSON API (requires a FRED API key).
2. **Parallel Tool Invocation**:
   - Configure the agent to trigger multiple search tools concurrently to reduce latency.
3. **Advanced Retrieval (RAG)**:
   - Implement semantic search and chunking for academic papers so the agent only processes relevant paragraphs rather than full paper text.
4. **Caching Layer**:
   - Introduce redis or local disk caching for search tool queries to avoid redundant API requests and speed up response times.
5. **Agent Evaluation Suite**:
   - Build a benchmarking pipeline to grade answer accuracy, citation completeness, and hallucination rates.






