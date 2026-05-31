import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from src.models import TransformerResult

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a data transformation agent.
Your job is to suggest and apply transformations to CSV data.
This includes: standardising date formats, normalising text casing, deriving new columns, encoding categoricals.
You must respond ONLY with valid JSON. No explanation, no markdown, no code fences.
JSON format:
{
    "transformations_applied": ["list of transformations applied"],
    "new_columns": ["list of new columns derived"],
    "rows_transformed": 10
}"""

def run(csv_preview: str, total_rows: int) -> TransformerResult:
    print("[Transformer Agent] Starting...")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Transform this CSV data ({total_rows} total rows):\n\n{csv_preview}"
            }
        ]
    )

    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(raw)
        result = TransformerResult(**data)
        print(f"[Transformer Agent] Done — {result.rows_transformed} rows transformed")
        return result
    except Exception as e:
        print(f"[Transformer Agent] Error parsing response: {e}")
        return TransformerResult(
            transformations_applied=["Could not parse response"],
            new_columns=[],
            rows_transformed=0
        )