import { useState, useEffect, useContext, useRef } from "react";
import axios from "axios";
import SuggestionsInput from "./SuggestionsInput.js";
import Link from "./link.ico";
import BrokenLink from "./broken-link.ico";
import { GlobalContext } from "./App.js";
import { API_URL } from "./App.js";

const LinkURL = `url(${Link})`;
const BrokenLinkURL = `url(${BrokenLink})`;

export function InvoiceItem({ ItemsList, setItemsList, setSelectedItemIndex, ExistingQuantities, isQuantitySufficient, Index, ValidationChecker, setValidationChecker}){
  const { ProjectID, StoreID } = useContext(GlobalContext);
  //const [ InitialQuantity, setInitialQuantity ] = useState(ItemsList[Index].Quantity);
  const [ Suggestions, setSuggestions ] = useState([]);
  const [ FilteredSuggestions, setFilteredSuggestions ] = useState([]);
  const [ Lock, setLock ] = useState([false, false, true]);

  const Item = useRef();

  const suggestProduct = async (NewItemsList) => {
    var RequestParams = {
      RequestType: "SearchProducts",
      ProjectID: ProjectID,
      StoreID: StoreID,
      Product_Name: NewItemsList[Index].ProductName,
      Trademark: NewItemsList[Index].Trademark,
      Manufacture_Country: NewItemsList[Index].ManufactureCountry
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setSuggestions(response.data.Data);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }


  useEffect(() => {
    let NewItemsList = [...ItemsList];
    let MatchedSuggestion = FilteredSuggestions.find(suggestion =>
      suggestion.Product_Name === ItemsList[Index].ProductName &&
      suggestion.Trademark === ItemsList[Index].Trademark &&
      suggestion.Manufacture_Country === ItemsList[Index].ManufactureCountry
    );
    
    if (MatchedSuggestion) {
      NewItemsList[Index] = {
        ...NewItemsList[Index],
        ProductName: MatchedSuggestion.Product_Name,
        ProductID: MatchedSuggestion.Product_ID,
        Trademark: MatchedSuggestion.Trademark,
        ManufactureCountry: MatchedSuggestion.Manufacture_Country,
        QuantityUnit: MatchedSuggestion.Quantity_Unit
      };
      ExistingQuantities[Index] = MatchedSuggestion.Quantity
    }

    setFilteredSuggestions(
      Suggestions.filter(suggestion => 
        !NewItemsList.some(item => item.ProductID === suggestion.Product_ID)
      )
    );
    
    if (
      ItemsList[Index].ProductName !== NewItemsList[Index].ProductName ||
      ItemsList[Index].ProductID !== NewItemsList[Index].ProductID ||
      ItemsList[Index].Trademark !== NewItemsList[Index].Trademark ||
      ItemsList[Index].ManufactureCountry !== NewItemsList[Index].ManufactureCountry ||
      ItemsList[Index].Quantity !== NewItemsList[Index].Quantity ||
      ItemsList[Index].UnitPrice !== NewItemsList[Index].UnitPrice ||
      ItemsList[Index].Price !== NewItemsList[Index].Price
    ) {
      setItemsList(NewItemsList);
    }
  },[Suggestions]);

  useEffect(() => {
    if ( ItemsList[Index].ProductID && ItemsList[Index].Quantity && ItemsList[Index].UnitPrice) {
      let NewValidationList = [...ValidationChecker];
      NewValidationList[Index] = true;
      setValidationChecker(NewValidationList);
      
    } else if (
      !ItemsList[Index].ProductName && !ItemsList[Index].Trademark && !ItemsList[Index].ManufactureCountry
      && !ItemsList[Index].Quantity && !ItemsList[Index].UnitPrice && !ItemsList[Index].Price
    ) {
      let NewItemsList = [...ItemsList];
      NewItemsList[Index] = {
        ProductName: "",
        ProductID: "",
        Trademark: "",
        ManufactureCountry: "",
        QuantityUnit: "",
        Quantity: "",
        UnitPrice: "",
        Price: ""
      };
      let NewValidationList = [...ValidationChecker];
      NewValidationList[Index] = undefined;
      setValidationChecker(NewValidationList);
    } else {
      let NewValidationList = [...ValidationChecker];
      NewValidationList[Index] = false;
      setValidationChecker(NewValidationList);
    }
  }, [ItemsList[Index]]);


  return(
    <tr ref={Item}>
      <td>{Index+1}</td>
      <td>
        <SuggestionsInput Value={ItemsList[Index].ProductName}
          Suggestions={FilteredSuggestions.map(suggestion => suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country)}
          Disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductID: "",
              QuantityUnit: "",
              ProductName: event.target.value
            };
            ExistingQuantities[Index] = undefined;
            setItemsList(NewItemsList);
            suggestProduct(NewItemsList);

          }}
          onSelect={(index) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductName: FilteredSuggestions[index].Product_Name,
              ProductID: FilteredSuggestions[index].Product_ID,
              Trademark: FilteredSuggestions[index].Trademark,
              ManufactureCountry: FilteredSuggestions[index].Manufacture_Country,
              QuantityUnit: FilteredSuggestions[index].Quantity_Unit
            };
            setItemsList(NewItemsList);
            ExistingQuantities[Index] = FilteredSuggestions[index].Quantity;

          }}
        />
      </td>
      <td>
        <SuggestionsInput Value={ItemsList[Index].Trademark}
          Suggestions={FilteredSuggestions.map(suggestion => suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country)}
          Disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductID: "",
              QuantityUnit: "",
              Trademark: event.target.value
            };
            ExistingQuantities[Index] = undefined;
            setItemsList(NewItemsList);
            suggestProduct(NewItemsList);

          }}
          onSelect={(index) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductName: FilteredSuggestions[index].Product_Name,
              ProductID: FilteredSuggestions[index].Product_ID,
              Trademark: FilteredSuggestions[index].Trademark,
              ManufactureCountry: FilteredSuggestions[index].Manufacture_Country,
              QuantityUnit: FilteredSuggestions[index].Quantity_Unit
            };
            setItemsList(NewItemsList);
            ExistingQuantities[Index] = FilteredSuggestions[index].Quantity;

          }}
        />
      </td>
      <td>
        <SuggestionsInput Value={ItemsList[Index].ManufactureCountry}
          Suggestions={FilteredSuggestions.map(suggestion => suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country)}
          Disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductID: "",
              QuantityUnit: "",
              ManufactureCountry: event.target.value
            };
            ExistingQuantities[Index] = undefined;
            setItemsList(NewItemsList);
            suggestProduct(NewItemsList);

          }}
          onSelect={(index) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductName: FilteredSuggestions[index].Product_Name,
              ProductID: FilteredSuggestions[index].Product_ID,
              Trademark: FilteredSuggestions[index].Trademark,
              ManufactureCountry: FilteredSuggestions[index].Manufacture_Country,
              QuantityUnit: FilteredSuggestions[index].Quantity_Unit
            };
            setItemsList(NewItemsList);
            ExistingQuantities[Index] = FilteredSuggestions[index].Quantity;

          }}
        />
      </td>
      <td>
        <input
          type="text"
          value={ItemsList[Index].ProductID}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          readOnly
        />
      </td>
      <td>
        <input type="number" value={ItemsList[Index].Quantity}
          placeholder={ExistingQuantities[Index] !== undefined && "الكمية الموجودة "+ExistingQuantities[Index]}
          disabled={Lock[0] || (Index > 0 ? !ValidationChecker[Index - 1]: false)}
          className={
            isQuantitySufficient ? "" : "Invalid-field-data"
          }
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            if (!isQuantitySufficient){ 
              isQuantitySufficient = true
            }
            let Value = event.target.value > 0 ? event.target.value : "";
            let OtherValues = Lock[1] ? {
              UnitPrice: ItemsList[Index].Price / Value,
              Price: ItemsList[Index].Price
            } : {
              Price: Value * ItemsList[Index].UnitPrice,
              UnitPrice: ItemsList[Index].UnitPrice
            }
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              Quantity: Value,
              ...OtherValues,
            };
            setItemsList(NewItemsList);
            //setItemChanged(!ItemChanged);
          }} 
        />
        <button className="Field-lock" 
          style={
            {
              display: (Index > 0 ? !ValidationChecker[Index - 1] && "none" : ""),
              backgroundImage: Lock[0] ? LinkURL : BrokenLinkURL
            }
          }
          onClick={(event) => {
            Lock[0] ? setLock([false, true, false]): setLock([true, false, false]);
          }}></button>
      </td>
      <td>
        <input
          type="text"
          value={ItemsList[Index].QuantityUnit}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          readOnly
        />
      </td>
      <td>
        <input type="number" value={ItemsList[Index].UnitPrice}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let Value = event.target.value > 0 ? event.target.value : "";
            let OtherValues = Lock[0] ? {
              Quantity: ItemsList[Index].Price / Value,
              Price: ItemsList[Index].Price
            } : {
              Price: Value * ItemsList[Index].Quantity,
              Quantity: ItemsList[Index].Quantity
            }
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              UnitPrice: Value,
              ...OtherValues,
            };
            setItemsList(NewItemsList);
            //setItemChanged(!ItemChanged);
          }}
          disabled={Lock[1] || (Index > 0 ? !ValidationChecker[Index - 1]: false)}
        />
        <button className="Field-lock" 
          style={
            {
              display: (Index > 0 ? !ValidationChecker[Index - 1] && "none" : ""),
              backgroundImage: Lock[1] ? LinkURL : BrokenLinkURL
            }
          }
          onClick={(event) => {
            Lock[1] ? setLock([true, false, false]): setLock([false, true, false]);
          }}></button>
      </td>
      <td>
        <input type="number" value={ItemsList[Index].Price}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let Value = event.target.value > 0 ? event.target.value : "";
            let OtherValues = Lock[1] ? {
              UnitPrice: Value / ItemsList[Index].Quantity,
              Quantity: ItemsList[Index].Quantity
            } : {
              Quantity: Value / ItemsList[Index].UnitPrice,
              UnitPrice: ItemsList[Index].UnitPrice
            }
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              Price: Value,
              ...OtherValues,
            };
            setItemsList(NewItemsList);
            //setItemChanged(!ItemChanged);
          }}
          disabled={Lock[2] || (Index > 0 ? !ValidationChecker[Index - 1]: false)}
        />
        <button className="Field-lock" 
          style={
            {
              display: (Index > 0 ? !ValidationChecker[Index - 1] && "none" : ""),
              backgroundImage: Lock[2] ? LinkURL : BrokenLinkURL
            }
          }
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onClick={(event) => {
            Lock[2] ? setLock([false, true, false]): setLock([false, false, true]);
          }}></button>
      </td>
    </tr>
  )
}

