# 🤖 Claude AI for Blender — Complete Integration

> Two ways to connect Claude AI with Blender — choose what fits your workflow.

![Blender](https://img.shields.io/badge/Blender-3.6%2B-orange?logo=blender)
![Claude AI](https://img.shields.io/badge/Claude-Sonnet-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Two Integrations

| | Add-on (Chat) | MCP Server (Control) |
|---|---|---|
| **What it does** | Chat with Claude inside Blender | Claude Desktop controls Blender |
| **Setup** | Simple — just API key | Advanced — Claude Desktop needed |
| **Use case** | Ask questions, get answers | Claude executes actions directly |
| **File** | `addon/claude_ai_addon.py` | `mcp/` folder |

---

## Option A — Claude AI Chat Add-on

Ask Claude anything about Blender from inside Blender's N-Panel.

### Features
- 💬 Chat panel in **View3D → N Panel → Claude AI**
- 🎯 Sends your scene info (render engine, active object) automatically
- ⚡ Quick question buttons for common problems
- 📋 Copy response to clipboard
- 🧵 Non-blocking — Blender stays responsive

### Install
1. Download `addon/claude_ai_addon.py`
2. Blender → `Edit → Preferences → Add-ons → Install`
3. Select the file → ✅ Enable
4. N Panel → Claude AI → ⚙️ Settings → Paste your API key
5. Ask anything!

**Get API key:** [console.anthropic.com](https://console.anthropic.com)

---

## Option B — MCP Server (Claude Desktop Controls Blender)

Claude Desktop can directly **create objects, change materials, run scripts, render** — all by typing natural language.

### Architecture
```
Claude Desktop ←→ MCP Server (Python) ←→ Blender Socket Server (Add-on)
```

### Available Tools (What Claude can do)

| Tool | What it does |
|---|---|
| `get_scene_info` | Read scene: engine, frames, object count |
| `list_objects` | See all objects in scene |
| `get_object_info` | Detailed info on one object |
| `create_object` | Create mesh, light, camera |
| `delete_object` | Delete by name |
| `move_object` | Teleport to XYZ position |
| `scale_object` | Resize X, Y, Z |
| `rotate_object` | Rotate in degrees |
| `set_material_color` | Color + roughness + metallic |
| `add_modifier` | Subdivision, Solidify, Mirror... |
| `set_render_engine` | EEVEE, Cycles, Workbench |
| `run_python` | Execute any bpy script |
| `select_object` | Make active |

### Setup (Step by Step)

**Step 1 — Install Blender Socket Server add-on**
1. Download `mcp/blender_socket_server.py`
2. Blender → `Edit → Preferences → Add-ons → Install`
3. Select the file → ✅ Enable
4. N Panel → Claude AI → **▶ Start Server**
5. Status shows 🟢 Running

**Step 2 — Install MCP Server**
```bash
pip install mcp
```

**Step 3 — Configure Claude Desktop**

Open Claude Desktop config file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this:
```json
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": ["C:/path/to/claude_mcp_server.py"]
    }
  }
}
```

**Step 4 — Restart Claude Desktop**

You will see a 🔨 tool icon — Blender is connected!

### Example Prompts
See `examples/example_prompts.md` for ready-to-use prompts.

**Quick examples:**
```
"Create a red metallic sphere at the origin"
"Add a subdivision surface level 3 to Cube"
"Make 10 random cubes scattered around the scene"
"Switch to Cycles and render the scene"
```

---

## File Structure

```
blender-claude-ai/
├── README.md
├── addon/
│   └── claude_ai_addon.py          ← Option A: Chat add-on (API key)
├── mcp/
│   ├── blender_socket_server.py    ← Blender add-on (runs socket server)
│   └── claude_mcp_server.py        ← MCP server for Claude Desktop
└── examples/
    └── example_prompts.md          ← Ready-to-use Claude prompts
```

---

## Related

- [blender-expert-skill](https://github.com/mhd347/blender-expert-skill) — Deep Blender knowledge skill for Claude

---

## License

MIT — free to use, modify, and share.

---

*Made with ❤️ by [@mhd_ameen_ai](https://x.com/mhd_ameen_ai)*
