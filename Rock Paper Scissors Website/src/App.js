import './App.css';
import React from 'react';

import { loadLayersModel, zeros } from '@tensorflow/tfjs';
import '@tensorflow/tfjs-backend-webgl';
import '@tensorflow/tfjs-backend-cpu';

import RobotPlayer from './RobotPlayer';
import HumanPlayer from './HumanPlayer';
import PlayButton from './PlayButton';
import ResultsConfidence from './ResultsConfidence';
import CameraHandler from './CameraHandler';
import report from './report.pdf';

class App extends React.Component {

  constructor() {
    super();
    //Sets state and binds methods
    this.state = {modelLoaded: false, model: null,
    leftSideIsHuman: true, rightSideIsHuman: false,
    handTrackingVisualised: false, score: {leftScore: 0, rightScore: 0},
    confidenceLeftSide: [0.0, 0.0, 0.0], confidenceRightSide: [0.0, 0.0, 0.0],
    leftSideResultRecieved: false, rightSideResultReceived: false,
    leftMove: 3, rightMove: 3,
    gamesPlayed: 0,
    noDraws: 0, countDownStarted: false};
    //Binds methods
    this.loadAndWarmNetwork = this.loadAndWarmNetwork.bind(this);
    this.changeHandTrackingState = this.changeHandTrackingState.bind(this);
    this.countDownStarted = this.countDownStarted.bind(this);
    this.countDownFinished = this.countDownFinished.bind(this);
    this.receiveResult = this.receiveResult.bind(this);
    this.leftImageReceived = this.leftImageReceived.bind(this);
    this.rightImageReceived = this.rightImageReceived.bind(this);
    this.changeLeftPlayerType = this.changeLeftPlayerType.bind(this);
    this.changeRightPlayerType = this.changeRightPlayerType.bind(this);
    this.loadReport = this.loadReport.bind(this);
    // Creates references for players and image handler
    this._leftPlayer = React.createRef();
    this._rightPlayer = React.createRef();
    this._cameraHandler = React.createRef();
  }

  componentDidMount() {
    this.loadAndWarmNetwork();
    this.initHandsModels();
  }

  // Intialises both hands models for players in order
  async initHandsModels() {
    // Can only load if references are defined
    if (!this.state.modelLoaded) return;
    if(this.state.leftSideIsHuman) await this._leftPlayer.current.initHands();
    if(this.state.rightSideIsHuman) await this._rightPlayer.current.initHands();
  }

  componentDidUpdate() {
    //Updates the camera handler data after a state change
    if (this.state.modelLoaded){
      const totHumans = (this.state.leftSideIsHuman? 1 : 0) + (this.state.rightSideIsHuman? 1 : 0);
      this._cameraHandler.current.setPlayerTypeInfo(totHumans, this.state.leftSideIsHuman);
    }
    // Handles update in case that both results have been receieved
    this.checkForGameResult();
    this.initHandsModels();
  }

  // Checks to see if both players have made their moves and updates object as appropriate
  checkForGameResult() {
    //Checks to see if a result is being expected
    if (this.state.score.leftScore + this.state.score.rightScore + this.state.noDraws
       !== this.state.gamesPlayed) {
      // Checks to see if both results have been received
      if (this.state.leftSideResultRecieved && this.state.rightSideResultReceived) {
        const leftWins = () => {
          this.setState({score: {leftScore: this.state.score.leftScore + 1, 
          rightScore: this.state.score.rightScore}, countDownStarted: false});};
        const rightWins = () => {        
          this.setState({score: {leftScore: this.state.score.leftScore, 
          rightScore: this.state.score.rightScore + 1}, countDownStarted: false});};
  
        const leftMove = this.state.leftMove;
        const rightMove = this.state.rightMove;
        //Calculates winner
        if (leftMove === rightMove) this.setState({noDraws: this.state.noDraws + 1, countDownStarted: false});//Draw
        else if (leftMove === 0 && rightMove === 1) rightWins();// [Rock, Paper]
        else if (leftMove === 0 && rightMove === 2) leftWins();// [Rock, Scissors]
        else if (leftMove === 1 && rightMove === 0) leftWins();// [Paper, Rock]
        else if (leftMove === 1 && rightMove === 2) rightWins();// [Paper, Scissors]
        else if (leftMove === 2 && rightMove === 0) rightWins();// [Scissors, Rock]
        else if (leftMove === 2 && rightMove === 1) leftWins();// [Scissors, Paper]
      }
    }
  }

  // Loads model and passes a dummy input through it to speed up future calls
  loadAndWarmNetwork() {
    loadLayersModel('/Trained Model/Rock Paper Scissors Model JS/model.json')
    .then((model) => {
      model.predict(zeros([1, 21, 3, 1]));
      this.setState({modelLoaded: true, model: model});
    })
  }

  // Changes hand tracking
  changeHandTrackingState() {
    const new_track = !this.state.handTrackingVisualised;
    this.setState({handTrackingVisualised: new_track}, () => {
      if (this.state.leftSideIsHuman) this._leftPlayer.current.enableLineDrawing(new_track);
      if (this.state.rightSideIsHuman) this._rightPlayer.current.enableLineDrawing(new_track);
    });
  }

  // Notifies players that countdown has started
  countDownStarted() {
    // Indicates that no moves have been received yet
    this.setState({leftSideResultRecieved: false, rightSideResultReceived: false, 
      leftMove: 3, rightMove: 3, countDownStarted: true}, () => {
      this._leftPlayer.current.gameStarted();
      this._rightPlayer.current.gameStarted();
    });
  }

