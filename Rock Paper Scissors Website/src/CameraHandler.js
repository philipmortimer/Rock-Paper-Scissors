// Handles the camera input. Starts a camera that coordinates sending image data to players
import { Camera } from "@mediapipe/camera_utils";
import React from 'react';

import '@tensorflow/tfjs-backend-webgl';
import '@tensorflow/tfjs-backend-cpu';

class CameraHandler extends React.Component {

    constructor(props) {
        super(props);
        this.noHumanPlayers = 1;
        this.isLeftPlayerHuman = true;
        this.handleFrame = this.handleFrame.bind(this);
        this.setPlayerTypeInfo = this.setPlayerTypeInfo.bind(this);
        this.handleFrame = this.handleFrame.bind(this);
        this.initCamera = this.initCamera.bind(this);
        this.loadedVideo = false;
    }

    componentDidMount() {
        this.initCamera();
    }

    // Sets info about which players are human
    setPlayerTypeInfo(noPlayers, isLeftHuman) {
        this.noHumanPlayers = noPlayers;
        this.isLeftPlayerHuman = isLeftHuman;
    }

    // Handles an inputted video frame
    async handleFrame(frame) {
        // If no human players, no processing required
        if (this.noHumanPlayers === 0 ) return;
        if(frame.videoHeight === 0 || frame.videoWidth === 0) {
            console.log("Video provided has zero dimensions");
            return;
        }
        // Converts video to an image of current frame
        const canvas = document.createElement('canvas');
        canvas.width = frame.videoWidth;
        canvas.height = frame.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(frame, 0, 0, canvas.width, canvas.height);
        if (this.noHumanPlayers === 1) {
            const res = this.findLargestSquareAndScaleTo300x300ThenFlip(canvas);
            if (this.isLeftPlayerHuman) this.props.leftImg(res);
            else this.props.rightImg(res);
        } else if (this.noHumanPlayers === 2) {
            this.props.leftImg(this.findLargestSquareAndScaleTo300x300ThenFlip
                (this.getHalfImage(canvas, true)));
            this.props.rightImg(this.findLargestSquareAndScaleTo300x300ThenFlip
                (this.getHalfImage(canvas, false)));
        }
    }

    // Splits an image in half horizontally. Returns either the left or right half of this.
    getHalfImage(image, isLeftHalf) {
        var canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const width = image.width / 2;
        const height = image.height;
        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(image, isLeftHalf? width : 0, 0, width, height,  0, 0, width, height);
        return canvas;
    }

    // Takes an image as an input and finds the largest square. This square is then
    // scaled to be 300 x 300. This image is then flipped.
    findLargestSquareAndScaleTo300x300ThenFlip(image) {
        // Gets largest square into a canvas
        const smallestDim = Math.min(image.height, image.width);
        var square = document.createElement('canvas');
        var squareCtx = square.getContext('2d');
        square.height = smallestDim;
        square.width = smallestDim;
        squareCtx.drawImage(image, (image.width - smallestDim) / 2, (image.height - smallestDim) / 2,
        smallestDim, smallestDim, 0, 0, smallestDim, smallestDim);
        //Resizes image to 300 x 300 and flips it
        var resize = document.createElement('canvas');
        var resizeCtx = resize.getContext('2d');
        resize.height = 300;
        resize.width = 300;
        resizeCtx.translate(resize.width, 0);
        resizeCtx.scale(-1, 1);
        resizeCtx.drawImage(square, 0, 0, 300, 300);
        return resize;
    }



    // Intiaises camera for game
    initCamera() {
        const videoElement = document.getElementsByClassName('input_video')[0];
        videoElement.onloadeddata = (event) => {
            this.loadedVideo = true;
        };
        const camera = new Camera(videoElement, {
            onFrame: async () => {
                if(this.loadedVideo) {
                    this.handleFrame(videoElement);
                }
            },
            width: 10000,
            height: 10000
        });
        camera.start();
    }
  
    render() {
        return (
            <video className="input_video"/>
        );
    }
  }
  export default CameraHandler;