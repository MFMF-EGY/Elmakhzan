import { useState, useEffect, useRef, createContext, useContext, use } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';
import { InvoiceItem } from './ItemComponents.js';
import { API_URL } from './App.js';

const QuantityAdjustmentsContext = createContext();

function QuantityAdjustmentsTabContent({ref}){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const [ SearchParam, setSearchParam ] = useState({
    OperationID: "",
    ProductName: "",
    Trademark: "",
    ManufactureCountry: "",
    OperationType: "",
    DateTime: "",
    Quantity: "",
    Note: ""
  });
  const [ UpdateTab, setUpdateTab ] = useState(false);
  const [ OperationsList, setOperationsList] = useState([]);
  const [ OpendForm, setOpendForm ] = useState(null);

  const DeleteOperationButtonRef = useRef(null);

  const SelectedRow = useRef(null);
  
  useEffect(() => {
    if (SelectedRow.current){SelectedRow.current.classList.remove("Selected-row");}
    SelectedRow.current = null;
    DeleteOperationButtonRef.current.disabled = true;
    setOpendForm(null); 
    fetchOperations();
  }, [UpdateTab, ProjectID, StoreID]);

  const fetchOperations = async () => {
    var RequestParams = {
      RequestType:"SearchAdjustmentOperations",
      ProjectID:ProjectID, StoreID:StoreID
    };
    if (SearchParam.OperationID){ RequestParams.Operation_ID = SearchParam.OperationID; }
    if (SearchParam.ProductName){ RequestParams.Product_Name = SearchParam.ProductName; }
    if (SearchParam.Trademark){ RequestParams.Trademark = SearchParam.Trademark; }
    if (SearchParam.ManufactureCountry){ RequestParams.Manufacture_Country = SearchParam.ManufactureCountry; }
    if (SearchParam.OperationType){ RequestParams.Operation_Type = SearchParam.OperationType; }
    if (SearchParam.DateTime){ RequestParams.Date_Time = SearchParam.DateTime; }
    if (SearchParam.Quantity){ RequestParams.Quantity = SearchParam.Quantity; }
    if (SearchParam.Note){ RequestParams.Reason = SearchParam.Note; }
    await axios.get(API_URL, {params: RequestParams})
      .then(
        (response)=>{
          if (!response.data.StatusCode)
            {setOperationsList(response.data.Data)}
          else
            {console.log(response.data)}
        })
      .catch((err)=>{console.log(err)});
  }

  const deleteOperation = async (OperationID) => {
    var RequestParams = {
      RequestType: "DeleteAdjustmentOperation",
      ProjectID: ProjectID, 
      OperationID: OperationID
    };
    await axios.get(API_URL, {params: RequestParams})
      .then(
        (response)=>{
          if (!response.data.StatusCode)
            {setUpdateTab(UpdateTab + 1)}
          else
            {console.log(response.data)}
        })
      .catch((err)=>{console.log(err)});
  }

  return(
    <QuantityAdjustmentsContext.Provider value={{ SearchParam, setSearchParam, UpdateTab, setUpdateTab, OperationsList,
      setOperationsList, OpendForm, setOpendForm, SelectedRow, DeleteOperationButtonRef }}>
      <div className="Tab-content" ref={ref}>
        <div className="Table-container">
          <table className="Table">
            <thead>
              <tr>
                <th>م</th>
                <th>الكود</th>
                <th>اسم المنتج</th>
                <th>العلامة التجارية</th>
                <th>البلد المصنع</th>
                <th>كود المنتج</th>
                <th>نوع العملية</th>
                <th>الوقت والتاريخ</th>
                <th>الكمية</th>
                <th>ملاحظات</th>
              </tr>
            </thead>
            <tbody>
              <AdjustmentOperationsTableBody/>
            </tbody> 
          </table>
          {OpendForm === "AddOperationForm" ? <AddOperationForm/> :
           OpendForm === "SearchOperationsForm" && <SearchOperationsForm/> }
        </div>
        <div className='Side-bar'>
          <button className="Sidebar-button" onClick={(event) => setOpendForm("AddOperationForm")}>إضافة عملية</button>
          <button className="Sidebar-button" ref={DeleteOperationButtonRef}
            onClick={(event) => deleteOperation(SelectedRow.current.children[1].innerText)}>حذف عملية</button>
          <button className="Sidebar-button" onClick={(event) => setOpendForm("SearchOperationsForm")}>بحث</button>
        </div>

      </div>
    </QuantityAdjustmentsContext.Provider> 
  );
}

