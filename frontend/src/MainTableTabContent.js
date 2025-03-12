import { useState, useEffect, useRef, createContext, useContext } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';

function MainTableTabContent({ref}){
  return (
    <div className="Tab-content" style={{display:"flex"}} ref={ref}></div>
  )
}

export default MainTableTabContent;