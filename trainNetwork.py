# Trains a neural network using combined dataset to categorise hand data as being
# either rock, paper or scissors.
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import datetime
import tensorflowjs as tfjs
import random

# Chooses seed for random num gen (either hard coded value or random one).
# If your model doesn't train very well, it may be a good idea to change the seed.
USE_PRE_SET_SEED = False
SEED = random.randint(0, 100000000)
if USE_PRE_SET_SEED:
    SEED = 66742697
tf.random.set_seed(SEED)

data_label_to_one_hot_encoded = {  # Converts data labels to one hot encoded scheme
    0: [1, 0, 0],
    1: [0, 1, 0],
    2: [0, 0, 1]
}


# Loads the data for the specified file into a features array and a label array
def get_data(file_name, remove_augmented_data, remove_non_augmented_data):
    data = np.genfromtxt(file_name, delimiter=',')
    if remove_augmented_data:
        data = np.array(list(filter(lambda x: x[64] == 0, data)))
    if remove_non_augmented_data:
        data = np.array(list(filter(lambda x: x[64] == 1, data)))
    # Generates data labels (using one-hot encoding scheme)
    labels_list = []
    for rec in data:
        labels_list.append(data_label_to_one_hot_encoded.get(rec[63]))
    labels = np.array(labels_list)
    # Generates feature array
    features_list = []
    for rec in data.tolist():
        # Converts flat csv list to 21 x 3 matrix
        matrix = [rec[0:-2][i:i + 3] for i in range(0, len(rec[0:-2]), 3)]
        features_list.append(matrix)
    features = np.array(features_list)
    return features, labels


# Creates ML model to be used
def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation='relu', input_shape=(21, 3, 1), padding='same'
                               ),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPool2D(pool_size=(2, 2), padding='same'),

        tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPool2D(pool_size=(2, 2), padding='valid'),

        tf.keras.layers.Flatten(),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(3, activation='softmax')
    ])
    model.compile(loss=tf.keras.losses.CategoricalCrossentropy(),
                  optimizer=tf.keras.optimizers.Adam(),
                  metrics=[tf.keras.metrics.CategoricalAccuracy()])
    return model


