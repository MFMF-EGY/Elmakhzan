import { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import Link from "./link.ico";
import BrokenLink from "./broken-link.ico";
import { GlobalContext } from "./App.js";
import { API_URL } from "./App.js";

const LinkURL = `url(${Link})`;
const BrokenLinkURL = `url(${BrokenLink})`;

export function InvoiceItem({InvoiceType, ItemsList, ExistingQuantities, Index, outerAutoFill}){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const [ Suggestions, setSuggestions ] = useState([]);
  const [ showProductSuggestions, setShowProductSuggestions ] = useState(false);
  const [ Lock, setLock ] = useState([false, false, true]);
  const InitialQuantity = useRef(Number(ItemsList[Index].Quantity));
  const ProductNameRef = useRef();
  const TrademarkRef = useRef();
  const ManufactureCountryRef = useRef();
  const QuantityRef = useRef();
  const UnitRef = useRef();
  const UnitPriceRef = useRef();
  const PriceRef = useRef();

  const suggestProduct = async (event) => {
    var RequestParams = {
      RequestType: "SearchProducts",
      ProjectID: ProjectID,
      StoreID: StoreID,
      Product_Name: event.target.value
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setSuggestions(response.data.Data);
          setShowProductSuggestions(true);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }

  const autoFill = () => {
    if (Lock[2]){
      PriceRef.current.value = ItemsList[Index].Price = QuantityRef.current.value * UnitPriceRef.current.value;
    } else if (Lock[1]){
      UnitPriceRef.current.value = ItemsList[Index].UnitPrice = PriceRef.current.value / QuantityRef.current.value;
    } else {
      QuantityRef.current.value = ItemsList[Index].Quantity = PriceRef.current.value / UnitPriceRef.current.value;
    }
    outerAutoFill();
    UnitPriceRef.current.className = Number(UnitPriceRef.current.value) <= 0 ? "Invalid-field-data" : "";
    PriceRef.current.className = Number(PriceRef.current.value) <= 0 ? "Invalid-field-data" : "";
    if (Number(QuantityRef.current.value) <= 0){
      QuantityRef.current.className = "Invalid-field-data";
    } else if (InvoiceType === "Selling"){
    QuantityRef.current.className = Number(QuantityRef.current.value) > ExistingQuantities[Index] ? "Invalid-field-data" : "";
    } else if (InvoiceType === "EditSelling"){
      QuantityRef.current.className = Number(QuantityRef.current.value) > Number(ExistingQuantities[Index]) + InitialQuantity.current ? "Invalid-field-data" : "";
    }
  }
  
  useEffect(() => {
    ProductNameRef.current.value = ItemsList[Index].ProductName;
    TrademarkRef.current.value = ItemsList[Index].Trademark;
    ManufactureCountryRef.current.value = ItemsList[Index].ManufactureCountry;
    QuantityRef.current.value = ItemsList[Index].Quantity;
    UnitRef.current.value = ItemsList[Index].QuantityUnit;
    UnitPriceRef.current.value = ItemsList[Index].UnitPrice;
    PriceRef.current.value = ItemsList[Index].Price;
  });
  return(
    <tr>
      <td>{Index+1}</td>
      <td>
        <input type="text" ref={ProductNameRef}
        onChange={(event) => { ItemsList[Index].ProductName = event.target.value; suggestProduct(event)
        Suggestions.length > 0 && setShowProductSuggestions(true)}} onBlur={(event)=>{}}/>
          {showProductSuggestions && Suggestions.length > 0 &&
            <ul className="Drop-list">
              {Suggestions.filter(suggestion => 
                !ItemsList.some(item => item.ProductID === suggestion.Product_ID & ItemsList[Index].ProductID !== suggestion.Product_ID)
              ).map((suggestion) => (
                <li key={suggestion.ProductID} onClick={(event) => {
                ItemsList[Index] = {
                  ...ItemsList[Index],
                  ProductName: suggestion.Product_Name,
                  ProductID: suggestion.Product_ID,
                  Trademark: suggestion.Trademark,
                  ManufactureCountry: suggestion.Manufacture_Country,
                  QuantityUnit: suggestion.Quantity_Unit
                }
                ExistingQuantities[Index] = suggestion.Quantity;
                setShowProductSuggestions(false);
              }}>
                {suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country}
              </li>
            ))}
          </ul>
        }
      </td>
      <td>{ItemsList[Index].ProductID}</td>
      <td><input type="text" ref={TrademarkRef} /></td>
      <td><input type="text" ref={ManufactureCountryRef} /></td>
      <td>
        <input type="number" ref={QuantityRef} placeholder={ExistingQuantities[Index] !== undefined && "الكمية الموجودة "+ExistingQuantities[Index]} disabled={Lock[0]}
        onChange={(event) => {ItemsList[Index].Quantity = event.target.value; autoFill()}} />
        <button className="Field-lock" style={
            Lock[0] ? {backgroundImage: LinkURL} : {backgroundImage: BrokenLinkURL}
          } onClick={(event) => {
            Lock[0] ? setLock([false, true, false]): setLock([true, false, false]);
          }}></button>
      </td>
      <td><input type="text" ref={UnitRef} /></td>
      <td>
        <input type="number" ref={UnitPriceRef} onChange={(event) => {ItemsList[Index].UnitPrice = event.target.value; autoFill()}} disabled={Lock[1]}/>
        <button className="Field-lock" style={
            Lock[1] ? {backgroundImage: LinkURL} : {backgroundImage: BrokenLinkURL}
          } onClick={(event) => {
            Lock[1] ? setLock([true, false, false]): setLock([false, true, false]);
          }}></button>
      </td>
      <td>
        <input type="number" ref={PriceRef} onChange={(event) => {ItemsList[Index].Price = event.target.value;autoFill()}} disabled={Lock[2]}/>
        <button className="Field-lock" style={
            Lock[2] ? {backgroundImage: LinkURL} : {backgroundImage: BrokenLinkURL}
          } onClick={(event) => {
            Lock[2] ? setLock([false, true, false]): setLock([false, false, true]);
          }}></button>
      </td>
    </tr>
  )
}

export function TransitionDocumentItem({ItemsList,Index}){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const [ ItemInfo, setItemInfo ] = useState(ItemsList.current[Index]);
  const [ Suggestions, setSuggestions ] = useState([]);
  const [ showSuggestions, setShowSuggestions ] = useState(false);
  const ProductNameRef = useRef();
  const TrademarkRef = useRef();
  const ManufactureCountryRef = useRef();
  const QuantityRef = useRef();
  const UnitRef = useRef();

  const suggestProduct = async (event) => {
    var RequestParams = {
      RequestType: "SearchProducts",
      ProjectID: ProjectID,
      StoreID: StoreID,
      Product_Name: event.target.value
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setSuggestions(response.data.Data);
          setShowSuggestions(true);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }
  useEffect(() => {
    ProductNameRef.current.value = ItemInfo.ProductName;
    TrademarkRef.current.value = ItemInfo.Trademark;
    ManufactureCountryRef.current.value = ItemInfo.ManufactureCountry;
    QuantityRef.current.value = ItemInfo.Quantity;
    UnitRef.current.value = ItemInfo.QuantityUnit;
    ItemsList.current[Index] = ItemInfo;
  });
  
  return(
    <tr>
      <td>{Index+1}</td>
      <td>
        <input type="text" ref={ProductNameRef} onChange={(event) => { ItemsList.current[Index].ProductName = event.target.value; suggestProduct(event)}}
        onFocus={(event)=>{Suggestions.length > 0 && setShowSuggestions(true)}} onBlur={(event)=>{}}/>
        {showSuggestions && Suggestions.length > 0 &&
          <ul className="Drop-list">
            {Suggestions.map((suggestion) => (
              <li key={suggestion.ProductID} onClick={(event) => {
                ItemsList.current[Index].ProductID = suggestion.Product_ID;
                setItemInfo({
                  ...ItemInfo,
                  ProductName: suggestion.Product_Name,
                  ProductID: suggestion.Product_ID,
                  Trademark: suggestion.Trademark,
                  ManufactureCountry: suggestion.Manufacture_Country,
                  QuantityUnit: suggestion.Quantity_Unit
                });
                setShowSuggestions(false);
              }}>
                {suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country}
              </li>
            ))}
          </ul>
        }
      </td>
      <td>{ItemInfo.ProductID}</td>
      <td><input type="text" ref={TrademarkRef}></input></td>
      <td><input type="text" ref={ManufactureCountryRef}></input></td>
      <td><input type="number" ref={QuantityRef} onChange={(event) => {ItemsList.current[Index].Quantity = event.target.value}}></input></td>
      <td><input type="text" ref={UnitRef}></input></td>
    </tr>
  )
}
