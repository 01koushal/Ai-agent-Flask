import json
from google import genai

client = genai.Client(
    api_key=""
)

MODEL = "models/gemini-flash-latest"

INTENT_PROMPT = """
Classify the user's message into ONE intent.

Intents:
- GREETING: greetings, casual talk, hello, hi
- THANKS: thanking messages
- HELP: asking what you can do
- DATA_QUERY: ANY question related to patients, diseases, conditions, counts, filters, hospitals, locations, age, gender, treatment, smoking, alcohol, or medical data
- OTHER: everything else

Rules:
- Ignore spelling mistakes
- Ignore grammar
- If the question mentions patients, diseases, hospitals, counts, or numbers → DATA_QUERY
- Return ONLY valid JSON

Format:
{
  "intent": "GREETING | THANKS | HELP | DATA_QUERY | OTHER"
}

"""

def classify_intent(message: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=INTENT_PROMPT + "\nUser message:\n" + message
    )

    try:
        data = json.loads(response.text.strip())
        return data.get("intent", "OTHER")
    except Exception:
        return "OTHER"



