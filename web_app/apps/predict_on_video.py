import base64
import os
import subprocess

import ffmpeg
from tensorflow.keras.models import load_model
import cv2
import numpy as np
import pandas as pd
from collections import deque
import moviepy.editor as moviepy
# from tensorflow.python.keras.models import

# Specify the height and width to which each video frame will be resized in our dataset.
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64

# Specify the number of frames of a video that will be fed to the model as one sequence.
SEQUENCE_LENGTH = 30

# Specify the directory containing the UCF50 dataset.
DATASET_DIR = "Dataset"

# Specify the list containing the names of the classes used for training. Feel free to choose any set of classes.
# CLASSES_LIST = ["walking", "fight", "running"]
# CLASSES_LIST = ["walking", "fight", "stealing", "running"]
CLASSES_LIST = ["handclapping", "jogging", "stealing", "lifting"]

# model = load_model('./Suspicious_Human_Activity_Detection_LRCN_Model_20240512_01.h5')
model = load_model('./Suspicious_Human_Activity_Detection_LRCN_Model_20240603.h5')
# model = load_model('./Suspicious_Human_Activity_Detection_LRCN_Model_20240520_stealing.h5')

def predict_on_video(video_file_path, SEQUENCE_LENGTH):
    output_file_path=replace_extension(video_file_path, new_extension='') + '_process.avi'
    '''
    This function will perform action recognition on a video using the LRCN model.
    Args:
    video_file_path:  The path of the video stored in the disk on which the action recognition is to be performed.
    output_file_path: The path where the ouput video with the predicted action being performed overlayed will be stored.
    SEQUENCE_LENGTH:  The fixed number of frames of a video that can be passed to the model as one sequence.
    '''

    # Initialize the VideoCapture object to read from the video file.
    video_reader = cv2.VideoCapture(video_file_path)

    # Get the width and height of the video.
    original_video_width = int(video_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_video_height = int(video_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print('original_video_width:' + str(original_video_width))
    print('original_video_height:' + str(original_video_height))

    # Initialize the VideoWriter Object to store the output video in the disk.
    video_writer = cv2.VideoWriter(output_file_path, cv2.VideoWriter_fourcc(*'MJPG'),
                                   video_reader.get(cv2.CAP_PROP_FPS), (original_video_width, original_video_height))
    # video_writer = cv2.VideoWriter(output_file_path, cv2.VideoWriter_fourcc(*'mp4v'),
    #                                video_reader.get(cv2.CAP_PROP_FPS), (original_video_width, original_video_height))

    # Get total number of frames in the video
    total_frames = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))

    # Get frames per second (FPS) of the video
    fps = video_reader.get(cv2.CAP_PROP_FPS)

    # Calculate total duration of the video in seconds
    total_seconds = total_frames / fps

    # Declare a queue to store video frames.
    frames_queue = deque(maxlen=SEQUENCE_LENGTH)

    # Initialize a variable to store the predicted action being performed in the video.
    predicted_class_name = ''
    result = []
    detects = []
    # Iterate until the video is accessed successfully.
    while video_reader.isOpened():

        # Read the frame.
        ok, frame = video_reader.read()

        # Check if frame is not read properly then break the loop.
        if not ok:
            print('Not ok')
            break

        # Resize the Frame to fixed Dimensions.
        resized_frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))

        # Normalize the resized frame by dividing it with 255 so that each pixel value then lies between 0 and 1.
        normalized_frame = resized_frame / 255

        # Appending the pre-processed frame into the frames list.
        frames_queue.append(normalized_frame)

        # Check if the number of frames in the queue are equal to the fixed sequence length.
        if len(frames_queue) == SEQUENCE_LENGTH:
            # Pass the normalized frames to the model and get the predicted probabilities.
            predicted_labels_probabilities = model.predict(np.expand_dims(frames_queue, axis=0))[0]

            # Get the index of class with highest probability.
            predicted_label = np.argmax(predicted_labels_probabilities)

            # Get the class name using the retrieved index.
            predicted_class_name = CLASSES_LIST[predicted_label]

            result.append(predicted_class_name)
            if predicted_class_name:
                # Calculate time associated with the current frame
                frame_number = int(video_reader.get(cv2.CAP_PROP_POS_FRAMES))
                fps = video_reader.get(cv2.CAP_PROP_FPS)
                frame_time = frame_number / fps
                minutes = int(frame_time // 60)
                seconds = int(frame_time % 60)
                print(f"{minutes:02d}:{seconds:02d}")

                # Write predicted class name on top of the frame.
                cv2.putText(frame, predicted_class_name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode()

                timePredict = (minutes, seconds, predicted_class_name, frame_base64)
                detects.append(timePredict)
        # Write The frame into the disk using the VideoWriter Object.
        video_writer.write(frame)

    # Release the VideoCapture and VideoWriter objects.
    video_reader.release()
    video_writer.release()

    print('Print video done')
    # output_path = output_file_path.replace('.avi', '.mp4');
    ouput_path = replace_extension(video_file_path, '.mp4')
    convert_avi_to_mp4(output_file_path, ouput_path)
    print('Output success: ' + ouput_path)
    result_labels = []
    # [result_labels.append(x) for x in result if x not in result_labels]

    dect_times = []
    check_times = []

    for item in detects:
        time = f"{item[0]:02d}:{item[1]:02d}"
        if time not in check_times:
            dect_times.append(item)
            check_times.append(time)
            if item[2] not in result_labels:
                result_labels.append(item[2])

    # Clean up process video
    os.remove(output_file_path)

    return (ouput_path, result_labels, dect_times, total_seconds)


def convert_avi_to_mp4(avi_file_path, output_name):
    avi_file_path = avi_file_path.replace('/', '\\')
    output_name = output_name.replace('/', '\\')
    # This command could have multiple commands separated by a new line \n
    # command = "ffmpeg -y -i {input} -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 {output}".format(input = avi_file_path, output = output_name)
    #
    # p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    #
    # (output, err) = p.communicate()
    #
    # print('output: ', output)
    # print('err: ', err)
    #
    # # This makes the wait possible
    # p_status = p.wait()
    # print('p_status: ' + str(p_status))
    #
    # # This will give you the output of the command being executed
    # return True

    try:
        (
            ffmpeg
            .input(avi_file_path)
            .output(output_name, vcodec='libx264', crf=23, preset='medium', acodec='aac', audio_bitrate='192k')
            .overwrite_output()
            .run()
        )
        print(f"Conversion successful: {output_name}")
    except ffmpeg.Error as e:
        print(f"Error during conversion: {e}")
        print(e.stderr.decode())


def replace_extension(file_path, new_extension = ''):
    # Split the file path into its directory path and filename
    directory, filename_with_extension = os.path.split(file_path)

    # Split the filename and its extension
    filename, _ = os.path.splitext(filename_with_extension)

    # Concatenate the new extension with the filename
    new_filename_with_extension = filename + new_extension

    # Construct the new file path
    new_file_path = os.path.join(directory, new_filename_with_extension)

    return new_file_path