# Plots accuracy and loss over time and saves to file
def save_training_results_plot(history):
    # Plots accuracy
    plt.plot(history.history['categorical_accuracy'])
    plt.plot(history.history['val_categorical_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.savefig('Training Process\\Data Output\\Trained Model\\Log\\accuracy.png')
    plt.show()

    # Plots loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.savefig('Training Process\\Data Output\\Trained Model\\Log\\loss.png')
    plt.show()


# Logs the model data to a log file to summarise performance details
def log_model_data(model, history, epochs, batch_size):
    # Note this function is a bit messy (and large), but essentially it's performing a large number of similar
    # calculations (e.g. accuracy and loss for different datasets) and writing them to file
    save_training_results_plot(history)  # Saves plots to files

    # Loads datasets
    val_features_aug, val_labels_aug = get_data('Training Process\\Data Output\\Combined Data\\Validation Data.csv',
                                                False, True)
    val_features_non_aug, val_labels_non_aug = get_data('Training Process\\Data Output\\Combined Data\\Validation '
                                                        'Data.csv', True, False)
    test_features_aug, test_labels_aug = get_data('Training Process\\Data Output\\Combined Data\\Test Data.csv',
                                                  False, True)
    test_features_non_aug, test_labels_non_aug = get_data('Training Process\\Data Output\\Combined Data\\Test '
                                                          'Data.csv', True, False)
    val_features, val_labels = get_data('Training Process\\Data Output\\Combined Data\\Validation Data.csv', False,
                                        False)
    test_features, test_labels = get_data('Training Process\\Data Output\\Combined Data\\Test Data.csv', False,
                                          False)

    # Evaluates loss and accuracy for all datasets loaded
    test_loss_aug, test_acc_aug = model.evaluate(test_features_aug, test_labels_aug, verbose=0)
    test_loss_non_aug, test_acc_non_aug = model.evaluate(test_features_non_aug, test_labels_non_aug, verbose=0)
    val_loss_aug, val_acc_aug = model.evaluate(val_features_aug, val_labels_aug, verbose=0)
    val_loss_non_aug, val_acc_non_aug = model.evaluate(val_features_non_aug, val_labels_non_aug, verbose=0)
    test_loss, test_acc = model.evaluate(test_features, test_labels, verbose=0)
    val_loss, val_acc = model.evaluate(val_features, val_labels, verbose=0)

    # Performs some calculations for combined accuracy and loss of validation + testing
    tot = len(val_features) + len(test_features)
    comb_acc = ((test_acc * len(test_features)) + (val_acc * len(val_features))) / tot
    comb_loss = ((test_loss * len(test_features)) + (val_loss * len(val_features))) / tot
    comb_acc_aug = ((test_acc_aug * len(test_features_aug)) + (val_acc_aug * len(val_features_aug))) / \
                   (len(test_features_aug) + len(val_features_aug))
    comb_loss_aug = ((test_loss_aug * len(test_features_aug)) + (val_loss_aug * len(val_features_aug))) / \
                    (len(test_features_aug) + len(val_features_aug))
    comb_acc_non_aug = ((test_acc_non_aug * len(test_features_non_aug)) + (val_acc_non_aug * len(val_features_non_aug))
                        ) / (len(test_features_non_aug) + len(val_features_non_aug))
    comb_loss_non_aug = ((test_loss_non_aug * len(test_features_non_aug)) + (val_loss_non_aug *
                                                                             len(val_features_non_aug))) / \
                        (len(test_features_non_aug) + len(val_features_non_aug))

    # Saves model summary to String
    string_list = []
    model.summary(print_fn=lambda x: string_list.append(x))
    short_model_summary = "\n".join(string_list)

    # Log file contents
    stars = "*" * 150
    contents = ["Log generated at: " + datetime.datetime.now().strftime("%c"),
                "This log is used to provide some information about the trained model.",
                "Categorical cross entropy was used for the loss function and the ADAM optimiser was also used.",
                "Model trained for " + str(epochs) + " epochs, using a batch size of " + str(batch_size) + " .",
                "Model uses dataset from combined folder (view log file there for more details).",
                "Please view png images in this folder to see loss and accuracy throughout training.",
                "Seed used for training randomness (using tf.random.set_seed(SEED)) = " + str(SEED),
                stars,
                "Validation set",
                "Total validation images: " + str(len(val_features)),
                "Overall categorical accuracy validation set: " + '{:.1%}'.format(val_acc),
                "Overall loss validation set: " + '{0:.2f}'.format(val_loss),
                "-Categorical accuracy augmented validation set: " + '{:.1%}'.format(val_acc_aug),
                "-Loss (Categorical Cross Entropy) augmented validation set: " + '{0:.2f}'.format(val_loss_aug),
                "-Total number of images in augmented validation set: " + str(len(val_features_aug)),
                "~Categorical accuracy non-augmented validation set: " + '{:.1%}'.format(val_acc_non_aug),
                "~Loss (Categorical Cross Entropy) non-augmented validation set: " + '{0:.2f}'.format(val_loss_non_aug),
                "~Total number of images in non-augmented validation set: " + str(len(val_features_non_aug)),
                stars,
                "Test set",
                "Total test images: " + str(len(test_features)),
                "Overall categorical accuracy test set: " + '{:.1%}'.format(test_acc),
                "Overall loss test set: " + '{0:.2f}'.format(test_loss),
                "-Categorical accuracy augmented test set: " + '{:.1%}'.format(test_acc_aug),
                "-Loss (Categorical Cross Entropy) augmented test set: " + '{0:.2f}'.format(test_loss_aug),
                "-Total number of images in augmented test set: " + str(len(test_features_aug)),
                "~Categorical accuracy non-augmented test set: " + '{:.1%}'.format(test_acc_non_aug),
                "~Loss (Categorical Cross Entropy) non-augmented test set: " + '{0:.2f}'.format(test_loss_non_aug),
                "~Total number of images in non-augmented test set: " + str(len(test_features_non_aug)),
                stars,
                "Combined set (test set + validation set combined)",
                "Total combined images: " + str(tot),
                "Overall categorical accuracy combined set: " + '{:.1%}'.format(comb_acc),
                "Overall loss combined set: " + '{0:.2f}'.format(comb_loss),
                "-Categorical accuracy augmented combined set: " + '{:.1%}'.format(comb_acc_aug),
                "-Loss (Categorical Cross Entropy) augmented combined set: " + '{0:.2f}'.format(comb_loss_aug),
                "-Total number of images in augmented combined set: " + str(len(test_features_aug) +
                                                                            len(val_features_aug)),
                "~Categorical accuracy non-augmented combined set: " + '{:.1%}'.format(comb_acc_non_aug),
                "~Loss (Categorical Cross Entropy) non-augmented combined set: " + '{0:.2f}'.format(comb_loss_non_aug),
                "~Total number of images in non-augmented combined set: " + str(len(test_features_non_aug) +
                                                                                len(val_features_non_aug)),
                stars,
                "Model summary:",
                str(short_model_summary),
                stars
                ]
    log_file_cont = map(lambda s: s + '\n', contents)

    # Writes log to text file
    with open('Training Process\\Data Output\\Trained Model\\Log\\log.txt', 'w') as f:
        f.write(stars + '\n')
        f.writelines(log_file_cont)
        f.write(stars)


# Trains model
def train_model(model):
    batch_size = 32
    epochs = 281
    train_features, train_labels = get_data('Training Process\\Data Output\\Combined Data\\Training Data.csv', False,
                                            False)
    val_features, val_labels = get_data('Training Process\\Data Output\\Combined Data\\Validation Data.csv', False,
                                        False)
    history = model.fit(train_features, train_labels, validation_data=(val_features, val_labels), epochs=epochs,
                        batch_size=batch_size)
    # Saves model
    model.save('Training Process\\Data Output\\Trained Model\\Rock Paper Scissors Model')
    tfjs.converters.save_keras_model(model, 'Training Process\\Data Output\\Trained Model\\Rock Paper Scissors Model JS'
                                     )
    log_model_data(model, history, epochs, batch_size)  # Logs model info
    tfjs.converters.save_keras_model(model, 'Rock Paper Scissors Website\\Public\\Trained Model\\Rock Paper Scissors '
                                            'Model JS')


# Main function
def main():
    print("Training Network. This will take a long time.")
    print("Seed used for training + model creation ", SEED)
    model = create_model()
    train_model(model)
    print("Trained network.")


if __name__ == "__main__":
    main()
