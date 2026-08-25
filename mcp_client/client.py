import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

SERVER_URL = "http://localhost:8000/sse"

def run_tool(tool_name, arguments):
    return asyncio.run(
        call_tool(
            tool_name,
            arguments
        )
    ) 

async def call_tool(tool_name, arguments):
    async with sse_client(SERVER_URL) as streams:
        async with ClientSession(*streams) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments
            )

            return result.content[0].text
        
from mcp_server.server import calculate_tiles_tool, estimate_materials, estimate_project, estimate_interior_tool

def get_tile_estimate(
        room_length,
        room_width,
        tile_length,
        tile_width
):
    response = calculate_tiles_tool(
        room_length=room_length,
        room_width=room_width,
        tile_length=tile_length,
        tile_width=tile_width
    )

    return response

def get_material_estimate(
        length,
        width,
        thickness
):
    response = estimate_materials(
        length=length,
        width=width,
        thickness=thickness
    )

    return response

def get_project_estimate(
        area_sqft,
        cost_per_sqft
):
    response = estimate_project(
        area_sqft=area_sqft,
        cost_per_sqft=cost_per_sqft
    )
    return response

def get_interior_estimate(
        area_sqft
):
    response = estimate_interior_tool(
        area_sqft=area_sqft
    )
    return response

