import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from src.models import AnomalyResult

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an anomaly detection agent.
Your job is to find statistical outliers, duplicate records, suspicious values, price anomalies, and impossible values in CSV data.
You must respond ONLY with valid JSON. No explanation, no markdown, no code fences.
JSON format:
{
    "anomalies": ["list of anomalies found with row numbers"],
    "anomaly_count": 2,
    "anomaly_score": 4.5,
    "flagged_rows": [7, 11]
}"""

def run(csv_preview: str, total_rows: int) -> AnomalyResult:
    print("[Anomaly Agent] Starting...")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Detect anomalies in this CSV data ({total_rows} total rows):\n\n{csv_preview}"
            }
        ]
    )

    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(raw)
        result = AnomalyResult(**data)
        print(f"[Anomaly Agent] Done — {result.anomaly_count} anomalies found")
        return result
    except Exception as e:
        print(f"[Anomaly Agent] Error parsing response: {e}")
        return AnomalyResult(
            anomalies=["Could not parse response"],
            anomaly_count=0,
            anomaly_score=0.0,
            flagged_rows=[]
        )