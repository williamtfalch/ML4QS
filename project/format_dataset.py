import datetime
import os


def _dataset2readings(path):
    original_lines = []
    formatted_lines = []
    timestamps = []
    num_lines_per_datapoint = 4

    with open(path) as f:
        original_lines = f.readlines()

    # iterate over every data instance, need to replace \ufeff for some reason..
    for i in range(len(original_lines)//num_lines_per_datapoint):
        timestamp = original_lines[i *
                                   num_lines_per_datapoint].replace("\ufeff", "")

        timestamp = datetime.datetime(
            int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]), int(timestamp[10:
                                                                                        12]), int(timestamp[12:14]), int(timestamp[14:16])
        ).strftime('%s') + timestamp[17:20]

        acceleration = list(
            map(lambda v: float(v),
                original_lines[i * num_lines_per_datapoint + 2][6:].split("  ")))
        gyroscope = list(
            map(lambda v: float(v),
                original_lines[i * num_lines_per_datapoint + 3][6:].split("  ")))

        timestamps.append(int(timestamp))
        formatted_lines.append(acceleration + gyroscope)

    return timestamps, formatted_lines


def _average_readings(timestamps, values, granularity):
    first_timestamp = timestamps[0]
    num_readings = len(timestamps)

    chunks = [[]]
    num_chunks = 1

    summed_chunks = []
    averaged_chunks = []

    for i in range(num_readings):
        if timestamps[i] > (first_timestamp + ((num_chunks) * granularity)):
            num_chunks += 1
            chunks.append([])

        chunks[num_chunks-1].append(values[i])

    for chunk in chunks:
        summed_chunks.append([sum(i) for i in zip(*chunk)])

    for i in range(num_chunks):
        formatted_timestamp = datetime.datetime.fromtimestamp((
            first_timestamp + i * granularity)/1000).strftime('%Y-%m-%d %H:%M:%S.%f')

        averaged_chunks.append([formatted_timestamp] +
                               [x / len(chunks[i]) for x in summed_chunks[i]])

    return averaged_chunks


def _averaged_readings2csv(path, averaged_readings):
    with open(path, "w") as f:
        f.write("timestamp,acc_x,acc_y,acc_z,gyr_x,gyr_y,gyr_z\n")

        for line in averaged_readings:
            f.write(','.join(list(map(lambda v: str(v), line))) + "\n")


def format_file(input_path, output_path, granularity=250):
    timestamps, values = _dataset2readings(input_path)
    averaged_readings = _average_readings(timestamps, values, granularity)
    _averaged_readings2csv(output_path, averaged_readings)


def format_folder(root_folder="./raw_data", granularity=250):
    # make output directory
    output_dir = './output_files'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    gesture_folders = next(os.walk(root_folder))[1]

    for gf in gesture_folders:
        # make output sub folder
        if not os.path.exists("{}/{}".format(output_dir, gf)):
            os.makedirs("{}/{}".format(output_dir, gf))

        files = [x[2] for x in os.walk("{}/{}".format(root_folder, gf))]

        txt_files = list(filter(lambda f: f[-3:] == "txt", files[0]))

        for tf in txt_files:
            input_path = "{}/{}/{}".format(root_folder, gf, tf)
            output_path = "{}/{}/{}".format(output_dir, gf, tf[:-3] + "csv")

            format_file(input_path, output_path)


format_folder()
