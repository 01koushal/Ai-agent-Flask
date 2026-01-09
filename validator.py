ALLOWED_FIELDS = {
    "patient_id",
    "age",
    "gender",
    "hospital_location",
    "smoker_status",
    "alcohol_use",
    "chronic_conditions"
}

ALLOWED_OPERATIONS = {"count", "find_one", "find_many"}

def validate_plan(plan: dict):
    if plan["operation"] not in ALLOWED_OPERATIONS:
        raise ValueError("Invalid operation")

    for field in plan.get("filter", {}):
        if field not in ALLOWED_FIELDS:
            raise ValueError(f"Unsafe field: {field}")

    if plan["operation"] == "find_many":
        plan["limit"] = min(plan.get("limit", 10), 10)

    return plan
