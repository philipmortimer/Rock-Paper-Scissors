// Creates bar chart to visualise model confidence that input is rock, paper or scissors.
import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    ResponsiveContainer
  } from 'recharts';

class ResultsConfidence extends React.Component {

    render() {
        const height = "100%";
        const width = "75%";
        const data = [{"move": "✊", "confidence": this.props.data[0] * 100.0}, 
            {"move": "✋", "confidence": this.props.data[1] * 100.0}, 
            {"move": "✌️", "confidence": this.props.data[2] * 100.0}];
        return (
            <ResponsiveContainer className={this.props.side+"Confidence"} width={width} height={height}>
                <BarChart data={data}>
                    <YAxis dataKey="confidence" tickFormatter={tick => `${tick}%` }/>
                    <XAxis dataKey="move" interval={0} />
                    <Bar
                        type="monotone"
                        dataKey="confidence"
                        barSize={30}
                    />
                </BarChart>
            </ResponsiveContainer>
        );
    }
}
  export default ResultsConfidence;