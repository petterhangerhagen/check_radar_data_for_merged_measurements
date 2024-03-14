import matplotlib.pyplot as plt
import numpy as np
from images_to_video import images_to_video_opencv, empty_folder
import progressbar
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

def plot(work_dir):
    fig, ax = plt.subplots(figsize=(11, 7.166666))
    data = np.load(f"{work_dir}/npy_files/occupancy_grid.npy",allow_pickle='TRUE').item()
    occupancy_grid = data["occupancy_grid"]
    origin_x = data["origin_x"]
    origin_y = data["origin_y"]
    colors = [(1, 1, 1), (0.8, 0.8, 0.8)]  # Black to light gray
    cm = LinearSegmentedColormap.from_list('custom_gray', colors, N=256)
    ax.imshow(occupancy_grid, cmap=cm, interpolation='none', origin='upper', 
              extent=[0, occupancy_grid.shape[1], 0, occupancy_grid.shape[0]])
    
    # Highlight origin
    ax.plot(origin_x, origin_y, c="red", marker="o", zorder=10, markersize=10)
    ax.annotate(f"Radar", (origin_x + 2, origin_y + 2), zorder=10, fontsize=15)
    
    display_second_occupancy_grid = True
    if display_second_occupancy_grid:
        # Load and display the second occupancy grid
        data2 = np.load(f"{work_dir}/npy_files/occupancy_grid_without_dilating.npy", allow_pickle=True).item()
        occupancy_grid2 = data2["occupancy_grid"]
        
        # Second imshow with alpha for overlap effect
        ax.imshow(occupancy_grid2, cmap="binary", interpolation='none', origin='upper', 
                extent=[0, occupancy_grid2.shape[1], 0, occupancy_grid2.shape[0]], alpha=0.2)
        
        # Create custom patches for legend
        first_image_patch = mpatches.Patch(color='gray', label='True land')
        second_image_patch = mpatches.Patch(color='black', alpha=0.2, label='Land after dilation')
        

        # Add legend
        # ax.legend(handles=[first_image_patch, second_image_patch], loc='upper left', fontsize=12)
        
    
    ax.set_xlim(origin_x-120,origin_x + 120)
    ax.set_ylim(origin_y-140, origin_y + 20)
    ax.set_aspect('equal')
    ax.set_xlabel('East [m]',fontsize=15)
    ax.set_ylabel('North [m]',fontsize=15)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.tight_layout()

    # reformating the x and y axis
    x_axis_list = np.arange(origin_x-120,origin_x+121,20)
    x_axis_list_str = []
    for x in x_axis_list:
        x_axis_list_str.append(str(int(x-origin_x)))
    plt.xticks(x_axis_list, x_axis_list_str)

    y_axis_list = np.arange(origin_y-140,origin_y+21,20)
    y_axis_list_str = []
    for y in y_axis_list:
        y_axis_list_str.append(str(int(y-origin_y)))
    plt.yticks(y_axis_list, y_axis_list_str) 

    ax.grid(True)    
    return fig, ax, origin_x, origin_y

def plot_measurements_in_background(measurement_dict,ax,origin_x=0,origin_y=0):
    # fig, ax = plt.subplots(figsize=(11, 7.166666))
    # ax.scatter(0, 0, color='black', marker='x',zorder=10)
    # ax.annotate("Radar position", (2, 2), (2, 2), textcoords="offset points", va="center", ha="center", size=15,zorder=10)
    # ax.set_xlim(-120, 120)
    # ax.set_ylim(-140, 20)
    # ax.set_aspect('equal')
    # ax.set_xlabel('East [m]', fontsize=15)
    # ax.set_ylabel('North [m]', fontsize=15)
    # plt.tick_params(axis='both', which='major', labelsize=15)
    # plt.tight_layout()
    for timestamp, measurements in measurement_dict.items():
        x = []
        y = []
        color = []
        for measurement in measurements:
            y.append(measurement[1] + origin_y)
            x.append(measurement[0] + origin_x)
            color.append(measurement[5])
        ax.scatter(x, y, c=color)
        # ax.set_title(f"Timestamp: {timestamp}")
    #     plt.pause(0.1)
    # plt.show()