export function TransitionDocumentItem({ItemsList, setItemsList, setSelectedItemIndex, Index, ExistingQuantities, isQuantitySufficient, ValidationChecker, setValidationChecker}){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  
  const InitialProductID = useRef(ItemsList[Index].ProductID);
  const [ InitialQuantity, setInitialQuantity ] = useState(ItemsList[Index].Quantity);
  const [ Suggestions, setSuggestions ] = useState([]);
  const [ FilteredSuggestions, setFilteredSuggestions ] = useState([]);

  const Item = useRef();

  const suggestProduct = async () => {
    var RequestParams = {
      RequestType: "SearchProducts",
      ProjectID: ProjectID,
      StoreID: StoreID,
      Product_Name: ItemsList[Index].ProductName,
      Trademark: ItemsList[Index].Trademark,
      Manufacture_Country: ItemsList[Index].ManufactureCountry
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setSuggestions(response.data.Data);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }


  useEffect(() => {
    let NewItemsList = [...ItemsList];
    let MatchedSuggestion = Suggestions.find(suggestion =>
      suggestion.Product_Name === ItemsList[Index].ProductName &&
      suggestion.Trademark === ItemsList[Index].Trademark &&
      suggestion.Manufacture_Country === ItemsList[Index].ManufactureCountry
    )
    if (MatchedSuggestion) {
      NewItemsList[Index] = {
        ...NewItemsList[Index],
        ProductName: MatchedSuggestion.Product_Name,
        ProductID: MatchedSuggestion.Product_ID,
        Trademark: MatchedSuggestion.Trademark,
        ManufactureCountry: MatchedSuggestion.Manufacture_Country,
        QuantityUnit: MatchedSuggestion.Quantity_Unit
      };
      ExistingQuantities[Index] = MatchedSuggestion.Quantity
    }
    setFilteredSuggestions(
      Suggestions.filter(suggestion => 
        !NewItemsList.some(item => item.ProductID === suggestion.Product_ID)
      )
    );

    if (
      ItemsList[Index].ProductName !== NewItemsList[Index].ProductName ||
      ItemsList[Index].ProductID !== NewItemsList[Index].ProductID ||
      ItemsList[Index].Trademark !== NewItemsList[Index].Trademark ||
      ItemsList[Index].ManufactureCountry !== NewItemsList[Index].ManufactureCountry ||
      ItemsList[Index].Quantity !== NewItemsList[Index].Quantity
    ) {
      setItemsList(NewItemsList);
    }
  },[Suggestions]);

  useEffect(() => {
    if ( ItemsList[Index].ProductID && ItemsList[Index].Quantity) {
      let NewValidationList = [...ValidationChecker];
      NewValidationList[Index] = true;
      setValidationChecker(NewValidationList);
      
    } else if (
      !ItemsList[Index].ProductName && !ItemsList[Index].Trademark && !ItemsList[Index].ManufactureCountry
      && !ItemsList[Index].Quantity
    ) {
      let NewItemsList = [...ItemsList];
      NewItemsList[Index] = {
        ProductName: "",
        ProductID: "",
        Trademark: "",
        ManufactureCountry: "",
        QuantityUnit: "",
        Quantity: ""
      };
      let NewValidationList = [...ValidationChecker];
      NewValidationList[Index] = undefined;
      setValidationChecker(NewValidationList);
    } else {
      let NewValidationList = [...ValidationChecker];
      NewValidationList[Index] = false;
      setValidationChecker(NewValidationList);
    }
  }, [ItemsList[Index]]);
  
  return(
    <tr ref={Item}>
      <td>{Index+1}</td>
      <td>
        <SuggestionsInput Value={ItemsList[Index].ProductName}
          Suggestions={FilteredSuggestions.map(suggestion => suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country)}
          Disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductID: "",
              QuantityUnit: "",
              ProductName: event.target.value
            };
            ExistingQuantities[Index] = undefined;
            setItemsList(NewItemsList);
            suggestProduct();
          }}
          onSelect={(index) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductName: FilteredSuggestions[index].Product_Name,
              ProductID: FilteredSuggestions[index].Product_ID,
              Trademark: FilteredSuggestions[index].Trademark,
              ManufactureCountry: FilteredSuggestions[index].Manufacture_Country,
              QuantityUnit: FilteredSuggestions[index].Quantity_Unit
            };
            setItemsList(NewItemsList);
          }}
        />
      </td>
      <td>
        <SuggestionsInput Value={ItemsList[Index].Trademark}
          Suggestions={FilteredSuggestions.map(suggestion => suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country)}
          Disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductID: "",
              QuantityUnit: "",
              Trademark: event.target.value
            };
            ExistingQuantities[Index] = undefined;
            setItemsList(NewItemsList);
            suggestProduct();
          }}
          onSelect={(index) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductName: FilteredSuggestions[index].Product_Name,
              ProductID: FilteredSuggestions[index].Product_ID,
              Trademark: FilteredSuggestions[index].Trademark,
              ManufactureCountry: FilteredSuggestions[index].Manufacture_Country,
              QuantityUnit: FilteredSuggestions[index].Quantity_Unit
            };
            setItemsList(NewItemsList);
            ExistingQuantities[Index] = FilteredSuggestions[index].Quantity;
          }}
        />
      </td>
      <td>
        <SuggestionsInput Value={ItemsList[Index].ManufactureCountry}
          Suggestions={FilteredSuggestions.map(suggestion => suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country)}
          Disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductID: "",
              QuantityUnit: "",
              ManufactureCountry: event.target.value
            };
            ExistingQuantities[Index] = undefined;
            setItemsList(NewItemsList);
            suggestProduct();
          }}
          onSelect={(index) => {
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              ProductName: FilteredSuggestions[index].Product_Name,
              ProductID: FilteredSuggestions[index].Product_ID,
              Trademark: FilteredSuggestions[index].Trademark,
              ManufactureCountry: FilteredSuggestions[index].Manufacture_Country,
              QuantityUnit: FilteredSuggestions[index].Quantity_Unit
            };
            setItemsList(NewItemsList);
            ExistingQuantities[Index] = FilteredSuggestions[index].Quantity;
          }}
        />
      </td>
      <td>
        <input
          type="text"
          value={ItemsList[Index].ProductID}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          readOnly
        />
      </td>
      <td>
        <input type="number" value={ItemsList[Index].Quantity} placeholder={ExistingQuantities[Index] !== undefined && "الكمية الموجودة "+ExistingQuantities[Index]}
          className={ 
            isQuantitySufficient ? "" : "Invalid-field-data"
          }
          disabled={Index > 0 ? !ValidationChecker[Index - 1]: false}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          onChange={(event) => {
            let Value = event.target.value > 0 ? event.target.value : "";
            let NewItemsList = [...ItemsList];
            NewItemsList[Index] = {
              ...NewItemsList[Index],
              Quantity: Value,
            };
            setItemsList(NewItemsList);
          }} 
        />
      </td>
      <td>
        <input type="text" value={ItemsList[Index].QuantityUnit}
          onFocus={() => {
            setSelectedItemIndex(Index);
          }}
          readOnly
        />
      </td>
    </tr>
  )
}
