import re

def classify_query(question: str) -> dict:
    q = question.lower().strip()

    # normalize common typos
    q = q.replace("how may", "how many")

    # ---------------- FIND ONE ----------------
    pid = re.search(r"(p\d+|patient\s*\d+)", q)
    if pid:
        num = re.search(r"\d+", pid.group()).group()
        return {
            "intent": "FIND_ONE",
            "patient_id": f"P{num.zfill(6)}"
        }

    # ---------------- COUNT ----------------
    if "how many" in q or "count" in q:

        # FEMALE FIRST (critical)
        if "female" in q:
            return {
                "intent": "COUNT",
                "filter": {"gender": "Female"}
            }

        if "male" in q:
            return {
                "intent": "COUNT",
                "filter": {"gender": "Male"}
            }

        # hospital locations (treated / lives / from / in)
        if "hyderabad" in q:
            return {
                "intent": "COUNT",
                "filter": {"hospital_location": "Hyderabad"}
            }

        if "chennai" in q:
            return {
                "intent": "COUNT",
                "filter": {"hospital_location": "Chennai"}
            }

        if "pune" in q:
            return {
                "intent": "COUNT",
                "filter": {"hospital_location": "Pune"}
            }

        # fallback: total count
        return {
            "intent": "COUNT",
            "filter": {}
        }

    # ---------------- LIST ----------------
    if "older than" in q:
        age = re.search(r"older than (\d+)", q)
        if age:
            return {
                "intent": "LIST",
                "filter": {"age": {"$gt": int(age.group(1))}}
            }

    return {"intent": "UNKNOWN"}
