import json
import numpy as np

def import_data_from_json(file_path: str):
    measurement_dict = {}
    measurement_dict['Timestamp'] = ["x","y","area","polygon_xs","polygon_ys"]
    measurement_dict_for_debugging = {}
    measurement_dict_for_debugging['Timestamp'] = ["x","y","area"]
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Define the first timestamp
    timestamp = data[0]["header"]["stamp"]["secs"]
    timestamps_nano = data[0]["header"]["stamp"]["nsecs"]
    first_timestamp = timestamp + timestamps_nano*10**(-9)

    for k, item in enumerate(data):
        if k == 0:
            timestamp = 0
        else:
            timestamp = item["header"]["stamp"]["secs"]
            timestamps_nano = item["header"]["stamp"]["nsecs"]
            timestamp = timestamp + timestamps_nano*10**(-9) - first_timestamp

        measurement_dict[timestamp] = []
        # Add a debugging dictionary with only the x, y and area
        measurement_dict_for_debugging[timestamp] = []
        item_data = item["scan"]
        for i, measurement in enumerate(item_data):
            if measurement["type"] == 3:
                y = measurement["cluster_centroid"]["x"]
                x = measurement["cluster_centroid"]["y"]
                area = measurement["area"]
                xs = []
                ys = []
                for point in measurement["hull"]["points"]:
                    xs.append(point["y"])
                    ys.append(point["x"])
                xs.append(xs[0])
                ys.append(ys[0])
            else:
                continue
            
            measurement_dict[timestamp].append([x,y,area,xs,ys])
            measurement_dict_for_debugging[timestamp].append((x,y,area))
    np.save('measurement_dict_for_debugging.npy', measurement_dict_for_debugging)
    np.save('measurement_dict.npy', measurement_dict)
    return measurement_dict
       
        

