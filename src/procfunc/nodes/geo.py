"""
Auto-generated Geometry Node bindings for Blender

WARNING: These type annotations are not guaranteed to be exhaustive or precise.

places of particular concern:
- What attribute nodes allow int/float/bool or also Color/Vector
- What geometry operations should we allow to apply on mismatching inputs? e.g. realize instances on a Mesh with no instances
"""

import logging
from dataclasses import dataclass
from typing import Any, Generic, Literal, NamedTuple, TypeVar

from procfunc import types as pt
from procfunc.nodes import types as nt
from procfunc.nodes.bindings_util import RuntimeResolveDataType, raise_io_error
from procfunc.nodes.bpy_node_info import NodeDataType

logger = logging.getLogger(__name__)

TDomain = Literal["POINT", "EDGE", "FACE", "CORNER", "CURVE", "INSTANCE", "LAYER"]

TAttribute = TypeVar("TAttribute", int, float, bool)

TMeshOrCurve = TypeVar(
    "TMeshOrCurve",
    pt.MeshObject,
    pt.CurveObject,
)
TAnyGeometry = TypeVar(
    "TAnyGeometry",
    pt.MeshObject,
    pt.CurveObject,
    pt.VolumeObject,
    nt.Instances,
)


class AccumulateFieldResult(NamedTuple, Generic[TAttribute]):
    leading: nt.ProcNode[TAttribute]
    total: nt.ProcNode[TAttribute]
    trailing: nt.ProcNode[TAttribute]


def accumulate_field(
    value: nt.ProcNode[TAttribute] | None = None,
    group_id: nt.SocketOrVal[int] = 0,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> AccumulateFieldResult[TAttribute]:
    """
    Uses a AccumulateField Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/field/accumulate_field.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeAccumulateField",
        inputs={"Group ID": group_id, "Value": value},
        attrs={
            "domain": domain,
            "data_type": data_type,
        },
    )
    return AccumulateFieldResult(
        leading=res._output_socket("leading"),
        total=res._output_socket("total"),
        trailing=res._output_socket("trailing"),
    )


class AttributeDomainSizeResult(NamedTuple):
    point_count: nt.ProcNode[int]
    edge_count: nt.ProcNode[int]
    face_count: nt.ProcNode[int]
    face_corner_count: nt.ProcNode[int]
    spline_count: nt.ProcNode[int]
    instance_count: nt.ProcNode[int]


def attribute_domain_size(
    geometry: nt.ProcNode[nt.Geometry],
    component: Literal["MESH", "POINTCLOUD", "CURVE", "INSTANCES"] = "MESH",
) -> AttributeDomainSizeResult:
    """
    Uses a AttributeDomainSize Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/attribute/domain_size.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeAttributeDomainSize",
        inputs={"Geometry": geometry},
        attrs={"component": component},
    )
    return AttributeDomainSizeResult(
        point_count=res._output_socket("point_count"),
        edge_count=res._output_socket("edge_count"),
        face_count=res._output_socket("face_count"),
        face_corner_count=res._output_socket("face_corner_count"),
        spline_count=res._output_socket("spline_count"),
        instance_count=res._output_socket("instance_count"),
    )


class AttributeStatisticResult(NamedTuple, Generic[TAttribute]):
    max: nt.ProcNode[TAttribute]
    mean: nt.ProcNode[TAttribute]
    median: nt.ProcNode[TAttribute]
    min: nt.ProcNode[TAttribute]
    range: nt.ProcNode[TAttribute]
    standard_deviation: nt.ProcNode[TAttribute]
    sum: nt.ProcNode[TAttribute]
    variance: nt.ProcNode[TAttribute]


def attribute_statistic(
    geometry: nt.ProcNode[nt.Geometry],
    attribute: nt.ProcNode[TAttribute] | None = None,
    selection: nt.SocketOrVal[bool] = True,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> AttributeStatisticResult[TAttribute]:
    """
    Uses a AttributeStatistic Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/attribute/attribute_statistic.html
    """

    if data_type is None:
        data_type = RuntimeResolveDataType(
            [
                NodeDataType.INT,
                NodeDataType.FLOAT,
                NodeDataType.FLOAT_VECTOR,
                NodeDataType.RGBA,
            ],
            ["Attribute"],
        )

    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeAttributeStatistic",
        inputs={"Attribute": attribute, "Geometry": geometry, "Selection": selection},
        attrs={"domain": domain, "data_type": data_type},
    )
    return AttributeStatisticResult(
        max=res._output_socket("max"),
        mean=res._output_socket("mean"),
        median=res._output_socket("median"),
        min=res._output_socket("min"),
        range=res._output_socket("range"),
        standard_deviation=res._output_socket("standard_deviation"),
        sum=res._output_socket("sum"),
        variance=res._output_socket("variance"),
    )


def blur_attribute(
    value: nt.ProcNode[TAttribute] | None = None,
    iterations: nt.SocketOrVal[int] = 1,
    weight: nt.SocketOrVal[float] = 1.0,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TAttribute]:
    """
    Uses a BlurAttribute Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/attribute/blur_attribute.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeBlurAttribute",
        inputs={"Iterations": iterations, "Value": value, "Weight": weight},
        attrs={
            "data_type": data_type,
        },
    )


class BoundBoxResult(NamedTuple):
    bounding_box: nt.ProcNode[pt.MeshObject]
    min: nt.ProcNode[pt.Vector]
    max: nt.ProcNode[pt.Vector]


def bound_box(geometry: nt.ProcNode[nt.Geometry]) -> BoundBoxResult:
    """
    Uses a BoundBox Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/bounding_box.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeBoundBox",
        inputs={"Geometry": geometry},
        attrs={},
    )
    return BoundBoxResult(
        node._output_socket("bounding_box"),
        node._output_socket("min"),
        node._output_socket("max"),
    )


@dataclass
class CaptureAttributeResult(Generic[TAnyGeometry]):
    geometry: nt.ProcNode[TAnyGeometry]
    attributes: dict[str, nt.ProcNode]

    def __getattr__(self, name: str) -> nt.ProcNode:
        if name in self.attributes:
            return self.attributes[name]
        else:
            return object.__getattribute__(self, name)


def capture_attribute(
    geometry: nt.ProcNode[TAnyGeometry],
    # active_index: int = 0, # TODO unsure how active_* function
    # active_item: Any = None,
    domain: TDomain = "POINT",
    **attributes: nt.SocketOrVal[TAttribute],
) -> CaptureAttributeResult[TAnyGeometry]:
    """
    Uses a CaptureAttribute Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/attribute/capture_attribute.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCaptureAttribute",
        inputs={"Geometry": geometry, **attributes},
        attrs={
            "domain": domain,
        },
    )
    return CaptureAttributeResult(
        geometry=res._output_socket("geometry"),
        attributes={k: res._output_socket(k) for k in attributes.keys()},
    )


def collection_info(
    collection: nt.SocketOrVal[pt.Collection],
    separate_children: nt.SocketOrVal[bool] = False,
    reset_children: nt.SocketOrVal[bool] = False,
    transform_space: Literal["ORIGINAL", "RELATIVE"] = "ORIGINAL",
) -> nt.ProcNode[nt.Instances]:
    """
    Uses a CollectionInfo Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/collection_info.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCollectionInfo",
        inputs={
            "Collection": collection,
            "Separate Children": separate_children,
            "Reset Children": reset_children,
        },
        attrs={"transform_space": transform_space},
    )


def convex_hull(geometry: nt.ProcNode[nt.Geometry]) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a ConvexHull Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/convex_hull.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeConvexHull",
        inputs={"Geometry": geometry},
        attrs={},
    )


class CornerResult(NamedTuple):
    corner_index: nt.ProcNode[int]
    total: nt.ProcNode[int]


def corners_of_edge(
    edge_index: nt.SocketOrVal[int] = 0,
    weights: nt.SocketOrVal[float] = 0.0,
    sort_index: nt.SocketOrVal[int] = 0,
) -> CornerResult:
    """
    Uses a CornersOfEdge Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/topology/corners_of_edge.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCornersOfEdge",
        inputs={"Edge Index": edge_index, "Weights": weights, "Sort Index": sort_index},
        attrs={},
    )
    return CornerResult(
        corner_index=res._output_socket("corner_index"),
        total=res._output_socket("total"),
    )


def corners_of_face(
    face_index: nt.SocketOrVal[int] = 0,
    weights: nt.SocketOrVal[float] = 0.0,
    sort_index: nt.SocketOrVal[int] = 0,
) -> CornerResult:
    """
    Uses a CornersOfFace Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/topology/corners_of_face.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCornersOfFace",
        inputs={"Face Index": face_index, "Weights": weights, "Sort Index": sort_index},
        attrs={},
    )
    return CornerResult(
        corner_index=res._output_socket("corner_index"),
        total=res._output_socket("total"),
    )


def corners_of_vertex(
    vertex_index: nt.SocketOrVal[int] = 0,
    weights: nt.SocketOrVal[float] = 0.0,
    sort_index: nt.SocketOrVal[int] = 0,
) -> CornerResult:
    """
    Uses a CornersOfVertex Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/topology/corners_of_vertex.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCornersOfVertex",
        inputs={
            "Vertex Index": vertex_index,
            "Weights": weights,
            "Sort Index": sort_index,
        },
        attrs={},
    )
    return CornerResult(
        corner_index=res._output_socket("corner_index"),
        total=res._output_socket("total"),
    )


def curve_arc(
    resolution: nt.SocketOrVal[int] = 16,
    radius: nt.SocketOrVal[float] = 1.0,
    start_angle: nt.SocketOrVal[float] = 0.0,
    sweep_angle: nt.SocketOrVal[float] = 5.497787,
    connect_center: nt.SocketOrVal[bool] = False,
    invert_arc: nt.SocketOrVal[bool] = False,
    mode: Literal["POINTS", "RADIUS"] = "RADIUS",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurveArc Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/arc.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveArc",
        inputs={
            "Resolution": resolution,
            "Radius": radius,
            "Start Angle": start_angle,
            "Sweep Angle": sweep_angle,
            "Connect Center": connect_center,
            "Invert Arc": invert_arc,
        },
        attrs={"mode": mode},
    )


def curve_endpoint_selection(
    start_size: nt.SocketOrVal[int] = 1, end_size: nt.SocketOrVal[int] = 1
) -> nt.ProcNode[bool]:
    """
    Uses a CurveEndpointSelection Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/endpoint_selection.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveEndpointSelection",
        inputs={"Start Size": start_size, "End Size": end_size},
        attrs={},
    )


# def curve_handle_type_selection(
#    handle_type: Literal["FREE", "AUTO", "VECTOR", "ALIGN"] = "AUTO",
#    mode: Literal["LEFT", "RIGHT"] = "RIGHT",
# ) -> t.ProcNode:
#    """
#    Uses a CurveHandleTypeSelection Geometry Node.
#
#    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/handle_type_selection.html
#    """
#    return t.ProcNode.from_nodetype(
#        node_type="GeometryNodeCurveHandleTypeSelection",
#        inputs={},
#        attrs={"handle_type": handle_type, "mode": mode},
#    )


def curve_length(curve: nt.ProcNode[pt.CurveObject]) -> nt.ProcNode[float]:
    """
    Uses a CurveLength Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/curve_length.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveLength",
        inputs={"Curve": curve},
        attrs={},
    )


class CurveOfPointResult(NamedTuple):
    curve_index: nt.ProcNode[int]
    index_in_curve: nt.ProcNode[int]


def curve_of_point(point_index: nt.SocketOrVal[int] = 0) -> CurveOfPointResult:
    """
    Uses a CurveOfPoint Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/topology/curve_of_point.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveOfPoint",
        inputs={"Point Index": point_index},
        attrs={},
    )
    return CurveOfPointResult(
        node._output_socket("curve_index"), node._output_socket("index_in_curve")
    )


def curve_bezier_segment(
    resolution: nt.SocketOrVal[int] = 16,
    start: nt.SocketOrVal[nt.pt.Vector] = (-1, 0, 0),
    start_handle: nt.SocketOrVal[nt.pt.Vector] = (-0.5, 0.5, 0),
    end_handle: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    end: nt.SocketOrVal[nt.pt.Vector] = (1, 0, 0),
    mode: Literal["POSITION", "OFFSET"] = "POSITION",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurvePrimitiveBezierSegment Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/bezier_segment.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurvePrimitiveBezierSegment",
        inputs={
            "Resolution": resolution,
            "Start": start,
            "Start Handle": start_handle,
            "End Handle": end_handle,
            "End": end,
        },
        attrs={"mode": mode},
    )


def curve_circle(
    resolution: nt.SocketOrVal[int] = 32,
    radius: nt.SocketOrVal[float] = 1.0,
    mode: Literal["POINTS", "RADIUS"] = "RADIUS",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurvePrimitiveCircle Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/curve_circle.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurvePrimitiveCircle",
        inputs={"Resolution": resolution, "Radius": radius},
        attrs={"mode": mode},
    )


def curve_line(
    start: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    end: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 1),
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurvePrimitiveLine Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/curve_line.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurvePrimitiveLine",
        inputs={"Start": start, "End": end},
        attrs={"mode": "POINTS"},
    )


