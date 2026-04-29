import importlib
import inspect
from pathlib import Path

from docutils import nodes as _docnodes
from sphinx import addnodes as _addnodes

import procfunc

project = "procfunc"
author = "Princeton Vision & Learning Lab"
release = procfunc.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "bpy": ("https://docs.blender.org/api/4.2", None),
}

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
    "special-members": True,
}
autodoc_typehints = "description"
autodoc_typehints_description_target = "all"
autodoc_class_signature = "separated"
autodoc_preserve_defaults = True
napoleon_google_docstring = True
napoleon_numpy_docstring = True

exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
html_title = f"procfunc {release}"

linkcheck_timeout = 15
linkcheck_retries = 2
linkcheck_workers = 8
linkcheck_anchors = True
linkcheck_ignore: list[str] = []


# Every entry becomes one long page. We enumerate the module's public names
# (``__all__`` if defined, otherwise everything not starting with ``_``) and
# emit an ``automodule`` block per submodule. Adding or removing a name from
# the package's ``__init__.py`` controls what shows up here on the next build.
DOC_PACKAGES = {
    "top_level": ("procfunc", "procfunc"),
    "compute_graph": ("procfunc.compute_graph", "pf.compute_graph"),
    "nodes": ("procfunc.nodes", "pf.nodes"),
    "ops": ("procfunc.ops", "pf.ops"),
    "tracer": ("procfunc.tracer", "pf.tracer"),
    "transforms": ("procfunc.transforms", "pf.transforms"),
    "transpiler": ("procfunc.transpiler", "pf.transpiler"),
    "types": ("procfunc.types", "pf.types"),
}

_BLENDER_DOCS = "https://docs.blender.org/api/current"

# Blender/mathutils names re-exported from ``procfunc`` for convenience. They
# are kept importable (e.g. ``pf.Vector``) but deliberately excluded from the
# top-level page's autodoc; this table links out to Blender's own docs instead.
# Values are ``(canonical dotted name, URL)`` — the dotted name is rendered as
# the alias-of text on the top-level page.
BLENDER_REEXPORT_URLS: dict[str, tuple[str, str]] = {
    "Vector": ("mathutils.Vector", f"{_BLENDER_DOCS}/mathutils.html#mathutils.Vector"),
    "Color": ("mathutils.Color", f"{_BLENDER_DOCS}/mathutils.html#mathutils.Color"),
    "Euler": ("mathutils.Euler", f"{_BLENDER_DOCS}/mathutils.html#mathutils.Euler"),
    "Quaternion": (
        "mathutils.Quaternion",
        f"{_BLENDER_DOCS}/mathutils.html#mathutils.Quaternion",
    ),
    "Matrix": ("mathutils.Matrix", f"{_BLENDER_DOCS}/mathutils.html#mathutils.Matrix"),
    "BVHTree": (
        "mathutils.bvhtree.BVHTree",
        f"{_BLENDER_DOCS}/mathutils.bvhtree.html#mathutils.bvhtree.BVHTree",
    ),
    "NodeGroup": ("bpy.types.NodeGroup", f"{_BLENDER_DOCS}/bpy.types.NodeGroup.html"),
    "Scene": ("bpy.types.Scene", f"{_BLENDER_DOCS}/bpy.types.Scene.html"),
    "ViewLayer": ("bpy.types.ViewLayer", f"{_BLENDER_DOCS}/bpy.types.ViewLayer.html"),
}


def _public_names(mod) -> list[str]:
    names = getattr(mod, "__all__", None)
    if names is None:
        names = [n for n in dir(mod) if not n.startswith("_")]
    return list(names)


def _doc_slug_for(modname: str) -> str | None:
    for slug, (name, _title) in DOC_PACKAGES.items():
        if name == modname:
            return slug
    return None


def _numpy_canonical(cls) -> str:
    """Dotted numpy path for ``cls``, dropping private submodule segments.

    e.g. ``numpy.random._generator.Generator`` → ``numpy.random.Generator``.
    """
    mod_parts = [p for p in cls.__module__.split(".") if not p.startswith("_")]
    return ".".join(mod_parts + [cls.__qualname__])


def _alias_entry(n: str, obj, role: str) -> str:
    """Format one bullet line for a re-exported name on the top-level page."""
    if n in BLENDER_REEXPORT_URLS:
        alias, url = BLENDER_REEXPORT_URLS[n]
        return f"* ``pf.{n}`` — alias of `{alias} <{url}>`_"
    canonical = getattr(obj, "__module__", "") or ""
    if canonical.startswith("procfunc"):
        parts = canonical.split(".")
        subpkg = ".".join(parts[:2]) if len(parts) >= 2 else canonical
        return f"* :{role}:`pf.{n} <{subpkg}.{n}>`"
    if canonical.startswith("numpy") and inspect.isclass(obj):
        target = _numpy_canonical(obj)
        return f"* ``pf.{n}`` — alias of :class:`{target}`"
    if canonical:
        return f"* ``pf.{n}`` — alias of ``{canonical}.{n}``"
    return f"* ``pf.{n}``"


