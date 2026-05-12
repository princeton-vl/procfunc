import sys

import bpy

import procfunc as pf

if __name__ == "__main__":

    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
    else:
        args = sys.argv

    code_fpath = args[0]
    rendering_dir = args[1]

    with open(code_fpath, "r") as f:
        code = f.read()

    code = code.strip().removeprefix("gpt_raw:")

    exec(code)

    for cam_name, filename in [('Camera1', 'render1.png'), ('Camera2', 'render2.png')]:
        if cam_name in bpy.data.objects:
            pf.ops.file.render(
                f"{rendering_dir}/{filename}",
                camera=cam_name,
                samples=512,
            )
