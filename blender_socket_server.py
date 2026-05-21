bl_info = {
    "name": "Claude MCP Socket Server",
    "author": "mhd_ameen_ai",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N Panel > Claude MCP",
    "description": "Runs a local socket server so Claude Desktop can control Blender",
    "category": "Development",
}

import bpy
import socket
import threading
import json
import traceback
import mathutils

# ── Server state ──
server_thread = None
server_running = False
server_socket = None
PORT = 9876
log_messages = []


def log(msg):
    log_messages.append(msg)
    if len(log_messages) > 50:
        log_messages.pop(0)
    print(f"[Claude MCP] {msg}")


# ─────────────────────────────────────────
#  Command Handlers
# ─────────────────────────────────────────

def handle_command(data):
    """Route incoming command to the right handler."""
    cmd = data.get("command", "")
    params = data.get("params", {})

    handlers = {
        "get_scene_info":     cmd_get_scene_info,
        "create_object":      cmd_create_object,
        "delete_object":      cmd_delete_object,
        "move_object":        cmd_move_object,
        "scale_object":       cmd_scale_object,
        "rotate_object":      cmd_rotate_object,
        "set_material_color": cmd_set_material_color,
        "add_modifier":       cmd_add_modifier,
        "set_render_engine":  cmd_set_render_engine,
        "render_scene":       cmd_render_scene,
        "run_python":         cmd_run_python,
        "list_objects":       cmd_list_objects,
        "select_object":      cmd_select_object,
        "get_object_info":    cmd_get_object_info,
    }

    if cmd not in handlers:
        return {"ok": False, "error": f"Unknown command: {cmd}"}

    try:
        return handlers[cmd](params)
    except Exception as e:
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}


def cmd_get_scene_info(params):
    scene = bpy.context.scene
    obj = bpy.context.active_object
    return {
        "ok": True,
        "scene_name": scene.name,
        "render_engine": scene.render.engine,
        "frame_current": scene.frame_current,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "object_count": len(bpy.data.objects),
        "active_object": obj.name if obj else None,
        "active_object_type": obj.type if obj else None,
        "blender_version": ".".join(str(v) for v in bpy.app.version),
    }


def cmd_list_objects(params):
    objects = []
    for obj in bpy.data.objects:
        objects.append({
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "visible": obj.visible_get(),
        })
    return {"ok": True, "objects": objects}


def cmd_create_object(params):
    obj_type = params.get("type", "CUBE").upper()
    name = params.get("name", "")
    location = params.get("location", [0, 0, 0])

    def create():
        type_map = {
            "CUBE":     bpy.ops.mesh.primitive_cube_add,
            "SPHERE":   bpy.ops.mesh.primitive_uv_sphere_add,
            "CYLINDER": bpy.ops.mesh.primitive_cylinder_add,
            "PLANE":    bpy.ops.mesh.primitive_plane_add,
            "CONE":     bpy.ops.mesh.primitive_cone_add,
            "TORUS":    bpy.ops.mesh.primitive_torus_add,
            "MONKEY":   bpy.ops.mesh.primitive_monkey_add,
            "LIGHT":    bpy.ops.object.light_add,
            "CAMERA":   bpy.ops.object.camera_add,
            "EMPTY":    bpy.ops.object.empty_add,
        }
        op = type_map.get(obj_type, bpy.ops.mesh.primitive_cube_add)
        op(location=location)
        obj = bpy.context.active_object
        if name:
            obj.name = name
        return obj.name

    result_container = []

    def run_in_main():
        result_container.append(create())

    bpy.app.timers.register(run_in_main, first_interval=0)
    import time
    time.sleep(0.2)

    obj_name = result_container[0] if result_container else "created"
    return {"ok": True, "message": f"Created {obj_type}: {obj_name}", "name": obj_name}


