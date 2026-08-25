from backend.calculators.tile import calculate_tiles

def tile_tool(
        room_length,
        room_width,
        tile_length,
        tile_width
):
    return calculate_tiles(
        room_length,
        room_width,
        tile_length,
        tile_width
    )