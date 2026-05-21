# Example Prompts — Claude Desktop Controlling Blender

Once connected, say these to Claude Desktop:

---

## Scene Management
- "What objects are in my Blender scene?"
- "Tell me about the active object"
- "What render engine am I using?"

## Creating Objects
- "Create a red metallic sphere at the origin"
- "Add a cube at position 3, 0, 0 and name it 'Box_A'"
- "Create a monkey head and scale it to 2x"
- "Add 5 spheres in a row along the X axis"

## Transforming Objects
- "Move Cube to position 0, 0, 5"
- "Rotate Suzanne 45 degrees on Z axis"
- "Scale the sphere to 0.5 on all axes"

## Materials
- "Make the cube bright orange and metallic"
- "Set Suzanne's color to skin tone (0.8, 0.6, 0.5)"
- "Make the sphere a mirror (roughness 0, metallic 1)"

## Modifiers
- "Add a subdivision surface level 3 to the cube"
- "Add a solidify modifier to the plane with thickness 0.1"
- "Add a mirror modifier to my character mesh"

## Rendering
- "Switch to Cycles render engine"
- "Switch to EEVEE"
- "Render the scene and save to /tmp/my_render.png"

## Python Scripts
- "Run a script that creates 10 random cubes"
- "Write and run a script to rename all objects with 'obj_' prefix"
- "Select all mesh objects in the scene"

## Complex Tasks
- "Create a simple solar system: sun in center, 3 planets orbiting around it at different distances with different colors"
- "Make a chess board pattern — 8x8 grid of black and white cubes"
- "Create a neon sign effect: text object with bright emission material"
