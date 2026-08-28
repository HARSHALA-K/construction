from mcp.server.fastmcp import FastMCP
from mcp_server.tools.tile import tile_tool
from mcp_server.tools.material import material_tool
from mcp_server.tools.project_estimator import project_tool
from mcp_server.tools.interior import estimate_interior_tool

mcp = FastMCP("Construction Tools")
@mcp.tool()
def calculate_tiles_tool(
        room_length: float,
        room_width: float,
        tile_length: float,
        tile_width: float
):

    return tile_tool(
        room_length=room_length,
        room_width=room_width,
        tile_length=tile_length,
        tile_width=tile_width
    ) 


@mcp.tool()
def estimate_materials(
    length: float,
    width: float,
    thickness: float,
    material_type: str,
    calculation_type: str
):
    
    return material_tool(
        length=length,
        width=width,
        thickness=thickness,
        material_type=material_type,
        calculation_type=calculation_type
    )

@mcp.tool()
def estimate_project(
        area_sqft: float,
        cost_per_sqft: float
):
    return project_tool(
        area_sqft=area_sqft,
        cost_per_sqft=cost_per_sqft
    )

@mcp.tool()
def estimate_interior(
        area_sqft: float
):
    return estimate_interior_tool(
        area_sqft=area_sqft
    )

if __name__ == "__main__":
    print("MCP server started")
    mcp.run(transport="sse")