#!/usr/bin/env python3
"""
Claude MCP Server for Blender
Connects Claude Desktop to Blender via socket.

Usage:
  pip install mcp
  python claude_mcp_server.py
"""

import asyncio
import socket
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

BLENDER_HOST = "localhost"
BLENDER_PORT = 9876

app = Server("blender-claude-mcp")


def send_to_blender(command: str, params: dict) -> dict:
    """Send a command to Blender socket server and get response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((BLENDER_HOST, BLENDER_PORT))
            payload = json.dumps({"command": command, "params": params}) + "\n"
            s.send(payload.encode("utf-8"))
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
                if response.endswith(b"\n"):
                    break
            return json.loads(response.decode("utf-8"))
    except ConnectionRefusedError:
        return {
            "ok": False,
            "error": "Cannot connect to Blender. Make sure Blender is open "
                     "and the Claude MCP Server add-on is started."
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def format_result(result: dict) -> str:
    if result.get("ok"):
        result.pop("ok", None)
        return json.dumps(result, indent=2)
    else:
        return f"Error: {result.get('error', 'Unknown error')}"


# ─────────────────────────────────────────
#  MCP Tools
# ─────────────────────────────────────────

@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="get_scene_info",
            description="Get information about the current Blender scene: render engine, frame, object count, active object.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="list_objects",
            description="List all objects in the Blender scene with their names, types and locations.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="get_object_info",
            description="Get detailed info about a specific object: location, rotation, scale, modifiers, materials, vertex count.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name"}
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="create_object",
            description="Create a new 3D object in Blender. Types: CUBE, SPHERE, CYLINDER, PLANE, CONE, TORUS, MONKEY, LIGHT, CAMERA, EMPTY",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "Object type (CUBE, SPHERE, etc.)"},
                    "name": {"type": "string", "description": "Name for the object"},
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "XYZ location [x, y, z]"
                    }
                },
                "required": ["type"]
            }
        ),
        types.Tool(
            name="delete_object",
            description="Delete an object from the Blender scene by name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name to delete"}
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="move_object",
            description="Move an object to a specific XYZ location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name"},
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "New XYZ location [x, y, z]"
                    }
                },
                "required": ["name", "location"]
            }
        ),
        types.Tool(
            name="scale_object",
            description="Scale an object to specific XYZ values.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name"},
                    "scale": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Scale values [x, y, z], e.g. [2, 2, 2]"
                    }
                },
                "required": ["name", "scale"]
            }
        ),
        types.Tool(
            name="rotate_object",
            description="Rotate an object in degrees on X, Y, Z axes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name"},
                    "rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Rotation in degrees [x, y, z]"
                    }
                },
                "required": ["name", "rotation"]
            }
        ),
        types.Tool(
            name="set_material_color",
            description="Set the material color (and optionally roughness/metallic) of an object using Principled BSDF.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name"},
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "RGBA color [r, g, b, a] — values 0.0 to 1.0"
                    },
                    "roughness": {"type": "number", "description": "0.0 = mirror, 1.0 = matte"},
                    "metallic": {"type": "number", "description": "0.0 = plastic, 1.0 = metal"}
                },
                "required": ["name", "color"]
            }
        ),
        types.Tool(
            name="add_modifier",
            description="Add a modifier to an object. Common types: SUBSURF, SOLIDIFY, BEVEL, MIRROR, ARRAY, BOOLEAN, DISPLACE",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name"},
                    "modifier": {"type": "string", "description": "Modifier type (e.g. SUBSURF)"},
                    "modifier_params": {
                        "type": "object",
                        "description": "Optional modifier settings, e.g. {\"levels\": 3}"
                    }
                },
                "required": ["name", "modifier"]
            }
        ),
        types.Tool(
            name="set_render_engine",
            description="Set Blender's render engine. Options: BLENDER_EEVEE, BLENDER_EEVEE_NEXT, CYCLES, BLENDER_WORKBENCH",
            inputSchema={
                "type": "object",
                "properties": {
                    "engine": {"type": "string", "description": "Render engine name"}
                },
                "required": ["engine"]
            }
        ),
        types.Tool(
            name="run_python",
            description="Run arbitrary Python (bpy) code in Blender. Use 'result' variable to return a value.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute in Blender"}
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="select_object",
            description="Select an object and make it the active object in Blender.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name to select"}
                },
                "required": ["name"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    result = send_to_blender(name, arguments)
    return [types.TextContent(type="text", text=format_result(result))]


# ─────────────────────────────────────────
#  Main
# ─────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
