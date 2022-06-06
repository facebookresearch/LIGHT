/* REACT */
import React from 'react'
import ReactDOM from 'react-dom'
/* STYLING */
import './index.css'
import 'bootstrap/dist/css/bootstrap.min.css';
/* REDUX */
import { store } from './app/store'
import { Provider } from 'react-redux'
/* COMPONENTS */
import LIGHTAppTaskFrame from './LIGHTAppTaskFrame'

ReactDOM.render(
  <Provider store={store}>
    <LIGHTAppTaskFrame />
  </Provider>,
  document.getElementById('app')
)