_PACKAGE_TEMPLATE = """\
{title}
{title_underline}

.. automodule:: {modname}
   :no-members:

{submodules_section}
{members_section}
{submodule_details}
"""

_TOPLEVEL_TEMPLATE = """\
{title}
{title_underline}

.. automodule:: {modname}
   :no-members:

Subpackages
-----------

The following submodules are accessible as attributes of ``procfunc``
(e.g. ``pf.nodes``, ``pf.tracer``):

{subpackage_list}

Types
-----

The following types are importable directly from ``procfunc``.
Internal types link to their canonical subpage; Blender/numpy
aliases link to upstream docs.

{type_list}

Functions
---------

The following functions are importable directly from ``procfunc``.

{func_list}
"""


def _emit_top_level_page(
    slug: str, modname: str, title: str, mod, out_dir: Path
) -> None:
    submodules: list[str] = []
    for n in _public_names(mod):
        try:
            attr = getattr(mod, n)
        except AttributeError:
            continue
        if inspect.ismodule(attr) and attr.__name__.startswith(modname + "."):
            submodules.append(attr.__name__)

    type_entries: list[tuple[str, object]] = []
    func_entries: list[tuple[str, object]] = []
    for n in dir(mod):
        if n.startswith("_"):
            continue
        try:
            attr = getattr(mod, n)
        except AttributeError:
            continue
        if inspect.ismodule(attr):
            continue
        if inspect.isclass(attr):
            type_entries.append((n, attr))
        elif callable(attr):
            func_entries.append((n, attr))
    type_entries.sort(key=lambda x: x[0].lower())
    func_entries.sort(key=lambda x: x[0].lower())

    subpackage_lines = []
    for sub in submodules:
        short = sub[len(modname) + 1 :]
        target_slug = _doc_slug_for(sub)
        if target_slug is not None:
            subpackage_lines.append(f"* ``pf.{short}`` — :doc:`{target_slug}`")
        else:
            subpackage_lines.append(f"* ``pf.{short}`` — :mod:`{sub}`")

    rst = _TOPLEVEL_TEMPLATE.format(
        title=title,
        title_underline="=" * len(title),
        modname=modname,
        subpackage_list="\n".join(subpackage_lines),
        type_list="\n".join(_alias_entry(n, obj, "class") for n, obj in type_entries),
        func_list="\n".join(_alias_entry(n, obj, "func") for n, obj in func_entries),
    )
    (out_dir / f"{slug}.rst").write_text(rst)


def _emit_package_page(slug: str, modname: str, title: str, out_dir: Path) -> None:
    mod = importlib.import_module(modname)
    if modname == "procfunc":
        _emit_top_level_page(slug, modname, title, mod, out_dir)
        return

    names = _public_names(mod)
    submodules: list[str] = []
    direct: list[str] = []
    for n in names:
        try:
            attr = getattr(mod, n)
        except AttributeError:
            continue
        if inspect.ismodule(attr) and attr.__name__.startswith(modname + "."):
            submodules.append(attr.__name__)
        else:
            direct.append(n)

    short_prefix = modname.replace("procfunc", "pf")

    if submodules:
        sub_lines = []
        for sub in submodules:
            short = sub.split(".")[-1]
            sub_lines.append(f"* :ref:`{short_prefix}.{short} <{sub}>` — ``{sub}``")
        submodules_section = "Submodules\n----------\n\n" + "\n".join(sub_lines)
    else:
        submodules_section = ""

    if direct:
        members_section = (
            f"Members\n-------\n\n"
            f".. automodule:: {modname}\n"
            f"   :members:\n   :imported-members:\n   :undoc-members:"
        )
    else:
        members_section = ""

    detail_blocks = []
    for sub in submodules:
        short = sub.split(".")[-1]
        header = f"``{short_prefix}.{short}``"
        detail_blocks.append(
            f".. _{sub}:\n\n"
            f"{header}\n{'-' * len(header)}\n\n"
            f".. automodule:: {sub}\n"
            f"   :members:\n   :undoc-members:"
        )

    rst = _PACKAGE_TEMPLATE.format(
        title=title,
        title_underline="=" * len(title),
        modname=modname,
        submodules_section=submodules_section,
        members_section=members_section,
        submodule_details="\n\n".join(detail_blocks),
    )
    (out_dir / f"{slug}.rst").write_text(rst)


def _generate(app, config):  # noqa: ARG001
    out_dir = Path(app.srcdir)
    for slug, (modname, title) in DOC_PACKAGES.items():
        _emit_package_page(slug, modname, title, out_dir)


def _clean_exit(app, exception):
    # bpy segfaults on interpreter teardown (see commit 10c0540); exit cleanly
    # once the build has successfully produced its output.
    import os
    import sys

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0 if exception is None else 1)


