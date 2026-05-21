bl_info = {
    "name": "Claude AI Assistant",
    "author": "mhd_ameen_ai",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N Panel > Claude AI",
    "description": "Ask Claude AI anything about Blender directly inside Blender",
    "category": "3D View",
}

import bpy
import threading
import urllib.request
import urllib.error
import json
from bpy.props import StringProperty, BoolProperty


# ─────────────────────────────────────────
#  Store conversation history per session
# ─────────────────────────────────────────
conversation_history = []


def call_claude_api(api_key, user_message, context_info=""):
    """Call Claude API and return response text."""

    system_prompt = """You are an expert Blender 3D assistant built into Blender itself.
The user is asking from inside Blender, so:
- Give short, direct answers
- Always include exact menu paths like: Properties → Render → Sampling
- Include keyboard shortcuts whenever relevant
- If code/script is needed, keep it concise and ready to copy-paste
- Current scene context will be provided when available"""

    # Add scene context if available
    if context_info:
        user_message = f"[Scene Info: {context_info}]\n\n{user_message}"

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": conversation_history
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
        reply = result["content"][0]["text"]

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    return reply


def get_scene_context():
    """Get basic scene info to give Claude context."""
    try:
        obj = bpy.context.active_object
        scene = bpy.context.scene

        info_parts = [
            f"Render engine: {scene.render.engine}",
            f"Objects in scene: {len(bpy.data.objects)}",
        ]

        if obj:
            info_parts.append(f"Active object: {obj.name} ({obj.type})")
            if obj.type == 'MESH':
                info_parts.append(
                    f"Verts: {len(obj.data.vertices)}, "
                    f"Faces: {len(obj.data.polygons)}"
                )

        return " | ".join(info_parts)
    except Exception:
        return ""


# ─────────────────────────────────────────
#  Operators
# ─────────────────────────────────────────

class CLAUDE_OT_ask(bpy.types.Operator):
    bl_idname = "claude.ask_question"
    bl_label = "Ask Claude"
    bl_description = "Send your question to Claude AI"

    def execute(self, context):
        props = context.scene.claude_props

        if not props.api_key.strip():
            props.response = "⚠️ Please enter your Anthropic API key in the settings."
            return {'FINISHED'}

        if not props.question.strip():
            props.response = "⚠️ Please type a question first."
            return {'FINISHED'}

        props.response = "⏳ Thinking..."
        props.is_loading = True

        question = props.question
        api_key = props.api_key
        include_context = props.include_scene_context
        scene_ctx = get_scene_context() if include_context else ""

        def fetch():
            try:
                reply = call_claude_api(api_key, question, scene_ctx)

                def update():
                    props.response = reply
                    props.is_loading = False
                    # Refresh UI
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()

                bpy.app.timers.register(update, first_interval=0.1)

            except urllib.error.HTTPError as e:
                error_body = e.read().decode()
                try:
                    error_json = json.loads(error_body)
                    msg = error_json.get("error", {}).get("message", str(e))
                except Exception:
                    msg = str(e)

                def show_error():
                    props.response = f"❌ API Error: {msg}"
                    props.is_loading = False

                bpy.app.timers.register(show_error, first_interval=0.1)

            except Exception as e:
                def show_error():
                    props.response = f"❌ Error: {str(e)}"
                    props.is_loading = False

                bpy.app.timers.register(show_error, first_interval=0.1)

        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()

        return {'FINISHED'}


class CLAUDE_OT_clear(bpy.types.Operator):
    bl_idname = "claude.clear_chat"
    bl_label = "Clear Chat"
    bl_description = "Clear conversation history and response"

    def execute(self, context):
        global conversation_history
        conversation_history = []
        context.scene.claude_props.response = ""
        context.scene.claude_props.question = ""
        return {'FINISHED'}


class CLAUDE_OT_copy_response(bpy.types.Operator):
    bl_idname = "claude.copy_response"
    bl_label = "Copy Response"
    bl_description = "Copy Claude's response to clipboard"

    def execute(self, context):
        response = context.scene.claude_props.response
        if response:
            bpy.context.window_manager.clipboard = response
            self.report({'INFO'}, "Response copied to clipboard!")
        return {'FINISHED'}


