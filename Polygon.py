from Line import Line
from Point import Point
from auxiliary_functions import distance_between_point_and_segment


class Polygon:
    def __init__(self, vertices: [Point], edges: [Line] = None):
        self.vertices = vertices
        self.edges = edges

    def is_inside(self, point):
        amount_of_crossings = 0
        vertices_amount = len(self.vertices)
        for (i, vertex) in enumerate(self.vertices):
            next_vertex = self.vertices[(i + 1) % vertices_amount]
            if ((vertex.x < point.x) and (point.x < next_vertex.x)) or (
                    (vertex.x > point.x) and (point.x > next_vertex.x)):
                ratio = (point.x - next_vertex.x) / (vertex.x - next_vertex.x)
                amount_of_crossings += 1 if ((ratio * vertex.y) + ((1 - ratio) * next_vertex.y)) >= point.y else 0
        return amount_of_crossings % 2 != 0

    def filter_insiders(self, points):
        good_points = []
        for point in points:
            if not self.is_inside(point):
                good_points.append(point)
        return good_points

    @staticmethod
    def filter_epsilon_by_variances(slices, edges, variances, eps=0.2):
        good_points = []
        min_variance = min(variances)
        max_variance = max(variances)
        for (pizza_slice, variance) in zip(slices, variances):
            if pizza_slice is not None:
                ratio = (variance - min_variance) / (max_variance - min_variance)
                for point in pizza_slice:
                    min_dist = 100000
                    for edge in edges:
                        dist = distance_between_point_and_segment(point.x, point.y, edge.point1.x, edge.point1.y,
                                                                  edge.point2.x, edge.point2.y)
                        if dist < min_dist:
                            min_dist = dist
                    if min_dist > (1 - ratio) * eps:
                        good_points.append(point)
        return good_points
