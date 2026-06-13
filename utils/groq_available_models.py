"""Script to fetch and list available models from Groq API in a clean, readable format."""

import os
from typing import Any, Dict, List
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def fetch_groq_models(api_key: str) -> List[Dict[str, Any]]:
    """Fetches the list of models from the Groq API.

    Args:
        api_key: The Groq API key used for authentication.

    Returns:
        A list of dictionaries representing the available models.

    Raises:
        requests.RequestException: If the HTTP request fails.
    """
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data: Dict[str, Any] = response.json()
    return data.get("data", [])


def print_models_table(models: List[Dict[str, Any]]) -> None:
    """Prints a clean, formatted table of available models.

    Args:
        models: A list of model metadata dictionaries.
    """
    if not models:
        print("No models found.")
        return

    # Sort models by owner first, then by ID
    sorted_models = sorted(
        models, key=lambda m: (m.get("owned_by", "").lower(), m.get("id", "").lower())
    )

    # Table headers
    header_id = "Model ID"
    header_owner = "Developer"
    header_ctx = "Context Window"
    header_max = "Max Output Tokens"

    # Find the maximum width of the model ID column dynamically
    id_width = max(len(m.get("id", "")) for m in sorted_models)
    id_width = max(id_width, len(header_id)) + 2
    owner_width = max(len(m.get("owned_by", "")) for m in sorted_models)
    owner_width = max(owner_width, len(header_owner)) + 2

    ctx_width = 16
    max_width = 18

    # Print header
    header_format = (
        f"{{:<{id_width}}} {{:<{owner_width}}} {{:>{ctx_width}}} {{:>{max_width}}}"
    )
    row_format = (
        f"{{:<{id_width}}} {{:<{owner_width}}} {{:>{ctx_width},}} {{:>{max_width},}}"
    )

    print(header_format.format(header_id, header_owner, header_ctx, header_max))
    print("-" * (id_width + owner_width + ctx_width + max_width + 3))

    for model in sorted_models:
        model_id = model.get("id", "Unknown")
        owner = model.get("owned_by", "Unknown")
        ctx = model.get("context_window", 0)
        max_tokens = model.get("max_completion_tokens", 0)

        # Fallback values if None is returned
        if ctx is None:
            ctx = 0
        if max_tokens is None:
            max_tokens = 0

        print(row_format.format(model_id, owner, ctx, max_tokens))


def main() -> None:
    """Main execution function to load configurations, fetch and print models."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable is not set.")
        return

    try:
        models = fetch_groq_models(api_key)
        print_models_table(models)
    except requests.RequestException as e:
        print(f"Error fetching models from Groq API: {e}")


if __name__ == "__main__":
    main()
