import re

def calculate_bricks(length,height,thickness):

    volume = length*height*thickness

    bricks = volume*500

    return round(bricks)

def extract_material_inputs(prompt):

    prompt = prompt.lower()

    result = {
        "length": None,
        "width": None,
        "thickness": None
    }

    # Supports:
    # 20x10
    # 20 x 10
    # 20*10
    # 20 x 10 wall

    size_match = re.search(
        r'(\d+(?:\.\d+)?)\s*(?:x|\*|×)\s*'
        r'(\d+(?:\.\d+)?)',
        prompt
    )

    if size_match:
        result["length"] = float(size_match.group(1))
        result["width"] = float(size_match.group(2))

    thickness_match = re.search(
        r'thickness\s*(?:is\s*)?'
        r'(\d+(?:\.\d+)?)',
        prompt
    )

    if thickness_match:
        result["thickness"] = float(
            thickness_match.group(1)
        )

    missing = [
        key
        for key, value in result.items()
        if value is None
    ]

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    return result