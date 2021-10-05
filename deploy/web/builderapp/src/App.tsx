/* REACT */
import React from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from './app/hooks';
/* STYLES */
import './App.css';
/* CUSTOM COMPONENTS */
import Routes from "./Routes";


const App = ()=> {
  return (
      <Routes/>
  );
}

export default App;