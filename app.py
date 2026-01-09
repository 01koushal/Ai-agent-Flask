from flask import Flask, render_template, request, jsonify

from llm_planner import generate_plan
from validator import validate_plan
from executor import execute

import re
import traceback

app = Flask(__name__)


def ask_agent(question: str):
    try:
        # ---- Direct patient lookup (non-tech friendly) ----
        match = re.search(r'patient\s+(p?\d+)', question, re.IGNORECASE)
        if match:
            from db import collection

            pid = match.group(1).upper()
            if not pid.startswith("P"):
                pid = "P" + pid.zfill(6)

            patient = collection.find_one({"patient_id": pid}, {"_id": 0})
            if patient:
                return patient
            else:
                return "No patient found with that ID."

        # ---- LLM → plan ----
        plan = generate_plan(question)

        # ---- Validate plan ----
        safe_plan = validate_plan(plan)

        # ---- Execute ----
        result = execute(safe_plan)
        op = safe_plan["operation"]

        if op == "count":
            if result == 0:
                return "No matching patients were found."
            return f"Total patients found: {result}"

        if op == "find_one":
            return result or "No matching patient found."

        if op == "find_many":
            if not result:
                return "No matching patients were found."
            return {
                "count": len(result),
                "patients": result
            }

        return "I couldn’t understand the request clearly."

    except Exception:
        print("\n❌ INTERNAL ERROR:")
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
