#!/usr/bin/python3
from math import sqrt, degrees, floor

import shapely.geometry
import Polygon
from statistics import variance
import numpy as np
from matplotlib.pyplot import plot, show, scatter, cm, title
from numpy import sqrt, linspace, vstack, arccos, dot, arctan, zeros_like
from numpy.linalg import linalg
from sklearn.cluster import DBSCAN

from Line import Line
from Point import Point


# create array of points from the file
def create_data(file_name):
    points = []
    for point in open(file_name).readlines():
        values = point.split(',')
        if len(values) > 7:
            points.append(Point(float(values[0]), float(values[2]), -1*float(values[1]), float(values[3]),
                                float(values[4]), float(values[5]), float(values[6]), float(values[7])))
        else:
            points.append(Point(float(values[0]), float(values[2]), -1*float(values[1])))
    return points


# array of x dimensions of the points
def get_x_dimension(points):
    return [point.x for point in points]


# array of y dimensions of the points
def get_y_dimension(points):
    return [point.y for point in points]


# array of z dimensions of the points
def get_z_dimension(points):
    return [point.z for point in points]


# using DBSCAN algorithm to find clusters. Points with label -1 are not in any cluster,
# all points in the same cluster have the same label which is in [0, number of clusters)
def find_filtered_clusters(points, original_points, eps, lines, is_debug=True, min_samples=25):
    data = vstack((get_x_dimension(points), get_y_dimension(points))).T
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(data)  # eps = 0.2, 3
    core_samples_mask = zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    if max(labels) == -1:
        return [None], 0
    # Black removed and is used for noise instead.
    if is_debug:
        unique_labels = set(labels)
        colors = [cm.Spectral(each)
                  for each in linspace(0, 1, len(unique_labels))]
        scatter(get_x_dimension(original_points), get_y_dimension(original_points), linewidth=0.1, s=2)

        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]

            class_member_mask = (labels == k)

            xy = data[class_member_mask & core_samples_mask]
            plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=14)

            xy = data[class_member_mask & ~core_samples_mask]
            plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=6)
        title('DBSCAN: Estimated number of clusters:' + str(max(labels) + 1))

    num_of_clusters = max(labels) + 1
    exit_points = []
    for cluster_label in range(num_of_clusters):
        cluster = []
        for i, label in enumerate(labels):
            if label == cluster_label:
                cluster.append([i, points[i]])
        entrance_point_index = get_index_of_farthest_to_polygon(cluster, lines)

        exit_points.append(points[entrance_point_index])
        if is_debug:
            x_exit = points[entrance_point_index].x
            y_exit = points[entrance_point_index].y
            plot(x_exit, y_exit, 'ro')
    if is_debug:
        show()

    for i in range(len(labels)):
        points[i].label = labels[i]

    return exit_points, (max(labels) + 1)


# minimum distance from point to the polygon
def find_distance_to_closest_segment(point, edges):
    min_dist = 1000
    for edge in edges:
        dist = distance_between_point_and_segment(point.x, point.y, edge.point1.x, edge.point1.y, edge.point2.x,
                                                  edge.point2.y)
        if min_dist > dist:
            min_dist = dist
    return min_dist


# minimum distance from "point" to "segment"
def distance_between_point_and_segment(x_point, y_point, x_segment_1, y_segment_1, x_segment_2, y_segment_2):
    side_difference_x_1 = x_point - x_segment_1
    side_difference_y_1 = y_point - y_segment_1
    segment_difference_x = x_segment_2 - x_segment_1
    segment_difference_y = y_segment_2 - y_segment_1

    dot = side_difference_x_1 * segment_difference_x + side_difference_y_1 * segment_difference_y
    len_sq = segment_difference_x ** 2 + segment_difference_y ** 2
    param = -1
    if len_sq != 0:  # in case of 0 length line
        param = dot / len_sq

    if param < 0:
        xx = x_segment_1
        yy = y_segment_1
    elif param > 1:
        xx = x_segment_2
        yy = y_segment_2

    else:
        xx = x_segment_1 + param * segment_difference_x
        yy = y_segment_1 + param * segment_difference_y

    distance_x = x_point - xx
    distance_y = y_point - yy
    return sqrt(distance_x * distance_x + distance_y * distance_y)


# point with maximum distance to the polygon
def get_index_of_farthest_to_polygon(cluster, edges):
    points_with_distance = [[i, find_distance_to_closest_segment(point, edges)] for i, point in cluster]
    points_with_distance.sort(key=lambda point_with_distance: point_with_distance[1])
    return points_with_distance[-1][0]


# center of mass of the points
def center_of_mass(points):
    x = 0
    y = 0
    for point in points:
        x += point.x
        y += point.y
    length = len(points)
    return Point(x / length, y / length, 0)


# angle between line1 and line2
def get_original_angle(line1, line2):
    vector_1 = np.array([1, line1.slope], dtype=float)
    vector_2 = np.array([1, line2.slope], dtype=float)
    # assuming that the destination is in front of you
    unit_vector_1 = vector_1 / linalg.norm(vector_1)
    unit_vector_2 = vector_2 / linalg.norm(vector_2)
    dot_product = dot(unit_vector_1, unit_vector_2)
    angle = degrees(arccos(dot_product))
    return angle


# for each slice compute the point that its distance to c is the median distance in this slice
def get_median_points(slices, center):
    median_points = []
    for pizza_slice in slices:
        if pizza_slice is not None:
            pizza_slice.sort(key=lambda point: calculate_distance(point, center))
            median_points.append(pizza_slice[floor(len(pizza_slice) * 0.5)])
    return median_points


