/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

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
import AppRouter from './AppRouter'
/* TESTING */
import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <Provider store={store}>
    <AppRouter />
  </Provider>,
  document.getElementById('root')
)

reportWebVitals();
