from backend.calculators.tile import calculate_tiles

def tile_tool(
        room_length: float,
        room_width: float,
        tile_length: float,
        tile_width: float,
        room_unit: str = "ft",
        tile_unit: str = "mm"
):
    return calculate_tiles(
        room_length = room_length,
        room_width = room_width,
        tile_length = tile_length,
        tile_width = tile_width,
        room_unit = room_unit,
        tile_unit = tile_unit
    )