# Rock-Paper-Scissors
This project trains a neural network to classify images of people playing rock paper scissors. This was done using a dataset of around 10,000 images. These images
are run through the Medaipipe Hands AI model that converts an image of a hand to cartesian coordinates of the hand's location. This data was augmented to increase the
size and diversity of the dataset. Using a CNN, I achieved ~98.3% classification accuracy.
Please consult "main.py" and the other 4 python files to understand the training process. If you wish to train your own model, simply place all images you wish to
train the model with in "Training Process/Raw Images". Then run "main.py" after you have installed the required dependencies.
Using this trained model, I created a react website that allows users to use their webcam as an input to play rock paper scissors. The website code can be found in the
"Rock Paper Scissors Website" folder. Simply change to this directory and run "npm start" (after having run "npm install" to install dependencies). This will
run the website.
I have made use of GitHub pages to host my website. So please visit "https://philipmortimer.github.io/" to see the website in action. However, please note that as
GitHub only allows one website to be hosted per account, there is a high possibilty that I will repurpose this link for something else in the future (hence, I can't
promise that this link will definitely work!).
Here are some screenshots of the website in action:

![p vs ai](https://user-images.githubusercontent.com/64362945/189451693-9693f5bf-395c-4bdd-b16f-f4ff3c866e75.png)

--------------------------------------------------------------------------------------------------------------------

![p vs ai](https://user-images.githubusercontent.com/64362945/189451715-ea00ee59-027a-4c79-b26e-2d8c652ef3ed.png)