def curve_line_from_direction(
    start: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    direction: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 1),
    length: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurveLineFromDirection Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/curve_line.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveLineFromDirection",
        inputs={"Start": start, "Direction": direction, "Length": length},
        attrs={"mode": "DIRECTION"},
    )


def curve_quadrilateral(
    width: nt.SocketOrVal[float] = 2.0,
    height: nt.SocketOrVal[float] = 2.0,
    mode: Literal[
        "RECTANGLE", "PARALLELOGRAM", "TRAPEZOID", "KITE", "POINTS"
    ] = "RECTANGLE",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurvePrimitiveQuadrilateral Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/quadrilateral.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurvePrimitiveQuadrilateral",
        inputs={"Width": width, "Height": height},
        attrs={"mode": mode},
    )


def curve_bezier(
    resolution: nt.SocketOrVal[int] = 16,
    start: nt.SocketOrVal[nt.pt.Vector] = (-1, 0, 0),
    middle: nt.SocketOrVal[nt.pt.Vector] = (0, 2, 0),
    end: nt.SocketOrVal[nt.pt.Vector] = (1, 0, 0),
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurveQuadraticBezier Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/quadratic_bezier.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveQuadraticBezier",
        inputs={"Resolution": resolution, "Start": start, "Middle": middle, "End": end},
        attrs={},
    )


def curve_set_handles(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    handle_type: Literal["FREE", "AUTO", "VECTOR", "ALIGN"] = "AUTO",
    mode: Literal["LEFT", "RIGHT"] = "RIGHT",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurveSetHandles Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/write/set_handle_type.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveSetHandles",
        inputs={"Curve": curve, "Selection": selection},
        attrs={"handle_type": handle_type, "mode": mode},
    )


def curve_spiral(
    resolution: nt.SocketOrVal[int] = 32,
    rotations: nt.SocketOrVal[float] = 2.0,
    start_radius: nt.SocketOrVal[float] = 1.0,
    end_radius: nt.SocketOrVal[float] = 2.0,
    height: nt.SocketOrVal[float] = 2.0,
    reverse: nt.SocketOrVal[bool] = False,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurveSpiral Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/curve_spiral.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveSpiral",
        inputs={
            "Resolution": resolution,
            "Rotations": rotations,
            "Start Radius": start_radius,
            "End Radius": end_radius,
            "Height": height,
            "Reverse": reverse,
        },
        attrs={},
    )


def curve_spline_type(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    spline_type: Literal["CATMULL_ROM", "POLY", "BEZIER", "NURBS"] = "POLY",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a CurveSplineType Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/write/set_spline_type.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveSplineType",
        inputs={"Curve": curve, "Selection": selection},
        attrs={"spline_type": spline_type},
    )


class CurveStarResult(NamedTuple):
    curve: nt.ProcNode[pt.CurveObject]
    outer_points: nt.ProcNode[bool]


def curve_star(
    points: nt.SocketOrVal[int] = 8,
    inner_radius: nt.SocketOrVal[float] = 1.0,
    outer_radius: nt.SocketOrVal[float] = 2.0,
    twist: nt.SocketOrVal[float] = 0.0,
) -> CurveStarResult:
    """
    Uses a CurveStar Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/primitives/star.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveStar",
        inputs={
            "Points": points,
            "Inner Radius": inner_radius,
            "Outer Radius": outer_radius,
            "Twist": twist,
        },
        attrs={},
    )
    return CurveStarResult(
        curve=res._output_socket("curve"),
        outer_points=res._output_socket("outer_points"),
    )


def curve_to_mesh(
    curve: nt.ProcNode[pt.CurveObject],
    profile_curve: nt.ProcNode[pt.CurveObject] | None = None,
    fill_caps: nt.SocketOrVal[bool] = False,
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a CurveToMesh Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/curve_to_mesh.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveToMesh",
        inputs={"Curve": curve, "Profile Curve": profile_curve, "Fill Caps": fill_caps},
        attrs={},
    )


class CurveToPointsResult(NamedTuple):
    points: nt.ProcNode[pt.MeshObject]
    tangent: nt.ProcNode[pt.Vector]
    normal: nt.ProcNode[pt.Vector]
    rotation: nt.ProcNode[pt.Vector]


def curve_to_points(
    curve: nt.ProcNode[pt.CurveObject],
    count: nt.SocketOrVal[int] = 10,
    length: nt.SocketOrVal[float] = 1.0,
    mode: Literal["EVALUATED", "COUNT", "LENGTH"] = "COUNT",
) -> CurveToPointsResult:
    """
    Uses a CurveToPoints Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/curve_to_points.html
    """
    inputs = {"Curve": curve}
    if mode == "COUNT":
        inputs["Count"] = count
    elif mode == "LENGTH":
        inputs["Length"] = length
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveToPoints",
        inputs=inputs,
        attrs={"mode": mode},
    )
    return CurveToPointsResult(
        points=res._output_socket("points"),
        tangent=res._output_socket("tangent"),
        normal=res._output_socket("normal"),
        rotation=res._output_socket("rotation"),
    )


def curve_to_points_evaluated(
    curve: nt.ProcNode[pt.CurveObject],
) -> CurveToPointsResult:
    """
    Uses a CurveToPoints Geometry Node with mode="EVALUATED".

    From Blender docs: Creates points based on how the curve is evaluated.
    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/curve_to_points.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveToPoints",
        inputs={"Curve": curve},
        attrs={"mode": "EVALUATED"},
    )
    return CurveToPointsResult(
        points=res._output_socket("points"),
        tangent=res._output_socket("tangent"),
        normal=res._output_socket("normal"),
        rotation=res._output_socket("rotation"),
    )


def curve_to_points_count(
    curve: nt.ProcNode[pt.CurveObject],
    count: nt.SocketOrVal[int] = 10,
) -> CurveToPointsResult:
    """
    Uses a CurveToPoints Geometry Node with mode="COUNT".

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/curve_to_points.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveToPoints",
        inputs={"Curve": curve, "Count": count},
        attrs={"mode": "COUNT"},
    )
    return CurveToPointsResult(
        points=res._output_socket("points"),
        tangent=res._output_socket("tangent"),
        normal=res._output_socket("normal"),
        rotation=res._output_socket("rotation"),
    )


def curve_to_points_length(
    curve: nt.ProcNode[pt.CurveObject],
    length: nt.SocketOrVal[float] = 0.1,
) -> CurveToPointsResult:
    """
    Uses a CurveToPoints Geometry Node with mode="LENGTH".

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/curve_to_points.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeCurveToPoints",
        inputs={"Curve": curve, "Length": length},
        attrs={"mode": "LENGTH"},
    )
    return CurveToPointsResult(
        points=res._output_socket("points"),
        tangent=res._output_socket("tangent"),
        normal=res._output_socket("normal"),
        rotation=res._output_socket("rotation"),
    )


def deform_curves_on_surface(
    curves: nt.ProcNode[pt.HairObject],
) -> nt.ProcNode[pt.HairObject]:
    """
    Uses a DeformCurvesOnSurface Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/deform_curves_on_surface.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeDeformCurvesOnSurface",
        inputs={"Curves": curves},
        attrs={},
    )


TDeleteGeometry = TypeVar(
    "TDeleteGeometry",
    nt.ProcNode[pt.MeshObject],
    nt.ProcNode[pt.CurveObject],
)


def delete_geometry(
    geometry: nt.ProcNode[TDeleteGeometry],
    selection: nt.SocketOrVal[bool] = True,
    domain: Literal["POINT", "EDGE", "FACE", "CURVE", "INSTANCE", "LAYER"] = "POINT",
    mode: Literal["ALL", "EDGE_FACE", "ONLY_FACE"] = "ALL",
) -> nt.ProcNode[TDeleteGeometry]:
    """
    Uses a DeleteGeometry Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/delete_geometry.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeDeleteGeometry",
        inputs={"Geometry": geometry, "Selection": selection},
        attrs={"domain": domain, "mode": mode},
    )


def distribute_points_in_grid(
    grid: nt.SocketOrVal[float] = 0.0,
    density: nt.SocketOrVal[float] = 1.0,
    seed: nt.SocketOrVal[int] = 0,
    mode: Literal["DENSITY_RANDOM", "DENSITY_GRID"] = "DENSITY_RANDOM",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a DistributePointsInGrid Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/distribute_points_in_volume.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeDistributePointsInGrid",
        inputs={"Grid": grid, "Density": density, "Seed": seed},
        attrs={"mode": mode},
    )


def distribute_points_in_volume(
    volume: nt.ProcNode[pt.VolumeObject],
    density: nt.SocketOrVal[float] = 1.0,
    seed: nt.SocketOrVal[int] = 0,
    mode: Literal["DENSITY_RANDOM", "DENSITY_GRID"] = "DENSITY_RANDOM",
) -> nt.ProcNode[pt.VolumeObject]:
    """
    Uses a DistributePointsInVolume Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/distribute_points_in_volume.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeDistributePointsInVolume",
        inputs={"Volume": volume, "Density": density, "Seed": seed},
        attrs={"mode": mode},
    )


class DistributePointsOnFacesResult(NamedTuple):
    points: nt.ProcNode[pt.MeshObject]
    normal: nt.ProcNode[pt.Vector]
    rotation: nt.ProcNode[pt.Vector]


def distribute_points_on_faces(
    mesh: nt.ProcNode[pt.MeshObject],
    selection: nt.SocketOrVal[bool] = True,
    density: nt.SocketOrVal[float] | None = None,
    seed: nt.SocketOrVal[int] = 0,
    use_legacy_normal: bool = False,
) -> DistributePointsOnFacesResult:
    """
    Uses a DistributePointsOnFaces Geometry Node with RANDOM distribution.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/distribute_points_on_faces.html
    """
    inputs: dict = {
        "Mesh": mesh,
        "Selection": selection,
        "Seed": seed,
    }
    if density is not None:
        inputs["Density"] = density

    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeDistributePointsOnFaces",
        inputs=inputs,
        attrs={
            "distribute_method": "RANDOM",
            "use_legacy_normal": use_legacy_normal,
        },
    )
    return DistributePointsOnFacesResult(
        points=res._output_socket("points"),
        normal=res._output_socket("normal"),
        rotation=res._output_socket("rotation"),
    )


def distribute_points_on_faces_poisson(
    mesh: nt.ProcNode[pt.MeshObject],
    selection: nt.SocketOrVal[bool] = True,
    distance_min: nt.SocketOrVal[float] = 0.0,
    density_max: nt.SocketOrVal[float] = 10.0,
    density_factor: nt.SocketOrVal[float] = 1.0,
    seed: nt.SocketOrVal[int] = 0,
    use_legacy_normal: bool = False,
) -> DistributePointsOnFacesResult:
    """
    Uses a DistributePointsOnFaces Geometry Node with POISSON distribution.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/distribute_points_on_faces.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeDistributePointsOnFaces",
        inputs={
            "Mesh": mesh,
            "Selection": selection,
            "Distance Min": distance_min,
            "Density Max": density_max,
            "Density Factor": density_factor,
            "Seed": seed,
        },
        attrs={
            "distribute_method": "POISSON",
            "use_legacy_normal": use_legacy_normal,
        },
    )
    return DistributePointsOnFacesResult(
        points=res._output_socket("points"),
        normal=res._output_socket("normal"),
        rotation=res._output_socket("rotation"),
    )


def dual_mesh(
    mesh: nt.ProcNode[pt.MeshObject], keep_boundaries: nt.SocketOrVal[bool] = False
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a DualMesh Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/dual_mesh.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeDualMesh",
        inputs={"Mesh": mesh, "Keep Boundaries": keep_boundaries},
        attrs={},
    )


class DuplicateElementsResult(NamedTuple, Generic[TAnyGeometry]):
    geometry: nt.ProcNode[TAnyGeometry]
    duplicate_index: nt.ProcNode[int]


def duplicate_elements(
    geometry: nt.ProcNode[TAnyGeometry],
    selection: nt.SocketOrVal[bool] = True,
    amount: nt.SocketOrVal[int] = 1,
    domain: Literal["POINT", "EDGE", "FACE", "SPLINE", "INSTANCE"] = "POINT",
) -> DuplicateElementsResult[TAnyGeometry]:
    """
    Uses a DuplicateElements Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/duplicate_elements.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeDuplicateElements",
        inputs={"Geometry": geometry, "Selection": selection, "Amount": amount},
        attrs={"domain": domain},
    )
    return DuplicateElementsResult(
        geometry=res._output_socket("Geometry"),
        duplicate_index=res._output_socket("Duplicate Index"),
    )


def edge_paths_to_curves(
    mesh: nt.ProcNode[pt.MeshObject],
    start_vertices: nt.SocketOrVal[bool] = True,
    next_vertex_index: nt.SocketOrVal[int] = -1,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a EdgePathsToCurves Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/edge_paths_to_curves.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeEdgePathsToCurves",
        inputs={
            "Mesh": mesh,
            "Start Vertices": start_vertices,
            "Next Vertex Index": next_vertex_index,
        },
        attrs={},
    )


def edge_paths_to_selection(
    start_vertices: nt.SocketOrVal[bool] = True,
    next_vertex_index: nt.SocketOrVal[int] = -1,
) -> nt.ProcNode[bool]:
    """
    Uses a EdgePathsToSelection Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/edge_paths_to_selection.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeEdgePathsToSelection",
        inputs={
            "Start Vertices": start_vertices,
            "Next Vertex Index": next_vertex_index,
        },
        attrs={},
    )