def _blender_docs_url(target: str) -> str | None:
    """Return a URL on docs.blender.org for a dotted Blender API target.

    Handles the references autodoc emits for signatures and docstrings, e.g.
    ``bpy.types.Object``, ``bpy.types.Object.name``, ``mathutils.Vector``,
    ``mathutils.bvhtree.BVHTree``. Returns None for anything we don't
    recognise so Sphinx can report it as a real missing reference.
    """
    if target.startswith("bpy.types."):
        tail = target[len("bpy.types.") :]
        cls, _, attr = tail.partition(".")
        anchor = f"#bpy.types.{cls}.{attr}" if attr else ""
        return f"{_BLENDER_DOCS}/bpy.types.{cls}.html{anchor}"
    if target.startswith("bpy.ops."):
        tail = target[len("bpy.ops.") :]
        cat, _, _ = tail.partition(".")
        return f"{_BLENDER_DOCS}/bpy.ops.{cat}.html#{target}"
    if target in ("bpy.data", "bpy.context", "bpy.app", "bpy.path", "bpy.utils"):
        return f"{_BLENDER_DOCS}/{target}.html"
    if target.startswith("bpy."):
        head = target.split(".", 2)[1]
        return f"{_BLENDER_DOCS}/bpy.{head}.html#{target}"
    if target.startswith("mathutils.bvhtree."):
        return f"{_BLENDER_DOCS}/mathutils.bvhtree.html#{target}"
    if target.startswith("mathutils.kdtree."):
        return f"{_BLENDER_DOCS}/mathutils.kdtree.html#{target}"
    if target.startswith("mathutils.geometry."):
        return f"{_BLENDER_DOCS}/mathutils.geometry.html#{target}"
    if target.startswith("mathutils.noise."):
        return f"{_BLENDER_DOCS}/mathutils.noise.html#{target}"
    if target.startswith("mathutils."):
        return f"{_BLENDER_DOCS}/mathutils.html#{target}"
    return None


_NUMPY_DOCS = "https://numpy.org/doc/stable/reference"


def _numpy_docs_url(target: str) -> str | None:
    """Return a URL on numpy.org for a dotted numpy API target."""
    if not target.startswith("numpy."):
        return None
    if target == "numpy.random.Generator" or target.startswith(
        "numpy.random.Generator."
    ):
        tail = target[len("numpy.random.Generator") :]
        return f"{_NUMPY_DOCS}/random/generator.html#numpy.random.Generator{tail}"
    return f"{_NUMPY_DOCS}/generated/{target}.html"


def _resolve_external_xref(app, env, node, contnode):  # noqa: ARG001
    target = node.get("reftarget", "")
    url = _blender_docs_url(target) or _numpy_docs_url(target)
    if url is None:
        return None
    ref = _docnodes.reference("", "", internal=False, refuri=url, reftitle=target)
    ref.append(contnode)
    return ref


_DUNDER_KEEP = frozenset({"__init__"})

_DUNDER_SKIP_ALWAYS = frozenset(
    {
        "__annotations__",
        "__dict__",
        "__weakref__",
        "__module__",
        "__doc__",
        "__slots__",
        "__subclasshook__",
        "__init_subclass__",
        "__class_getitem__",
        "__dataclass_fields__",
        "__dataclass_params__",
        "__match_args__",
        "__orig_bases__",
        "__parameters__",
        "__post_init__",
    }
)


def _skip_private(app, what, name, obj, skip, options):  # noqa: ARG001
    if skip:
        return skip
    if name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
        return True
    is_dunder = name.startswith("__") and name.endswith("__")
    if is_dunder and name not in _DUNDER_KEEP:
        return True
    return None


_OBJECT_DUNDERS = frozenset(
    n for n in dir(object) if n.startswith("__") and n.endswith("__")
)


def _append_dunder_summary(app, what, name, obj, options, lines):  # noqa: ARG001
    if what != "class" or not inspect.isclass(obj):
        return
    dunders = sorted(
        n
        for n in dir(obj)
        if n.startswith("__")
        and n.endswith("__")
        and n not in _DUNDER_KEEP
        and n not in _DUNDER_SKIP_ALWAYS
        and n not in _OBJECT_DUNDERS
        and callable(getattr(obj, n, None))
    )
    if not dunders:
        return
    summary = ", ".join(f"``{d}``" for d in dunders)
    lines.append("")
    lines.append(f"**Supported special methods:** {summary}")
    lines.append("")


def _move_dunder_summaries(app, doctree, docname):  # noqa: ARG001
    for para in list(doctree.findall(_docnodes.paragraph)):
        if not para.astext().startswith("Supported special methods:"):
            continue
        parent = para.parent
        if not isinstance(parent, _addnodes.desc_content):
            continue
        parent.remove(para)
        parent.append(para)


def setup(app):
    app.connect("config-inited", _generate)
    app.connect("missing-reference", _resolve_external_xref)
    app.connect("autodoc-skip-member", _skip_private)
    app.connect("autodoc-process-docstring", _append_dunder_summary)
    app.connect("doctree-resolved", _move_dunder_summaries)
    app.connect("build-finished", _clean_exit)
    return {"parallel_read_safe": True}
