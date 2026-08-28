from backend.calculators.material import calculate_material


def material_tool(
    length: float,
    width: float,
    thickness: float,
    material_type: str,
    calculation_type: str
):
    """
    MCP-facing material calculation tool.
    """

    return calculate_material(
        length=length,
        width=width,
        thickness=thickness,
        material_type=material_type,
        calculation_type=calculation_type
    )