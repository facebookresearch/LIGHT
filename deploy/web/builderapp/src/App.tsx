import React from 'react';
import {useAppDispatch, useAppSelector} from './app/hooks';
import {incremented, amountAdded} from './features/counter/counter-slice';
import logo from './logo.svg';
import './App.css';

function App() {
  const count = useAppSelector((state)=> state.counter.value);
  const dispatch = useAppDispatch()

  const handleClick = ()=> {
    dispatch(amountAdded(5))
  }

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.tsx</code> and save to reload.
        </p>
        <p>Hello</p>
        <button onClick={handleClick}>
          count : {count}
        </button>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
