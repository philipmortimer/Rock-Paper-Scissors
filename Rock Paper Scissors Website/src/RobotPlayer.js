// Class used for robot players
import './Player.css';
import React from 'react';

class RobotPlayer extends React.Component {

    constructor(props) {
        super(props);
        this.state = {moveSelected: 3, imagesLoaded: false};
        this.images = [null, null, null];
        this.loadImages = this.loadImages.bind(this);
    }

    // Does anything that may need to occur before object is closed
    cleanUpBeforeClose() {}

    componentDidMount() { 
        this.renderCanvas();
        this.loadImages();
     }

    componentDidUpdate() { this.renderCanvas(); }

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

    // Makes a random move by returning an integer in range [0, 1, 2]
    makeMove() { 
        const move = Math.floor(Math.random() * 3);
        this.setState({moveSelected: move},() => {
            this.props.onResult(move, this.props.isLeftPlayer, 
                [move === 0? 1 : 0, move === 1? 1 : 0, move === 2? 1 : 0]);
        }); 
    }

    // Resets component so no move is selected
    gameStarted() { this.setState({moveSelected: 3}); }

    renderCanvas() {
        //Gets out canvas
        const canvasElement = document.getElementById("outputCanvasRobot" + this.props.isLeftPlayer);
        const canvasCtx = canvasElement.getContext("2d");
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        if (this.state.moveSelected !== 3 && this.state.imagesLoaded){
            canvasCtx.drawImage(this.images[this.state.moveSelected], 0, 0, 
                canvasElement.width, canvasElement.height);
        }
    }
  
    render() {
      return (
        <div className={this.props.isLeftPlayer? "leftPlayer" : "rightPlayer"}>
            <span>🤖 AI</span>
            <canvas id={"outputCanvasRobot" + this.props.isLeftPlayer} width="300" height="300"></canvas>
        </div>
      )
    }
  }
  export default RobotPlayer;