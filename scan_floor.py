from statistics import mean
from matplotlib.pyplot import scatter, plot, show, axis, title, figure
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import Pizza
import Polygon
from auxiliary_functions import center_of_mass, calculate_distance, \
    get_x_dimension, get_y_dimension, create_data, clusters_min_heights, create_clusters_polygons, create_clusters, \
    min_height_of_cluster, find_filtered_clusters, get_median_points, create_min_bounding_boxes, \
    boxes_lengths_and_widths, grade_by_length_to_width_ratio, max_length_to_width_ratio, grade_by_cluster_min_height,\
    max_diff_from_local_to_global_min, global_min_height, smooth_polygon, get_variances_by_slices, get_z_dimension


# plot polygon descriptor over point cloud
def show_polygon(exit_points, points):
    scatter(get_x_dimension(points), get_y_dimension(points), linewidth=0.1, s=2)
    for point in exit_points:
        plot(point.x, point.y, 'ro')
    plot(get_x_dimension(exit_points), get_y_dimension(exit_points), color="pink")
    title("B: all points, P: polygon descriptor")
    show()


# after grading each point, compare with other grades and choose best points
def handle_grades(grades, points, exit_points, avg_ratio, avg_min_height, ratios, min_heights):
    avg_grade = sum(grades)/len(grades)
    green = []
    red = []
    yellow = []
    fig = figure()
    ax = fig.add_subplot()
    for point in exit_points:
        if grades[point.label] > avg_grade+5.0:
            green.append(point)
        elif grades[point.label] < avg_grade-5.0:
            red.append(point)
        else:
            yellow.append(point)

    for point in exit_points:
        i = point.label
        point_str = "Grade: " + str('%.2f' % grades[i]) + "\n"
        if ratios[i] >= avg_ratio:
            point_str = point_str + "ratio: Good" + "\n"
        else:
            point_str = point_str + "ratio: Bad" + "\n"
        if min_heights[i] >= avg_min_height:
            point_str = point_str + "min height: Good" + "\n"
        else:
            point_str = point_str + "min height: Bad" + "\n"
        ax.text(exit_points[i].x, exit_points[i].y, point_str, fontsize=7, style='italic', bbox={'facecolor': 'red', 'alpha': 0.1, 'pad': 2})
        # Create a Rectangle patch
        rect = patches.Rectangle((exit_points[i].x-0.1, exit_points[i].y-0.15), 0.2, 0.3, linewidth=1, edgecolor='black', facecolor='none')
        # Add the patch to the Axes
        ax.add_patch(rect)

    scatter(get_x_dimension(points), get_y_dimension(points), linewidth=0.1, s=2)
    for point in green:
        plot(point.x, point.y, 'go')
    for point in red:
        plot(point.x, point.y, 'ro')
    for point in yellow:
        plot(point.x, point.y, 'yo')
    show()


# the "main" function
def get_polygon_checkpoints(points_file_path, is_debug=False, angle=10, angle_range=10, join_clusters_eps=0.15):
    # all points in the point cloud
    points = create_data(points_file_path)
    # print point cloud in 3D
    fig = figure()
    ax1 = fig.add_subplot(projection='3d')
    ax1.scatter(get_x_dimension(points), get_x_dimension(points), get_z_dimension(points))
    ax1.set_xlabel('X-axis', fontsize=15, rotation=150)
    ax1.set_ylabel('Y-axis', fontsize=15)
    ax1.set_zlabel('Z-axis', fontsize=15, rotation=60)
    title('3D point cloud')
    show()
    # center of mass of points; we position a “pizza” that its center is center
    center = center_of_mass(points)
    # the pizza
    lines = Pizza.create_pizza_lines(center, angle)
    slices = Pizza.create_slices(lines, points, angle)
    #  for each slice compute the point that its distance to center is the median distance in this slice
    median_points = get_median_points(slices, center)
    radius = mean([calculate_distance(point, center) for point in median_points]) / 2
    exit_points = median_points
    # when three vertices of the polygon create an angle which clode to 180, remove the middle point
    polygon = smooth_polygon(exit_points, angle_range)
    #  the inside (floor, furniture, ...) of my space isn’t interesting so we remove it
    filtered_points = polygon.filter_insiders(points)
    # new slices after filtering
    slices = Pizza.create_slices(lines, filtered_points, angle)
    variances = get_variances_by_slices(slices, center)
    #  filter points outside the polygon by variances
    filtered_points = polygon.filter_epsilon_by_variances(slices, polygon.edges, variances, radius)
    # plot after removing inside points and high-density points
    scatter(get_x_dimension(points), get_y_dimension(points), linewidth=0.1, s=2)
    for point in filtered_points:
        plot(point.x, point.y, 'r*')
        title("After inside & variance filter. Remaining points in RED")
    show()
    # DBSCAN algorithm
    exit_points, num_of_clusters = find_filtered_clusters(filtered_points, points, join_clusters_eps, polygon.edges,
                                                          is_debug, min_samples=5)
    # assessing clusters
    clusters = create_clusters(filtered_points, num_of_clusters)
    polygons = create_clusters_polygons(clusters, num_of_clusters)
    min_bounding_boxes = create_min_bounding_boxes(polygons, num_of_clusters)
    lengths, widths = boxes_lengths_and_widths(min_bounding_boxes, num_of_clusters)
    max_ratio_length_to_width = max_length_to_width_ratio(lengths, widths, num_of_clusters)
    min_heights = clusters_min_heights(clusters, num_of_clusters)
    min_height_global = global_min_height(min_heights)
    max_diff_to_min = max_diff_from_local_to_global_min(min_heights, min_height_global)
    grades = []
    ratios = []
    min_heights = []
    sum_of_ratios = 0
    sum_of_min_heights = 0
    # grade each point (representative of its cluster)
    for point in exit_points:
        i = point.label
        cluster = clusters[i]
        cluster_min_height = min_height_of_cluster(cluster)
        length = lengths[i]
        width = widths[i]
        grade_min_height = grade_by_cluster_min_height(min_height_global, cluster_min_height, max_diff_to_min)
        grade_ratio = grade_by_length_to_width_ratio(length, width, max_ratio_length_to_width)
        grade = 0.5*grade_min_height+0.5*grade_ratio
        grades.append(grade)
        ratios.append(grade_ratio)
        min_heights.append(grade_min_height)
        sum_of_ratios += grade_ratio
        sum_of_min_heights += grade_min_height

    avg_ratio = sum_of_ratios/num_of_clusters
    avg_min_height = sum_of_min_heights/num_of_clusters
    handle_grades(grades, points, exit_points, avg_ratio, avg_min_height, ratios, min_heights)

    return exit_points


if __name__ == '__main__':
    get_polygon_checkpoints("indoor_example.csv", True)
    get_polygon_checkpoints("outdoor_example.csv", True)

# room parameters
# angle = 20, angle_range = 5
# filter_epsilon : eps = 0.5
# DBSCAN : eps = 0.15 , min_samples = 25
# join_clusters : eps = 0.001

# open space parameters
# angle = 20, angle_range = 5
# filter_epsilon : eps = 0.2
# DBSCAN : eps = 0.15 , min_samples = 25 ??
# join_clusters : eps = 0.005

# pay attention - the scale is 20 / 50 times larger than orb slam, some the parameters will change accordingly
