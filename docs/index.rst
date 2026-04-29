procfunc
========

.. automodule:: procfunc

Public API
----------

What appears on each page below is controlled entirely by what each module
exports. Add a name to the relevant ``__init__.py`` (or to its ``__all__``)
and it will show up on the next build; remove it and it disappears. Submodule
pages likewise follow each submodule's ``__all__`` when defined, or fall back
to every non-underscore name.

.. toctree::
   :maxdepth: 2

   top_level
   compute_graph
   nodes
   ops
   tracer
   transforms
   transpiler
   types

Index
-----

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
