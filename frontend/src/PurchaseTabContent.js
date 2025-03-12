import { useState, useEffect, useRef, createContext, useContext } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';

function PurchaseTabContent({ref}){
  return (
    <div className="Tab-content" ref={ref}></div>
  )
}

export default PurchaseTabContent;