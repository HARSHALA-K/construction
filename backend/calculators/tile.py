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

def extract_tile_inputs(prompt):

    prompt = prompt.lower()

    result = {
        "room_length": None,
        "room_width": None,
        "tile_length": None,
        "tile_width": None
    }

    # --------------------------------------------------------
    # Room dimensions
    # Examples:
    # 20x20 room
    # 20 x 20 ft room
    # 20*20 room
    # --------------------------------------------------------

    room_match = re.search(
        r'(\d+(?:\.\d+)?)\s*[x*]\s*(\d+(?:\.\d+)?)\s*(ft|feet)?\s*room',
        prompt.lower()
    )

    if room_match:
        result["room_length"] = float(room_match.group(1))
        result["room_width"] = float(room_match.group(2))

    # --------------------------------------------------------
    # Tile dimensions
    #
    # Supports:
    # 600x600
    # 600 x 600
    # 600*600
    # 600 * 600 mm
    # 600mm x 600mm
    # --------------------------------------------------------

    tile_match = re.search(
        r'(\d+(?:\.\d+)?)\s*[x*]\s*(\d+(?:\.\d+)?)\s*(mm|cm)?',
        prompt.lower()
    )

    if tile_match:
        result["tile_length"] = float(tile_match.group(1))
        result["tile_width"] = float(tile_match.group(2))

    # --------------------------------------------------------
    # Missing fields
    # --------------------------------------------------------

    missing = [
        key
        for key, value in result.items()
        if value is None
    ]

    result["missing"] = missing
    result["complete"] = len(missing) == 0

    return result