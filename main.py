# This file combines all steps needed to create AI model for rock paper scissors.
# First, upload all images for dataset into "Training Process/Raw Images". Place rock images in rock image
# folder (or any sub-folder within this folder). Do the same for paper and scissors. Some images are already
# in each folder. Images should be of a single hand and common image formats like "png" and "jpg" are supported.
# Run this python script to create and train model (importing relevant libraries first).
# To see which libraries to import, view "augmentData.py", "combineData.py" and "trainNetwork.py" import statements.
# This code goes through all hand images and runs a pre-trained AI model that extracts the real world 3d coords
# of 21 locations of an image of a hand. These datapoints are stored in a csv file. This occurs when you run
# "processData.py". Next, this data is augmented using a number of transformations (e.g. enlarging hand) to
# increase size and diversity of dataset. These are then stored in a separate csv file. This occurs in
# "augmentData.py". "combineData.py" combines augmented data and 'normal' data into a training, test and
# validation set. "trainNetwork.py" trains a neural network using this data and saves the model.
# This script simply runs the 4 python files in order:
# processData.py -> augmentData.py -> combineData.py -> trainNetwork.py
# The execution of this script will take a long time (as training a network is very expensive)
# Will probably take several hours to execute whole script.
# Trained model can be found in "Training Process/Data Output/Trained Model/Rock Paper Scissors Model"
import processData
import augmentData
import combineData
import trainNetwork


# Main function
def main():
    print("Beginning main script. This may take several hours.")
    processData.main()
    augmentData.main()
    combineData.main()
    trainNetwork.main()
    print("Script completed.")


if __name__ == "__main__":
    main()
