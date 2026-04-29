from .cleanup import (
    coerce_shaders_to_materialresult,
    eliminate_duplicate_result_types,
    eliminate_duplicate_subgraphs,
    extract_shader_vectors_as_inputs,
    fill_graph_defaults_with_call_node,
    remove_v1_name_from_graph,
    replace_ids,
)
from .convert import (
    colors_to_hsv_definition,
)
from .distribution import (
    distribution_to_mode,
    outlier_distribution,
)
from .extract_materials import (
    extract_materials_from_graph,
    extract_materials_from_graphs,
)
from .infer_distribution import (
    infer_distribution_hypercube,
    infer_nodegroup_distributions,
)
from .parameters import (
    extract_parameter_distributions,
)
from .util import (
    map_graph_list,
    map_subgraphs,
)

__all__ = [
    "coerce_shaders_to_materialresult",
    "eliminate_duplicate_result_types",
    "eliminate_duplicate_subgraphs",
    "extract_shader_vectors_as_inputs",
    "fill_graph_defaults_with_call_node",
    "remove_v1_name_from_graph",
    "replace_ids",
    "colors_to_hsv_definition",
    "distribution_to_mode",
    "outlier_distribution",
    "infer_distribution_hypercube",
    "infer_nodegroup_distributions",
    "extract_parameter_distributions",
    "map_graph_list",
    "map_subgraphs",
]
