import { useState, useEffect, useRef, createContext, useContext, use } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';
import { TransitionDocumentItem } from './ItemComponents.js';
import ItemsListEditor from './ItemsListEditor.js';
import { API_URL } from './App.js';

const TransitionTabContext = createContext();

export function TransitionTabContent({ref}){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const [ SearchParams, setSearchParams ] = useState({
    DocumentID: "",
    DateTime: "",
    StoreID: StoreID
  });
  const [ UpdateTab, setUpdateTab ] = useState(0);
  const [ DocumentsList, setDocumentsList ] = useState([]);
  const [ OpendForm, setOpendForm ] = useState(null);

  const EditDocumentButtonRef = useRef(null);
  const DeleteDocumentButtonRef = useRef(null);
  const SearchDocumentButtonRef = useRef(null);
  const PrintDocumentButtonRef = useRef(null);

  const SelectedRow = useRef(null);

  useEffect(() => {
    if (SelectedRow.current){SelectedRow.current.classList.remove("Selected-row");}
    SelectedRow.current = null;
    EditDocumentButtonRef.current.disabled = true;
    DeleteDocumentButtonRef.current.disabled = true;
    PrintDocumentButtonRef.current.disabled = true;
    setOpendForm(null);
    fetchDocuments();
  }, [UpdateTab, ProjectID, StoreID]);

  const fetchDocuments = async () => {
    let RequestParams = {
      RequestType: "SearchTransitionDocuments",
      ProjectID: ProjectID,
      StoreID: StoreID
    }
    if (SearchParams.DocumentID){RequestParams.DocumentID = SearchParams.DocumentID;}
    if (SearchParams.DateTime){RequestParams.DateTime = SearchParams.DateTime;}
    if (SearchParams.DestinationStoreName){RequestParams.DestinationStoreName = SearchParams.DestinationStoreName;}
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setDocumentsList(response.data.Data);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }

  const deleteDocument = async (event) => {
    let RequestParams = {
      RequestType: "DeleteTransitionDocument",
      ProjectID: ProjectID,
      StoreID: StoreID,
      DocumentID: SelectedRow.current.id
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setUpdateTab(UpdateTab+1);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }

  return (
    <TransitionTabContext.Provider value={{ SearchParams, setSearchParams, UpdateTab, setUpdateTab, DocumentsList,
      setDocumentsList, OpendForm, setOpendForm, SelectedRow, EditDocumentButtonRef, DeleteDocumentButtonRef, PrintDocumentButtonRef }}>
    
      <div className="Tab-content" ref={ref}>
        <div className="Table-container">
          <table className="Table" id="Transition-documents-table">
            <thead>
              <tr>
                <th>م</th>
                <th>الكود</th>
                <th>الوقت والتاريخ</th>
                <th>من مخزن</th>
                <th>إلى مخزن</th>
              </tr>
            </thead>
            <tbody>
              <TransitionDocumentsTableBody />
            </tbody>
          </table>
          {OpendForm === "CreateDocumentForm" ? <CreateDocumentForm /> :
          OpendForm === "SearchDocumentForm" ? <SearchDocumentForm /> :
          OpendForm === "EditDocumentForm" && <EditDocumentForm />}
        </div>
        <div className='Side-bar'>
          <button className='Sidebar-button' onClick={(event) => setOpendForm("CreateDocumentForm")}>إنشاء مستند</button>
          <button className='Sidebar-button' ref={SearchDocumentButtonRef} onClick={(event) => setOpendForm("SearchDocumentForm")}>بحث</button>
          <button className='Sidebar-button' ref={EditDocumentButtonRef} onClick={(event) => setOpendForm("EditDocumentForm")}>تعديل مستند</button>
          <button className='Sidebar-button' ref={DeleteDocumentButtonRef} onClick={(event) => deleteDocument(event)}>حذف مستند</button>
          <button className='Sidebar-button' ref={PrintDocumentButtonRef}>طباعة</button>
        </div>
      </div>

    </TransitionTabContext.Provider>
  )
}
function CreateDocumentForm(){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const { setOpendForm, UpdateTab, setUpdateTab } = useContext(TransitionTabContext);
  const [ Processing, setProcessing ] = useState(false);
  const [ Stores, setStores ] = useState([]);
  const [ DocumentInfo, setDocumentInfo ] = useState({
    DestinationStoreID: ""
  });
  const [ ItemsList, setItemsList ] = useState(Array.from({ length: 12 }, () => ({
    ProductName: "",
    ProductID: "",
    Trademark: "",
    ManufactureCountry: "",
    Quantity: "",
    QuantityUnit: "",
  })));
  const [ ValidationChecker, setValidationChecker ] = useState(Array.from({ length: 12 }, () => undefined));
  const [ SelectedItemIndex, setSelectedItemIndex ] = useState(null);
  const ExistingQuantities = useRef([]);
  const InsufficientQuantityProducts = useRef([]);

  const fetchExistingQuantites = async (ItemsList) => {
    let RequestParams = {
      RequestType: "GetProductsQuantities",
      ProjectID: ProjectID,
      StoreID: StoreID,
    }
    let ProductIDs = ItemsList.map((item) => item.ProductID);
    for (let i = 0; i < ProductIDs.length; i++){
      RequestParams[`ProductsIDs[${i}]`] = ProductIDs[i] ? ProductIDs[i] : undefined;
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          ExistingQuantities.current = response.data.Data;
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => {
        console.log(error);
      })
  }

  const CreateDocument = async () => {
    setProcessing(true);
    let RequestParams = {
      RequestType: "Transit",
      ProjectID: ProjectID,
      SourceStoreID: StoreID,
      DestinationStoreID: DocumentInfo.DestinationStoreID,
      Orders: ItemsList.map((item) => (item.ProductID !== "" && item.Quantity !== "" ? {
        ProductID: item.ProductID,
        Quantity: item.Quantity
      } : null))
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setUpdateTab(UpdateTab+1);
        } else if (response.data.StatusCode === 6){
          InsufficientQuantityProducts.current = response.data.Data.ProductsIDs;
          fetchExistingQuantites(ItemsList);
          setProcessing(false);
          alert("كميات غير متوفرة");
        }else{
          setProcessing(false);
          console.log(response.data);
        }
      })
      .catch((error) => {
        setProcessing(false);
        console.log(error);
      })
  }

  useEffect(() => {
    let RequestParams = {
      RequestType: "GetStores",
      ProjectID: ProjectID
    }
    axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setStores(response.data.Data.filter((store) => store.Store_ID !== Number(StoreID)));
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }, []);

  return (
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={(event) => setOpendForm(null)}>X</button>
        </div>
        
        <div>
          <div>
            <label>المخزن المقصد</label>
            <select type="text"
              value={DocumentInfo.DestinationStoreID}
              onChange={(event) => 
                setDocumentInfo({...DocumentInfo, DestinationStoreID: event.target.value})
              }
            >
              <option value="">اختر مخزن</option>
              {Stores.map((store) => (
                <option key={store.Store_ID} value={store.Store_ID}>{store.Store_Name}</option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <table className='Table InputTable'>
            <thead>
              <tr>
                <th>م</th>
                <th>اسم المنتج</th>
                <th>العلامة التجارية</th>
                <th>بلد الصنع</th>
                <th>الكود</th>
                <th>الكمية</th>
                <th>الوحدة</th>
              </tr>
            </thead>
            <tbody>
              {ItemsList.map((item, index) => (
                <TransitionDocumentItem
                  ItemsList={ItemsList}
                  setItemsList={setItemsList}
                  setSelectedItemIndex={setSelectedItemIndex}
                  Index={index}
                  ExistingQuantities={ExistingQuantities.current}
                  isQuantitySufficient={!InsufficientQuantityProducts.current.some((product) => Number(product) === item.ProductID)}
                  ValidationChecker={ValidationChecker}
                  setValidationChecker={setValidationChecker}
                />
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <ItemsListEditor
            ItemsList={ItemsList}
            setItemsList={setItemsList}
            ExistingQuantities={ExistingQuantities.current}
            SelectedItemIndex={SelectedItemIndex}
            ValidationChecker={ValidationChecker}
            setValidationChecker={setValidationChecker}
            ItemFieldsStructure={{
              ProductName: "",
              ProductID: "",
              Trademark: "",
              ManufactureCountry: "",
              Quantity: "",
              QuantityUnit: ""
            }} 
          />
        </div>
        <div>
          <button
            className="Form-submit"
            onClick={(event) => CreateDocument(event)}
            disabled={
              Processing || ValidationChecker.includes(false) || !ValidationChecker.includes(true) || DocumentInfo.DestinationStoreID === ""
            }
          >إنشاء</button>
        </div>
      </div>
    </div>
  );
}

function SearchDocumentForm(){
  const { SearchParams, setSearchParams, UpdateTab, setUpdateTab, setOpendForm } = useContext(TransitionTabContext);
  const SearchDocument = async (event) => {
    setUpdateTab(UpdateTab+1);
  }
  return (
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={(event) => setOpendForm(null)}>X</button>
        </div>
        <div>
          <label>الكود</label>
          <input type="text" value={SearchParams.DocumentID} onChange={(event) => setSearchParams({...SearchParams, DocumentID: event.target.value})}></input>
        </div>
        <div>
          <label>الوقت والتاريخ</label>
          <input type="text" value={SearchParams.DateTime} onChange={(event) => setSearchParams({...SearchParams, DateTime: event.target.value})}></input>
        </div>
        <div>
          <label>المخزن المقصد</label>
          <input type="text" value={SearchParams.DestinationStoreName} onChange={(event) => setSearchParams({...SearchParams, DestinationStoreName: event.target.value})}></input>
        </div>
        <div>
          <button onClick={(event) => SearchDocument(event)}>بحث</button>
        </div>
      </div>
    </div>
  );
}

function EditDocumentForm(){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const { UpdateTab, setUpdateTab, setOpendForm, SelectedRow } = useContext(TransitionTabContext);
  const [ Stores, setStores ] = useState([])
  const [ Loading, setLoading ] = useState(true);
  const [ DocumentInfo, setDocumentInfo ] = useState({});
  const SourceStoreNameFieldRef = useRef();
  const DestinationStoreNameFieldRef = useRef();
  const [ ItemsList, setItemsList ] = useState(Array.from({ length: 12 }, () => ({
    ProductName: "",
    ProductID: "",
    Trademark: "",
    ManufactureCountry: "",
    Quantity: "",
    QuantityUnit: "",
  })));
  const [ ValidationChecker, setValidationChecker ] = useState(Array.from({ length: 12 }, () => undefined));
  const [ SelectedItemIndex, setSelectedItemIndex ] = useState(null);
  const ExistingQuantities = useRef([]);

  const fetchDocument = async () => {
    let RequestParams = {
      RequestType: "GetTransitionDocument",
      ProjectID: ProjectID,
      DocumentID: SelectedRow.current.children[1].innerText
    }
    await axios.get(API_URL, {params: RequestParams})
    .then((response) => {
      if (!response.data.StatusCode){
        let NewItemsList = Array.from({ length: 12 }, () => ({
          ProductName: "",
          ProductID: "",
          Trademark: "",
          ManufactureCountry: "",
          Quantity: "",
          QuantityUnit: "",
        }));
        response.data.Data.Items.forEach((item, index) => {
          NewItemsList[index] = {
            ProductName: item.Product_Name,
            ProductID: item.Product_ID,
            Trademark: item.Trademark,
            ManufactureCountry: item.Manufacture_Country,
            Quantity: item.Quantity,
            QuantityUnit: item.Quantity_Unit,
          }
        });
        setItemsList(NewItemsList);
        setValidationChecker(Array.from({ length: 12 }, (_, index) => index < response.data.Data.Items.length ? true : undefined));
        setDocumentInfo({
          DocumentID: response.data.Data.Document_ID,
          DateTime: response.data.Data.DateTime,
          SourceStoreID: response.data.Data.Source_Store_ID,
          DestinationStoreID: response.data.Data.Destination_Store_ID
        });
        setLoading(false);
      }else{
        console.log(response.data);
        setLoading("error")
      }
    })
    .catch((error) => {
      console.log(error);
      setLoading("error");
    })
  }
  const EditDocument = async (event) => {
    let RequestParams = {
      RequestType: "EditTransitionDocument",
      ProjectID: ProjectID,
      StoreID: StoreID,
      DocumentID: SelectedRow.current.children[1].innerText,
      SourceStoreID: SourceStoreNameFieldRef.current.value,
      DestinationStoreID: DestinationStoreNameFieldRef.current.value,
      Orders: ItemsList.current.map((item) => (item.ProductID !== "" && item.Quantity !== "" ? {
        ProductID: item.ProductID,
        Quantity: item.Quantity
      } : null))
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setUpdateTab(UpdateTab+1);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }
  useEffect(() => {
    let RequestParams = {
      RequestType: "GetStores",
      ProjectID: ProjectID
    }
    axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setStores(response.data.Data.filter((store) => store.Store_ID !== Number(StoreID)));
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
    fetchDocument();
  }, [])
  return (
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={(event) => setOpendForm(null)}>X</button>
        </div>
        {Loading === false?
          <>
          <div>
            <div>
              <label>الكود</label>
              <input type="text" defaultValue={DocumentInfo.DocumentID} disabled />
            </div>
            <div>
              <label>من مخزن</label>
              <select type="text" ref={SourceStoreNameFieldRef} defaultValue={DocumentInfo.SourceStoreID}>
                {Stores.map((store) => (
                  <option key={store.Store_ID} value={store.Store_ID}>{store.Store_Name}</option>
                ))}
              </select>
            </div>
            <div>
              <label>إلى مخزن</label>
              <select type="text" ref={DestinationStoreNameFieldRef} defaultValue={DocumentInfo.DestinationStoreID}>
                {Stores.map((store) => (
                  <option key={store.Store_ID} value={store.Store_ID}>{store.Store_Name}</option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <table className='Table InputTable'>
              <thead>
                <tr>
                  <th>م</th>
                  <th>اسم المنتج</th>
                  <th>العلامة التجارية</th>
                  <th>بلد الصنع</th>
                  <th>الكود</th>
                  <th>الكمية</th>
                  <th>الوحدة</th>
                </tr>
              </thead>
              <tbody>
              {ItemsList.map((item, index) => (
                <TransitionDocumentItem 
                  ItemsList={ItemsList}
                  setItemsList={setItemsList}
                  setSelectedItemIndex={setSelectedItemIndex}
                  Index={index}
                  ExistingQuantities={ExistingQuantities}
                  ValidationChecker={ValidationChecker}
                  setValidationChecker={setValidationChecker}
                />
              ))}
              </tbody>
            </table>
          </div>
          <div>
            <ItemsListEditor
              ItemsList={ItemsList}
              setItemsList={setItemsList}
              ExistingQuantities={ExistingQuantities.current}
              SelectedItemIndex={SelectedItemIndex}
              setSelectedItemIndex={setSelectedItemIndex}
              ValidationChecker={ValidationChecker}
              setValidationChecker={setValidationChecker}
              ItemFieldsStructure={{
                ProductName: "",
                ProductID: "",
                Trademark: "",
                ManufactureCountry: "",
                Quantity: "",
                QuantityUnit: ""
              }} 
            />
          </div>
          <div>
            <button
              className="Form-submit"
              onClick={(event) => EditDocument(event)}
              disabled={
                Loading || ValidationChecker.includes(false) || !ValidationChecker.includes(true) ||
                SourceStoreNameFieldRef.current.value === "" || DestinationStoreNameFieldRef.current.value === ""
              }
            >تعديل</button>
          </div>
          </>
        : Loading === "error" ? "error" : "loading"}
      </div>
    </div>
  );
}

function TransitionDocumentsTableBody(){
  const { DocumentsList, SelectedRow, EditDocumentButtonRef, DeleteDocumentButtonRef, PrintDocumentButtonRef } = useContext(TransitionTabContext);
  const selectRow = (event) => {
    if (SelectedRow.current){SelectedRow.current.classList.remove("Selected-row");}
    SelectedRow.current = event.target.parentElement;
    SelectedRow.current.classList.add("Selected-row");
    EditDocumentButtonRef.current.disabled = false;
    DeleteDocumentButtonRef.current.disabled = false;
    PrintDocumentButtonRef.current.disabled = false;
  }

  return (
    DocumentsList.map((document, index) => (
      <tr key={index} id={document.Document_ID} onClick={(event) => selectRow(event)}>
        <td>{index + 1}</td>
        <td>{document.Document_ID}</td>
        <td>{document.DateTime}</td>
        <td>{document.Source_Store_Name}</td>
        <td>{document.Destination_Store_Name}</td>
      </tr>
    ))
  )
}
export default TransitionTabContent;