function AddOperationForm(){
  const { ProjectID, StoreID } = useContext(GlobalContext);
  const { UpdateTab, setUpdateTab, setOpendForm } = useContext(QuantityAdjustmentsContext);
  const [ ProductInfo, setProductInfo ] = useState({
    Product_ID: "",
    Product_Name: "",
    Trademark: "",
    Manufacture_Country: "",
    Quantity: "",
    Quantity_Unit: ""
  });
  const [Params, setParams] = useState({
    OperationType: "Increase",
    Quantity: "",
    Note: ""
  });
  const [ Suggestions, setSuggestions ] = useState([]);
  const [ showProductSuggestions, setShowProductSuggestions ] = useState(false);

  const suggestProduct = async (Field) => {
    var RequestParams = {
      RequestType: "SearchProducts",
      ProjectID: ProjectID,
      StoreID: StoreID,
      Product_Name: ProductInfo.Product_Name,
      Trademark: ProductInfo.Trademark,
      Manufacture_Country: ProductInfo.Manufacture_Country
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setSuggestions(response.data.Data);
          setShowProductSuggestions(Field);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }

  const addOperation = async () => {
    var RequestParams = {
      RequestType:"AdjustProductQuantity",
      ProjectID:ProjectID, StoreID:StoreID,
      ProductID: ProductInfo.Product_ID,
      OperationType: Params.OperationType,
      Quantity: Params.Quantity,
      Note: Params.Note,
    };
    await axios.get(API_URL, {params: RequestParams})
      .then(
        (response)=>{
          if (!response.data.StatusCode)
            {setUpdateTab(UpdateTab + 1)}
          else
            {console.log(response.data)}
        })
      .catch((err)=>{console.log(err)});
  }

  const SuggestionsSelect =  () => {
    return <ul className="Drop-list">
      {Suggestions.map((suggestion) => (
        <li key={suggestion.Product_ID} onClick={(event) => {
          setProductInfo(suggestion);
          setShowProductSuggestions(false);
        }}>
        {suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country}
        </li>
      ))}
    </ul>
  }

  const checkQuantityValidation = () => {
    if ( Params.Quantity < 0 ){
      return false;
    }
    if (Params.OperationType === "Decrease" || Params.OperationType === "Damage" ||
        Params.OperationType === "Lost") {
      if (Number(Params.Quantity) > Number(ProductInfo.Quantity)) {
        return false;
      }
    }
    return true;
  }
  
  return (
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={() => setOpendForm("")}>X</button>
        </div>
        <div>
          <label>اسم المنتج</label>
          <div>
            <input type="text" onChange={(event) => {
              suggestProduct("ProductNameField");
              setProductInfo({
                ...ProductInfo,
                Product_Name: event.target.value,
              });
            }}
            value={ProductInfo.Product_Name} />
            {showProductSuggestions === "ProductNameField" && Suggestions.length > 0 &&
              <SuggestionsSelect/>
            }
          </div>
        </div>
        <div>
          <label>العلامة التجارية</label>
          <div>
            <input type="text" value={ProductInfo.Trademark}
              onChange={(event) => {
                suggestProduct("TrademarkField");
                setProductInfo({
                  ...ProductInfo,
                  Trademark: event.target.value,
                });
              }}/>
            {showProductSuggestions === "TrademarkField" && Suggestions.length > 0 &&
              <SuggestionsSelect/>
            }
          </div>
        </div>
        <div>
          <label>البلد المصنع</label>
          <div>
            <input type="text" value={ProductInfo.Manufacture_Country}
              onChange={(event) => {
                suggestProduct("ManufactureCountryField");
                setProductInfo({
                  ...ProductInfo,
                  Manufacture_Country: event.target.value,
                });
              }}/>
            {showProductSuggestions === "ManufactureCountryField" && Suggestions.length > 0 &&
              <SuggestionsSelect/>
            }
          </div>
        </div>
        <div>
          <label>كود المنتج</label>
          <input type="text" value={ProductInfo.Product_ID} disabled/>
        </div>
        <div>
          <label>نوع العملية</label>
          <select value={Params.OperationType} onChange={(event) => {setParams({...Params, OperationType:event.target.value})}}>
            <option value="Increase">زيادة</option>
            <option value="Decrease">نقص</option>
            <option value="Damage">تالف</option>
            <option value="Lost">فاقد</option>
            <option value="Found">مرتجع</option>
            <option value="Maintenance">صيانة</option>
          </select>
        </div>
        <div>
          <label>الكمية</label>
          <input type="number" defaultValue={Params.Quantity}
            placeholder={ProductInfo.Quantity !== "" && 'الكمية الموجودة '+ProductInfo.Quantity}
            className={ checkQuantityValidation() ? "" : "Invalid-field-data" }
            onChange={(event) => {
              setParams({...Params, Quantity: event.target.value})
            }}/>
        </div>
        <div>
          <label>ملاحظات</label>
          <input type="text" defaultValue={Params.Note}
            onChange={(event) => {setParams({...Params, Note:event.target.value})}}/>
        </div>
        <div>
          <button onClick={addOperation}
            disabled={
              ProductInfo.Product_ID === "" || 
              !checkQuantityValidation() ||
              Params.OperationType === "" ||
              Params.Quantity === ""
            }>إضافة</button>
        </div>
      </div>
    </div>
  )
}
function SearchOperationsForm(){
  const { ProjectID, StoreID } = useContext(GlobalContext);
  const { SearchParam, setSearchParam, UpdateTab, setUpdateTab, setOpendForm } = useContext(QuantityAdjustmentsContext);
  const [ ProductInfo, setProductInfo ] = useState({
    Product_Name: SearchParam.ProductName,
    Trademark: SearchParam.Trademark,
    Manufacture_Country: SearchParam.ManufactureCountry
  });
  const [Params, setParams] = useState({
    OperationID: SearchParam.OperationID,
    OperationType: SearchParam.OperationType,
    Quantity: SearchParam.Quantity,
    Note: SearchParam.Note
  });
  const [ Suggestions, setSuggestions ] = useState([]);
  const [ showProductSuggestions, setShowProductSuggestions ] = useState(false);

  const suggestProduct = async (Field) => {
    var RequestParams = {
      RequestType: "SearchProducts",
      ProjectID: ProjectID,
      StoreID: StoreID,
      Product_Name: ProductInfo.Product_Name,
      Trademark: ProductInfo.Trademark,
      Manufacture_Country: ProductInfo.Manufacture_Country
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setSuggestions(response.data.Data);
          setShowProductSuggestions(Field);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }
  const SearchAdjustmentOperations = () => {
    setSearchParam({
      OperationID: Params.OperationID,
      ProductName: ProductInfo.Product_Name,
      Trademark: ProductInfo.Trademark,
      ManufactureCountry: ProductInfo.Manufacture_Country,
      OperationType: Params.OperationType,
      DateTime: "",
      Quantity: Params.Quantity,
      Note: Params.Note
    });
    setUpdateTab(!UpdateTab);
  }

  const SuggestionsSelect =  () => {
    return <ul className="Drop-list">
      {Suggestions.map((suggestion) => (
        <li key={suggestion.Product_ID} onClick={(event) => {
          setProductInfo(suggestion);
          setShowProductSuggestions(false);
        }}>
        {suggestion.Product_Name + " - " + suggestion.Trademark + " - " + suggestion.Manufacture_Country}
        </li>
      ))}
    </ul>
  }
  
  return (
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={() => setOpendForm("")}>X</button>
        </div>
        <div>
          <label>كود العملية</label>
          <input type="text" value={Params.OperationID}
            onChange={(event) => {setParams({...Params, OperationID:event.target.value})}}/>
        </div>
        <div>
          <label>اسم المنتج</label>
          <div>
            <input type="text" onChange={(event) => {
              suggestProduct("ProductNameField");
              setProductInfo({
                ...ProductInfo,
                Product_Name: event.target.value,
              });
            }}
            onBlur={() => setShowProductSuggestions(false)}
            value={ProductInfo.Product_Name} />
            {showProductSuggestions === "ProductNameField" && Suggestions.length > 0 &&
              <SuggestionsSelect/>
            }
          </div>
        </div>
        <div>
          <label>العلامة التجارية</label>
          <div>
            <input type="text" value={ProductInfo.Trademark}
              onChange={(event) => {
                suggestProduct("TrademarkField");
                setProductInfo({
                  ...ProductInfo,
                  Trademark: event.target.value,
                });
              }}
              onBlur={() => setShowProductSuggestions(false)}
            />
            {showProductSuggestions === "TrademarkField" && Suggestions.length > 0 &&
              <SuggestionsSelect/>
            }
          </div>
        </div>
        <div>
          <label>البلد المصنع</label>
          <div>
            <input type="text" value={ProductInfo.Manufacture_Country}
              onChange={(event) => {
                suggestProduct("ManufactureCountryField");
                setProductInfo({
                  ...ProductInfo,
                  Manufacture_Country: event.target.value,
                });
              }}
              onBlur={() => setShowProductSuggestions(false)}
            />
            {showProductSuggestions === "ManufactureCountryField" && Suggestions.length > 0 &&
              <SuggestionsSelect/>
            }
          </div>
        </div>
        <div>
          <label>نوع العملية</label>
          <select value={Params.OperationType} onChange={(event) => {setParams({...Params, OperationType:event.target.value})}}>
            <option value="Increase">زيادة</option>
            <option value="Decrease">نقص</option>
            <option value="Damage">تالف</option>
            <option value="Lost">فاقد</option>
            <option value="Found">مرتجع</option>
            <option value="Maintenance">صيانة</option>
          </select>
        </div>
        <div>
          <label>الكمية</label>
          <input type="number" defaultValue={Params.Quantity}
            onChange={(event) => {
              setParams({...Params, Quantity: event.target.value})
            }}/>
        </div>
        <div>
          <label>ملاحظات</label>
          <input type="text" defaultValue={Params.Note}
            onChange={(event) => {setParams({...Params, Note:event.target.value})}}/>
        </div>
        <div>
          <button onClick={SearchAdjustmentOperations}>ابحث</button>
        </div>
      </div>
    </div>
  )
}

function AdjustmentOperationsTableBody(){
  const { OperationsList, SelectedRow, DeleteOperationButtonRef } = useContext(QuantityAdjustmentsContext);
  const selectRow = (event) => {
    if (SelectedRow.current){SelectedRow.current.classList.remove("Selected-row");}
    SelectedRow.current = event.currentTarget;
    SelectedRow.current.classList.add("Selected-row");
    DeleteOperationButtonRef.current.disabled = false;
  }
  let OperationTypes = {
    Increase: "زيادة",
    Decrease: "نقص",
    Damage: "تالف",
    Lost: "فاقد",
    Found: "مرتجع",
    Maintenance: "صيانة"
  }
  return (
    OperationsList.map((operation, index) => (
      <tr onClick={(event)=>selectRow(event)}>
        <td>{index + 1}</td>
        <td>{operation.Operation_ID}</td>
        <td>{operation.Product_Name}</td>
        <td>{operation.Trademark}</td>
        <td>{operation.Manufacture_Country}</td>
        <td>{operation.Product_ID}</td>
        <td>{OperationTypes[operation.Operation_Type]}</td>
        <td>{operation.DateTime}</td>
        <td>{operation.Quantity}</td>
        <td>{operation.Reason}</td>
      </tr>
    ))
  );
}
export default QuantityAdjustmentsTabContent;