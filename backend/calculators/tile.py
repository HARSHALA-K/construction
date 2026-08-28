import math
import re

def calculate_tiles(
    room_length,
    room_width,
    tile_length,
    tile_width,
    waste_percent=10
):
    # convert mm to feet
    tile_length_ft = tile_length / 304.8
    tile_width_ft = tile_width / 304.8
    room_area = room_length * room_width
    tile_area = tile_length_ft * tile_width_ft
    

    tiles = room_area / tile_area

    tiles *= (1 + waste_percent/100)

    return math.ceil(tiles)

import re


def extract_tile_inputs(prompt):
    prompt = prompt.lower()

    result = {
        "room_length": None,
        "room_width": None,
        "tile_length": None,
        "tile_width": None
    }

    # ---------------------------------------------------------
    # ROOM DIMENSIONS
    # Examples:
    # 20 x 15 ft room
    # 20 × 15 ft room
    # 20x15 room
    # ---------------------------------------------------------

    room_match = re.search(
        r'(\d+(?:\.\d+)?)\s*[x×*]\s*'
        r'(\d+(?:\.\d+)?)\s*'
        r'(?:ft|feet)?\s*room',
        prompt
    )

    if room_match:
        result["room_length"] = float(room_match.group(1))
        result["room_width"] = float(room_match.group(2))

    # ---------------------------------------------------------
    # TILE DIMENSIONS
    # Examples:
    # 600 x 600 mm tiles
    # 600 × 600 mm tiles
    # 600x600mm
    # ---------------------------------------------------------

    tile_match = re.search(
        r'(\d+(?:\.\d+)?)\s*[x×*]\s*'
        r'(\d+(?:\.\d+)?)\s*'
        r'(?:mm|millimeter|millimetre|cm)?\s*tiles?',
        prompt
    )

    if tile_match:
        result["tile_length"] = float(tile_match.group(1))
        result["tile_width"] = float(tile_match.group(2))

    # ---------------------------------------------------------
    # FALLBACK TILE EXTRACTION
    # Handles cases where "tiles" isn't immediately after
    # the dimensions.
    # ---------------------------------------------------------

    if (
        result["tile_length"] is None
        or result["tile_width"] is None
    ):
        tile_match = re.search(
            r'(\d+(?:\.\d+)?)\s*[x×*]\s*'
            r'(\d+(?:\.\d+)?)\s*'
            r'(?:mm|millimeter|millimetre|cm)?',
            prompt
        )

        if tile_match:
            a = float(tile_match.group(1))
            b = float(tile_match.group(2))

            # Don't accidentally use the room dimensions
            # as the tile dimensions.
            if a != result["room_length"] or b != result["room_width"]:
                result["tile_length"] = a
                result["tile_width"] = b

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

    return result