def cmd_delete_object(params):
    name = params.get("name", "")
    if name not in bpy.data.objects:
        return {"ok": False, "error": f"Object '{name}' not found"}

    def delete():
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    bpy.app.timers.register(delete, first_interval=0)
    return {"ok": True, "message": f"Deleted: {name}"}


def cmd_move_object(params):
    name = params.get("name", "")
    location = params.get("location", [0, 0, 0])
    obj = bpy.data.objects.get(name)
    if not obj:
        return {"ok": False, "error": f"Object '{name}' not found"}

    def move():
        obj.location = mathutils.Vector(location)

    bpy.app.timers.register(move, first_interval=0)
    return {"ok": True, "message": f"Moved {name} to {location}"}


def cmd_scale_object(params):
    name = params.get("name", "")
    scale = params.get("scale", [1, 1, 1])
    obj = bpy.data.objects.get(name)
    if not obj:
        return {"ok": False, "error": f"Object '{name}' not found"}

    def do_scale():
        obj.scale = mathutils.Vector(scale)

    bpy.app.timers.register(do_scale, first_interval=0)
    return {"ok": True, "message": f"Scaled {name} to {scale}"}


def cmd_rotate_object(params):
    import math
    name = params.get("name", "")
    rotation_deg = params.get("rotation", [0, 0, 0])
    obj = bpy.data.objects.get(name)
    if not obj:
        return {"ok": False, "error": f"Object '{name}' not found"}

    def do_rotate():
        obj.rotation_euler = mathutils.Euler(
            [math.radians(a) for a in rotation_deg], 'XYZ'
        )

    bpy.app.timers.register(do_rotate, first_interval=0)
    return {"ok": True, "message": f"Rotated {name} by {rotation_deg} degrees"}


def cmd_set_material_color(params):
    name = params.get("name", "")
    color = params.get("color", [1, 1, 1, 1])
    roughness = params.get("roughness", 0.5)
    metallic = params.get("metallic", 0.0)

    obj = bpy.data.objects.get(name)
    if not obj:
        return {"ok": False, "error": f"Object '{name}' not found"}

    def set_mat():
        mat_name = f"{name}_material"
        mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = roughness
            bsdf.inputs["Metallic"].default_value = metallic
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

    bpy.app.timers.register(set_mat, first_interval=0)
    return {"ok": True, "message": f"Set material on {name} → color {color}"}


def cmd_add_modifier(params):
    name = params.get("name", "")
    mod_type = params.get("modifier", "SUBSURF").upper()
    mod_params = params.get("modifier_params", {})

    obj = bpy.data.objects.get(name)
    if not obj:
        return {"ok": False, "error": f"Object '{name}' not found"}

    def add_mod():
        mod = obj.modifiers.new(name=mod_type, type=mod_type)
        for k, v in mod_params.items():
            if hasattr(mod, k):
                setattr(mod, k, v)

    bpy.app.timers.register(add_mod, first_interval=0)
    return {"ok": True, "message": f"Added {mod_type} modifier to {name}"}


def cmd_set_render_engine(params):
    engine = params.get("engine", "CYCLES").upper()

    def set_engine():
        bpy.context.scene.render.engine = engine

    bpy.app.timers.register(set_engine, first_interval=0)
    return {"ok": True, "message": f"Render engine set to {engine}"}


def cmd_render_scene(params):
    output_path = params.get("output_path", "/tmp/claude_render.png")

    def render():
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)

    bpy.app.timers.register(render, first_interval=0)
    return {"ok": True, "message": f"Rendering to {output_path}"}


def cmd_run_python(params):
    """Run arbitrary Python code in Blender — use carefully!"""
    code = params.get("code", "")
    result_container = []

    def run():
        try:
            local_vars = {}
            exec(code, {"bpy": bpy, "mathutils": mathutils}, local_vars)
            result_container.append({"ok": True, "result": str(local_vars.get("result", "done"))})
        except Exception as e:
            result_container.append({"ok": False, "error": str(e)})

    bpy.app.timers.register(run, first_interval=0)
    import time
    time.sleep(0.3)
    return result_container[0] if result_container else {"ok": True, "result": "executed"}


