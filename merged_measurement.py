"""
Author: Petter Hangerhagen
Email: petthang@stud.ntnu.no
Date: February 27, 2024
Description: 
"""
import numpy as np
from utilities import euclidean_distance, Track


class CloseMeasurementsPair:
    """
    Class for storing two close measurements and the distance between them
    """
    def __init__(self, timestamp, measurement1, measurement2,circle):
        self.timestamp = timestamp
        self.measurement1 = measurement1[0:2]
        self.measurement2 = measurement2[0:2]
        self.measurement1_polygon = (measurement1[3], measurement1[4])
        self.measurement2_polygon = (measurement2[3], measurement2[4])
        self.circle_center = circle[0]
        self.circle_radius = circle[1]
        self.areas = [measurement1[2], measurement2[2]]
        self.distance_between = np.sqrt((measurement1[0]-measurement2[0])**2 + (measurement1[1]-measurement2[1])**2)

    def __repr__(self) -> str:
        temp_str = f"Timestamp: {self.timestamp:.2f}\n"
        temp_str += f"Measurement 1: {self.measurement1}\n"
        temp_str += f"Measurement 2: {self.measurement2}\n"
        temp_str += f"Distance between measurements: {self.distance_between:.2f}\n"
        return temp_str
    
class MergeMeasurements:
    """
    Class for storing the previous and current measurements that are merged
    """
    def __init__(self, close_measurement_pair, current_timestamp, current_measurement):
        self.prev_timestamp = close_measurement_pair.timestamp
        self.prev_measurement1 = close_measurement_pair.measurement1
        self.prev_measurement2 = close_measurement_pair.measurement2
        self.distance_between = close_measurement_pair.distance_between
        self.prev_measurement1_polygon = close_measurement_pair.measurement1_polygon
        self.prev_measurement2_polygon = close_measurement_pair.measurement2_polygon
        self.area = close_measurement_pair.areas

        self.current_timestamp = current_timestamp
        self.current_measurement = current_measurement[0:2]
        self.current_measurement_polygon = (current_measurement[3], current_measurement[4])
        self.current_area = current_measurement[2]

    def __repr__(self) -> str:
        temp_str = f"Previous timestamp: {self.prev_timestamp:.2f}\n"
        temp_str += f"Previous measurement 1: {self.prev_measurement1}\n"
        temp_str += f"Previous measurement 2: {self.prev_measurement2}\n"
        temp_str += f"Distance between measurements: {self.distance_between:.2f}\n"
        temp_str += f"Pervious measurement 1 area: {self.area[0]}\n"
        temp_str += f"Pervious measurement 2 area: {self.area[1]}\n"
        temp_str += f"Current timestamp: {self.current_timestamp:.2f}\n"
        temp_str += f"Current measurement: {self.current_measurement}\n"
        temp_str += f"Current measurement area: {self.current_area}\n"
        return temp_str
    
    def add_track_ids(self, track_ids):
        self.track_ids = track_ids

    def plot_MM_init(self, ax, origin_x=0, origin_y=0):
        ax.scatter(self.prev_measurement1[0] + origin_x, self.prev_measurement1[1] + origin_y, c="#1f77b4", zorder=10, label='Close measurement pair')
        ax.scatter(self.prev_measurement2[0] + origin_x, self.prev_measurement2[1] + origin_y, c='#1f77b4', zorder=10)
        ax.plot(np.array(self.prev_measurement1_polygon[0]) + origin_x, np.array(self.prev_measurement1_polygon[1]) + origin_y, c='#1f77b4',linewidth=3, zorder=9, label='Close measurement pair cluster area')
        ax.plot(np.array(self.prev_measurement2_polygon[0]) + origin_x, np.array(self.prev_measurement2_polygon[1]) + origin_y, c='#1f77b4',linewidth=3, zorder=9)
        ax.scatter(self.current_measurement[0] + origin_x, self.current_measurement[1] + origin_y, c='#ff7f0e', zorder=10, label='Merged measurement')
        ax.plot(np.array(self.current_measurement_polygon[0]) + origin_x, np.array(self.current_measurement_polygon[1]) + origin_y, c='#ff7f0e',linewidth=3, zorder=8, label='Merged measurement cluster area')


    def plot_MM_update(self, ax, origin_x=0, origin_y=0):
        ax.scatter(self.prev_measurement1[0] + origin_x, self.prev_measurement1[1] + origin_y, c='#1f77b4', zorder=10)
        ax.scatter(self.prev_measurement2[0] + origin_x, self.prev_measurement2[1] + origin_y, c='#1f77b4', zorder=10)
        ax.scatter(self.current_measurement[0] + origin_x, self.current_measurement[1] + origin_y, c='#ff7f0e', zorder=10)
        ax.plot(np.array(self.current_measurement_polygon[0]) + origin_x, np.array(self.current_measurement_polygon[1]) + origin_y, c='#ff7f0e',linewidth=2, zorder=10)
     
