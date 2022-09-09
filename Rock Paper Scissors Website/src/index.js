import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <App />
);

/*code should be:
 root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
but removing strict mode fixes issue with mediapipe interface and react
as it prevents rendering occuring twice (which leads to issues).
Other workarounds exist, but this is what I've done at moment. */

/* When designing website style, I used the following sites as inpiration:
https://www.romaglushko.com/lab/rock-paper-scissors/
https://trekhleb.dev/machine-learning-experiments/#/experiments/RockPaperScissorsMobilenetV2
*/

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