class EdgesOfCornerResult(NamedTuple):
    next_edge_index: nt.ProcNode[int]
    previous_edge_index: nt.ProcNode[int]


def edges_of_corner(corner_index: nt.SocketOrVal[int] = 0) -> EdgesOfCornerResult:
    """
    Uses a EdgesOfCorner Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/topology/edges_of_corner.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeEdgesOfCorner",
        inputs={"Corner Index": corner_index},
        attrs={},
    )
    return EdgesOfCornerResult(
        next_edge_index=res._output_socket("next_edge_index"),
        previous_edge_index=res._output_socket("previous_edge_index"),
    )


class EdgesOfVertexResult(NamedTuple):
    edge_index: nt.ProcNode[int]
    total: nt.ProcNode[int]


def edges_of_vertex(
    vertex_index: nt.SocketOrVal[int] = 0,
    weights: nt.SocketOrVal[float] = 0.0,
    sort_index: nt.SocketOrVal[int] = 0,
) -> EdgesOfVertexResult:
    """
    Uses a EdgesOfVertex Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/topology/edges_of_vertex.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeEdgesOfVertex",
        inputs={
            "Vertex Index": vertex_index,
            "Weights": weights,
            "Sort Index": sort_index,
        },
        attrs={},
    )
    return EdgesOfVertexResult(
        edge_index=res._output_socket("edge_index"),
        total=res._output_socket("total"),
    )


def edges_to_face_groups(
    boundary_edges: nt.SocketOrVal[bool] = True,
) -> nt.ProcNode[int]:
    """
    Uses a EdgesToFaceGroups Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/edges_to_face_groups.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeEdgesToFaceGroups",
        inputs={"Boundary Edges": boundary_edges},
        attrs={},
    )


class ExtrudeMeshResult(NamedTuple):
    mesh: nt.ProcNode[pt.MeshObject]
    top: nt.ProcNode[bool]
    side: nt.ProcNode[bool]


def extrude_mesh(
    mesh: nt.ProcNode[pt.MeshObject],
    selection: nt.SocketOrVal[bool] = True,
    offset: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    offset_scale: nt.SocketOrVal[float] = 1.0,
    individual: nt.SocketOrVal[bool] = True,
    mode: Literal["VERTICES", "EDGES", "FACES"] = "FACES",
) -> ExtrudeMeshResult:
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeExtrudeMesh",
        inputs={
            "Mesh": mesh,
            "Selection": selection,
            "Offset": offset,
            "Offset Scale": offset_scale,
            "Individual": individual,
        },
        attrs={"mode": mode},
    )
    return ExtrudeMeshResult(
        node._output_socket("mesh"),
        node._output_socket("top"),
        node._output_socket("side"),
    )


class FaceOfCornerResult(NamedTuple):
    face_index: nt.ProcNode[int]
    index_in_face: nt.ProcNode[int]


def face_of_corner(corner_index: nt.SocketOrVal[int] = 0) -> FaceOfCornerResult:
    """
    Uses a FaceOfCorner Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/topology/face_of_corner.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeFaceOfCorner",
        inputs={"Corner Index": corner_index},
        attrs={},
    )
    return FaceOfCornerResult(
        node._output_socket("face_index"), node._output_socket("index_in_face")
    )


def field_at_index(
    value: TAttribute | None = None,
    index: nt.SocketOrVal[int] = 0,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TAttribute]:
    """
    Uses a FieldAtIndex Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/field/evaluate_at_index.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeFieldAtIndex",
        inputs={"Index": index, "Value": value},
        attrs={
            "domain": domain,
            "data_type": data_type,
        },
    )


TFieldOnDomain = TypeVar(
    "TFieldOnDomain", nt.SocketOrVal[bool], nt.SocketOrVal[int], nt.SocketOrVal[float]
)


def field_on_domain(
    value: TFieldOnDomain = 0,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TFieldOnDomain]:
    """
    Uses a FieldOnDomain Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/field/evaluate_on_domain.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeFieldOnDomain",
        inputs={"Value": value},
        attrs={
            "domain": domain,
            "data_type": data_type,
        },
    )


def fill_curve(
    curve: nt.ProcNode[pt.CurveObject],
    group_id: nt.SocketOrVal[int] = 0,
    mode: Literal["TRIANGLES", "NGONS"] = "TRIANGLES",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a FillCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/fill_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeFillCurve",
        inputs={"Curve": curve, "Group ID": group_id},
        attrs={"mode": mode},
    )


def fillet_curve(
    curve: nt.ProcNode[pt.CurveObject],
    radius: nt.SocketOrVal[float] = 0.25,
    limit_radius: nt.SocketOrVal[bool] = False,
    count: nt.SocketOrVal[int] = 1,
    mode: Literal["BEZIER", "POLY"] = "BEZIER",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a FilletCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/fillet_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeFilletCurve",
        inputs={
            "Curve": curve,
            "Radius": radius,
            "Limit Radius": limit_radius,
            "Count": count,
        },
        attrs={"mode": mode},
    )


def flip_faces(
    mesh: nt.ProcNode[pt.MeshObject], selection: nt.SocketOrVal[bool] = True
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a FlipFaces Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/flip_faces.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeFlipFaces",
        inputs={"Mesh": mesh, "Selection": selection},
        attrs={},
    )


def geometry_to_instance(
    geometry: nt.ProcNode[TAnyGeometry],
) -> nt.ProcNode[nt.Instances]:
    """
    Uses a GeometryToInstance Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/geometry_to_instance.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeGeometryToInstance",
        inputs={"Geometry": geometry},
        attrs={},
    )


def get_named_grid(
    volume: nt.ProcNode[nt.Geometry],
    name: nt.SocketOrVal[str] = "",
    remove: nt.SocketOrVal[bool] = True,
) -> nt.ProcNode:
    """
    Uses a GetNamedGrid Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/volume/index.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeGetNamedGrid",
        inputs={"Name": name, "Remove": remove, "Volume": volume},
        attrs={},
    )


def grid_to_mesh(
    grid: nt.SocketOrVal[float] = 0.0,
    threshold: nt.SocketOrVal[float] = 0.1,
    adaptivity: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a GridToMesh Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/volume/operations/volume_to_mesh.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeGridToMesh",
        inputs={"Grid": grid, "Threshold": threshold, "Adaptivity": adaptivity},
        attrs={},
    )


'''
def group(node_tree: Any = None) -> t.ProcNode:
    """
    Uses a Group Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/group.html
    """
    return t.ProcNode.from_nodetype(
        node_type="GeometryNodeGroup",
        inputs={},
        attrs={"node_tree": node_tree},
    )
'''


class ImageInfoResult(NamedTuple):
    width: nt.ProcNode[int]
    height: nt.ProcNode[int]
    has_alpha: nt.ProcNode[bool]
    frame_count: nt.ProcNode[int]
    fps: nt.ProcNode[float]


def image_info(
    image: nt.SocketOrVal[pt.Image], frame: nt.SocketOrVal[int] = 0
) -> ImageInfoResult:
    """
    Uses a ImageInfo Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/image_info.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeImageInfo",
        inputs={"Image": image, "Frame": frame},
        attrs={},
    )
    return ImageInfoResult(
        node._output_socket("width"),
        node._output_socket("height"),
        node._output_socket("has_alpha"),
        node._output_socket("frame_count"),
        node._output_socket("fps"),
    )


def image_texture(
    image: nt.SocketOrVal[pt.Image],
    vector: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    frame: nt.SocketOrVal[int] = 0,
    extension: Literal["REPEAT", "EXTEND", "CLIP", "MIRROR"] = "REPEAT",
    interpolation: Literal["Linear", "Closest", "Cubic"] = "Linear",
) -> nt.ProcNode:
    """
    Uses a ImageTexture Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/image_info.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeImageTexture",
        inputs={"Image": image, "pt.Vector": vector, "Frame": frame},
        attrs={"extension": extension, "interpolation": interpolation},
    )


def index_of_nearest(
    position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    group_id: nt.SocketOrVal[int] = 0,
) -> nt.ProcNode[int]:
    """
    Uses a IndexOfNearest Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/sample/index_of_nearest.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeIndexOfNearest",
        inputs={"Position": position, "Group ID": group_id},
        attrs={},
    )


def input_active_camera() -> nt.ProcNode[pt.Object]:
    """
    Uses a InputActiveCamera Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/active_camera.html
    """
    raise_io_error("input_active_camera", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputActiveCamera",
        inputs={},
        attrs={},
    )


class InputCurveHandlePositionsResult(NamedTuple):
    left: nt.ProcNode[pt.Vector]
    right: nt.ProcNode[pt.Vector]


def input_curve_handle_positions(
    relative: nt.SocketOrVal[bool] = False,
) -> InputCurveHandlePositionsResult:
    """
    Uses a InputCurveHandlePositions Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/curve_handle_position.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputCurveHandlePositions",
        inputs={"Relative": relative},
        attrs={},
    )
    return InputCurveHandlePositionsResult(
        node._output_socket("left"), node._output_socket("right")
    )


def input_curve_tilt() -> nt.ProcNode[float]:
    """
    Uses a InputCurveTilt Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/curve_tilt.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputCurveTilt",
        inputs={},
        attrs={},
    )


def input_edge_smooth() -> nt.ProcNode[bool]:
    """
    Uses a InputEdgeSmooth Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/is_edge_smooth.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputEdgeSmooth",
        inputs={},
        attrs={},
    )


def input_id() -> nt.ProcNode[int]:
    """
    Uses a InputID Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/id.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputID", inputs={}, attrs={}
    )


def input_image(image: Any = None) -> nt.ProcNode[pt.Image]:
    """
    Uses a InputImage Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/image.html
    """

    raise_io_error("input_image", logger=logger)
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputImage",
        inputs={},
        attrs={"image": image},
    )


def input_index() -> nt.ProcNode[int]:
    """
    Uses a InputIndex Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/input_index.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputIndex",
        inputs={},
        attrs={},
    )


def input_instance_rotation() -> nt.ProcNode[pt.Vector]:
    """
    Uses a InputInstanceRotation Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/rotation.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputInstanceRotation",
        inputs={},
        attrs={},
    )


def input_instance_scale() -> nt.ProcNode[pt.Vector]:
    """
    Uses a InputInstanceScale Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/instance_scale.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputInstanceScale",
        inputs={},
        attrs={},
    )


def input_material(material: Any = None) -> nt.ProcNode[pt.Material]:
    """
    Uses a InputMaterial Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/constant/material.html
    """
    raise_io_error("input_material", logger=logger)

    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMaterial",
        inputs={},
        attrs={"material": material},
    )


def input_material_index() -> nt.ProcNode[int]:
    """
    Uses a InputMaterialIndex Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/material/material_index.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMaterialIndex",
        inputs={},
        attrs={},
    )


class InputMeshEdgeAngleResult(NamedTuple):
    unsigned_angle: nt.ProcNode[float]
    signed_angle: nt.ProcNode[float]


def input_mesh_edge_angle() -> InputMeshEdgeAngleResult:
    """
    Uses a InputMeshEdgeAngle Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/edge_angle.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMeshEdgeAngle",
        inputs={},
        attrs={},
    )
    return InputMeshEdgeAngleResult(
        node._output_socket("unsigned_angle"), node._output_socket("signed_angle")
    )


def input_mesh_edge_neighbors() -> nt.ProcNode[int]:
    """
    Uses a InputMeshEdgeNeighbors Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/edge_neighbors.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMeshEdgeNeighbors",
        inputs={},
        attrs={},
    )


class InputMeshEdgeVerticesResult(NamedTuple):
    vertex_index_1: nt.ProcNode[int]
    vertex_index_2: nt.ProcNode[int]
    position_1: nt.ProcNode[pt.Vector]
    position_2: nt.ProcNode[pt.Vector]


def input_mesh_edge_vertices() -> InputMeshEdgeVerticesResult:
    """
    Uses a InputMeshEdgeVertices Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/edge_vertices.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMeshEdgeVertices",
        inputs={},
        attrs={},
    )
    return InputMeshEdgeVerticesResult(
        node._output_socket("vertex_index_1"),
        node._output_socket("vertex_index_2"),
        node._output_socket("position_1"),
        node._output_socket("position_2"),
    )


def input_mesh_face_area() -> nt.ProcNode[float]:
    """
    Uses a InputMeshFaceArea Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/face_area.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMeshFaceArea",
        inputs={},
        attrs={},
    )


def input_mesh_face_is_planar(
    threshold: nt.SocketOrVal[float] = 0.01,
) -> nt.ProcNode[bool]:
    """
    Uses a InputMeshFaceIsPlanar Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/face_is_planar.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMeshFaceIsPlanar",
        inputs={"Threshold": threshold},
        attrs={},
    )


