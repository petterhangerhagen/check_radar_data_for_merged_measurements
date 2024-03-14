"""
Author: Petter Hangerhagen
Email: petthang@stud.ntnu.no
Date: February 27, 2024
Description: 
"""
import import_data_from_json
import merged_measurement
import plotting
import utilities
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

"""
IMPORTANT: Need to change the radar_data_path and wokring_directory to the correct paths!!
"""
work_dir = "/home/aflaptop/Desktop/merged_measurement"
radar_data_path = "/home/aflaptop/Documents/radar_data"


def write_filenames_to_txt(filename, txt_filename):
    """
    Writes the filename to the txt file, if the filename is not already written
    """
    with open(txt_filename, 'r') as f:
        lines = f.readlines()
    files = []
    for line in lines:
        files.append(line[:-1])

    already_written = False
    if os.path.basename(filename) in files:
        already_written = True
        print(f"File {os.path.basename(filename)} already written to txt file")

    if not already_written:
        with open(txt_filename, 'a') as f:
            f.write(os.path.basename(filename) + "\n")
   
def find_files(root,txt_filename):
    """
    Finds the files in the root directory that are given in the txt file
    """
    with open(txt_filename, 'r') as f:
        lines = f.readlines()
    files = []
    for line in lines:
        files.append(line[:-1])

    path_list = []
    for item in os.listdir(root):
        list_of_files = glob.glob(os.path.join(root, item, '*.json'))
        for file in list_of_files:
            if  os.path.basename(file) in files:
                path_list.append(file)

    return path_list

def make_new_directory(filename):
    plotting_dir = f"{work_dir}/merged_measurements_plots"
    filename = filename[:-5]
    save_dir = os.path.join(plotting_dir,filename)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    return save_dir
  


def main():
    # root = f"{radar_data_path}/data_aug_15-18"
    # root = f"{radar_data_path}/data_aug_18-19"
    # root = f"{radar_data_path}/data_aug_22-23"
    # root = f"{radar_data_path}/data_aug_25-26-27"
    # root = f"{radar_data_path}/data_aug_28-29-30-31"
    # root = f"{radar_data_path}/data_sep_1-2-3-4-5-6-7"
    # root = f"{radar_data_path}/data_sep_8-9-11-14"
    # root = f"{radar_data_path}/data_sep_17-18-19-24"
    # path_list = glob.glob(os.path.join(root, '*.json'))


    txt_filename = f"{work_dir}/merged_measurements.txt"
    # path_list = find_files(radar_data_path,txt_filename)

    path_list = [f"{radar_data_path}/data_aug_18-19/rosbag_2023-08-19-14-22-41.json"]
    
    plot_only_map = False
    if plot_only_map:   
        fig, ax, originx, origin_y = plotting.plot()
        plt.savefig("/home/aflaptop/Desktop/merged_measurement/land_with_and_without_filter.png",dpi=400)
        plt.show()

    for i, file_path in enumerate(path_list):
        if True:
            print(f"Processing file {i+1} of {len(path_list)}")
            filename = os.path.basename(file_path)
            print(f"File: {filename}")
            measurement_dict = import_data_from_json.import_data_from_json(file_path)
            measurement_dict.pop('Timestamp')
            measurement_dict = utilities.add_color_scaling(measurement_dict)

            vertices = [(100, 0), (100, -40), (0, -80), (-50,-110), (-90, -120), (-105, -110),(-50,-60),(-25,-20),(0,0)]
            measurement_dict = utilities.filter_out_measurements_outside_area(measurement_dict, vertices)
    
            merged_measurements_object = merged_measurement.ComputeMergeMeasurements(measurement_dict, filename)
            merged_measurements_object.check_for_merge_measurements()
            merged_measurements = merged_measurements_object.new_merged_measurements
            print(f"Number of merged measurements: {len(merged_measurements)}")
            
            if len(merged_measurements) == 0:
                # plotting.plot_for_vizualization_without_merged_measurements(measurement_dict, filename, work_dir)
                continue
            else:
                # plotting.plot_for_vizualization(merged_measurements, measurement_dict, filename, work_dir)
                save_dir = make_new_directory(filename)
                plotting.plot_for_report(measurement_dict, merged_measurements, save_dir, filename)
                write_filenames_to_txt(file_path, txt_filename)


if __name__ == "__main__":
    main()