# array of slices' variances
def get_variances_by_slices(slices, center):
    variances = []
    for pizza_slice in slices:
        if pizza_slice is not None and len(pizza_slice) > 2:
            variances.append(variance([calculate_distance(point, center) for point in pizza_slice]))
        else:
            variances.append(0)
    return variances


#  simply, when three vertices of the polygon create an angle which clode to 180, remove the middle point
def smooth_polygon(exit_points, angle_range):
    exit_points.append(exit_points[0])
    polygon = Polygon.Polygon(exit_points)
    end = False
    while not end:
        edges = []
        temp = polygon.vertices[0]
        for vertex in polygon.vertices[1:]:
            edges.append(Line(temp, vertex))
            temp = vertex
        temp = edges[0]
        for i, edge in enumerate(edges):
            if i == 0:
                continue
            current_angle = get_original_angle(temp, edge)
            if not (angle_range < current_angle < 180 - angle_range):
                polygon.vertices.remove(polygon.vertices[i])
                break
            if i == len(edges) - 1:
                end = True
                break
            temp = edge
        polygon.edges = edges
    return polygon


# return angle in degrees
def get_angle_in_degrees_from_slope(slope):
    return degrees(arctan(slope))


# distance between point p1 and point p2
def calculate_distance(p1, p2):
    return sqrt(((p2.x - p1.x) ** 2) + ((p2.y - p1.y) ** 2))


# are p1 and p2 the sam point (with same coordinates)
def is_same_point(p1, p2):
    return p1.x == p2.x and p1.y == p2.y and p1.z == p2.z


# return array with all the points in cluster number i (points' label = i)
def points_with_label_i(points, i):
    points_with_label_i_arr = []
    for point in points:
        if point.label == i:
            points_with_label_i_arr.append(point)
    return points_with_label_i_arr


# return array of clusters. In index i, we have cluster number i (points with label = i).
def create_clusters(points, num_of_clusters):
    clusters = []
    for i in range(num_of_clusters):
        cluster = points_with_label_i(points, i)
        clusters.append(cluster)
    return clusters


# minimum height of a point in a specific cluster. "local min"
def min_height_of_cluster(cluster):
    min_height = cluster[0].z
    for point in cluster:
        if point.z < min_height:
            min_height = point.z
    return min_height


# array containing of minimum height of cluster i in index i
def clusters_min_heights(clusters, num_of_clusters):
    min_heights = []
    for i in range(num_of_clusters):
        min_height = min_height_of_cluster(clusters[i])
        min_heights.append(min_height)
    return min_heights


# minimum height of a point in all clusters. "global min"
def global_min_height(min_heights):
    return min(min_heights)


# maximum difference from any local minimum height to the global minimum height
def max_diff_from_local_to_global_min(min_heights, all_min_height):
    diffs = []
    for i in range(len(min_heights)):
        diffs.append(abs(min_heights[i]-all_min_height))
    return max(diffs)


# grade point according to its cluster's min height
def grade_by_cluster_min_height(all_min_height, local_min_height, max_diff_to_min):
    diff = abs(local_min_height-all_min_height)
    if max_diff_to_min == 0:
        return 100
    return 100-100*(diff/max_diff_to_min)


# for each cluster, create a polygon from its points
def create_clusters_polygons(clusters, num_of_clusters):
    pgons = []
    for i in range(num_of_clusters):
        pgon = shapely.geometry.Polygon(zip(get_x_dimension(clusters[i]), get_y_dimension(clusters[i])))
        pgons.append(pgon)
    return pgons


# for each cluster, create a minimum bounding box around its polygon
def create_min_bounding_boxes(polygons, num_of_clusters):
    boxes = []
    for i in range(num_of_clusters):
        pgon = polygons[i]
        box = pgon.minimum_rotated_rectangle
        boxes.append(box)
    return boxes


# for each cluster, calculate the length and width of its minimum bounding box
def boxes_lengths_and_widths(boxes, num_of_clusters):
    lengths = []
    widths = []
    for i in range(num_of_clusters):
        box = boxes[i]
        # get coordinates of polygon vertices
        x, y = box.exterior.coords.xy
        # get length of bounding box edges
        edge_length = (shapely.geometry.Point(x[0], y[0]).distance(shapely.geometry.Point(x[1], y[1])),
                       shapely.geometry.Point(x[1], y[1]).distance(shapely.geometry.Point(x[2], y[2])))
        # get length of polygon as the longest edge of the bounding box
        length = max(edge_length)
        # get width of polygon as the shortest edge of the bounding box
        width = min(edge_length)
        lengths.append(length)
        widths.append(width)
    return lengths, widths


# return cluster's minimum bounding box's length to width ratio
def length_to_width_ratio(length, width):
    return length/width


# return maximum length to width ratio of clusters' bounding boxes'
def max_length_to_width_ratio(lengths, widths, num_of_clusters):
    max_ratio = 0
    for i in range(num_of_clusters):
        ratio = length_to_width_ratio(lengths[i], widths[i])
        if ratio > max_ratio:
            max_ratio = ratio
    return max_ratio


# grade according to cluster's minimum bounding box's length to width ratio
def grade_by_length_to_width_ratio(length, width, max_ratio):
    if max_ratio == 0:
        return 100
    ratio = length_to_width_ratio(length, width)
    return 100*(ratio/max_ratio)