class InputMeshFaceNeighborsResult(NamedTuple):
    vertex_count: nt.ProcNode[int]
    face_count: nt.ProcNode[int]


def input_mesh_face_neighbors() -> InputMeshFaceNeighborsResult:
    """
    Uses a InputMeshFaceNeighbors Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/face_neighbors.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMeshFaceNeighbors",
        inputs={},
        attrs={},
    )

    return InputMeshFaceNeighborsResult(
        vertex_count=res._output_socket("vertex_count"),
        face_count=res._output_socket("face_count"),
    )


class InputMeshIslandResult(NamedTuple):
    island_index: nt.ProcNode[int]
    island_count: nt.ProcNode[int]


def input_mesh_island() -> InputMeshIslandResult:
    """
    Uses a InputMeshIsland Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/mesh_island.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMeshIsland",
        inputs={},
        attrs={},
    )
    return InputMeshIslandResult(
        node._output_socket("island_index"), node._output_socket("island_count")
    )


class InputMeshVertexNeighborsResult(NamedTuple):
    vertex_count: nt.ProcNode[int]
    face_count: nt.ProcNode[int]


def input_mesh_vertex_neighbors() -> InputMeshVertexNeighborsResult:
    """
    Uses a InputMeshVertexNeighbors Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/vertex_neighbors.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputMeshVertexNeighbors",
        inputs={},
        attrs={},
    )
    return InputMeshVertexNeighborsResult(
        node._output_socket("vertex_count"), node._output_socket("face_count")
    )


class InputNamedAttributeResult(NamedTuple):
    attribute: nt.ProcNode
    exists: nt.ProcNode[bool]


def input_named_attribute(
    name: nt.SocketOrVal[str] = "",
    data_type: NodeDataType | None = None,
) -> InputNamedAttributeResult:
    """
    Uses a InputNamedAttribute Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/named_attribute.html
    """
    assert data_type is not NodeDataType.FLOAT_VECTOR_2D, (
        "GeometryNodeInputNamedAttribute does not support FLOAT_VECTOR_2D; use FLOAT_VECTOR instead"
    )
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputNamedAttribute",
        inputs={"Name": name},
        attrs={"data_type": data_type},
    )
    return InputNamedAttributeResult(
        node._output_socket("attribute"), node._output_socket("exists")
    )


def input_named_layer_selection(name: nt.SocketOrVal[str] = "") -> nt.ProcNode[bool]:
    """
    Uses a InputNamedLayerSelection Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/selection.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputNamedLayerSelection",
        inputs={"Name": name},
        attrs={},
    )


def input_normal() -> nt.ProcNode[pt.Vector]:
    """
    Uses a InputNormal Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/normal.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputNormal",
        inputs={},
        attrs={},
    )


def input_position() -> nt.ProcNode[pt.Vector]:
    """
    Uses a InputPosition Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/position.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputPosition",
        inputs={},
        attrs={},
    )


def input_radius() -> nt.ProcNode[float]:
    """
    Uses a InputRadius Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/radius.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputRadius",
        inputs={},
        attrs={},
    )


class InputSceneTimeResult(NamedTuple):
    seconds: nt.ProcNode[float]
    frame: nt.ProcNode[int]


def input_scene_time() -> InputSceneTimeResult:
    """
    Uses a InputSceneTime Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/scene_time.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputSceneTime",
        inputs={},
        attrs={},
    )
    return InputSceneTimeResult(
        seconds=node._output_socket("seconds"),
        frame=node._output_socket("frame"),
    )


def input_shade_smooth() -> nt.ProcNode[bool]:
    """
    Uses a InputShadeSmooth Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/write/set_shade_smooth.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputShadeSmooth",
        inputs={},
        attrs={},
    )


class InputShortestEdgePathsResult(NamedTuple):
    next_vertex_index: nt.ProcNode[int]
    total_cost: nt.ProcNode[float]


def input_shortest_edge_paths(
    end_vertex: nt.SocketOrVal[bool] = False, edge_cost: nt.SocketOrVal[float] = 1.0
) -> InputShortestEdgePathsResult:
    """
    Uses a InputShortestEdgePaths Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/shortest_edge_paths.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputShortestEdgePaths",
        inputs={"End Vertex": end_vertex, "Edge Cost": edge_cost},
        attrs={},
    )
    return InputShortestEdgePathsResult(
        next_vertex_index=res._output_socket("next_vertex_index"),
        total_cost=res._output_socket("total_cost"),
    )


def input_spline_cyclic() -> nt.ProcNode[bool]:
    """
    Uses a InputSplineCyclic Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/is_spline_cyclic.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputSplineCyclic",
        inputs={},
        attrs={},
    )


def input_spline_resolution() -> nt.ProcNode[int]:
    """
    Uses a InputSplineResolution Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/spline_resolution.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputSplineResolution",
        inputs={},
        attrs={},
    )


def input_tangent() -> nt.ProcNode[pt.Vector]:
    """
    Uses a InputTangent Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/curve_tangent.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInputTangent",
        inputs={},
        attrs={},
    )


def instance_on_points(
    points: nt.ProcNode[nt.Geometry] | None = None,
    instance: nt.ProcNode[nt.Geometry] | None = None,
    selection: nt.SocketOrVal[bool] = True,
    pick_instance: nt.SocketOrVal[bool] = False,
    instance_index: nt.SocketOrVal[int] = 0,
    rotation: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    scale: nt.SocketOrVal[nt.pt.Vector] = (1, 1, 1),
) -> nt.ProcNode[nt.Instances]:
    """
    Uses a InstanceOnPoints Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/instance_on_points.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInstanceOnPoints",
        inputs={
            "Points": points,
            "Selection": selection,
            "Instance": instance,
            "Pick Instance": pick_instance,
            "Instance Index": instance_index,
            "Rotation": rotation,
            "Scale": scale,
        },
        attrs={},
    )


def instance_transform() -> nt.ProcNode:
    """
    Uses a InstanceTransform Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/instance_transform.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInstanceTransform",
        inputs={},
        attrs={},
    )


def instances_to_points(
    instances: nt.ProcNode[nt.Instances] | None = None,
    selection: nt.SocketOrVal[bool] = True,
    position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    radius: nt.SocketOrVal[float] = 0.05,
) -> nt.ProcNode[nt.Points]:
    """
    Uses a InstancesToPoints Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/instances_to_points.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInstancesToPoints",
        inputs={
            "Instances": instances,
            "Selection": selection,
            "Position": position,
            "Radius": radius,
        },
        attrs={},
    )


class InterpolateCurvesResult(NamedTuple):
    curves: nt.ProcNode[pt.HairObject]
    closest_index: nt.ProcNode[int]
    closest_weight: nt.ProcNode[float]


def interpolate_curves(
    guide_curves: nt.ProcNode[pt.HairObject],
    points: nt.ProcNode[nt.Geometry],
    guide_up: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    guide_group_id: nt.SocketOrVal[int] = 0,
    point_up: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    point_group_id: nt.SocketOrVal[int] = 0,
    max_neighbors: nt.SocketOrVal[int] = 4,
) -> InterpolateCurvesResult:
    """
    Uses a InterpolateCurves Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/interpolate_curves.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeInterpolateCurves",
        inputs={
            "Guide Curves": guide_curves,
            "Guide Up": guide_up,
            "Guide Group ID": guide_group_id,
            "Points": points,
            "Point Up": point_up,
            "Point Group ID": point_group_id,
            "Max Neighbors": max_neighbors,
        },
        attrs={},
    )

    return InterpolateCurvesResult(
        curves=res._output_socket("curves"),
        closest_index=res._output_socket("closest_index"),
        closest_weight=res._output_socket("closest_weight"),
    )


def is_viewport() -> nt.ProcNode[bool]:
    """
    Uses a IsViewport Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/is_viewport.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeIsViewport",
        inputs={},
        attrs={},
    )


def join_geometry(
    geometries: list[nt.ProcNode[TAnyGeometry]],
) -> nt.ProcNode[TAnyGeometry]:
    """
    Uses a JoinGeometry Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/join_geometry.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeJoinGeometry",
        inputs={"Geometry": geometries},
        attrs={},
    )


def material_selection(
    material: nt.SocketOrVal[pt.Material] = None,
) -> nt.ProcNode[bool]:
    """
    Uses a MaterialSelection Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/material/material_selection.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMaterialSelection",
        inputs={"Material": material},
        attrs={},
    )


"""
TMenuSwitch = TypeVar(
    "TMenuSwitch",
    nt.SocketOrVal[bool],
    nt.SocketOrVal[int],
    nt.SocketOrVal[pt.Color],
    nt.SocketOrVal[str],
    nt.SocketOrVal[float],
    nt.SocketOrVal[nt.pt.Vector],
)


def menu_switch(
    a: TMenuSwitch = 0,
    b: TMenuSwitch = 0,
    menu: Any = "A",
    active_index: int = 1,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TMenuSwitch]:
    
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [
                NodeDataType.BOOLEAN,
                NodeDataType.INT,
                NodeDataType.RGBA,
                NodeDataType.STRING,
                NodeDataType.FLOAT,
                NodeDataType.FLOAT_VECTOR,
            ],
            ["A", "B"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMenuSwitch",
        inputs={"A": a, "B": b, "Menu": menu},
        attrs={
            "active_index": active_index,
            "data_type": data_type,
        },
    )
"""


def merge_by_distance(
    geometry: nt.ProcNode[nt.Geometry],
    selection: nt.SocketOrVal[bool] = True,
    distance: nt.SocketOrVal[float] = 0.001,
    mode: Literal["ALL", "CONNECTED"] = "ALL",
) -> nt.ProcNode[nt.Geometry]:
    """
    Uses a MergeByDistance Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/merge_by_distance.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMergeByDistance",
        inputs={"Geometry": geometry, "Selection": selection, "Distance": distance},
        attrs={"mode": mode},
    )


def mesh_boolean(
    mesh_1: nt.ProcNode[nt.Geometry] | None = None,
    mesh_2: nt.ProcNode[nt.Geometry] | None = None,
    self_intersection: nt.SocketOrVal[bool] = False,
    hole_tolerant: nt.SocketOrVal[bool] = False,
    operation: Literal["INTERSECT", "UNION", "DIFFERENCE"] = "DIFFERENCE",
    solver: Literal["EXACT", "FLOAT"] = "FLOAT",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a MeshBoolean Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/mesh_boolean.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshBoolean",
        inputs={
            "Mesh 1": mesh_1,
            "Mesh 2": mesh_2,
            "Self Intersection": self_intersection,
            "Hole Tolerant": hole_tolerant,
        },
        attrs={"operation": operation, "solver": solver},
    )


def mesh_circle(
    vertices: nt.SocketOrVal[int] = 32,
    radius: nt.SocketOrVal[float] = 1.0,
    fill_type: Literal["NONE", "NGON", "TRIANGLE_FAN"] = "NONE",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a MeshCircle Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/primitives/mesh_circle.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshCircle",
        inputs={"Vertices": vertices, "Radius": radius},
        attrs={"fill_type": fill_type},
    )


class MeshResult(NamedTuple):
    mesh: nt.ProcNode[pt.MeshObject]
    uv_map: nt.ProcNode[pt.MeshObject]


class MeshConeResult(NamedTuple):
    mesh: nt.ProcNode[pt.MeshObject]
    uv_map: nt.ProcNode[pt.MeshObject]
    top: nt.ProcNode[pt.MeshObject]
    bottom: nt.ProcNode[pt.MeshObject]
    side: nt.ProcNode[pt.MeshObject]


def mesh_cone(
    vertices: nt.SocketOrVal[int] = 32,
    side_segments: nt.SocketOrVal[int] = 1,
    fill_segments: nt.SocketOrVal[int] = 1,
    radius_top: nt.SocketOrVal[float] = 0.0,
    radius_bottom: nt.SocketOrVal[float] = 1.0,
    depth: nt.SocketOrVal[float] = 2.0,
    fill_type: Literal["NONE", "NGON", "TRIANGLE_FAN"] = "NGON",
) -> MeshConeResult:
    """
    Uses a MeshCone Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/primitives/cone.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshCone",
        inputs={
            "Vertices": vertices,
            "Side Segments": side_segments,
            "Fill Segments": fill_segments,
            "Radius Top": radius_top,
            "Radius Bottom": radius_bottom,
            "Depth": depth,
        },
        attrs={"fill_type": fill_type},
    )
    return MeshConeResult(
        mesh=res._output_socket("mesh"),
        uv_map=res._output_socket("uv_map"),
        top=res._output_socket("top"),
        bottom=res._output_socket("bottom"),
        side=res._output_socket("side"),
    )


