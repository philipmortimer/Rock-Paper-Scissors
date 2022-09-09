# Converts raw images to data ready to use in training process
import mediapipe as mp
import cv2
import os
import csv
from io import StringIO
import datetime

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


# Locates all files to be processed
def get_all_files(root):
    res = []
    for path, sub, files in os.walk(root):
        for name in files:
            res.append(os.path.join(path, name))
    return res


# Runs all files through model and stores results
def run_images_through_model(scissor_files, rock_files, paper_files):
    model_output = []
    # Stores number of images where no hands are detected
    # As with other data structs here, index 0 = rock, 1 = paper and 2 = scissors.
    no_hand_detected = [0, 0, 0]
    total_images = [0, 0, 0]  # Stores number of each type of image
    # Interpret as [[left_rock, right_rock], [left_paper, right_paper], [left_scissors, right_scissors]]
    left_or_rights = [[0, 0], [0, 0], [0, 0]]
    with mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
    ) as hands:
        for idx, file_list in enumerate([rock_files, paper_files, scissor_files]):
            for file in file_list:
                # Read an image, flip it around y-axis for correct handedness output if needed
                image = cv2.flip(cv2.imread(file), 1)
                # Convert the BGR image to RGB before processing.
                results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                # Checks to see whether a hand has been detected
                if not results.multi_hand_world_landmarks:
                    no_hand_detected[idx] += 1
                else:
                    total_images[idx] += 1
                    # Creates output vector
                    # Adds hand coords to output in form [x0,y0,z0,x1,y1,z1...]
                    out = [f(coords) for coords in results.multi_hand_world_landmarks[0].landmark
                           for f in (lambda l: l.x, lambda l: l.y, lambda l: l.z)]
                    out.append(idx)  # Indicates, rock, paper or scissors
                    left_or_rights[idx][results.multi_handedness[0].classification[0].index] += 1
                    model_output.append(out)
    return model_output, left_or_rights, total_images, no_hand_detected


# Writes model output to text file.
def write_data_to_file(model_output):
    output = StringIO(newline='')
    csv_writer = csv.writer(output)
    csv_writer.writerows(model_output)
    with open('Training Process\\Data Output\\Processed Data\\Processed Data.csv', 'w', newline='') as f_output:
        f_output.write(output.getvalue().rstrip())


# Writes details of data processing to log file
def write_log_file(model_output, left_or_rights, total_images, no_hand_detected):
    stars = "*" * 150
    total_left = left_or_rights[0][0] + left_or_rights[1][0] + left_or_rights[2][0]
    total_right = len(model_output) - total_left
    log_file_cont = map(lambda s: s + '\n',
                        ["Log generated at: " + datetime.datetime.now().strftime("%c"),
                         "This log is used to provide some information about the images processed.",
                         "Please note that the calculation of whether an image is right or left handed"
                         " is based on the assumption that the image is taken by a selfie cam and hence is flipped"
                         ". If this is NOT the case, the hand output can be flipped. Please note that handedness"
                         " is not used for training the AI, just there for curiosity",
                         stars,
                         "Rock",
                         "Left Hands: " + str(left_or_rights[0][0]),
                         "Right hands: " + str(left_or_rights[0][1]),
                         "Images where no hands were detected: " + str(no_hand_detected[0]),
                         "Total Rock: " + str(total_images[0]),
                         stars,
                         "Paper",
                         "Left Hands: " + str(left_or_rights[1][0]),
                         "Right hands: " + str(left_or_rights[1][1]),
                         "Images where no hands were detected: " + str(no_hand_detected[1]),
                         "Total Paper: " + str(total_images[1]),
                         stars,
                         "Scissors",
                         "Left Hands: " + str(left_or_rights[2][0]),
                         "Right hands: " + str(left_or_rights[2][1]),
                         "Images where no hands were detected: " + str(no_hand_detected[2]),
                         "Total Scissors: " + str(total_images[2]),
                         stars,
                         "Total",
                         "Left Hands: " + str(total_left),
                         "Right hands: " + str(total_right),
                         "Images where no hands were detected: " + str(sum(no_hand_detected)),
                         "Total images: " + str(len(model_output))
                         ])
    with open('Training Process\\Data Output\\Processed Data\\Log Processed Data.txt', 'w') as f:
        f.write(stars + '\n')
        f.writelines(log_file_cont)
        f.write(stars)


# Main function
def main():
    print("Processing Data. This may take some time.")
    model_output, left_or_rights, total_images, no_hand_detected = \
        run_images_through_model(get_all_files('Training Process\\Raw Images\\Scissors'),
                                 get_all_files('Training Process\\Raw Images\\Rock'),
                                 get_all_files('Training Process\\Raw Images\\Paper'))
    write_data_to_file(model_output)
    write_log_file(model_output, left_or_rights, total_images, no_hand_detected)
    print("Processed Data.")


if __name__ == "__main__":
    main()
