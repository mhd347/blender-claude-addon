# 🤖 Claude AI Assistant for Blender

> Ask Claude AI anything about Blender — directly inside Blender, without leaving your workflow.

![Blender + Claude AI](https://img.shields.io/badge/Blender-3.6%2B-orange?logo=blender) ![Claude AI](https://img.shields.io/badge/Claude-Sonnet-blueviolet) ![License](https://img.shields.io/badge/License-MIT-green)

---

## What does this add-on do?

This Blender add-on adds a **Claude AI chat panel** inside Blender's N-Panel (sidebar).

You can ask any Blender question and get an expert answer instantly — without switching tabs, searching docs, or watching tutorials.

**Examples:**
- *"My Cycles render has fireflies, how do I fix it?"*
- *"How do I scatter 1000 trees on a terrain with Geometry Nodes?"*
- *"Write me a Python script to rename all objects in my scene"*
- *"What's the fastest way to UV unwrap this character?"*

Claude sees your **active scene context** (render engine, active object, vertex count) and gives answers specific to your situation.

---

## Features

- 💬 Full conversation — Claude remembers previous messages in the session
- 🎯 Scene context — Claude knows your render engine, active object, etc.
- ⚡ Quick question buttons — one click for common questions
- 📋 Copy response to clipboard
- 🔒 API key stored securely with password field
- 🧵 Non-blocking — Blender stays responsive while Claude is thinking

---

## Installation

### Step 1 — Get an API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / Log in
3. Create an API key
4. Copy it

### Step 2 — Install the Add-on
1. Download `claude_ai_addon.py`
2. Open Blender
3. `Edit → Preferences → Add-ons → Install`
4. Select `claude_ai_addon.py`
5. ✅ Enable the add-on

### Step 3 — Enter API Key
1. Open 3D Viewport
2. Press `N` to open N-Panel
3. Click **"Claude AI"** tab
4. Expand **⚙️ Settings**
5. Paste your API key

### Step 4 — Ask Away!
Type your question → Click **✨ Ask Claude** → Get expert answer!

---

## Usage

```
3D Viewport → N Panel (press N) → Claude AI tab
```

| Feature | How to use |
|---|---|
| Ask a question | Type in the box → Click "Ask Claude" |
| Quick questions | Click any pre-made button |
| Copy answer | Click "📋 Copy" button |
| New conversation | Click "🗑️ Clear" |
| Scene context | Toggle in Settings |

---

## Requirements

- Blender 3.6 or newer (works with Blender 4.x)
- Anthropic API key ([get one here](https://console.anthropic.com))
- Internet connection

---

## Cost

This add-on uses the **Claude Sonnet** model via API.
Anthropic charges per token — typical Blender questions cost **$0.001–0.005** each.
New accounts get **free credits** to start.

---

## Related

- [blender-expert-skill](https://github.com/mhd347/blender-expert-skill) — Claude AI skill with deep Blender knowledge

---

## License

MIT — free to use, modify, and share.

---

*Made with ❤️ by [@mhd_ameen_ai](https://x.com/mhd_ameen_ai)*
