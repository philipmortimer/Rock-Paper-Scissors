Place images inside of Raw Images folder (with rock, paper and scissors images in relevant folders). jpg and png image formats are supported. Other formats are likely supported too, but haven't been tested by me.
Script will run data through the mediapipe hands model to produce a csv file (stored in "Data Output/Processed Data/Processed Data.csv").
The first 63 values represent the x,y and z coordinates of the detected hand at 21 points.
They are in the order x_point0, y_point0, z_point0, x_point1, y_point1, z_point1 ... z_point20.
For more details on what each point means, please view "Data Explanation/Hand.html" [taken from "https://google.github.io/mediapipe/solutions/hands.html", bearing in mind that the data in the csv file is
multi_hands_world_landmarks.
The final value of each row in the csv file is the label. 0 = rock, 1 = paper and 2 =scissors.
Consult "Data Output/Processed Data/Log Processed Data.txt" for a breakdown on processed data.
Data augmentation occurs on processed data to enhance size and diversity of dataset. Please view this in "Data Output/Augmented Processed Data". The data in the csv file follows the same format as the processed data.
"Data Output/Combined Data" contains the data actually used to train / evaluate the neural network. Please read the log file for details of data. In short, data is stored in following way:
Each record has 65 fields. The first 63 fields store the multi_hand_world_landmark coordinates. I.e. the 21 x, y and z coordinates of various points on the hand.
These fields are stored in the form x0, y0, z0, x1, y1, z1, ... z20
The next field represents the data label (0 = rock, 1 = paper, 2 = scissors)
The final element represents whether the data is augmented or not (0 = not augmented and 1 = augmented). This last item is obviously not used for training but is helpful for network performance analysis.
The trained model can be found in "Data Output/Trained Model/Rock Paper Scissors Model". The corresponding log and additional info can be found in "Data Output/Trained Model/Log". This model takes in a 21 x 3 input matrix with the first column being all x coords in order x0 to x20. Second col is y coords and third col is z coords. The model produces three outputs. If the largest output is the 0th output, then the network is predicting rock. 1st output = paper and 2nd output = scissors. (I.e. a targeted one-hot encoded output).


