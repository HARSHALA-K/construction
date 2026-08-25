import re

def estimate_interior(
        area_sqft
):
    painting = area_sqft * 25
    flooring = area_sqft * 120
    ceiling = area_sqft * 90

    kitchen = 200000

    total = (
            painting +
            flooring +
            ceiling +
            kitchen
    )

    return {
        "Painting Cost": painting,
        "Flooring Cost": flooring,
        "False Ceiling Cost": ceiling,
        "Modular Kitchen Cost": kitchen,
        "Total Interior Cost": total
    }

def extract_interior_inputs(prompt):

    prompt = prompt.lower()

    result = {
        "area_sqft": None
    }

    area_match = re.search(
        r'(\d+(?:\.\d+)?)\s*'
        r'(?:sqft|sq\s*ft|square\s*feet)',
        prompt
    )

    if area_match:
        result["area_sqft"] = float(
            area_match.group(1)
        )

    missing = [
        key
        for key, value in result.items()
        if value is None
    ]

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    return result