def mesh_cube(
    size: nt.SocketOrVal[nt.pt.Vector] = (1, 1, 1),
    vertices_x: nt.SocketOrVal[int] = 2,
    vertices_y: nt.SocketOrVal[int] = 2,
    vertices_z: nt.SocketOrVal[int] = 2,
) -> MeshResult:
    """
    Uses a MeshCube Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/primitives/cube.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshCube",
        inputs={
            "Size": size,
            "Vertices X": vertices_x,
            "Vertices Y": vertices_y,
            "Vertices Z": vertices_z,
        },
        attrs={},
    )
    return MeshResult(
        mesh=res._output_socket("mesh"),
        uv_map=res._output_socket("uv_map"),
    )


class MeshCylinderResult(NamedTuple):
    mesh: nt.ProcNode[pt.MeshObject]
    top: nt.ProcNode[pt.MeshObject]
    side: nt.ProcNode[pt.MeshObject]
    bottom: nt.ProcNode[pt.MeshObject]
    uv_map: nt.ProcNode[pt.MeshObject]


def mesh_cylinder(
    vertices: nt.SocketOrVal[int] = 32,
    side_segments: nt.SocketOrVal[int] = 1,
    fill_segments: nt.SocketOrVal[int] = 1,
    radius: nt.SocketOrVal[float] = 1.0,
    depth: nt.SocketOrVal[float] = 2.0,
    fill_type: Literal["NONE", "NGON", "TRIANGLE_FAN"] = "NGON",
) -> MeshCylinderResult:
    """
    Uses a MeshCylinder Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/primitives/cylinder.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshCylinder",
        inputs={
            "Vertices": vertices,
            "Side Segments": side_segments,
            "Fill Segments": fill_segments,
            "Radius": radius,
            "Depth": depth,
        },
        attrs={"fill_type": fill_type},
    )
    return MeshCylinderResult(
        mesh=res._output_socket("mesh"),
        top=res._output_socket("top"),
        side=res._output_socket("side"),
        bottom=res._output_socket("bottom"),
        uv_map=res._output_socket("uv_map"),
    )


def mesh_face_set_boundaries(
    face_group_id: nt.SocketOrVal[int] = 0,
) -> nt.ProcNode[bool]:
    """
    Uses a MeshFaceSetBoundaries Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/face_group_boundaries.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshFaceSetBoundaries",
        inputs={"Face Group ID": face_group_id},
        attrs={},
    )


def mesh_grid(
    size_x: nt.SocketOrVal[float] = 1.0,
    size_y: nt.SocketOrVal[float] = 1.0,
    vertices_x: nt.SocketOrVal[int] = 3,
    vertices_y: nt.SocketOrVal[int] = 3,
) -> MeshResult:
    """
    Uses a MeshGrid Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/primitives/grid.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshGrid",
        inputs={
            "Size X": size_x,
            "Size Y": size_y,
            "Vertices X": vertices_x,
            "Vertices Y": vertices_y,
        },
        attrs={},
    )
    return MeshResult(
        mesh=res._output_socket("mesh"),
        uv_map=res._output_socket("uv_map"),
    )


def mesh_icosphere(
    radius: nt.SocketOrVal[float] = 1.0, subdivisions: nt.SocketOrVal[int] = 1
) -> MeshResult:
    """
    Uses a MeshIcoSphere Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/primitives/icosphere.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshIcoSphere",
        inputs={"Radius": radius, "Subdivisions": subdivisions},
        attrs={},
    )
    return MeshResult(
        mesh=res._output_socket("mesh"),
        uv_map=res._output_socket("uv_map"),
    )


def mesh_line(
    start_location: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    offset: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 1),
    count: nt.SocketOrVal[int] = 10,
    count_mode: Literal["TOTAL", "RESOLUTION"] = "TOTAL",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a MeshLine Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/primitives/mesh_line.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshLine",
        inputs={"Count": count, "Start Location": start_location, "Offset": offset},
        attrs={"count_mode": count_mode, "mode": "OFFSET"},
    )


def mesh_line_from_endpoints(
    start_location: nt.SocketOrVal[nt.pt.Vector],
    end_location: nt.SocketOrVal[nt.pt.Vector],
    count: nt.SocketOrVal[int] = 10,
    count_mode: Literal["TOTAL", "RESOLUTION"] = "TOTAL",
) -> nt.ProcNode[pt.MeshObject]:
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshLine",
        inputs={
            "Count": count,
            "Start Location": start_location,
            "Offset": end_location,  # 4.2 uses "Offset" key in both cases
        },
        attrs={"count_mode": count_mode, "mode": "END_POINTS"},
    )


def mesh_to_curve(
    mesh: nt.ProcNode[pt.MeshObject], selection: nt.SocketOrVal[bool] = True
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a MeshToCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/mesh_to_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshToCurve",
        inputs={"Mesh": mesh, "Selection": selection},
        attrs={},
    )


def mesh_to_density_grid(
    mesh: nt.ProcNode[pt.MeshObject],
    density: nt.SocketOrVal[float] = 1.0,
    voxel_size: nt.SocketOrVal[float] = 0.3,
    gradient_width: nt.SocketOrVal[float] = 0.2,
) -> nt.ProcNode:
    """
    Uses a MeshToDensityGrid Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/mesh_to_volume.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshToDensityGrid",
        inputs={
            "Mesh": mesh,
            "Density": density,
            "Voxel Size": voxel_size,
            "Gradient Width": gradient_width,
        },
        attrs={},
    )


def mesh_to_points(
    mesh: nt.ProcNode[pt.MeshObject],
    selection: nt.SocketOrVal[bool] = True,
    position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    radius: nt.SocketOrVal[float] = 0.05,
    mode: Literal["VERTICES", "EDGES", "FACES", "CORNERS"] = "VERTICES",
) -> nt.ProcNode[nt.Points]:
    """
    Uses a MeshToPoints Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/mesh_to_points.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshToPoints",
        inputs={
            "Mesh": mesh,
            "Selection": selection,
            "Position": position,
            "Radius": radius,
        },
        attrs={"mode": mode},
    )


def mesh_to_sdf_grid(
    mesh: nt.ProcNode[pt.MeshObject],
    voxel_size: nt.SocketOrVal[float] = 0.3,
    band_width: nt.SocketOrVal[int] = 3,
) -> nt.ProcNode:
    """
    Uses a MeshToSDFGrid Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/mesh_to_volume.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshToSDFGrid",
        inputs={"Mesh": mesh, "Voxel Size": voxel_size, "Band Width": band_width},
        attrs={},
    )


def mesh_to_volume(
    mesh: nt.ProcNode[pt.MeshObject],
    density: nt.SocketOrVal[float] = 1.0,
    voxel_amount: nt.SocketOrVal[float] = 64.0,
    interior_band_width: nt.SocketOrVal[float] = 0.2,
    resolution_mode: Literal["VOXEL_AMOUNT", "VOXEL_SIZE"] = "VOXEL_AMOUNT",
) -> nt.ProcNode[pt.VolumeObject]:
    """
    Uses a MeshToVolume Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/mesh_to_volume.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshToVolume",
        inputs={
            "Mesh": mesh,
            "Density": density,
            "Voxel Amount": voxel_amount,
            "Interior Band Width": interior_band_width,
        },
        attrs={"resolution_mode": resolution_mode},
    )


def mesh_uv_sphere(
    segments: nt.SocketOrVal[int] = 32,
    rings: nt.SocketOrVal[int] = 16,
    radius: nt.SocketOrVal[float] = 1.0,
) -> MeshResult:
    """
    Uses a MeshUVSphere Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/primitives/uv_sphere.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeMeshUVSphere",
        inputs={"Segments": segments, "Rings": rings, "Radius": radius},
        attrs={},
    )
    return MeshResult(
        mesh=res._output_socket("mesh"),
        uv_map=res._output_socket("uv_map"),
    )


TObjectInfo = TypeVar("TObjectInfo", pt.MeshObject, pt.CurveObject, pt.VolumeObject)


class ObjectInfoResult(NamedTuple, Generic[TObjectInfo]):
    geometry: nt.ProcNode[TObjectInfo]
    transform: nt.ProcNode[pt.Vector]
    location: nt.ProcNode[pt.Vector]
    rotation: nt.ProcNode[pt.Vector]
    scale: nt.ProcNode[pt.Vector]


def object_info(
    object: nt.SocketOrVal[TObjectInfo],
    as_instance: nt.SocketOrVal[bool] = False,
    transform_space: Literal["ORIGINAL", "RELATIVE"] = "ORIGINAL",
) -> ObjectInfoResult[TObjectInfo]:
    """
    Uses a ObjectInfo Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/object_info.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeObjectInfo",
        inputs={"Object": object, "As Instance": as_instance},
        attrs={"transform_space": transform_space},
    )
    return ObjectInfoResult(
        geometry=res._output_socket("geometry"),
        transform=res._output_socket("transform"),
        location=res._output_socket("location"),
        rotation=res._output_socket("rotation"),
        scale=res._output_socket("scale"),
    )


def offset_corner_in_face(
    corner_index: nt.SocketOrVal[int] = 0, offset: nt.SocketOrVal[int] = 0
) -> nt.ProcNode[int]:
    """
    Uses a OffsetCornerInFace Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/topology/offset_corner_in_face.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeOffsetCornerInFace",
        inputs={"Corner Index": corner_index, "Offset": offset},
        attrs={},
    )


class OffsetPointInCurveResult(NamedTuple):
    is_valid_offset: nt.ProcNode[bool]
    point_index: nt.ProcNode[int]


def offset_point_in_curve(
    point_index: nt.SocketOrVal[int] = 0, offset: nt.SocketOrVal[int] = 0
) -> OffsetPointInCurveResult:
    """
    Uses a OffsetPointInCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/topology/offset_point_in_curve.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeOffsetPointInCurve",
        inputs={"Point Index": point_index, "Offset": offset},
        attrs={},
    )
    return OffsetPointInCurveResult(
        is_valid_offset=res._output_socket("is_valid_offset"),
        point_index=res._output_socket("point_index"),
    )


def points(
    count: nt.SocketOrVal[int] = 1,
    position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    radius: nt.SocketOrVal[float] = 0.1,
) -> nt.ProcNode[nt.Points]:
    """
    Uses a Points Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/points.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodePoints",
        inputs={"Count": count, "Position": position, "Radius": radius},
        attrs={},
    )


class PointsOfCurveResult(NamedTuple):
    point_index: nt.ProcNode[int]
    total: nt.ProcNode[int]


def points_of_curve(
    curve_index: nt.SocketOrVal[int] = 0,
    weights: nt.SocketOrVal[float] = 0.0,
    sort_index: nt.SocketOrVal[int] = 0,
) -> PointsOfCurveResult:
    """
    Uses a PointsOfCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/topology/points_of_curve.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodePointsOfCurve",
        inputs={
            "Curve Index": curve_index,
            "Weights": weights,
            "Sort Index": sort_index,
        },
        attrs={},
    )
    return PointsOfCurveResult(
        point_index=res._output_socket("point_index"),
        total=res._output_socket("total"),
    )


def points_to_curves(
    points: nt.ProcNode[nt.Geometry],
    curve_group_id: nt.SocketOrVal[int] = 0,
    weight: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a PointsToCurves Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/points_to_curves.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodePointsToCurves",
        inputs={"Points": points, "Curve Group ID": curve_group_id, "Weight": weight},
        attrs={},
    )


def points_to_sdf_grid(
    points: nt.ProcNode[nt.Points],
    radius: nt.SocketOrVal[float] = 0.5,
    voxel_size: nt.SocketOrVal[float] = 0.3,
) -> nt.ProcNode:
    """
    Uses a PointsToSDFGrid Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/points_to_volume.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodePointsToSDFGrid",
        inputs={"Points": points, "Radius": radius, "Voxel Size": voxel_size},
        attrs={},
    )


def points_to_vertices(
    points: nt.ProcNode[nt.Points], selection: nt.SocketOrVal[bool] = True
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a PointsToVertices Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/points_to_vertices.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodePointsToVertices",
        inputs={"Points": points, "Selection": selection},
        attrs={},
    )


def points_to_volume(
    points: nt.ProcNode[nt.Points],
    density: nt.SocketOrVal[float] = 1.0,
    voxel_amount: nt.SocketOrVal[float] = 64.0,
    radius: nt.SocketOrVal[float] = 0.5,
    resolution_mode: Literal["VOXEL_AMOUNT", "VOXEL_SIZE"] = "VOXEL_AMOUNT",
) -> nt.ProcNode[pt.VolumeObject]:
    """
    Uses a PointsToVolume Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/points_to_volume.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodePointsToVolume",
        inputs={
            "Points": points,
            "Density": density,
            "Voxel Amount": voxel_amount,
            "Radius": radius,
        },
        attrs={"resolution_mode": resolution_mode},
    )


class ProximityResult(NamedTuple):
    position: nt.ProcNode[nt.pt.Vector]
    distance: nt.ProcNode[float]
    is_valid: nt.ProcNode[bool]


def proximity(
    geometry: nt.ProcNode[pt.MeshObject],
    group_id: nt.SocketOrVal[int] = 0,
    sample_position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    sample_group_id: nt.SocketOrVal[int] = 0,
    target_element: Literal["POINTS", "EDGES", "FACES"] = "FACES",
) -> ProximityResult:
    """
    Uses a Proximity Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/sample/geometry_proximity.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeProximity",
        inputs={
            "Geometry": geometry,
            "Group ID": group_id,
            "Sample Position": sample_position,
            "Sample Group ID": sample_group_id,
        },
        attrs={"target_element": target_element},
    )
    return ProximityResult(
        position=res._output_socket("position"),
        distance=res._output_socket("distance"),
        is_valid=res._output_socket("is_valid"),
    )


