from db import collection
from normalizer import normalize_filter

def execute(plan: dict):
    op = plan["operation"]
    filt = normalize_filter(plan.get("filter", {}))

    if op == "count":
        return collection.count_documents(filt)

    if op == "find_one":
        return collection.find_one(
        filt,
        {
            "_id": 0,
            "embedding": 0,
            "text_for_embedding": 0
        }
    )


    if op == "find_many":
        return list(
        collection.find(
            filt,
            {
                "_id": 0,
                "embedding": 0,
                "text_for_embedding": 0
            }
        ).limit(plan.get("limit", 10))
    )

    if op == "group_count":
        field = plan["group_by"]

    pipeline = [
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    result = list(collection.aggregate(pipeline))
    return {r["_id"]: r["count"] for r in result}

