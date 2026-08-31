import math
import re

def calculate_tiles(
    room_length,
    room_width,
    tile_length,
    tile_width,
    room_unit="ft",
    tile_unit="mm",
    waste_percent=10
):
    """
    Calculate the number of tiles required.

    Converts both room and tile dimensions to metres
    before calculating area.

    Supported units:
        m, metre, meter
        ft, feet, foot
        mm, millimeter
        cm, centimeter
    """

    # ---------------------------------------------------------
    # UNIT CONVERSION TO METRES
    # ---------------------------------------------------------

    unit_to_m = {
        "m": 1,
        "meter": 1,
        "metre": 1,

        "ft": 0.3048,
        "feet": 0.3048,
        "foot": 0.3048,

        "cm": 0.01,
        "centimeter": 0.01,
        "centimeters": 0.01,

        "mm": 0.001,
        "millimeter": 0.001,
        "millimeters": 0.001,
    }

    room_unit = room_unit.lower().strip()
    tile_unit = tile_unit.lower().strip()

    if room_unit not in unit_to_m:
        raise ValueError(f"Unsupported room unit: {room_unit}")

    if tile_unit not in unit_to_m:
        raise ValueError(f"Unsupported tile unit: {tile_unit}")

    # ---------------------------------------------------------
    # CONVERT TO METRES
    # ---------------------------------------------------------

    room_length_m = room_length * unit_to_m[room_unit]
    room_width_m = room_width * unit_to_m[room_unit]

    tile_length_m = tile_length * unit_to_m[tile_unit]
    tile_width_m = tile_width * unit_to_m[tile_unit]

    # ---------------------------------------------------------
    # AREA CALCULATION
    # ---------------------------------------------------------

    room_area = room_length_m * room_width_m
    tile_area = tile_length_m * tile_width_m

    if tile_area <= 0:
        raise ValueError("Tile dimensions must be greater than zero.")

    tiles = room_area / tile_area

    # Add wastage
    tiles *= (1 + waste_percent / 100)

    return math.ceil(tiles)


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
    # Find ALL dimension pairs
    # Handles:
    # 10 x 12
    # 10x12
    # 10 × 12
    # 600 x 600 mm
    # ---------------------------------------------------------

    dimension_matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*[x×*]\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(ft|feet|foot|m|meters?|cm|centimeters?|mm|millimeters?)?",
        prompt
    )

    print("DEBUG TILE DIMENSION MATCHES:", dimension_matches)

    if dimension_matches:
        result["room_length"] = float(dimension_matches[0][0])
        result["room_width"] = float(dimension_matches[0][1])

        if dimension_matches[0][2]:
            result["room_unit"] = dimension_matches[0][2]

    # ---------------------------------------------------------
    # TILE DIMENSIONS
    # Prefer a dimension pair followed by mm/cm
    # ---------------------------------------------------------

    tile_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[x×*]\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(mm|millimeters?|cm|centimeters?|m|meters?|ft|feet|foot)"
        r"(?:\s*)tiles?",
        prompt
    )

    print("DEBUG TILE UNIT MATCH:", tile_match.groups() if tile_match else None)

    if tile_match:
        result["tile_length"] = float(tile_match.group(1))
        result["tile_width"] = float(tile_match.group(2))
        result["tile_unit"] = tile_match.group(3)

    # ---------------------------------------------------------
    # FALLBACK
    # If there is no mm/cm after tile dimensions,
    # use the SECOND dimension pair.
    # ---------------------------------------------------------

    if (
        result["tile_length"] is None
        or result["tile_width"] is None
    ):
        if len(dimension_matches) >= 2:
            result["tile_length"] = float(dimension_matches[1][0])
            result["tile_width"] = float(dimension_matches[1][1])

    # ---------------------------------------------------------
    # MISSING FIELDS
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