TRaycast = TypeVar(
    "TRaycast", nt.SocketOrVal[bool], nt.SocketOrVal[int], nt.SocketOrVal[float]
)


class RaycastResult(NamedTuple):
    attribute: nt.ProcNode[nt.pt.Vector]
    hit_distance: nt.ProcNode[float]
    hit_normal: nt.ProcNode[nt.pt.Vector]
    hit_position: nt.ProcNode[nt.pt.Vector]
    is_hit: nt.ProcNode[bool]


def raycast(
    geometry: nt.ProcNode[pt.MeshObject],
    attribute: TRaycast = 0,
    ray_direction: nt.SocketOrVal[nt.pt.Vector] = (0, 0, -1),
    ray_length: nt.SocketOrVal[float] = 100.0,
    source_position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    mapping: Literal["INTERPOLATED", "NEAREST"] = "INTERPOLATED",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> RaycastResult:
    """
    Uses a Raycast Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/sample/raycast.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Attribute"],
        )
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeRaycast",
        inputs={
            "Attribute": attribute,
            "Ray Direction": ray_direction,
            "Ray Length": ray_length,
            "Source Position": source_position,
            "Target Geometry": geometry,
        },
        attrs={
            "mapping": mapping,
            "data_type": data_type,
        },
    )
    return RaycastResult(
        attribute=res._output_socket("attribute"),
        hit_distance=res._output_socket("hit_distance"),
        hit_normal=res._output_socket("hit_normal"),
        hit_position=res._output_socket("hit_position"),
        is_hit=res._output_socket("is_hit"),
    )


def realize_instances(
    geometry: nt.ProcNode[nt.Geometry] | nt.ProcNode[nt.Instances],
    selection: nt.SocketOrVal[bool] = True,
    realize_all: nt.SocketOrVal[bool] = True,
    depth: nt.SocketOrVal[int] = 0,
) -> nt.ProcNode[nt.Geometry]:
    """
    Uses a RealizeInstances Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/realize_instances.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeRealizeInstances",
        inputs={
            "Geometry": geometry,
            "Selection": selection,
            "Realize All": realize_all,
            "Depth": depth,
        },
        attrs={},
    )


def remove_attribute(
    geometry: nt.ProcNode[TAnyGeometry],
    name: nt.SocketOrVal[str] = "",
    pattern_mode: Literal["EXACT", "WILDCARD"] = "EXACT",
) -> nt.ProcNode[TAnyGeometry]:
    """
    Uses a RemoveAttribute Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/attribute/remove_named_attribute.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeRemoveAttribute",
        inputs={"Geometry": geometry, "Name": name},
        attrs={"pattern_mode": pattern_mode},
    )


def replace_material(
    geometry: nt.ProcNode[pt.MeshObject],
    old: nt.SocketOrVal[pt.Material] | None = None,
    new: nt.SocketOrVal[pt.Material] | None = None,
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a ReplaceMaterial Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/material/replace_material.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeReplaceMaterial",
        inputs={"Geometry": geometry, "Old": old, "New": new},
        attrs={},
    )


def resample_curve_evaluated(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a ResampleCurve Geometry Node with mode="EVALUATED".

    From Blender docs: Evaluate the spline’s points based on the resolution attribute for NURBS and Bézier splines. Changes nothing for poly splines.
    https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/curve/operations/resample_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeResampleCurve",
        inputs={"Curve": curve, "Selection": selection},
        attrs={"mode": "EVALUATED"},
    )


def resample_curve_count(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    count: nt.SocketOrVal[int] = 10,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a ResampleCurve Geometry Node with mode="COUNT".
    https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/curve/operations/resample_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeResampleCurve",
        inputs={"Curve": curve, "Selection": selection, "Count": count},
        attrs={"mode": "COUNT"},
    )


def resample_curve_length(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    length: nt.SocketOrVal[float] = 1.0,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a ResampleCurve Geometry Node with mode="LENGTH".
    https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/curve/operations/resample_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeResampleCurve",
        inputs={"Curve": curve, "Selection": selection, "Length": length},
        attrs={"mode": "LENGTH"},
    )


def reverse_curve(
    curve: nt.ProcNode[pt.CurveObject], selection: nt.SocketOrVal[bool] = True
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a ReverseCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/reverse_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeReverseCurve",
        inputs={"Curve": curve, "Selection": selection},
        attrs={},
    )


def rotate_instances(
    instances: nt.ProcNode[nt.Instances],
    selection: nt.SocketOrVal[bool] = True,
    rotation: Any = (0, 0, 0),
    pivot_point: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    local_space: nt.SocketOrVal[bool] = True,
) -> nt.ProcNode[nt.Instances]:
    """
    Uses a RotateInstances Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/rotate_instances.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeRotateInstances",
        inputs={
            "Instances": instances,
            "Selection": selection,
            "Rotation": rotation,
            "Pivot Point": pivot_point,
            "Local Space": local_space,
        },
        attrs={},
    )


def sdf_grid_boolean(
    grid_1: nt.SocketOrVal[float] = 0.0, grid_2: nt.SocketOrVal[float] = 0.0
) -> nt.ProcNode[nt.Geometry]:
    """
    Uses a SDFGridBoolean Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/volume/index.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSDFGridBoolean",
        inputs={"Grid 1": grid_1, "Grid 2": grid_2},
        attrs={},
    )


class SampleCurveResult(NamedTuple):
    normal: nt.ProcNode[nt.pt.Vector]
    position: nt.ProcNode[nt.pt.Vector]
    tangent: nt.ProcNode[nt.pt.Vector]
    value: nt.ProcNode[TAttribute]


def sample_curve(
    curves: nt.ProcNode[nt.Geometry],
    curve_index: nt.SocketOrVal[int] = 0,
    factor: nt.SocketOrVal[float] = 0.0,
    value: nt.SocketOrVal[TAttribute] | None = None,
    mode: Literal["FACTOR", "LENGTH"] = "FACTOR",
    use_all_curves: bool = False,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> SampleCurveResult:
    """
    Uses a SampleCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/sample/sample_curve.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    inputs = {
        "Curves": curves,
        "Factor": factor,
        "Value": value,
    }
    if not use_all_curves:
        inputs["Curve Index"] = curve_index
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSampleCurve",
        inputs=inputs,
        attrs={
            "mode": mode,
            "use_all_curves": use_all_curves,
            "data_type": data_type,
        },
    )
    return SampleCurveResult(
        normal=res._output_socket("normal"),
        position=res._output_socket("position"),
        tangent=res._output_socket("tangent"),
        value=res._output_socket("value"),
    )


def sample_curve_length(
    curves: nt.ProcNode[nt.Geometry],
    length: nt.SocketOrVal[float] = 0.0,
    curve_index: nt.SocketOrVal[int] = 0,
    value: nt.SocketOrVal[TAttribute] | None = None,
    use_all_curves: bool = False,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> SampleCurveResult:
    """
    Uses a SampleCurve Geometry Node with LENGTH mode.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/sample/sample_curve.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    inputs = {
        "Curves": curves,
        "Length": length,
        "Value": value,
    }
    if not use_all_curves:
        inputs["Curve Index"] = curve_index
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSampleCurve",
        inputs=inputs,
        attrs={
            "mode": "LENGTH",
            "use_all_curves": use_all_curves,
            "data_type": data_type,
        },
    )
    return SampleCurveResult(
        normal=res._output_socket("normal"),
        position=res._output_socket("position"),
        tangent=res._output_socket("tangent"),
        value=res._output_socket("value"),
    )


'''
TSampleGrid = TypeVar(
    "TSampleGrid",
    nt.SocketOrVal[bool],
    nt.SocketOrVal[int],
    nt.SocketOrVal[float],
    nt.SocketOrVal[nt.pt.Vector],
)

def sample_grid(
    grid: TSampleGrid = 0,
    position: t.SocketOrVal[t.pt.Vector] = (0, 0, 0),
    interpolation_mode: Literal["NEAREST", "TRILINEAR", "TRIQUADRATIC"] = "TRILINEAR",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> t.ProcNode:
    """
    Uses a SampleGrid Geometry Node.

    TODO: link
    """
    if data_type is None:
        data_type = RuntimeResolveDataType([NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT, NodeDataType.FLOAT_VECTOR], ["Grid"])
    return t.ProcNode.from_nodetype(
        node_type="GeometryNodeSampleGrid",
        inputs={"Grid": grid, "Position": position},
        attrs={
            "interpolation_mode": interpolation_mode,
            "data_type": data_type,
        },
    )


TSampleGridIndex = TypeVar(
    "TSampleGridIndex",
    t.SocketOrVal[bool],
    t.SocketOrVal[int],
    t.SocketOrVal[float],
    t.SocketOrVal[t.pt.Vector],
)


def sample_grid_index(
    grid: TSampleGridIndex = 0,
    x: t.SocketOrVal[int] = 0,
    y: t.SocketOrVal[int] = 0,
    z: t.SocketOrVal[int] = 0,
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> t.ProcNode:
    """
    Uses a SampleGridIndex Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/volume/index.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT, NodeDataType.FLOAT_VECTOR],
            ["Grid"],
        )
    return t.ProcNode.from_nodetype(
        node_type="GeometryNodeSampleGridIndex",
        inputs={"Grid": grid, "X": x, "Y": y, "Z": z},
        attrs={
            "data_type": data_type,
        },
    )