class CLAUDE_OT_quick_question(bpy.types.Operator):
    bl_idname = "claude.quick_question"
    bl_label = ""
    bl_description = "Ask this quick question"

    question: StringProperty()

    def execute(self, context):
        context.scene.claude_props.question = self.question
        bpy.ops.claude.ask_question()
        return {'FINISHED'}


# ─────────────────────────────────────────
#  Properties
# ─────────────────────────────────────────

class ClaudeProperties(bpy.types.PropertyGroup):
    api_key: StringProperty(
        name="API Key",
        description="Your Anthropic API key (get it from console.anthropic.com)",
        default="",
        subtype='PASSWORD'
    )
    question: StringProperty(
        name="Question",
        description="Ask Claude anything about Blender",
        default=""
    )
    response: StringProperty(
        name="Response",
        description="Claude's answer",
        default=""
    )
    is_loading: BoolProperty(default=False)
    show_settings: BoolProperty(name="Show Settings", default=False)
    include_scene_context: BoolProperty(
        name="Include Scene Context",
        description="Send current scene info to Claude for better answers",
        default=True
    )


# ─────────────────────────────────────────
#  Panel UI
# ─────────────────────────────────────────

class CLAUDE_PT_main_panel(bpy.types.Panel):
    bl_label = "🤖 Claude AI"
    bl_idname = "CLAUDE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Claude AI"

    def draw(self, context):
        layout = self.layout
        props = context.scene.claude_props

        # ── Settings Section ──
        box = layout.box()
        row = box.row()
        row.prop(props, "show_settings",
                 icon='TRIA_DOWN' if props.show_settings else 'TRIA_RIGHT',
                 emboss=False, text="⚙️ Settings")

        if props.show_settings:
            box.prop(props, "api_key", text="API Key")
            box.prop(props, "include_scene_context")
            sub = box.row()
            sub.scale_y = 0.7
            sub.label(text="Get key: console.anthropic.com", icon='URL')

        # ── Quick Questions ──
        box2 = layout.box()
        box2.label(text="Quick Questions:", icon='QUESTION')
        col = box2.column(align=True)

        quick_questions = [
            ("Fix fireflies in Cycles", "My Cycles render has fireflies, how do I fix it?"),
            ("Setup HDRI lighting", "How do I set up HDRI lighting in Blender?"),
            ("Unwrap UVs", "What's the best way to UV unwrap my model?"),
            ("Scatter objects", "How do I scatter objects on a surface with Geometry Nodes?"),
        ]

        for label, question in quick_questions:
            op = col.operator("claude.quick_question", text=label)
            op.question = question

        layout.separator()

        # ── Question Input ──
        layout.label(text="Ask anything:", icon='OUTLINER_DATA_FONT')
        layout.prop(props, "question", text="")

        # ── Ask Button ──
        row = layout.row(align=True)
        row.scale_y = 1.5
        ask_btn = row.operator(
            "claude.ask_question",
            text="⏳ Asking..." if props.is_loading else "✨ Ask Claude",
            icon='PLAY'
        )
        ask_btn

        layout.separator()

        # ── Response ──
        if props.response:
            box3 = layout.box()
            box3.label(text="Claude's Answer:", icon='INFO')

            # Word wrap the response in UI
            response_lines = props.response.split('\n')
            col3 = box3.column(align=True)
            for line in response_lines:
                # Split long lines for display
                while len(line) > 55:
                    col3.label(text=line[:55])
                    line = line[55:]
                if line:
                    col3.label(text=line)

            # Action buttons
            row2 = box3.row(align=True)
            row2.operator("claude.copy_response", text="📋 Copy", icon='COPYDOWN')
            row2.operator("claude.clear_chat", text="🗑️ Clear", icon='TRASH')
        else:
            layout.label(text="Response will appear here", icon='BLANK1')
            row3 = layout.row()
            row3.operator("claude.clear_chat", text="Clear History", icon='TRASH')


# ─────────────────────────────────────────
#  Register / Unregister
# ─────────────────────────────────────────

classes = [
    ClaudeProperties,
    CLAUDE_OT_ask,
    CLAUDE_OT_clear,
    CLAUDE_OT_copy_response,
    CLAUDE_OT_quick_question,
    CLAUDE_PT_main_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.claude_props = bpy.props.PointerProperty(type=ClaudeProperties)
    print("✅ Claude AI Assistant Add-on loaded!")


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.claude_props
    print("Claude AI Assistant Add-on unloaded.")


if __name__ == "__main__":
    register()
