# Combines augmented and processed data to produce a file of training data, test data and validation data.
# Roughly 80% of data will be training, 10% testing and 10% validation
# Each record will have 65 fields.
# The 63 fields will store the multi_hand_world_landmarks coordinates in the form
# x0, y0, z0, x1, y1, z1, ... z20
# The next element will be the label (0 = rock, 1 = paper, 2 = scissors)
# The final element will represent whether the data is augmented or not (0 = not augmented, 1 = augmented)
import csv
from io import StringIO
import datetime
import math
import random

SEED = 1056
random.seed(SEED)
stars = "*" * 150


# Combines augmented data and processed data into one list. Also adds marker to indicate which
# records are augmented / not augmented.
def combine_data():
    data = list(csv.reader(open('Training Process\\Data Output\\Processed Data\\Processed Data.csv')))
    augmented_data = list(csv.reader(open('Training Process\\Data Output\\Augmented Processed Data\\Augmented '
                                          'Processed Data.csv')))
    combined_data = []
    for idx, vals in enumerate([data, augmented_data]):
        for rec in vals:
            val = rec
            val.append(str(idx))
            combined_data.append(val)
    random.shuffle(combined_data)  # Randomly shuffles list
    return combined_data


# Splits data into three arrays (training, test and validation)
#  Roughly 80%-10%-10% split (80% for training data)
def split_data(data):
    no_train = math.floor(0.8 * len(data))
    no_test = math.floor(0.5 * (len(data) - no_train))
    no_val = len(data) - no_test - no_train
    training = data[0:no_train]
    test = data[no_train:no_train + no_test]
    validation = data[no_train + no_test: no_train + no_test + no_val]
    return training, test, validation


# Writes data to specified file
def write_data_to_file(data, file_name):
    output = StringIO(newline='')
    csv_writer = csv.writer(output)
    csv_writer.writerows(data)
    with open(file_name, 'w', newline='') as f_output:
        f_output.write(output.getvalue().rstrip())


# Writes details of combined data to log file
def write_log_file(training, test, validation):
    contents = ["Log generated at: " + datetime.datetime.now().strftime("%c"),
                "This log is used to provide some information about the combined data.",
                "These three data files combine both processed data and augmented variants of the processed "
                "data.",
                "Augmentation was achieved in number of ways (e.g. rotation, stretching etc.).",
                "Each record has 65 fields. The first 63 fields store the multi_hand_world_landmark "
                "coordinates. I.e. the 21 x, y and z coordinates of various points on the hand.",
                "These fields are stored in the form x0, y0, z0, x1, y1, z1, ... z20",
                "The next field represents the data label (0 = rock, 1 = paper, 2 = scissors)",
                "The final element represents whether the data is augmented or not (0 = not augmented"
                " and 1 = augmented).",
                stars]
    contents += data_break_down(training, "Training")
    contents += data_break_down(test, "Test")
    contents += data_break_down(validation, "Validation")
    log_file_cont = map(lambda s: s + '\n', contents)
    with open('Training Process\\Data Output\\Combined Data\\Combined Data Log.txt', 'w') as f:
        f.write(stars + '\n')
        f.writelines(log_file_cont)
        f.write(stars)


# Analyses data and returns a list of Strings containing the details
def data_break_down(data, name):
    return [
        name,
        "Total images: " + str(len(data)),
        "Total augmented images: " + str(len(list(filter(lambda x: x[64] == '1', data)))),
        "Total non-augmented images: " + str(len(list(filter(lambda x: x[64] == '0', data)))),
        "-- Rock images validation (augmented): " + str(len(list(filter(lambda x: x[63] == '0' and x[64] == '1', data)))
                                                        ),
        "-- Paper images validation (augmented): " + str(len(list(filter(lambda x: x[63] == '1' and x[64] == '1', data))
                                                             )),
        "-- Scissors images validation (augmented): " + str(len(list(filter(lambda x: x[63] == '2' and x[64] == '1',
                                                                            data)))),
        "~~ Rock images validation (not augmented): " + str(len(list(filter(lambda x: x[63] == '0' and x[64] == '0',
                                                                            data)))),
        "~~ Paper images validation (not augmented): " + str(len(list(filter(lambda x: x[63] == '1' and x[64] == '0',
                                                                             data)))),
        "~~ Scissors images validation (not augmented): " + str(len(list(filter(lambda x: x[63] == '2' and x[64] == '0',
                                                                                data)))),
        stars
    ]


# Main function
def main():
    print("Combining Data.")
    combined_data = combine_data()
    training_data, test_data, validation_data = split_data(combined_data)
    write_data_to_file(training_data, 'Training Process\\Data Output\\Combined Data\\Training Data.csv')
    write_data_to_file(test_data, 'Training Process\\Data Output\\Combined Data\\Test Data.csv')
    write_data_to_file(validation_data, 'Training Process\\Data Output\\Combined Data\\Validation Data.csv')
    write_log_file(training_data, test_data, validation_data)
    print("Combined data.")


if __name__ == "__main__":
    main()
