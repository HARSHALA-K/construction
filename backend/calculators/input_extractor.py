import re


# ============================================================
# HELPER
# ============================================================

def _extract_numbers(text):
    """
    Extract all integer/decimal numbers from text.
    """
    return [
        float(x)
        for x in re.findall(r"\d+(?:\.\d+)?", text)
    ]


# ============================================================
# TILE INPUT EXTRACTOR
# ============================================================

def extract_tile_inputs(prompt):
    prompt = prompt.lower()

    result = {
        "room_length": None,
        "room_width": None,
        "tile_length": None,
        "tile_width": None,
        "room_unit": None,
        "tile_unit": None
    }

    # ---------------------------------------------------------
    # Find dimension pairs WITH their units
    # ---------------------------------------------------------
    dimension_matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*[x×*]\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(mm|millimeters?|cm|centimeters?|m|meters?|ft|feet|foot)\b",
        prompt
    )

    print("DEBUG TILE DIMENSION MATCHES:", dimension_matches)

    # ---------------------------------------------------------
    # ROOM
    # ---------------------------------------------------------
    if dimension_matches:
        result["room_length"] = float(dimension_matches[0][0])
        result["room_width"] = float(dimension_matches[0][1])
        result["room_unit"] = dimension_matches[0][2]

    # ---------------------------------------------------------
    # TILE
    # ---------------------------------------------------------
    if len(dimension_matches) >= 2:
        result["tile_length"] = float(dimension_matches[1][0])
        result["tile_width"] = float(dimension_matches[1][1])
        result["tile_unit"] = dimension_matches[1][2]

    # ---------------------------------------------------------
    # Missing fields
    # ---------------------------------------------------------
    missing = [
        key
        for key, value in result.items()
        if value is None
    ]

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    print("DEBUG TILE FINAL EXTRACTION:", result)

    return result
# ============================================================
# MATERIAL INPUT EXTRACTOR
# ============================================================

def extract_material_inputs(prompt: str):
    """
    Extract material calculation inputs.

    Required:
        length
        width
        thickness
        material_type
        calculation_type

    calculation_type:
        - brickwork
        - concrete
    """

    prompt = prompt.lower()

    result = {
        "length": None,
        "width": None,
        "thickness": None,
        "material_type": None,
        "calculation_type": None,
    }

    # --------------------------------------------------------
    # MATERIAL TYPE
    # --------------------------------------------------------

    material_match = re.search(
        r"\b("
        r"bricks?"
        r"|cement"
        r"|sand"
        r"|aggregate"
        r"|steel"
        r"|rebar"
        r"|reinforcement"
        r")\b",
        prompt
    )

    if material_match:
        material = material_match.group(1)

        if material in {"brick", "bricks"}:
            result["material_type"] = "brick"

        elif material in {
            "rebar",
            "reinforcement",
            "steel"
        }:
            result["material_type"] = "steel"

        else:
            result["material_type"] = material

   # --------------------------------------------------------
    # CALCULATION TYPE
    # --------------------------------------------------------

    # Brick / masonry context
    if (
        result["material_type"] == "brick"
        or re.search(
            r"\b("
            r"brickwork"
            r"|masonry"
            r"|brick wall"
            r"|brick walls"
            r")\b",
            prompt
        )
    ):
        result["calculation_type"] = "brickwork"

        # If the user said brickwork/masonry but did not
        # explicitly say "brick", infer the material category.
        if result["material_type"] is None:
            result["material_type"] = "brick"

    # Concrete context
    elif (
        result["material_type"] in {
            "cement",
            "sand",
            "aggregate"
        }
        or re.search(
            r"\b("
            r"concrete"
            r"|rcc"
            r"|concrete mix"
            r"|concrete work"
            r")\b",
            prompt
        )
    ):
        result["calculation_type"] = "concrete"

    # --------------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------------

    size_match = re.search(
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:x|\*|×)\s*"
        r"(\d+(?:\.\d+)?)",
        prompt
    )

    if size_match:
        result["length"] = float(
            size_match.group(1)
        )

        result["width"] = float(
            size_match.group(2)
        )

    # --------------------------------------------------------
    # EXPLICIT LENGTH
    # --------------------------------------------------------

    if result["length"] is None:

        length_match = re.search(
            r"(?:length|long)\s*"
            r"(?:is|=|:)?\s*"
            r"(\d+(?:\.\d+)?)",
            prompt
        )

        if length_match:
            result["length"] = float(
                length_match.group(1)
            )

    # --------------------------------------------------------
    # EXPLICIT WIDTH
    # --------------------------------------------------------

    if result["width"] is None:

        width_match = re.search(
            r"(?:width|wide)\s*"
            r"(?:is|=|:)?\s*"
            r"(\d+(?:\.\d+)?)",
            prompt
        )

        if width_match:
            result["width"] = float(
                width_match.group(1)
            )

    # --------------------------------------------------------
    # THICKNESS
    # --------------------------------------------------------

    thickness_match = re.search(
        r"(?:thickness|thick)\s*"
        r"(?:is|=|:)?\s*"
        r"(\d+(?:\.\d+)?)",
        prompt
    )

    if thickness_match:
        result["thickness"] = float(
            thickness_match.group(1)
        )

    # --------------------------------------------------------
    # FALLBACK FOR THREE NUMBERS
    # --------------------------------------------------------

    numbers = _extract_numbers(prompt)

    if len(numbers) >= 3:

        if result["length"] is None:
            result["length"] = numbers[0]

        if result["width"] is None:
            result["width"] = numbers[1]

        if result["thickness"] is None:
            result["thickness"] = numbers[2]

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    required_fields = [
        "length",
        "width",
        "thickness",
        "material_type",
        "calculation_type",
    ]

    missing = [
        field
        for field in required_fields
        if result[field] is None
    ]

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    return result


