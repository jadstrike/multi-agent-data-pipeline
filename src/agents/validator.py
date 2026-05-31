import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from src.models import ValidatorResult

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a data validation agent.
Your job is to validate CSV data for schema correctness, data types, null values, and constraint violations.
You must respond ONLY with valid JSON. No explanation, no markdown, no code fences.
JSON format:
{
    "schema_ok": true,
    "violations": ["list of validation failures found"],
    "passed_checks": ["list of checks that passed"],
    "completeness_score": 95.5
}"""

def run(csv_preview: str, total_rows: int) -> ValidatorResult:
    print("[Validator Agent] Starting...")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Validate this CSV data ({total_rows} total rows):\n\n{csv_preview}"
            }
        ]
    )

    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(raw)
        result = ValidatorResult(**data)
        print(f"[Validator Agent] Done — completeness score: {result.completeness_score}%")
        return result
    except Exception as e:
        print(f"[Validator Agent] Error parsing response: {e}")
        return ValidatorResult(
            schema_ok=False,
            violations=["Could not parse response"],
            passed_checks=[],
            completeness_score=0.0
        )