  // Receives the result of a move being made. If both moves have been made,
  // the score is updated. Also updates ResultConfidence visualiser if needed
  receiveResult(move, isLeftPlayer, confidenceInResults) {
    if (isLeftPlayer) {
      this.setState({confidenceLeftSide: confidenceInResults, leftSideResultRecieved: true,
      leftMove: move});
    } else{
      this.setState({confidenceRightSide: confidenceInResults, rightSideResultReceived: true,
        rightMove: move});
    }
  }

  // Used to send video frame from Camera Handler to left player
  leftImageReceived(img) {
    if(this.state.leftSideIsHuman){
      this._leftPlayer.current.videoFrameReceieved(img);
    }
  }

  // Used to send video frame from Camera Handler to right player
  rightImageReceived(img) {
    if(this.state.rightSideIsHuman){
      this._rightPlayer.current.videoFrameReceieved(img);
    }
  }

  // Gets moves made by players
  countDownFinished() {
    this.setState({gamesPlayed: this.state.gamesPlayed + 1}, () => {
      //Makes moves
      this._leftPlayer.current.makeMove();
      this._rightPlayer.current.makeMove();
    });
  }

  //Changes the left player from a robot to a human and vice versa
  changeLeftPlayerType() {
    this._leftPlayer.current.cleanUpBeforeClose();
    this.setState({leftSideIsHuman: !this.state.leftSideIsHuman, leftSideResultRecieved: false,
    leftResultConfidence: [0.0, 0.0, 0.0]}, () => {
      //unfreezes both player videos / moves
      this._leftPlayer.current.gameStarted();
      this._rightPlayer.current.gameStarted();
    });
  }

  //Changes the right player from a robot to a human and vice versa
  changeRightPlayerType() {
    this._rightPlayer.current.cleanUpBeforeClose();
    this.setState({rightSideIsHuman: !this.state.rightSideIsHuman, rightSideResultReceived: false,
    rightResultConfidence: [0.0, 0.0, 0.0]}, () => {
        //unfreezes both player videos / moves
        this._leftPlayer.current.gameStarted();
        this._rightPlayer.current.gameStarted();
    });
  }

  // Takes user to report on how game was developed
  loadReport() {
    const lnk = document.getElementById("linkReport");
    lnk.click();
  }

  render() {     
    //Displays confidence in results if appropriate
    const leftResultConfidence = this.state.leftSideIsHuman && this.state.leftSideResultRecieved?
      <ResultsConfidence data={this.state.confidenceLeftSide} side="left"/>
      : <p />;
    const rightResultConfidence = this.state.rightSideIsHuman && this.state.rightSideResultReceived?
      <ResultsConfidence data={this.state.confidenceRightSide} side="right"/>
      : <p />;

    const leftPlayer = this.state.leftSideIsHuman?          
    <HumanPlayer className="leftPlayer" ref={this._leftPlayer} onResult={this.receiveResult}
    tfModel={this.state.model} handTracking={this.state.handTrackingVisualised} isLeftPlayer={true} /> : 
    <RobotPlayer className="leftPlayer" ref={this._leftPlayer} onResult={this.receiveResult} 
    isLeftPlayer={true}/>;

    const rightPlayer = this.state.rightSideIsHuman?       
    <HumanPlayer className="rightPlayer" ref={this._rightPlayer} onResult={this.receiveResult}
    tfModel={this.state.model} handTracking={this.state.handTrackingVisualised} isLeftPlayer={false}/> : 
    <RobotPlayer className="rightPlayer" ref={this._rightPlayer} onResult={this.receiveResult} 
    isLeftPlayer={false}/>;
    return (
      !this.state.modelLoaded? <div>
        Loading...
      </div> :

      <div className="gridContainer">
        {leftPlayer}
        {rightPlayer}
        {leftResultConfidence}
        {rightResultConfidence}
        <button className="leftChangeBtn" disabled={this.state.countDownStarted} onClick={this.changeLeftPlayerType}>
          Change to {this.state.leftSideIsHuman? "🤖" : "🧠"} </button>
        <button disabled={this.state.countDownStarted} className="rightChangeBtn" onClick={this.changeRightPlayerType}>
          Change to {this.state.rightSideIsHuman? "🤖" : "🧠"} </button>
        <div className="scorePlayAndTrack">
          <p className="score">{this.state.score.leftScore} : {this.state.score.rightScore}</p>
          <PlayButton className="playButton" 
          countDownFinished={this.countDownFinished} countDownStarted={this.countDownStarted} />
          <button className="handTracking" onClick={this.changeHandTrackingState}
            id={this.state.handTrackingVisualised?"disableTrack" : "enableTrack"}
            disabled={!this.state.leftSideIsHuman && !this.state.rightSideIsHuman}>
              {this.state.handTrackingVisualised? "Disable Tracking" : "Enable Tracking"}
          </button>
        </div>
        <button className="moreInfo" type="button" onClick={() => {this.loadReport();}}> 
          Read about game making process! 
        </button>
        <a id="linkReport" href={report} target="_blank" rel="noopener noreferrer">Link to game report pdf
        </a>
        <CameraHandler ref={this._cameraHandler} leftImg={this.leftImageReceived}
        rightImg={this.rightImageReceived}/>
      </div>
      )
  }
}
export default App;
