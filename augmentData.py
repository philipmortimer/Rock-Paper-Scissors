# Takes processed data and augments it to increase size of dataset
# It also adds more variety to dataset, hopefully leading to a better ML model
# Only the augmented results are actually saved to file (the non-augmented data is already
# stored in a different file)
import random
import csv
from typing import NamedTuple
import mediapipe as mp
from scipy.spatial.transform import Rotation as R
from numpy.random import RandomState
import datetime
from io import StringIO

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
SEED = 923  # All random num generations use a seed to ensure reproducibility
random.seed(SEED)  # Sets seed of random generator
rand_state = RandomState(SEED)


# Loads processed data into an array of floats
# Each list item [record] has two elements. Element 0
# is a 21 x 3 matrix of all points and element 1 is the output label
def get_data():
    temp_data_str = list(csv.reader(open('Training Process\\Data Output\\Processed '
                                         'Data\\Processed Data.csv')))
    temp_data_float = [list(map(float, i)) for i in temp_data_str]
    data = []
    for rec in temp_data_float:
        matrix = [rec[0:-1][i:i + 3] for i in range(0, len(rec[0:-1]), 3)]
        data.append([matrix, int(rec[-1])])
    return data


# Plots hand given the relevant 21 x 3 matrix. This is useful for debugging.
# This code is very hacky and as such, should only be used for debugging.
def plot_hand(mat):
    class Point:
        def __init__(self, x, y, z):
            self.x = x
            self.y = y
            self.z = z
            self.visibility = 1.0
            self.presence = 1.0

        def HasField(self, field):
            return True

    landmark = NamedTuple('Land', landmark=list)
    points = []
    for coords in mat:
        points.append(Point(coords[0], coords[1], coords[2]))
    landmark_list = landmark(points)
    mp_drawing.plot_landmarks(landmark_list, mp_hands.HAND_CONNECTIONS, azimuth=5)


# Translates hands some random distance in the x,y and z directions
# Takes a 21 x 3 matrix and a random number generator as input.
# Returns translated matrix
def translate_hand(matrix):
    new_mat = copy_matrix(matrix)
    for i in range(3):
        add_constant_to_coords(new_mat, random.normalvariate(0, 1), i)
    return new_mat


# Multiplies all x,y and z coordinates by different constants greater than 0
def change_size(matrix):
    new_mat = copy_matrix(matrix)
    for i in range(3):
        mult_coords_by_scalar(new_mat, pos_normal_num(1, 0.25), i)
    return new_mat


# Stretches / shrinks hand using same constant of multiplication for x,y and z coords.
def change_size_equal(matrix):
    new_mat = copy_matrix(matrix)
    scale = pos_normal_num(1, 1)
    for i in range(3):
        mult_coords_by_scalar(new_mat, scale, i)
    return new_mat


# Returns a normal number. Keeps generating numbers, until one > 0 is found
def pos_normal_num(mean, sigma):
    x = random.normalvariate(mean, sigma)
    if x <= 0:
        x = pos_normal_num(mean, sigma)
    return x


# Returns a copy of inputted matrix
def copy_matrix(matrix):
    return [[i for i in row] for row in matrix]


# Multiplies all values in specific column of 2d list by specified scalar
def mult_coords_by_scalar(grid, scalar, col_index):
    for row in grid:
        row[col_index] *= scalar


# Adds a constant to all columns in the grid
def add_constant_to_coords(grid, constant, col_index):
    for row in grid:
        row[col_index] += constant


# Rotates the 21 x 3 matrix
def rotate_hand(matrix):
    return R.random(random_state=rand_state).apply(matrix).tolist()


# Reflects x coords around y-axis.
# This has the effect of swapping right hand to left hand and vice versa
def flip_hand(matrix):
    new_mat = copy_matrix(matrix)
    mult_coords_by_scalar(new_mat, -1, 0)
    return new_mat


# Augments a single hand using a probabilistic approach
def augment_hand(hand_matrix):
    new_mat = copy_matrix(hand_matrix)
    # Applies various transformations. Note frequency weighting derived based on likely harm
    # each augmentation could cause. This is an estimation and could be suboptimal
    if random.random() <= 0.8:
        new_mat = rotate_hand(new_mat)
    if random.random() <= 0.7:
        new_mat = change_size_equal(new_mat)
    if random.random() <= 0.7:
        new_mat = translate_hand(new_mat)
    if random.random() <= 0.4:
        new_mat = change_size(new_mat)
    return new_mat


# Augments data provided into a new data list
def augment_data(data):
    augmented_data_temp = []
    # Stores number of rock, paper and scissors. Index 0 = rock, 1 = scissors and 2 = paper.
    total_type_image = [0, 0, 0]
    for record in data:
        # 6 augmented items per real item [3 flipped, 3 normal]
        augmented_data_temp.append([augment_hand(record[0]), record[1]])
        augmented_data_temp.append([augment_hand(flip_hand(record[0])), record[1]])
        augmented_data_temp.append([augment_hand(record[0]), record[1]])
        augmented_data_temp.append([augment_hand(flip_hand(record[0])), record[1]])
        augmented_data_temp.append([augment_hand(record[0]), record[1]])
        augmented_data_temp.append([augment_hand(flip_hand(record[0])), record[1]])
    augmented_data = []
    for aug in augmented_data_temp:  # Flattens data
        total_type_image[aug[1]] += 1
        field = flatten_matrix(aug[0])
        field.append(aug[1])
        augmented_data.append(field)
    return augmented_data, total_type_image


# Writes details of data augmentation to log file
def write_log_file(augmented_data, data, total_image_type):
    stars = "*" * 150
    log_file_cont = map(lambda s: s + '\n',
                        ["Log generated at: " + datetime.datetime.now().strftime("%c"),
                         "This log is used to provide some information about the images augmented.",
                         "Note that no processed images are deleted in data augmentation step.",
                         "The file containing augmented images ONLY contains augmented data",
                         stars,
                         "Total processed images used to produce augmented data: " + str(len(data)),
                         "Total augmented images produced: " + str(len(augmented_data)),
                         "Total number of rock in augmented set: " + str(total_image_type[0]),
                         "Total number of paper in augmented set: " + str(total_image_type[1]),
                         "Total number of scissors in augmented set: " + str(total_image_type[2]),
                         stars
                         ])
    with open('Training Process\\Data Output\\Augmented Processed Data\\Log Augmented Data.txt', 'w') as f:
        f.write(stars + '\n')
        f.writelines(log_file_cont)
        f.write(stars)


# Writes augmented data to text file.
def write_data_to_file(augmented_data):
    output = StringIO(newline='')
    csv_writer = csv.writer(output)
    csv_writer.writerows(augmented_data)
    with open('Training Process\\Data Output\\Augmented Processed Data\\Augmented Processed Data.csv', 'w',
              newline='') as f_output:
        f_output.write(output.getvalue().rstrip())


# Flattens a 2d matrix into a 1d matrix
def flatten_matrix(matrix):
    return [j for sub in matrix for j in sub]


# Main function
def main():
    print("Augmenting Data.")
    data = get_data()
    augmented_data, total_image_type = augment_data(data)
    write_data_to_file(augmented_data)
    write_log_file(augmented_data, data, total_image_type)
    print("Augmented data.")


if __name__ == "__main__":
    main()
