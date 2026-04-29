"""Blender script: transpile the active object's materials/geonodes back to v1 NodeWrangler code.

Usage (run inside Blender):
    blender --background file.blend --python transpile_blend_to_v1.py -- output.py
"""
import sys
from pathlib import Path

import bpy
from infinigen.core.nodes.node_transpiler import transpiler

argv = sys.argv[sys.argv.index("--") + 1:]
output_path = Path(argv[0])

obj = bpy.data.objects.get("Cube") or bpy.context.active_object
if obj is None:
    raise RuntimeError("No object found to transpile")

code = transpiler.transpile_object(obj)

output_path.write_text(code)
print(f"Wrote v1 code to {output_path}")
