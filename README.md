# Titan Research Agent

An AI research agent designed for financial and regulatory search, built using **PydanticAI** and **Groq**. 

## Architecture Overview

The main orchestration approach I used was a simple ReAct agent. The main reason I did this was to keep things simple and give the agent more 
autonomy to choose tools and make decisions. I would evaluate this agent more fully and depending on its performance I would then consider 
using more complex agent orchestration approaches.

More details here:

- **Framework**: Built with [PydanticAI](https://pydantic.dev/pydantic-ai) for robust type-safety, structured LLM outputs, and clean developer APIs.
- **Model**: I used open source models via Groq API. I used an API instead of a locally-runnable model to provide better extensibility in the future for switching models. For example, if the company continued to grow and this tool was heavily utilized, using an API approach would allow switching to Claude or Open AI more easily. In general I'm not as familiar with open source models but here is what I found and settled on:
    - I started with llama-3.3-70b-versatile but it would consistently struggle with tool calling, something to investigate more. 
    - I tried openai/gpt-oss-120b due to positive reviews online but it was taking a long time.
    - I eventually settled on meta-llama/llama-4-scout-17b-16e-instruct based on reviews, speed and consistent performance I personally saw for this agent. 

- **Modular Search Tools**:
  - The tools adhere to a consistent interface defined in [base.py] via the `BaseResearchTool` abstract class and Pydantic models `ToolResult` / `ToolResultItem`.
- **Evaluation** Added an evaluation framwork for simple tests cases. I would have dug deeper on this with more test cases and an LLM as a judge.
- **Added json logging** provides logs for the latest trace


## Setup

### Prerequisites

- **Python**: `>=3.13` (managed by `uv`)
- **API Key**: A Groq API key (from [Groq Console](https://console.groq.com/)). FRED api key is needed as well.


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
FRED_API_KEY=your_fred_api_key_here
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
  - I ran each questions and recorded responses here along with an LLM as a judge response: `evaluation/eval_results.md`. In general and with my limited knowledge the performance seems to be doing well.
  When it comes to Multi-step reasoning one example where I saw better performance with multiple steps was for the question: "What is the current US unemployment rate and how has it changed over the past year?". The first time I implemented this, there was only one tool call to get the unemployment rate. With changes to the tool, the agent now calls it twice to also get the past years worth of data from Fred. Here is the example trace:
```
    "steps": [
    {
      "step_number": 1,
      "tool_selected": "search_fred",
      "tool_input": {
        "query": "US unemployment rate past year"
      },
      "request_url": "https://api.stlouisfed.org/fred/series/search?search_text=US%20unemployment%20rate%20past%20year&api_key=MASKED&file_type=json&limit=3",
    },
    {
      "step_number": 2,
      "tool_selected": "search_fred",
      "tool_input": {
        "query": "US unemployment rate"
      },
      "request_url": "https://api.stlouisfed.org/fred/series/search?search_text=US%20unemployment%20rate&api_key=MASKED&file_type=json&limit=3",
    }
  ],
```

  

- **Limitations**:
  - **Context Limits**: Since it's a single-turn architecture, very large tool outputs could exhaust the context window if not truncated or summarized first.
  - **Sequential Search**: The current version performs tools calls sequentially. If multiple tool calls are required, it can introduce latency.

## What You Would Do Differently with More Time

1. Stronger code review. I personally prefer to go line by line. I briefly reviewed all code but with more time I would go into more depth with the API calls, etc.
2. Production considerations
    - if this were something going into production I would consider things like parallel tool calls and caching layers to return common queries.
3. Logging
    - I would provide better logging. I'm just logging the basic json for the latest trace. I would consider using a db to store traces or probably better a third party observability platform like Langfuse or Braintrust.
3. Evaluation
    - The evaluation I attempted here is weak. Part of that is I don't have as strong banking research knowledge; including an SME would be key. In general though I would focus on more test cases and evaluating the llm as a judge (evaluating the evaluator). This takes time going through each case line by line.






