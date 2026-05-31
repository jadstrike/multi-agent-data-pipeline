import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from src.models import CleanerResult

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a data cleaning agent. 
Your job is to analyse CSV data and identify all cleaning issues.
You must respond ONLY with valid JSON. No explanation, no markdown, no code fences.
JSON format:
{
    "issues_fixed": ["list of issues you found and fixed"],
    "rows_affected": 5,
    "cleaned_columns": ["col1", "col2"]
}"""

def run(csv_preview: str, total_rows: int) -> CleanerResult:
    print("[Cleaner Agent] Starting...")
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Clean this CSV data ({total_rows} total rows):\n\n{csv_preview}"
            }
        ]
    )
    
    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    
    try:
        data = json.loads(raw)
        result = CleanerResult(**data)
        print(f"[Cleaner Agent] Done — {result.rows_affected} rows affected")
        return result
    except Exception as e:
        print(f"[Cleaner Agent] Error parsing response: {e}")
        return CleanerResult(
            issues_fixed=["Could not parse response"],
            rows_affected=0,
            cleaned_columns=[]
        )