def cmd_get_object_info(params):
    name = params.get("name", "")
    obj = bpy.data.objects.get(name)
    if not obj:
        return {"ok": False, "error": f"Object '{name}' not found"}

    info = {
        "ok": True,
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "modifiers": [m.type for m in obj.modifiers],
        "materials": [m.name for m in obj.data.materials] if hasattr(obj.data, 'materials') else [],
    }
    if obj.type == 'MESH':
        info["vertex_count"] = len(obj.data.vertices)
        info["face_count"] = len(obj.data.polygons)
    return info


def cmd_select_object(params):
    name = params.get("name", "")
    obj = bpy.data.objects.get(name)
    if not obj:
        return {"ok": False, "error": f"Object '{name}' not found"}

    def select():
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    bpy.app.timers.register(select, first_interval=0)
    return {"ok": True, "message": f"Selected: {name}"}


# ─────────────────────────────────────────
#  Socket Server
# ─────────────────────────────────────────

def socket_server():
    global server_socket, server_running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", PORT))
    server_socket.listen(5)
    server_socket.settimeout(1.0)
    log(f"Server started on port {PORT}")

    while server_running:
        try:
            client, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
        except socket.timeout:
            continue
        except Exception:
            break

    server_socket.close()
    log("Server stopped")


def handle_client(client):
    try:
        data = b""
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            data += chunk
            if data.endswith(b"\n"):
                break

        request = json.loads(data.decode("utf-8"))
        response = handle_command(request)
        client.send((json.dumps(response) + "\n").encode("utf-8"))
    except Exception as e:
        try:
            client.send((json.dumps({"ok": False, "error": str(e)}) + "\n").encode("utf-8"))
        except Exception:
            pass
    finally:
        client.close()


# ─────────────────────────────────────────
#  Operators & Panel
# ─────────────────────────────────────────

class MCP_OT_start_server(bpy.types.Operator):
    bl_idname = "mcp.start_server"
    bl_label = "Start MCP Server"

    def execute(self, context):
        global server_thread, server_running
        if server_running:
            self.report({'WARNING'}, "Server already running!")
            return {'FINISHED'}
        server_running = True
        server_thread = threading.Thread(target=socket_server, daemon=True)
        server_thread.start()
        self.report({'INFO'}, f"Claude MCP Server started on port {PORT}")
        return {'FINISHED'}


class MCP_OT_stop_server(bpy.types.Operator):
    bl_idname = "mcp.stop_server"
    bl_label = "Stop MCP Server"

    def execute(self, context):
        global server_running
        server_running = False
        self.report({'INFO'}, "Server stopped")
        return {'FINISHED'}


class MCP_PT_panel(bpy.types.Panel):
    bl_label = "🔌 Claude MCP Server"
    bl_idname = "MCP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Claude AI"

    def draw(self, context):
        layout = self.layout

        status = "🟢 Running" if server_running else "🔴 Stopped"
        layout.label(text=f"Status: {status}")
        layout.label(text=f"Port: {PORT}")

        row = layout.row(align=True)
        if not server_running:
            row.operator("mcp.start_server", text="▶ Start Server", icon='PLAY')
        else:
            row.operator("mcp.stop_server", text="⏹ Stop Server", icon='PAUSE')

        layout.separator()
        layout.label(text="Recent Log:")
        box = layout.box()
        col = box.column(align=True)
        for msg in log_messages[-5:]:
            col.label(text=msg[:50])


# ─────────────────────────────────────────
#  Register
# ─────────────────────────────────────────

classes = [MCP_OT_start_server, MCP_OT_stop_server, MCP_PT_panel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print(f"✅ Claude MCP Server Add-on loaded (port {PORT})")


def unregister():
    global server_running
    server_running = False
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
