import numpy as np
from matplotlib.cm import get_cmap

class Track:
    def __init__(self, track_id):
        self.track_id = track_id
        self.measurements = []

    def add_measurement(self, timestamp, x, y):
        self.measurements.append({'timestamp': timestamp, 'x': x, 'y': y})

    def sort_by_timestamp(self):
        self.measurements = sorted(self.measurements, key=lambda k: k['timestamp'])

    def calculate_distance(self):
        if len(self.measurements) < 2:
            return 0.0  # Distance is zero if there's only one measurement

        start_point = (self.measurements[0]['x'], self.measurements[0]['y'])
        end_point = (self.measurements[-1]['x'], self.measurements[-1]['y'])
        return euclidean_distance(start_point, end_point)
    
    def total_distance(self):
        total_distance = 0
        for i in range(len(self.measurements)-1):
            total_distance += euclidean_distance((self.measurements[i]['x'], self.measurements[i]['y']), (self.measurements[i+1]['x'], self.measurements[i+1]['y']))
        return total_distance

    def __repr__(self) -> str:
        temp_str = f"Track {self.track_id} with {len(self.measurements)} measurements\n"
        for measurement in self.measurements:
            temp_str += f"Timestamp: {measurement['timestamp']:.2f}, x: {measurement['x']:.2f}, y: {measurement['y']:.2f}\n"
        return temp_str  

def euclidean_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def add_color_scaling(measurement_dict):
    data = measurement_dict
    cmap = get_cmap('Greys')
    timestamps = []
    for timestamp, measurements in data.items():
        timestamps.append(timestamp)
    timestamps = np.asarray(timestamps)
    interval = (timestamps-timestamps[0]+timestamps[-1]/5)/(timestamps[-1]-timestamps[0]+timestamps[-1]/5)

    for timestamp, measurements in data.items():
        # Iterate over each measurement and assign a color based on position
        for index, measurement in enumerate(measurements):
            measurement_color = cmap(interval[timestamps == timestamp])

            # Append the color value to the measurement
            measurement.append(measurement_color.squeeze())
           

    return data

def point_inside_polygon(measurement, vertices):
    """
    Function for checking if a point is inside a polygon
    """
    x = measurement[0]
    y = measurement[1]
    n = len(vertices)
    inside = False
    p1x, p1y = vertices[0]
    for i in range(n + 1):
        p2x, p2y = vertices[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def filter_out_measurements_outside_area(measurement_dict,vertices):
    new_measurement_dict = {}
    for timestamp, measurements in measurement_dict.items():
        new_measurement_dict[timestamp] = []
        for measurement in measurements:
            if point_inside_polygon((measurement[0], measurement[1]), vertices):
                new_measurement_dict[timestamp].append(measurement)
    return new_measurement_dict


