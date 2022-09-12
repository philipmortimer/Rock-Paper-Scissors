// Class used for human players (with camera input)
import './Player.css';
import React from 'react';
import { Hands, HAND_CONNECTIONS } from "@mediapipe/hands";
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";

import { zeros, tensor1d } from '@tensorflow/tfjs';
import '@tensorflow/tfjs-backend-webgl';
import '@tensorflow/tfjs-backend-cpu';

const SEND_IMAGE_TIMES = 10; //Number of times final result is sent to Hands model

class HumanPlayer extends React.Component {

    constructor(props) {
        super(props);
        this.state = {moveSelected: 3, gamePaused: false,
                    move: 3, handsLoaded: false,
                    hands: null,
                    imagesLoaded: false};
        this.images = [null, null, null];
        this.loadImages = this.loadImages.bind(this);
        this.renderCanvas = this.renderCanvas.bind(this);
        this.makeMove = this.makeMove.bind(this);
        this.videoFrameReceieved = this.videoFrameReceieved.bind(this);
        this.initHands.bind(this);
        this.drawHandLines = this.props.handTracking;

        // Variables used when producing model output
        this.finalResult = null; // Stores the hands model output
        this.noSends = 0; // Stores number of times final image has been passed through model
        this.inputImage = null; // Stores input image for model
    }

    // Closes hands model
    cleanUpBeforeClose() {
        if(this.state.handsLoaded) this.state.hands.close();
    }

    // Sets the line drawing variable
    enableLineDrawing(drawLines) { this.drawHandLines = drawLines; }

    //Creates hands object and configures it as required
    async initHands() {
        if (this.state.handsLoaded) return; // No need to reload model
        const hands = new Hands({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
        },
        });
        //Static image mode is not a supported feature in JS
        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5,
        });
        hands.onResults(this.renderCanvas);
        await hands.initialize();
        this.setState({hands: hands, handsLoaded: true});
    }

    componentDidMount() {
        this.loadImages();
    }

    // Occurs when play button is presssed
    gameStarted() { 
        this.setState({gamePaused: false});
    }

    // Takes image / video of player to produce guess
    makeMove() {
        while(!this.state.handsLoaded) {
            console.log("Waiting for hands model to load before making move");
        }
        this.setState({gamePaused: true, move: 3}, () => {
            this.finalResult = null;
            this.noSends = 0;
    
            // Gets image from output canvas and passes it through model
            //Gets out canvas
            const canvasElement = document.getElementById("outputCanvasHuman" + this.props.isLeftPlayer);
            const img = new Image();
            img.onload = () => {
                this.inputImage = img;
                this.state.hands.send(img);
            };
            img.src = canvasElement.toDataURL();
        });
    }

    // Loads images
    loadImages() {
        const loadedImage = (img, i) => {                
            this.images[i] = img;
            this.setState({imagesLoaded: this.images[0] !== null && this.images[1] !== null &&
                this.images[2] !== null});
        };
        const imageFiles = ["/Images/rock_emoji.png", "/Images/paper_emoji.png", "/Images/scissors_emoji.png"];
        for (let i = 0; i < this.images.length; i++){
            const img = new Image();     
            img.onload = () => { loadedImage(img, i); };
            img.src = imageFiles[i];
        }
    }

    // Sends image to hands model
    videoFrameReceieved(frame) {
        // Sends image for proccessing if hands model has been loaded
        if(this.state.handsLoaded) this.state.hands.send({image: frame})
    }

    // Sends Hands model data to tensorflow model to produce output
    sendCoordsToTfModel(multiHandWorldLandmarks) {
        let points = [];
        let inp = zeros([1, 21, 3, 1]);;
        if(multiHandWorldLandmarks.length !== 0) {
            for (const coords of multiHandWorldLandmarks[0]){
                points.push(coords.x, coords.y, coords.z);
            }
            inp = tensor1d(points).reshape([1, 21, 3, 1]);
        }
        const result = this.props.tfModel.predict(inp).dataSync();
        const resultArray = [result[0], result[1], result[2]];
        const move = resultArray.indexOf(Math.max(...resultArray)); //Returns index of move
        this.setState({move: move}, () => {
            this.props.onResult(move, this.props.isLeftPlayer, resultArray);
        });
        return move;
    }


    renderCanvas(results) {
        //Draws webcam to canvas
        //Gets out canvas
        const canvasElement = document.getElementById("outputCanvasHuman" + this.props.isLeftPlayer); 
        const canvasCtx = canvasElement.getContext("2d");
        if (!this.state.gamePaused) { // If the game is paused, no additional rendering needed  
            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(
                results.image, 0, 0, canvasElement.width, canvasElement.height);
            // Draws detected hand if required
            if (this.drawHandLines){
                if (results.multiHandLandmarks) {
                    for (const landmarks of results.multiHandLandmarks) {
                      drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS,
                                     {color: '#00FF00', lineWidth: 5});
                      drawLandmarks(canvasCtx, landmarks, {color: '#FF0000', lineWidth: 2});
                    }
                }
            }
            canvasCtx.restore();
        }else { // If game is paused, check to see if result is needed
            if (this.noSends < SEND_IMAGE_TIMES){
                this.finalResult = results;
                this.state.hands.send(this.inputImage);
                this.noSends++;

                //Checks to see if that was last call for processing
                if( this.noSends === SEND_IMAGE_TIMES) {
                    const move = this.sendCoordsToTfModel(results.multiHandWorldLandmarks);
                    // Draws image of choosen move over screen
                    canvasCtx.save();
                    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
                    canvasCtx.drawImage(
                        this.finalResult.image, 0, 0, canvasElement.width, canvasElement.height);
                    // Draws detected hand if required
                    if (this.drawHandLines){
                        if (this.finalResult.multiHandLandmarks) {
                            for (const landmarks of this.finalResult.multiHandLandmarks) {
                            drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS,
                                            {color: '#00FF00', lineWidth: 5});
                            drawLandmarks(canvasCtx, landmarks, {color: '#FF0000', lineWidth: 2});
                            }
                        }
                    }
                    if (this.state.imagesLoaded){
                        canvasCtx.drawImage(this.images[move], 0, 0, canvasElement.width, canvasElement.height);                        
                    }
                    canvasCtx.restore();
                }
            }
        }
    }
  
    render() {
        return (
            <div className={this.props.isLeftPlayer? "leftPlayer" : "rightPlayer"}>
                <span>{this.state.handsLoaded? "🧠 Person" : "Loading..."}</span>
                <canvas id={"outputCanvasHuman" + this.props.isLeftPlayer} width="300" height="300">
                </canvas>
            </div>
            );

    }
  }
  export default HumanPlayer;