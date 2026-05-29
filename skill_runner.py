import anthropic
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def load_skill(skill_name: str) -> str:
    path = Path(f"skills/{skill_name}.md")
    return path.read_text(encoding="utf-8")

def run_skill(skill_name: str, user_input: str) -> str:
    system_prompt = load_skill(skill_name)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16384,
        system=system_prompt,
        messages=[{"role": "user", "content": user_input}]
    )
    return message.content[0].text
