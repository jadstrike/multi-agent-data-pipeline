import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an action item extraction agent.
Your job is to extract all action items, decisions, deadlines, and follow-ups from document text.
You must respond ONLY with valid JSON. No explanation, no markdown, no code fences.
JSON format:
{
    "action_items": ["action1", "action2"],
    "decisions_made": ["decision1", "decision2"],
    "deadlines": ["deadline1 - date", "deadline2 - date"],
    "follow_ups": ["follow up1", "follow up2"],
    "owners": ["person/team responsible1", "person/team responsible2"],
    "priority_actions": ["most urgent action1", "most urgent action2"],
    "total_actions": 8
}"""

class ActionExtractorResult:
    def __init__(self, **kwargs):
        self.action_items = kwargs.get("action_items", [])
        self.decisions_made = kwargs.get("decisions_made", [])
        self.deadlines = kwargs.get("deadlines", [])
        self.follow_ups = kwargs.get("follow_ups", [])
        self.owners = kwargs.get("owners", [])
        self.priority_actions = kwargs.get("priority_actions", [])
        self.total_actions = kwargs.get("total_actions", 0)

    def model_dump(self):
        return self.__dict__

def run(text_preview: str, total_pages: int) -> ActionExtractorResult:
    print("[Action Extractor Agent] Starting...")

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Extract all action items from this document ({total_pages} pages):\n\n{text_preview}"
            }
        ]
    )

    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(raw)
        result = ActionExtractorResult(**data)
        print(f"[Action Extractor Agent] Done — {result.total_actions} actions found")
        return result
    except Exception as e:
        print(f"[Action Extractor Agent] Error: {e}")
        return ActionExtractorResult(
            action_items=["Could not parse response"],
            total_actions=0
        )