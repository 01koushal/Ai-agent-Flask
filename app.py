from flask import Flask, render_template, request, jsonify

from llm_planner import generate_plan
from validator import validate_plan
from executor import execute
from intent_classifier import classify_intent

import re
import traceback

app = Flask(__name__)


def ask_agent(question: str):
    try:
        q = question.lower().strip()
        if q in ["hi", "hello", "hey", "hii", "hlo"]:
            return "Hello 👋 How can I help you with patient data today?"
        if q in ["thanks", "thank you", "thx"]:
            return "You're welcome 😊"

        # ---------- AI INTENT CLASSIFICATION ----------
        intent = classify_intent(question)

        # ⛔ STOP HERE FOR NON-DATA INTENTS
        if intent == "GREETING":
            return "Hello 👋 How can I help you with patient data today?"

        if intent == "THANKS":
            return "You're welcome 😊"

        if intent == "HELP":
            return (
                "You can ask things like:\n"
                "- How many patients are there?\n"
                "- Female patients from Hyderabad\n"
                "- Patient P000123\n"
                "- Location wise patient count"
            )

        # ---------- DIRECT PATIENT ID LOOKUP ----------
        match = re.search(r'patient\s+(p?\d+)', question, re.IGNORECASE)
        if match:
            from db import collection

            pid = match.group(1).upper()
            if not pid.startswith("P"):
                pid = "P" + pid.zfill(6)

            patient = collection.find_one({"patient_id": pid}, {"_id": 0})
            return patient or "No patient found with that ID."

        # ---------- LLM → QUERY PLAN ----------
        plan = generate_plan(question)
        if plan.get("error") == "LLM_UNAVAILABLE":
            return (
                "The AI service is currently busy 😓\n"
                "Please try again in a few seconds."
            )
        if plan.get("use_db") is False:
            return plan.get("answer")
        plan.pop("use_db", None)

        safe_plan = validate_plan(plan)
        result = execute(safe_plan)

        op = safe_plan["operation"]

        if op == "group_count":
            return result

        if op == "count":
            return (
                "No matching patients were found."
                if result == 0
                else f"Total patients found: {result}"
            )

        if op == "find_one":
            return result or "No matching patient found."

        if op == "find_many":
            return (
                "No matching patients were found."
                if not result
                else {"count": len(result), "patients": result}
            )

        return "I couldn’t understand the request clearly."

    except Exception:
        traceback.print_exc()
        return "Sorry, I couldn’t process that request. Please try rephrasing."

# ---------------- FLASK ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Please ask a question."})

    answer = ask_agent(question)
    return jsonify({"answer": answer})


if __name__ == "__main__":
    print("✅ Using MongoDB Atlas")
    app.run(debug=True)
