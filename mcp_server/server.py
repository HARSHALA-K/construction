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
        room_length,
        room_width,
        tile_length,
        tile_width
    ) 


@mcp.tool()
def estimate_materials(
        length: float,
        width: float,
        thickness: float
):
    return material_tool(
        length,
        width,
        thickness
    )

@mcp.tool()
def estimate_project(
        area_sqft: float,
        cost_per_sqft: float
):
    return project_tool(
        area_sqft,
        cost_per_sqft
    )

@mcp.tool()
def estimate_interior(
        area_sqft: float
):
    return estimate_interior_tool(
        area_sqft
    )

if __name__ == "__main__":
    print("MCP server started")
    mcp.run(transport="sse")