'''


def sample_index(
    geometry: nt.ProcNode[TAnyGeometry],
    index: nt.SocketOrVal[int] = 0,
    value: nt.ProcNode[TAttribute] | None = None,
    clamp: bool = False,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TAttribute]:
    """
    Uses a SampleIndex Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/sample/sample_index.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSampleIndex",
        inputs={"Geometry": geometry, "Index": index, "Value": value},
        attrs={
            "clamp": clamp,
            "domain": domain,
            "data_type": data_type,
        },
    )


def sample_nearest(
    geometry: nt.ProcNode[nt.Points],
    sample_position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    domain: Literal["POINT", "EDGE", "FACE", "CORNER"] = "POINT",
) -> nt.ProcNode[int]:
    """
    Uses a SampleNearest Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/sample/sample_nearest.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSampleNearest",
        inputs={"Geometry": geometry, "Sample Position": sample_position},
        attrs={"domain": domain},
    )


class SampleResult(NamedTuple, Generic[TAttribute]):
    value: nt.ProcNode[TAttribute]
    is_valid: nt.ProcNode[bool]


def sample_nearest_surface(
    mesh: nt.ProcNode[pt.MeshObject],
    value: nt.ProcNode[TAttribute] | None = None,
    group_id: nt.SocketOrVal[int] = 0,
    sample_group_id: nt.SocketOrVal[int] = 0,
    sample_position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> SampleResult[TAttribute]:
    """
    Uses a SampleNearestSurface Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/sample/sample_nearest_surface.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSampleNearestSurface",
        inputs={
            "Group ID": group_id,
            "Mesh": mesh,
            "Sample Group ID": sample_group_id,
            "Sample Position": sample_position,
            "Value": value,
        },
        attrs={
            "data_type": data_type,
        },
    )
    return SampleResult(
        is_valid=res._output_socket("is_valid"),
        value=res._output_socket("value"),
    )


def sample_uv_surface(
    mesh: nt.ProcNode[pt.MeshObject],
    value: nt.ProcNode[TAttribute] | None = None,
    sample_uv: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    uv_map: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> SampleResult[TAttribute]:
    """
    Uses a SampleUVSurface Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/sample/sample_uv_surface.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSampleUVSurface",
        inputs={"Mesh": mesh, "Sample UV": sample_uv, "UV Map": uv_map, "Value": value},
        attrs={
            "data_type": data_type,
        },
    )
    return SampleResult(
        is_valid=res._output_socket("is_valid"),
        value=res._output_socket("value"),
    )


def scale_elements(
    geometry: nt.ProcNode[nt.Geometry],
    selection: nt.SocketOrVal[bool] = True,
    scale: nt.SocketOrVal[float] = 1.0,
    center: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    axis: nt.SocketOrVal[nt.pt.Vector] | None = None,
    domain: Literal["FACE", "EDGE"] = "FACE",
    scale_mode: Literal["UNIFORM", "SINGLE_AXIS"] = "UNIFORM",
) -> nt.ProcNode[nt.Geometry]:
    """
    Uses a ScaleElements Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/scale_elements.html
    """
    inputs = {
        "Geometry": geometry,
        "Selection": selection,
        "Scale": scale,
        "Center": center,
    }
    if scale_mode == "SINGLE_AXIS" and axis is not None:
        inputs["Axis"] = axis
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeScaleElements",
        inputs=inputs,
        attrs={"domain": domain, "scale_mode": scale_mode},
    )


def scale_instances(
    instances: nt.ProcNode[nt.Instances],
    selection: nt.SocketOrVal[bool] = True,
    scale: nt.SocketOrVal[nt.pt.Vector] = (1, 1, 1),
    center: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    local_space: nt.SocketOrVal[bool] = True,
) -> nt.ProcNode[nt.Instances]:
    """
    Uses a ScaleInstances Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/scale_instances.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeScaleInstances",
        inputs={
            "Instances": instances,
            "Selection": selection,
            "Scale": scale,
            "Center": center,
            "Local Space": local_space,
        },
        attrs={},
    )


def self_object() -> nt.ProcNode[pt.Object]:
    """
    Uses a SelfObject Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/self_object.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSelfObject",
        inputs={},
        attrs={},
    )


class SeparateComponentsResult(NamedTuple):
    mesh: nt.ProcNode[pt.MeshObject]
    curve: nt.ProcNode[pt.CurveObject]
    point_cloud: nt.ProcNode[nt.Points]
    volume: nt.ProcNode[pt.VolumeObject]
    instances: nt.ProcNode[nt.Instances]


def separate_components(
    geometry: nt.ProcNode[nt.Geometry],
) -> SeparateComponentsResult:
    """
    Uses a SeparateComponents Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/separate_components.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSeparateComponents",
        inputs={"Geometry": geometry},
        attrs={},
    )
    return SeparateComponentsResult(
        node._output_socket("mesh"),
        node._output_socket("curve"),
        node._output_socket("point_cloud"),
        node._output_socket("volume"),
        node._output_socket("instances"),
    )


class SeparateGeometryResult(NamedTuple, Generic[TMeshOrCurve]):
    selection: nt.ProcNode[TMeshOrCurve]
    inverted: nt.ProcNode[TMeshOrCurve]


def separate_geometry(
    geometry: nt.ProcNode[TMeshOrCurve],
    selection: nt.SocketOrVal[bool] = True,
    domain: Literal["POINT", "EDGE", "FACE", "CURVE", "INSTANCE", "LAYER"] = "POINT",
) -> SeparateGeometryResult[TMeshOrCurve]:
    """
    Uses a SeparateGeometry Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/separate_geometry.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSeparateGeometry",
        inputs={"Geometry": geometry, "Selection": selection},
        attrs={"domain": domain},
    )

    return SeparateGeometryResult(
        selection=res._output_socket("selection"),
        inverted=res._output_socket("inverted"),
    )


def set_curve_handle_positions(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    position: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    offset: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    mode: Literal["LEFT", "RIGHT"] = "LEFT",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a SetCurveHandlePositions Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/write/set_handle_positions.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetCurveHandlePositions",
        inputs={
            "Curve": curve,
            "Selection": selection,
            "Position": position,
            "Offset": offset,
        },
        attrs={"mode": mode},
    )


def set_curve_normal(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    mode: Literal["MINIMUM_TWIST", "Z_UP", "FREE"] = "MINIMUM_TWIST",
    normal: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 1),
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a SetCurveNormal Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/write/set_curve_normal.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetCurveNormal",
        inputs={"Curve": curve, "Selection": selection, "Normal": normal},
        attrs={"mode": mode},
    )


def set_curve_radius(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    radius: nt.SocketOrVal[float] = 0.005,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a SetCurveRadius Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/write/set_curve_radius.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetCurveRadius",
        inputs={"Curve": curve, "Selection": selection, "Radius": radius},
        attrs={},
    )


def set_curve_tilt(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    tilt: nt.SocketOrVal[float] = 0.0,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a SetCurveTilt Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/write/set_curve_tilt.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetCurveTilt",
        inputs={"Curve": curve, "Selection": selection, "Tilt": tilt},
        attrs={},
    )


def set_id(
    geometry: nt.ProcNode[TAnyGeometry],
    selection: nt.SocketOrVal[bool] = True,
    id: nt.SocketOrVal[int] = 0,
) -> nt.ProcNode[TAnyGeometry]:
    """
    Uses a SetID Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/write/set_id.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetID",
        inputs={"Geometry": geometry, "Selection": selection, "ID": id},
        attrs={},
    )


def set_instance_transform(
    instances: nt.ProcNode[nt.Instances],
    transform: nt.SocketOrVal[pt.Matrix] | None = None,
    selection: nt.SocketOrVal[bool] = True,
) -> nt.ProcNode[nt.Instances]:
    """
    Uses a SetInstanceTransform Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/set_instance_transform.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetInstanceTransform",
        inputs={"Instances": instances, "Selection": selection, "Transform": transform},
        attrs={},
    )


def set_material(
    geometry: nt.ProcNode[pt.MeshObject],
    material: nt.SocketOrVal[pt.Material] = None,
    selection: nt.SocketOrVal[bool] = None,
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a SetMaterial Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/material/set_material.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetMaterial",
        inputs={"Geometry": geometry, "Selection": selection, "Material": material},
        attrs={},
    )


def set_material_index(
    geometry: nt.ProcNode[pt.MeshObject],
    selection: nt.SocketOrVal[bool] = True,
    material_index: nt.SocketOrVal[int] = 0,
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a SetMaterialIndex Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/material/set_material_index.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetMaterialIndex",
        inputs={
            "Geometry": geometry,
            "Selection": selection,
            "Material Index": material_index,
        },
        attrs={},
    )


def set_point_radius(
    points: nt.ProcNode[pt.PointCloudObject],
    selection: nt.SocketOrVal[bool] = True,
    radius: nt.SocketOrVal[float] = 0.05,
) -> nt.ProcNode[pt.PointCloudObject]:
    """
    Uses a SetPointRadius Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/point/set_point_radius.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetPointRadius",
        inputs={"Points": points, "Selection": selection, "Radius": radius},
        attrs={},
    )


def set_position(
    geometry: nt.ProcNode[TAnyGeometry],
    selection: nt.SocketOrVal[bool] = True,
    position: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    offset: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
) -> nt.ProcNode[TAnyGeometry]:
    """
    Uses a SetPosition Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/write/set_position.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetPosition",
        inputs={
            "Geometry": geometry,
            "Selection": selection,
            "Position": position,
            "Offset": offset,
        },
        attrs={},
    )


def set_shade_smooth(
    geometry: nt.ProcNode[pt.MeshObject],
    selection: nt.SocketOrVal[bool] = True,
    shade_smooth: nt.SocketOrVal[bool] = True,
    domain: Literal["EDGE", "FACE"] = "FACE",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a SetShadeSmooth Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/write/set_shade_smooth.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetShadeSmooth",
        inputs={
            "Geometry": geometry,
            "Selection": selection,
            "Shade Smooth": shade_smooth,
        },
        attrs={"domain": domain},
    )


def set_spline_cyclic(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    cyclic: nt.SocketOrVal[bool] = False,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a SetSplineCyclic Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/write/set_spline_cyclic.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetSplineCyclic",
        inputs={"Geometry": curve, "Selection": selection, "Cyclic": cyclic},
        attrs={},
    )


def set_spline_resolution(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    resolution: nt.SocketOrVal[int] = 12,
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a SetSplineResolution Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/write/set_spline_resolution.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSetSplineResolution",
        inputs={"Geometry": curve, "Selection": selection, "Resolution": resolution},
        attrs={},
    )


def sort_elements(
    geometry: nt.ProcNode[TAnyGeometry],
    selection: nt.SocketOrVal[bool] = True,
    group_id: nt.SocketOrVal[int] = 0,
    sort_weight: nt.SocketOrVal[float] = 0.0,
    domain: Literal["POINT", "EDGE", "FACE", "CURVE", "INSTANCE"] = "POINT",
) -> nt.ProcNode[TAnyGeometry]:
    """
    Uses a SortElements Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/sort_elements.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSortElements",
        inputs={
            "Geometry": geometry,
            "Selection": selection,
            "Group ID": group_id,
            "Sort Weight": sort_weight,
        },
        attrs={"domain": domain},
    )


class SplineLengthResult(NamedTuple):
    length: nt.ProcNode[float]
    point_count: nt.ProcNode[int]


def spline_length() -> SplineLengthResult:
    """
    Uses a SplineLength Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/spline_length.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSplineLength",
        inputs={},
        attrs={},
    )
    return SplineLengthResult(
        node._output_socket("length"), node._output_socket("point_count")
    )


class SplineParameterResult(NamedTuple):
    factor: nt.ProcNode[float]
    length: nt.ProcNode[float]
    index: nt.ProcNode[int]


def spline_parameter() -> SplineParameterResult:
    """
    Uses a SplineParameter Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/read/spline_parameter.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSplineParameter",
        inputs={},
        attrs={},
    )
    return SplineParameterResult(
        node._output_socket("factor"),
        node._output_socket("length"),
        node._output_socket("index"),
    )


def split_edges(
    mesh: nt.ProcNode[pt.MeshObject], selection: nt.SocketOrVal[bool] = True
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a SplitEdges Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/split_edges.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSplitEdges",
        inputs={"Mesh": mesh, "Selection": selection},
        attrs={},
    )


class SplitToInstancesResult(NamedTuple):
    instances: nt.ProcNode[nt.Instances]
    group_id: nt.ProcNode[int]


def split_to_instances(
    geometry: nt.ProcNode[pt.MeshObject],
    selection: nt.SocketOrVal[bool] = True,
    group_id: nt.SocketOrVal[int] = 0,
    domain: Literal["POINT", "EDGE", "FACE", "CURVE", "INSTANCE", "LAYER"] = "POINT",
) -> SplitToInstancesResult:
    """
    Uses a SplitToInstances Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/split_to_instances.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSplitToInstances",
        inputs={"Geometry": geometry, "Selection": selection, "Group ID": group_id},
        attrs={"domain": domain},
    )
    return SplitToInstancesResult(
        instances=res._output_socket("instances"),
        group_id=res._output_socket("group_id"),
    )


def store_named_attribute(
    geometry: nt.ProcNode[TMeshOrCurve],
    name: nt.SocketOrVal[str] = "",
    selection: nt.SocketOrVal[bool] = True,
    value: nt.SocketOrVal[TAttribute] | None = None,
    domain: TDomain = "POINT",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> nt.ProcNode[TMeshOrCurve]:
    """
    Uses a StoreNamedAttribute Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/attribute/store_named_attribute.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )

    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeStoreNamedAttribute",
        inputs={
            "Geometry": geometry,
            "Name": name,
            "Selection": selection,
            "Value": value,
        },
        attrs={
            "domain": domain,
            "data_type": data_type,
        },
    )


def store_named_grid(
    volume: nt.ProcNode[nt.Geometry],
    grid: nt.SocketOrVal[float] = 0.0,
    name: nt.SocketOrVal[str] = "",
) -> nt.ProcNode:
    """
    Uses a StoreNamedGrid Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/volume/index.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeStoreNamedGrid",
        inputs={"Grid": grid, "Name": name, "Volume": volume},
        attrs={},
    )


def string_join(
    strings: list[nt.SocketOrVal[str]],
    delimiter: nt.SocketOrVal[str] = "",
) -> nt.ProcNode[str]:
    """
    Uses a StringJoin Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/text/join_strings.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeStringJoin",
        inputs={"Delimiter": delimiter, "Strings": strings},
        attrs={},
    )


class StringToCurvesResult(NamedTuple):
    curve_instances: nt.ProcNode[nt.Instances]
    line: nt.ProcNode[pt.CurveObject]
    pivot_point: nt.ProcNode[nt.pt.Vector]


def string_to_curves(
    string: nt.SocketOrVal[str],
    size: nt.SocketOrVal[float] = 1.0,
    character_spacing: nt.SocketOrVal[float] = 1.0,
    word_spacing: nt.SocketOrVal[float] = 1.0,
    line_spacing: nt.SocketOrVal[float] = 1.0,
    text_box_width: nt.SocketOrVal[float] = 0.0,
    align_x: Literal["LEFT", "CENTER", "RIGHT", "JUSTIFY", "FLUSH"] = "LEFT",
    align_y: Literal[
        "TOP", "TOP_BASELINE", "MIDDLE", "BOTTOM_BASELINE", "BOTTOM"
    ] = "TOP_BASELINE",
    overflow: Literal["OVERFLOW", "SCALE_TO_FIT", "TRUNCATE"] = "OVERFLOW",
    pivot_mode: Literal[
        "MIDPOINT",
        "TOP_LEFT",
        "TOP_CENTER",
        "TOP_RIGHT",
        "BOTTOM_LEFT",
        "BOTTOM_CENTER",
        "BOTTOM_RIGHT",
    ] = "BOTTOM_LEFT",
) -> StringToCurvesResult:
    """
    Uses a StringToCurves Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/utilities/text/string_to_curves.html
    """
    res = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeStringToCurves",
        inputs={
            "String": string,
            "Size": size,
            "Character Spacing": character_spacing,
            "Word Spacing": word_spacing,
            "Line Spacing": line_spacing,
            "Text Box Width": text_box_width,
        },
        attrs={
            "align_x": align_x,
            "align_y": align_y,
            "overflow": overflow,
            "pivot_mode": pivot_mode,
        },
    )

    return StringToCurvesResult(
        curve_instances=res._output_socket("curve_instances"),
        line=res._output_socket("line"),
        pivot_point=res._output_socket("pivot_point"),
    )


def subdivide_curve(
    curve: nt.ProcNode[pt.CurveObject], cuts: nt.SocketOrVal[int] = 1
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a SubdivideCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/subdivide_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSubdivideCurve",
        inputs={"Curve": curve, "Cuts": cuts},
        attrs={},
    )


def subdivide_mesh(
    mesh: nt.ProcNode[pt.MeshObject], level: nt.SocketOrVal[int] = 1
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a SubdivideMesh Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/subdivide_mesh.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSubdivideMesh",
        inputs={"Mesh": mesh, "Level": level},
        attrs={},
    )


def subdivision_surface(
    mesh: nt.ProcNode[pt.MeshObject],
    level: nt.SocketOrVal[int] = 1,
    edge_crease: nt.SocketOrVal[float] = 0.0,
    vertex_crease: nt.SocketOrVal[float] = 0.0,
    boundary_smooth: Literal["PRESERVE_CORNERS", "ALL"] = "ALL",
    uv_smooth: Literal[
        "NONE",
        "PRESERVE_CORNERS",
        "PRESERVE_CORNERS_AND_JUNCTIONS",
        "PRESERVE_CORNERS_JUNCTIONS_AND_CONCAVE",
        "PRESERVE_BOUNDARIES",
        "SMOOTH_ALL",
    ] = "PRESERVE_BOUNDARIES",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a SubdivisionSurface Geometry Node.

    See: http://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/operations/mesh/subdivision_surface.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeSubdivisionSurface",
        inputs={
            "Mesh": mesh,
            "Level": level,
            "Edge Crease": edge_crease,
            "Vertex Crease": vertex_crease,
        },
        attrs={"boundary_smooth": boundary_smooth, "uv_smooth": uv_smooth},
    )


_SWITCH_DATA_TYPES = [
    NodeDataType.BOOLEAN,
    NodeDataType.INT,
    NodeDataType.FLOAT,
    NodeDataType.FLOAT_VECTOR,
    NodeDataType.ROTATION,
    NodeDataType.FLOAT_MATRIX,
    NodeDataType.STRING,
    NodeDataType.RGBA,
    NodeDataType.OBJECT,
    # NodeDataType.IMAGE, # TODO verify support
    NodeDataType.GEOMETRY,
    NodeDataType.COLLECTION,
    # NodeDataType.TEXTURE, # TODO verify support
    NodeDataType.MATERIAL,
]

'''

