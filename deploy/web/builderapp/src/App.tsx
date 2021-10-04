/* REACT */
import React from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from './app/hooks';
import {incremented, amountAdded} from './features/counter/counter-slice';
/* STYLES */
import './App.css';
/* CUSTOM COMPONENTS */
import NavBar from "./components/NavBar";
import { Navbar } from 'react-bootstrap';
import Routes from "./Routes";


const App = ()=> {
  const count = useAppSelector((state)=> state.counter.value);
  const dispatch = useAppDispatch()

  const handleClick = ()=> {
    dispatch(amountAdded(5))
  }

  return (
    <div className="App">
      <div style={{width:"100%", background:"blue", height:"50px"}}/>
      <Routes/>
    </div>
  );
}

export default App;