import json
from google import genai

# ⚠️ HARD-CODED API KEY (FOR LOCAL TESTING ONLY)
client = genai.Client(
    api_key="AIzaSyDPGF_FYppP_Z5Szgrktk4hMuEjhIOvoro"
)

MODEL_NAME = "models/gemini-flash-latest"  # ✅ THIS IS THE KEY FIX

SYSTEM_PROMPT = """
You are an AI assistant that interprets NON-TECHNICAL human questions
and converts them into MongoDB query intent.

IMPORTANT:
- Users are NON-TECHNICAL
- They do NOT know database field names
- They speak in natural language

MEANINGS:
- "treated in <city>" → hospital_location
- "patients from <city>" → hospital_location
- "male / female" → gender
- "age above X" → age > X
- "age below X" → age < X
- "age X" → age == X
- If condition is not found in schema → still include it

RULES:
- Output ONLY valid JSON
- No explanations
- No markdown

ALLOWED FIELDS:
patient_id, age, gender, hospital_location,
smoker_status, alcohol_use, chronic_conditions

JSON FORMAT:
{
  "operation": "count | find_one | find_many",
  "filter": {},
  "limit": 10
}
SPECIAL AGGREGATION RULE:

If the user asks:
- "from which locations patients are more"
- "location wise patient count"
- "patients grouped by city"
- "which hospital location has more patients"

Then OUTPUT ONLY this JSON:

{
  "operation": "group_count",
  "group_by": "hospital_location"
}


"""

def generate_plan(question: str) -> dict:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=SYSTEM_PROMPT + "\nUser Question:\n" + question
    )

    text = response.text.strip()

    try:
        return json.loads(text)
    except Exception:
        raise ValueError(f"Invalid JSON from Gemini:\n{text}")