class Tool3DCursorResult(NamedTuple):
    location: t.ProcNode[pt.Vector]
    rotation: t.ProcNode[pt.Vector]

def tool3_d_cursor() -> Tool3DCursorResult:
    """
    Uses a Tool3DCursor Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/3d_cursor.html
    """
    node = t.ProcNode.from_nodetype(
        node_type="GeometryNodeTool3DCursor",
        inputs={},
        attrs={},
    )
    return Tool3DCursorResult(node._output_socket("location"), node._output_socket("rotation"))


class ToolActiveElementResult(NamedTuple):
    index: t.ProcNode[int]
    exists: t.ProcNode[bool]


def tool_active_element(domain: TDomain = "POINT") -> ToolActiveElementResult:
    """
    Uses a ToolActiveElement Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/active_element.html
    """
    node = t.ProcNode.from_nodetype(
        node_type="GeometryNodeToolActiveElement",
        inputs={},
        attrs={"domain": domain},
    )
    return ToolActiveElementResult(node._output_socket("index"), node._output_socket("exists"))


class ToolFaceSetResult(NamedTuple):
    face_set: t.ProcNode[int]
    exists: t.ProcNode[bool]


def tool_face_set() -> ToolFaceSetResult:
    """
    Uses a ToolFaceSet Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/read/face_set.html
    """
    node = t.ProcNode.from_nodetype(
        node_type="GeometryNodeToolFaceSet",
        inputs={},
        attrs={},
    )
    return ToolFaceSetResult(node._output_socket("face_set"), node._output_socket("exists"))


class ToolMousePositionResult(NamedTuple):
    mouse_x: t.ProcNode[float]
    mouse_y: t.ProcNode[float]
    region_width: t.ProcNode[int]
    region_height: t.ProcNode[int]


def tool_mouse_position() -> ToolMousePositionResult:
    """
    Uses a ToolMousePosition Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/mouse_position.html
    """
    node = t.ProcNode.from_nodetype(
        node_type="GeometryNodeToolMousePosition",
        inputs={},
        attrs={},
    )
    return ToolMousePositionResult(
        node._output_socket("mouse_x"), node._output_socket("mouse_y"), node._output_socket("region_width"), node._output_socket("region_height")
    )


def tool_selection() -> t.ProcNode:
    """
    Uses a ToolSelection Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/read/selection.html
    """
    return t.ProcNode.from_nodetype(
        node_type="GeometryNodeToolSelection",
        inputs={},
        attrs={},
    )


def tool_set_face_set(
    mesh: t.ProcNode[pt.MeshObject],
    selection: t.SocketOrVal[bool] = True,
    face_set: t.SocketOrVal[int] = 0,
) -> t.ProcNode:
    """
    Uses a ToolSetFaceSet Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/write/set_face_set.html
    """
    return t.ProcNode.from_nodetype(
        node_type="GeometryNodeToolSetFaceSet",
        inputs={"Mesh": mesh, "Selection": selection, "Face Set": face_set},
        attrs={},
    )


def tool_set_selection(
    geometry: t.ProcNode[t.Geometry],
    selection: t.SocketOrVal[bool] = True,
    domain: TDomain = "POINT",
) -> t.ProcNode:
    """
    Uses a ToolSetSelection Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/write/set_selection.html
    """
    return t.ProcNode.from_nodetype(
        node_type="GeometryNodeToolSetSelection",
        inputs={"Geometry": geometry, "Selection": selection},
        attrs={"domain": domain},
    )
'''


def transform(
    geometry: nt.ProcNode[TMeshOrCurve],
    translation: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    rotation: Any = (0, 0, 0),
    scale: nt.SocketOrVal[nt.pt.Vector] = (1, 1, 1),
) -> nt.ProcNode[TMeshOrCurve]:
    """
    Uses a Transform Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/geometry/operations/transform_geometry.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeTransform",
        inputs={
            "Geometry": geometry,
            "Translation": translation,
            "Rotation": rotation,
            "Scale": scale,
        },
        attrs={"mode": "COMPONENTS"},
    )


def transform_by_matrix(
    geometry: nt.ProcNode[TMeshOrCurve],
    matrix: nt.SocketOrVal[pt.Matrix],
):
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeTransformByMatrix",
        inputs={
            "Geometry": geometry,
            "Matrix": matrix,
        },
        attrs={"mode": "MATRIX"},
    )


def translate_instances(
    instances: nt.ProcNode[nt.Instances],
    selection: nt.SocketOrVal[bool] = True,
    translation: nt.SocketOrVal[nt.pt.Vector] = (0, 0, 0),
    local_space: nt.SocketOrVal[bool] = True,
) -> nt.ProcNode[nt.Instances]:
    """
    Uses a TranslateInstances Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/instances/translate_instances.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeTranslateInstances",
        inputs={
            "Instances": instances,
            "Selection": selection,
            "Translation": translation,
            "Local Space": local_space,
        },
        attrs={},
    )


def triangulate(
    mesh: nt.ProcNode[pt.MeshObject],
    selection: nt.SocketOrVal[bool] = True,
    minimum_vertices: nt.SocketOrVal[int] = 4,
    ngon_method: Literal["BEAUTY", "CLIP"] = "BEAUTY",
    quad_method: Literal[
        "BEAUTY", "FIXED", "FIXED_ALTERNATE", "SHORTEST_DIAGONAL", "LONGEST_DIAGONAL"
    ] = "SHORTEST_DIAGONAL",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a Triangulate Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/operations/triangulate.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeTriangulate",
        inputs={
            "Mesh": mesh,
            "Selection": selection,
            "Minimum Vertices": minimum_vertices,
        },
        attrs={"ngon_method": ngon_method, "quad_method": quad_method},
    )


def trim_curve(
    curve: nt.ProcNode[pt.CurveObject],
    selection: nt.SocketOrVal[bool] = True,
    start: nt.SocketOrVal[float] = 0.0,
    end: nt.SocketOrVal[float] = 1.0,
    mode: Literal["FACTOR", "LENGTH"] = "FACTOR",
) -> nt.ProcNode[pt.CurveObject]:
    """
    Uses a TrimCurve Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/curve/operations/trim_curve.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeTrimCurve",
        inputs={"Curve": curve, "Selection": selection, "Start": start, "End": end},
        attrs={"mode": mode},
    )


def uv_pack_islands(
    uv: nt.SocketOrVal[pt.Vector] = (0, 0, 0),
    selection: nt.SocketOrVal[bool] = True,
    margin: nt.SocketOrVal[float] = 0.001,
    rotate: nt.SocketOrVal[bool] = True,
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a UVPackIslands Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/uv/pack_uv_islands.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeUVPackIslands",
        inputs={"UV": uv, "Selection": selection, "Margin": margin, "Rotate": rotate},
        attrs={},
    )


def uv_unwrap(
    selection: nt.SocketOrVal[bool] = True,
    seam: nt.SocketOrVal[bool] = False,
    margin: nt.SocketOrVal[float] = 0.001,
    fill_holes: nt.SocketOrVal[bool] = True,
    method: Literal["ANGLE_BASED", "CONFORMAL"] = "ANGLE_BASED",
) -> nt.ProcNode[pt.Vector]:
    """
    Uses a UVUnwrap Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/uv/uv_unwrap.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeUVUnwrap",
        inputs={
            "Selection": selection,
            "Seam": seam,
            "Margin": margin,
            "Fill Holes": fill_holes,
        },
        attrs={"method": method},
    )


def vertex_of_corner(corner_index: nt.SocketOrVal[int] = 0) -> nt.ProcNode[int]:
    """
    Uses a VertexOfCorner Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/mesh/topology/vertex_of_corner.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeVertexOfCorner",
        inputs={"Corner Index": corner_index},
        attrs={},
    )


TViewer = TypeVar(
    "TViewer", nt.SocketOrVal[bool], nt.SocketOrVal[int], nt.SocketOrVal[float]
)


'''
def viewer(
    geometry: t.ProcNode[t.Geometry],
    value: TViewer = 0,
    domain: TDomain = "AUTO",
    data_type: NodeDataType | RuntimeResolveDataType | None = None,
) -> t.ProcNode:
    """
    Uses a Viewer Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/output/viewer.html
    """
    if data_type is None:
        data_type = RuntimeResolveDataType(
            [NodeDataType.BOOLEAN, NodeDataType.INT, NodeDataType.FLOAT],
            ["Value"],
        )
    return t.ProcNode.from_nodetype(
        node_type="GeometryNodeViewer",
        inputs={"Geometry": geometry, "Value": value},
        attrs={
            "domain": domain,
            "data_type": data_type,
        },
    )
'''


class ViewportTransformResult(NamedTuple):
    projection: nt.ProcNode
    view: nt.ProcNode
    is_orthographic: nt.ProcNode[bool]


def viewport_transform() -> ViewportTransformResult:
    """
    Uses a ViewportTransform Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/input/scene/viewport_transform.html
    """
    node = nt.ProcNode.from_nodetype(
        node_type="GeometryNodeViewportTransform",
        inputs={},
        attrs={},
    )
    return ViewportTransformResult(
        node._output_socket("projection"),
        node._output_socket("view"),
        node._output_socket("is_orthographic"),
    )


def volume_cube(
    density: nt.SocketOrVal[float] = 1.0,
    background: nt.SocketOrVal[float] = 0.0,
    min: nt.SocketOrVal[nt.pt.Vector] = (-1, -1, -1),
    max: nt.SocketOrVal[nt.pt.Vector] = (1, 1, 1),
    resolution_x: nt.SocketOrVal[int] = 32,
    resolution_y: nt.SocketOrVal[int] = 32,
    resolution_z: nt.SocketOrVal[int] = 32,
) -> nt.ProcNode[pt.VolumeObject]:
    """
    Uses a VolumeCube Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/volume/primitives/volume_cube.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeVolumeCube",
        inputs={
            "Density": density,
            "Background": background,
            "Min": min,
            "Max": max,
            "Resolution X": resolution_x,
            "Resolution Y": resolution_y,
            "Resolution Z": resolution_z,
        },
        attrs={},
    )


def volume_to_mesh(
    volume: nt.ProcNode[pt.VolumeObject],
    threshold: nt.SocketOrVal[float] = 0.1,
    adaptivity: nt.SocketOrVal[float] = 0.0,
    resolution_mode: Literal["GRID", "VOXEL_AMOUNT", "VOXEL_SIZE"] = "GRID",
) -> nt.ProcNode[pt.MeshObject]:
    """
    Uses a VolumeToMesh Geometry Node.

    See: https://docs.blender.org/manual/en/4.2/modeling/geometry_nodes/volume/operations/volume_to_mesh.html
    """
    return nt.ProcNode.from_nodetype(
        node_type="GeometryNodeVolumeToMesh",
        inputs={"Volume": volume, "Threshold": threshold, "Adaptivity": adaptivity},
        attrs={"resolution_mode": resolution_mode},
    )
