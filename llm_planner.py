import json
from google import genai

# ⚠️ HARD-CODED API KEY (FOR LOCAL TESTING ONLY)
client = genai.Client(
    api_key="AIzaSyDDjSg9fvoZY6TCnBN2QPDhLU-jkaSyKmg"
)

MODEL_NAME = "models/gemini-flash-latest"  # ✅ THIS IS THE KEY FIX

SYSTEM_PROMPT = """
You are an AI assistant that interprets NON-TECHNICAL human questions
and decides whether database access is required.

TASK:
1. If the question can be answered without database access
   (greeting, small talk, capability questions) → answer directly.
2. If the question is about patient data → generate a MongoDB query plan.

IMPORTANT:
- Users are NON-TECHNICAL
- They do NOT know database field names
- They speak in natural language
- Ignore spelling and grammar mistakes

MEANINGS:
- "treated in <city>" → hospital_location
- "patients from <city>" → hospital_location
- "male / female" → gender
- "age above X" → age > X
- "age below X" → age < X
- "age X" → age == X
- ANY disease or medical condition (diabetes, arthritis, asthma, jaundice, etc.)
  → chronic_conditions (string match)

RULES (CRITICAL):
- NEVER invent new field names
- Use ONLY these fields:
  patient_id, age, gender, hospital_location,
  smoker_status, alcohol_use, chronic_conditions
- If a condition is not an exact field, map it to chronic_conditions
- Output ONLY valid JSON
- No explanations
- No markdown

WHEN DATABASE IS NOT REQUIRED:
Output ONLY this JSON:
{
  "use_db": false,
  "answer": "<natural language reply>"
}

WHEN DATABASE IS REQUIRED:
Output ONLY this JSON:
{
  "use_db": true,
  "operation": "count | find_one | find_many | group_count",
  "filter": {},
  "limit": 10
}

SPECIAL AGGREGATION RULE:
If the user asks:
- "from which locations patients are more"
- "location wise patient count"
- "patients grouped by city"
- "which hospital location has more patients"

Then output:
{
  "use_db": true,
  "operation": "group_count",
  "group_by": "hospital_location"
}



"""

def generate_plan(question: str) -> dict:
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=SYSTEM_PROMPT + "\nUser Question:\n" + question
        )

        text = response.text.strip()
        return json.loads(text)

    except Exception as e:
        # 🔴 Gemini overloaded / quota / network issue
        return {
            "error": "LLM_UNAVAILABLE",
            "message": str(e)
        }
