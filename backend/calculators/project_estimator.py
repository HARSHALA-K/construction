import re

def estimate_cost(area,cost_per_sqft):

    return area*cost_per_sqft

def extract_project_inputs(prompt):

    prompt = prompt.lower()

    result = {
        "area_sqft": None,
        "cost_per_sqft": None
    }

    # Area:
    # 1500 sqft
    # 1500 sq ft
    # 1500 square feet

    area_match = re.search(
        r'(\d+(?:\.\d+)?)\s*'
        r'(?:sqft|sq\s*ft|square\s*feet)',
        prompt
    )

    if area_match:
        result["area_sqft"] = float(
            area_match.group(1)
        )

    # Cost:
    # 2500 per sqft
    # 2500/sqft
    # ₹2500 per sqft

    cost_match = re.search(
        r'(?:₹\s*)?'
        r'(\d+(?:\.\d+)?)\s*'
        r'(?:per\s*)?(?:sqft|sq\s*ft|/sqft)',
        prompt
    )

    if cost_match:
        result["cost_per_sqft"] = float(
            cost_match.group(1)
        )

    missing = [
        key
        for key, value in result.items()
        if value is None
    ]

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    return result