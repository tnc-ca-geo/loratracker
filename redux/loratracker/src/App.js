import React from 'react';
import logo from './logo.svg';
import { Counter } from './features/counter/Counter';
import { MapContainer } from './features/map/Map';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <MapContainer />
      </header>
    </div>
  );
}

export default App;
