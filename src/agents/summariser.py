import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from src.models import SummariserResult

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a data summarisation agent.
Your job is to produce a business-readable summary of CSV data with key statistics and actionable recommendations.
You must respond ONLY with valid JSON. No explanation, no markdown, no code fences.
JSON format:
{
    "summary": "one paragraph business-readable summary of the dataset",
    "key_stats": {
        "Total Rows": "15",
        "Categories": "4",
        "Date Range": "Jan 2024"
    },
    "recommendations": ["recommendation 1", "recommendation 2"]
}"""

def run(csv_preview: str, total_rows: int, context: str = "") -> SummariserResult:
    print("[Summariser Agent] Starting...")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Summarise this CSV data ({total_rows} total rows):\n\n{csv_preview}\n\nContext from other agents:\n{context}"
            }
        ]
    )

    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(raw)
        result = SummariserResult(**data)
        print(f"[Summariser Agent] Done — {len(result.recommendations)} recommendations generated")
        return result
    except Exception as e:
        print(f"[Summariser Agent] Error parsing response: {e}")
        return SummariserResult(
            summary="Could not parse response",
            key_stats={},
            recommendations=[]
        )