def plot_for_vizualization(merged_measurements, measurement_dict, filename, work_dir):
    bar = progressbar.ProgressBar(maxval=len(measurement_dict)).start()

    merged_measurements = sorted(merged_measurements, key=lambda x: x.prev_timestamp)
    merged_measurements_timestamps = []
    merged_measurements_timestamps_current = []
    for merged_measurement in merged_measurements:
        merged_timestamp = merged_measurement.prev_timestamp
        if merged_timestamp not in merged_measurements_timestamps:
            merged_measurements_timestamps.append(merged_timestamp)
        merged_timestamp_current = merged_measurement.current_timestamp
        if merged_timestamp_current not in merged_measurements_timestamps_current:
            merged_measurements_timestamps_current.append(merged_timestamp_current)

    x = []
    y = []
    color = []
    
    merged_measurements_already_plotted = []
    merged_measurements_index = 0
    for k, (timestamp, measurements) in enumerate(measurement_dict.items()):
        merged_measurements_to_plot = []
        fig, ax, origin_x, origin_y = plot()
        ax.set_title(f"Timestamp: {timestamp}")

        if timestamp < merged_measurements_timestamps[merged_measurements_index]:
            for measurement in measurements:
                x.append(measurement[0] + origin_x)
                y.append(measurement[1] + origin_y)
                color.append(measurement[5])

        elif timestamp == merged_measurements_timestamps[merged_measurements_index]:
            for measurement in measurements:
                x.append(measurement[0] + origin_x) 
                y.append(measurement[1] + origin_y)
                color.append(measurement[5])
            for merged_measurement in merged_measurements:
                if merged_measurement.prev_timestamp == timestamp:
                    merged_measurements_to_plot.append(merged_measurement)

        elif timestamp == merged_measurements_timestamps_current[merged_measurements_index]:
            for measurement in measurements:
                x.append(measurement[0] + origin_x)
                y.append(measurement[1] + origin_y)
                color.append(measurement[5])
            if merged_measurements_index < len(merged_measurements_timestamps)-1:
                merged_measurements_index += 1

        else:
            for measurement in measurements:
                y.append(measurement[1] + origin_y)
                x.append(measurement[0] + origin_x)
                color.append(measurement[5])

        ax.scatter(x, y, c=color)
        for merged_measurement in merged_measurements_already_plotted:
            merged_measurement.plot_MM_update(ax, origin_x, origin_y)
        for merged_measurement in merged_measurements_to_plot:
            merged_measurement.plot_MM_init(ax, origin_x, origin_y)
            merged_measurements_already_plotted.append(merged_measurement)
        
        plt.savefig(f"{work_dir}/videos/temp/image_{k}.png")
        plt.close()
        bar.update(k)

    # Saving the video
    photos_file_path = f"{work_dir}/videos/temp"
    video_name = f'{work_dir}/videos/{filename[:-5]}.avi'
    images_to_video_opencv(photos_file_path, video_name, 1)
    print(f"\nSaving the video to {video_name}")
    # plt.close()
    empty_folder(photos_file_path)

def plot_for_vizualization_without_merged_measurements(measurement_dict, filename, work_dir):

    bar = progressbar.ProgressBar(maxval=len(measurement_dict)).start()

    x = []
    y = []
    color = []
    
    for k, (timestamp, measurements) in enumerate(measurement_dict.items()):
        fig, ax, origin_x, origin_y = plot()
        ax.set_title(f"Timestamp: {timestamp}")
        for measurement in measurements:
            y.append(measurement[1] + origin_y)
            x.append(measurement[0] + origin_x)
            color.append(measurement[5])
        ax.scatter(x, y, c=color)
        plt.savefig(f"{work_dir}/videos/temp/image_{k}.png")
        plt.close()
        bar.update(k)

    # Saving the video
    photos_file_path = f"{work_dir}/videos/temp"
    video_name = f'{work_dir}/videos/{filename[:-5]}.avi'
    images_to_video_opencv(photos_file_path, video_name, 1)
    print(f"\nSaving the video to {video_name}")
    # plt.close()
    empty_folder(photos_file_path)

def plot_for_report(measurement_dict, merged_measurements, save_dir, filename, work_dir):
    timestamps = list(measurement_dict.keys())
    k = 0
    for k, merged_measurement in enumerate(merged_measurements):
        
        measurement_dict_for_plotting = {}
        start_timestamp = merged_measurement.prev_timestamp
        timestamp_index = timestamps.index(start_timestamp)
        for i in range(timestamp_index-30,timestamp_index+10):
            try:
                timestamp = timestamps[i]
            except:
                continue
            if timestamp not in measurement_dict_for_plotting:
                measurement_dict_for_plotting[timestamp] = []
            for measurement in measurement_dict[timestamp]:
                measurement_dict_for_plotting[timestamp].append([measurement[0], measurement[1]])
            
        measurement_dict_for_plotting = dict(sorted(measurement_dict_for_plotting.items()))

        # Determine color scaling based on timestamps
        timestamps_list = list(measurement_dict_for_plotting.keys())
        color_scale = np.linspace(timestamps_list[0], timestamps_list[-1], len(timestamps_list))

        fig, ax, origin_x, origin_y = plot(work_dir)
        
        x = []
        y = []
        colors = []
        for timestamp, measurements in measurement_dict_for_plotting.items():
            for measurement in measurements:
                x.append(measurement[0]+origin_x)
                y.append(measurement[1]+origin_y)
                colors.append(color_scale[timestamps_list.index(timestamp)])
        sc = ax.scatter(x, y, c=colors, cmap='Greys')
        merged_measurement.plot_MM_init(ax, origin_x, origin_y)
        ax.legend(loc='upper left', fontsize=13)
        plt.savefig(f"{save_dir}/{filename[:-5]}_merged_measurement_number_{k+1}.png")
        plt.close()
    print(f"Saved {k+1} plots to {save_dir}")

    fig, ax, origin_x, origin_y = plot(work_dir)
    plot_measurements_in_background(measurement_dict, ax, origin_x, origin_y)
    for merged_measurement in merged_measurements:
        merged_measurement.plot_MM_init(ax, origin_x, origin_y)
    plt.savefig(f"{save_dir}/{filename[:-5]}_all_merged_measurements.png",dpi=400)
    plt.close()
    


