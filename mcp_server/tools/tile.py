from backend.calculators.tile import calculate_tiles

def tile_tool(
        room_length: float,
        room_width: float,
        tile_length: float,
        tile_width: float
):
    return calculate_tiles(
        room_length = room_length,
        room_width = room_width,
        tile_length = tile_length,
        tile_width = tile_width
    )