ALLOWED_FIELDS = {
    "patient_id",
    "age",
    "gender",
    "hospital_location",
    "smoker_status",
    "alcohol_use",
    "chronic_conditions"
}

ALLOWED_OPERATIONS = {
    "count",
    "find_one",
    "find_many",
    "group_count"
}


def validate_plan(plan: dict):
    op = plan.get("operation")

    if op not in ALLOWED_OPERATIONS:
        raise ValueError("Invalid operation")

    # validate filters
    for field in plan.get("filter", {}):
        if field not in ALLOWED_FIELDS:
            raise ValueError(f"Unsafe field: {field}")

    # validate aggregation
    if op == "group_count":
        if plan.get("group_by") != "hospital_location":
            raise ValueError("Unsafe group_by field")

    if op == "find_many":
        plan["limit"] = min(plan.get("limit", 10), 10)

    return plan

