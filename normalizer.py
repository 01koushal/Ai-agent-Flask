def normalize_filter(filt: dict) -> dict:
    normalized = {}

    for key, value in filt.items():
        # text fields → case-insensitive
        if isinstance(value, str):
            normalized[key] = {
                "$regex": value,
                "$options": "i"
            }

        # age handling
        elif isinstance(value, dict):
            normalized[key] = value

        else:
            normalized[key] = value

    return normalized
