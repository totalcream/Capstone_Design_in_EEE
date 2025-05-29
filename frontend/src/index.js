// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { MathJaxContext } from 'better-react-mathjax';

const mathJaxConfig = {
  loader: { load: ['input/tex', 'output/chtml'] },
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$']],
  }
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <MathJaxContext config={mathJaxConfig}>
      <App />
    </MathJaxContext>
  </React.StrictMode>
);

reportWebVitals();