# ============================================================
# PROJECT INPUT EXTRACTOR
# ============================================================

def extract_project_inputs(prompt):
    """
    Extract project cost estimation inputs.

    Expected:
        area_sqft
        cost_per_sqft

    Examples:
        "Estimate cost for 2000 sqft at 2500 per sqft"
    """

    prompt = prompt.lower()

    result = {
        "area_sqft": None,
        "cost_per_sqft": None,
    }

    # --------------------------------------------------------
    # Area
    # --------------------------------------------------------

    area_match = re.search(
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:sq\.?\s*ft|sqft|square\s*feet|square\s*ft)",
        prompt
    )

    if area_match:
        result["area_sqft"] = float(area_match.group(1))

    # --------------------------------------------------------
    # Cost per sqft
    # --------------------------------------------------------

    cost_match = re.search(
        r"(?:₹|rs\.?|inr)?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:per|/)\s*"
        r"(?:sq\.?\s*ft|sqft|square\s*feet|square\s*ft)",
        prompt
    )

    if cost_match:
        result["cost_per_sqft"] = float(cost_match.group(1))

    # --------------------------------------------------------
    # Alternative wording:
    #
    # "2000 sqft with cost 2500"
    # --------------------------------------------------------

    if result["area_sqft"] is None:

        numbers = _extract_numbers(prompt)

        if numbers:
            result["area_sqft"] = numbers[0]

    if result["cost_per_sqft"] is None:

        cost_keyword_match = re.search(
            r"(?:cost|rate|price)"
            r"(?:\s+per\s+sqft)?"
            r"\s*(?:is|=|:)?\s*"
            r"(?:₹|rs\.?|inr)?\s*"
            r"(\d+(?:\.\d+)?)",
            prompt
        )

        if cost_keyword_match:
            result["cost_per_sqft"] = float(
                cost_keyword_match.group(1)
            )

    # --------------------------------------------------------
    # Missing
    # --------------------------------------------------------

    missing = [
        key
        for key, value in result.items()
        if value is None
    ]

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    return result


# ============================================================
# INTERIOR INPUT EXTRACTOR
# ============================================================

def extract_interior_inputs(prompt):
    """
    Extract interior estimation input.

    Supported:
        "Interior estimate for 1200 sqft"
        "How much for a 1500 square feet apartment?"

    Important:
        BHK numbers are NOT treated as area.
    """

    prompt = prompt.lower()

    result = {
        "area_sqft": None,
        "bhk": None
    }

    # --------------------------------------------------------
    # BHK
    # --------------------------------------------------------
    bhk_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*bhk\b",
        prompt
    )

    if bhk_match:
        result["bhk"] = int(float(bhk_match.group(1)))

    # --------------------------------------------------------
    # Explicit square feet
    # --------------------------------------------------------
    area_match = re.search(
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:sq\.?\s*ft|sqft|square\s*feet|square\s*ft)",
        prompt
    )

    if area_match:
        result["area_sqft"] = float(area_match.group(1))

    # --------------------------------------------------------
    # Missing
    # --------------------------------------------------------
    missing = []

    # Area is required for your CURRENT cost calculator
    if result["area_sqft"] is None:
        missing.append("area_sqft")

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    return result