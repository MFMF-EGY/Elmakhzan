import { useState, useEffect, useContext, useRef, use } from "react";
import axios from "axios";
import { GlobalContext } from "./App.js";

function InvoiceItem({ItemsList,Index}){
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
  const UnitPriceRef = useRef();
  const PriceRef = useRef();

  const suggestProduct = async (event) => {
    var RequestParams = {
      RequestType: "SearchProducts",
      ProjectID: ProjectID,
      StoreID: StoreID,
      Product_Name: event.target.value
    }
    await axios.get('http://localhost:8000/apis/v1.0/commercial', {params: RequestParams})
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
    UnitPriceRef.current.value = ItemInfo.UnitPrice;
    PriceRef.current.value = ItemInfo.Price;
    ItemsList.current[Index] = ItemInfo;
  },[ItemInfo]);
  
  return(
    <tr>
      <td>{Index+1}</td>
      <td>
        <input type="text" ref={ProductNameRef} onChange={(event) => { suggestProduct(event)}}
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
      <td><input type="number" ref={UnitPriceRef} onChange={(event) => {ItemsList.current[Index].UnitPrice = event.target.value}}></input></td>
      <td><input type="number" ref={PriceRef}></input></td>
    </tr>
  )
}

export default InvoiceItem;