class ComputeMergeMeasurements:
    def __init__(self, measurement_dict, filename):
        self.measurement_dict = measurement_dict
        self.filename = filename

        # Parameters for determining close measurements and measurement area thresholds.
        self.distance_between_measurements = 20
        self.measurement_area_threshold = 5

        # Parameters for tracking, including distance and time between consecutive measurements in a track.
        self.distance_between_measurements_in_track = 15
        self.time_between_measurements_in_track = 4
        self.tracks = self.establish_tracks()  # Initializes tracks based on the measurements.

        # Lists for storing information about measurements that are close and potentially merged.
        self.close_measurements = []
        self.merged_measurements = []
        self.new_merged_measurements = []

    def get_circle(self, point1, point2):
        # Calculate the center and radius of a circle that encompasses two points.
        center_x, center_y = ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)
        radius = (euclidean_distance(point1, point2) / 2) * 0.8  # Slightly reduce radius for a buffer.
        center = (center_x, center_y)
        return (center, radius)

    def get_next_key_in_measurement_dict(self, current_key):
        # Find the next key in the measurement dictionary, if any, following the current key.
        d = self.measurement_dict
        keys = list(d.keys())
        try:
            current_index = keys.index(current_key)
            return keys[current_index + 1]  # Return the next key.
        except (ValueError, IndexError):
            return None  # Return None if current_key is the last key or not found.

    def check_next_measurement(self, next_timestamp, close_measurement_object):
        # Check if the next measurement at next_timestamp should be considered as merged with the current one.
        merge_measurements = None
        number_of_merged_measurements_at_next_timestamp = 0
        next_measurements_to_plot = []
        if next_timestamp is not None:
            next_measurements = self.measurement_dict[next_timestamp]
            for next_measurement in next_measurements:
                # Check if the there are multiple measurements inside an extended circle around the current measurement.
                if euclidean_distance(next_measurement, close_measurement_object.circle_center) < close_measurement_object.circle_radius * 2:
                    next_measurements_to_plot.append(next_measurement)
                # Check if the next measurement is inside the circle around the current measurement.
                if euclidean_distance(next_measurement, close_measurement_object.circle_center) < close_measurement_object.circle_radius:
                    if next_measurement[2] > (close_measurement_object.areas[0] + close_measurement_object.areas[1]):
                        number_of_merged_measurements_at_next_timestamp += 1
                        merge_measurements = MergeMeasurements(close_measurement_object, next_timestamp, next_measurement)
        
        # Decide whether to add the merge_measurements to the list of merged measurements or not.
        # There should only be one merged measurement at the next timestamp, and it should inside the circle.
        if merge_measurements is not None and len(next_measurements_to_plot) > 1:
            print("Maybe not merged measurement after all, since there are more than one measurement close to the circle")
        elif merge_measurements is None:
            # If no merge is necessary, no action is taken.
            pass
        else:
            # We only have one measurement in the area, and it is considered merged.
            self.merged_measurements.append(merge_measurements)

    def establish_tracks(self):
        """
        Used to establish "tracks", which are used to filter out noise
        """
        # Establish tracks from the measurements by linking measurements that are close in space and time.
        tracks = []
        track_counter = 0
        for timestamp, measurements in self.measurement_dict.items():
            if not tracks:
                # Initialize tracks with the first set of measurements if tracks list is empty.
                for measurement in measurements:
                    track = Track(track_counter)
                    track.add_measurement(timestamp, measurement[0], measurement[1])
                    tracks.append(track)
                    track_counter += 1
                continue

            # For subsequent measurements, attempt to add them to existing tracks based on proximity criteria.
            for measurement in measurements:
                distances_to_last = []
                distance_to_second_last = []
                y = measurement[0]
                x = measurement[1]
                for track in tracks:
                    # Calculate distances from the measurement to the last and second-last points in each track.
                    distance_to_track = euclidean_distance((track.measurements[-1]['x'], track.measurements[-1]['y']), (x, y))
                    distances_to_last.append(distance_to_track)
                    if len(track.measurements) > 1:
                        distance_to_second_last.append(euclidean_distance((track.measurements[-2]['x'], track.measurements[-2]['y']), (x, y)))
                    else:
                        distance_to_second_last.append(1000)  # Arbitrary large distance if no second-last measurement.

                # Decide whether to add the measurement to an existing track or start a new one based on the distances and time.
                if min(distances_to_last) < self.distance_between_measurements_in_track:
                    track_index = distances_to_last.index(min(distances_to_last))
                    last_timestamp = tracks[track_index].measurements[-1]['timestamp']
                    # If the time gap is small enough, add the measurement to the track.
                    if timestamp - last_timestamp < self.time_between_measurements_in_track:
                        tracks[track_index].add_measurement(timestamp, x, y)
                    else:
                        # If the time gap is too large, start a new track.
                        track = Track(track_counter)
                        track.add_measurement(timestamp, x, y)
                        tracks.append(track)
                        track_counter += 1

                elif min(distance_to_second_last) < self.distance_between_measurements_in_track:
                    # Similar logic for second-last measurements.
                    track_index = distance_to_second_last.index(min(distance_to_second_last))
                    last_timestamp = tracks[track_index].measurements[-1]['timestamp']
                    if timestamp - last_timestamp < self.time_between_measurements_in_track:
                        tracks[track_index].add_measurement(timestamp, x, y)
                    else:
                        track = Track(track_counter)
                        track.add_measurement(timestamp, x, y)
                        tracks.append(track)
                        track_counter += 1
                
                else:
                    # If no existing track is suitable, start a new track.
                    track = Track(track_counter)
                    track.add_measurement(timestamp, x, y)
                    tracks.append(track)
                    track_counter += 1
        return tracks  # Return the list of established tracks.

    def check_tracks_for_same_measurement(self):
        """
        One limitation of the current implementation is that it does not consider the possibility of a single object being split into
        two clusters due to the radar's limited resolution.
        This function checks if the previous and current measurements involved in a merge are part of the same track. If they are,
        the merge is considered to be a false positive and is removed from the list of merged measurements.
        """
        new_merged_measurements = []
        for merged_measurement in self.merged_measurements:
            track_id_of_current_measurement = None
            track_id_of_prev_measurement1 = None
            track_id_of_prev_measurement2 = None
            for track in self.tracks:
                # Identify the tracks of the current and previous measurements involved in a merge.
                for measurement in track.measurements:
                    if measurement['y'] == merged_measurement.current_measurement[0] and measurement['x'] == merged_measurement.current_measurement[1]:
                        track_id_of_current_measurement = track.track_id
                    elif measurement['y'] == merged_measurement.prev_measurement1[0] and measurement['x'] == merged_measurement.prev_measurement1[1]:
                        track_id_of_prev_measurement1 = track.track_id
                    elif measurement['y'] == merged_measurement.prev_measurement2[0] and measurement['x'] == merged_measurement.prev_measurement2[1]:
                        track_id_of_prev_measurement2 = track.track_id

            # If the current and previous measurements are from different tracks, consider them truly merged.
            if track_id_of_current_measurement != track_id_of_prev_measurement1 or track_id_of_current_measurement != track_id_of_prev_measurement2:
                new_merged_measurements.append(merged_measurement)
        self.new_merged_measurements = new_merged_measurements


    def check_for_merge_measurements(self):
        """
        The main function for checking for merged measurements.
        First establishes close measurements, then checks if the next measurement is also close to the circle around the current
        measurement. If it is, the two measurements are considered merged.
        """
        for timestamp, measurements in self.measurement_dict.items():
            for i in range(len(measurements)):
                for j in range(i+1, len(measurements)):
                    if euclidean_distance(measurements[i], measurements[j]) < self.distance_between_measurements:
                        if measurements[i][2] > self.measurement_area_threshold and measurements[j][2] > self.measurement_area_threshold:
                            circle = self.get_circle(measurements[i], measurements[j])
                            self.close_measurements.append(CloseMeasurementsPair(timestamp, measurements[i], measurements[j],circle))

        if self.close_measurements == []:
            print("No close measurements, resulting in no merged measurements")
        else:
            for close_measurement_object in self.close_measurements:
                timestamp = close_measurement_object.timestamp
                next_timestamp = self.get_next_key_in_measurement_dict(timestamp)
                self.check_next_measurement(next_timestamp,close_measurement_object)

            self.check_tracks_for_same_measurement()       


