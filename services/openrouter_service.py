from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def analyze_threat(incident):
    risk_score = 10

    if "otp" in incident.lower():
        risk_score += 40

    if "password" in incident.lower():
        risk_score += 35

    if "bank" in incident.lower():
        risk_score += 20

    if "link" in incident.lower():
        risk_score += 15

    if "click" in incident.lower():
        risk_score += 15

    if "whatsapp" in incident.lower():
        risk_score += 10

    risk_score = min(risk_score, 100)
    response = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        max_tokens=250,
        temperature=0.2,
        messages=[
            {
    "role": "system",
    "content": """
You are a cybersecurity analyst.

Analyze the incident.

Return EXACTLY:

Threat Type: <value>
Risk Level: <Low/Medium/High/Critical>
Explanation: <one sentence>
Recommended Action: <one sentence>

Do not use markdown.
Do not use tables.
Do not use bullet points.
Do not add introductions.
Do not add conclusions.
"""
},
            {
                "role": "user",
                "content": incident
            }
        ]
    )

    ai_result = response.choices[0].message.content

    return f"Risk Score: {risk_score}/100\n\n{ai_result}"