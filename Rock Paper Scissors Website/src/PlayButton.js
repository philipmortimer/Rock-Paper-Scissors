// This component will contain the play button and will also display a three second countdown
// for players to make their move.
import React from 'react';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faPlay } from "@fortawesome/free-solid-svg-icons/faPlay"

class PlayButton extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {playButtonPressed: false, number: 3};
        this.startCountDown = this.startCountDown.bind(this);
    }

    startCountDown() {
        this.setState({playButtonPressed: true, number: 3});
        this.props.countDownStarted();
        //Counts down every second until 0, then resets button
        const timerId = window.setInterval(() => {
            const newNum = this.state.number - 1;
            if (newNum > 0){
                this.setState({number: newNum});
            }else{
                this.setState({playButtonPressed: false, number: 3});
                this.props.countDownFinished();
                window.clearInterval(timerId);
            }
        }, 1000);
    }

    render() {
        return (
            this.state.playButtonPressed? (
                <div className="playButtonTxt">{this.state.number}</div>
            ) :

            (<div className="playButtonBtnDiv">
                <button className="playButtonBtn" onClick={this.startCountDown}>
                  <FontAwesomeIcon icon={faPlay} /> Play
                </button>
            </div>)
        )
    }
}
  export default PlayButton;