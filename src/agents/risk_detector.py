import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a document risk detection agent.
Your job is to identify risks, sensitive data, PII, compliance issues and red flags in documents.
You must respond ONLY with valid JSON. No explanation, no markdown, no code fences.
JSON format:
{
    "pii_detected": true,
    "pii_types": ["names", "emails", "phone numbers"],
    "compliance_risks": ["GDPR risk - personal data present", "risk2"],
    "legal_risks": ["unsigned contract clause", "risk2"],
    "financial_risks": ["large payment terms", "risk2"],
    "overall_risk_score": 7.5,
    "risk_level": "high",
    "recommendations": ["recommendation1", "recommendation2"]
}"""

class RiskDetectorResult:
    def __init__(self, **kwargs):
        self.pii_detected = kwargs.get("pii_detected", False)
        self.pii_types = kwargs.get("pii_types", [])
        self.compliance_risks = kwargs.get("compliance_risks", [])
        self.legal_risks = kwargs.get("legal_risks", [])
        self.financial_risks = kwargs.get("financial_risks", [])
        self.overall_risk_score = kwargs.get("overall_risk_score", 0.0)
        self.risk_level = kwargs.get("risk_level", "low")
        self.recommendations = kwargs.get("recommendations", [])

    def model_dump(self):
        return self.__dict__

def run(text_preview: str, total_pages: int) -> RiskDetectorResult:
    print("[Risk Detector Agent] Starting...")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Detect risks in this document ({total_pages} pages):\n\n{text_preview}"
            }
        ]
    )

    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(raw)
        result = RiskDetectorResult(**data)
        print(f"[Risk Detector Agent] Done — risk level: {result.risk_level}, score: {result.overall_risk_score}/10")
        return result
    except Exception as e:
        print(f"[Risk Detector Agent] Error: {e}")
        return RiskDetectorResult(
            pii_detected=False,
            overall_risk_score=0.0,
            risk_level="unknown",
            recommendations=["Could not parse response"]
        )