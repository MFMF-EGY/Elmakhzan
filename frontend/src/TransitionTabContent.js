import { useState, useEffect, useRef, createContext, useContext, use } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';
import { TransitionDocumentItem } from './ItemComponents.js';
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
  const [ Stores, setStores ] = useState([]);
  const DestinationStoreIDRef = useRef();
  const Itemslist = useRef(Array.from({ length: 12 }, () => ({
    ProductName: "",
    ProductID: "",
    Trademark: "",
    ManufactureCountry: "",
    Quantity: "",
    QuantityUnit: "",
  })));
  const CreateDocument = async (event) => {
    let RequestParams = {
      RequestType: "Transit",
      ProjectID: ProjectID,
      SourceStoreID: StoreID,
      DestinationStoreID: DestinationStoreIDRef.current.value,
      Orders: Itemslist.current.map((item) => (item.ProductID !== "" && item.Quantity !== "" && item.UnitPrice !== "" ? {
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
          setStores(response.data.Data);
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
            <select type="text" ref={DestinationStoreIDRef}>
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
                <th>الكود</th>
                <th>العلامة التجارية</th>
                <th>بلد الصنع</th>
                <th>الكمية</th>
                <th>الوحدة</th>
              </tr>
            </thead>
            <tbody>
              {Itemslist.current.map((item, index) => (
                <TransitionDocumentItem Index={index} ItemInfo={item} ItemsList={Itemslist} />
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <button onClick={(event) => CreateDocument(event)}>إنشاء</button>
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
  const ItemsList = useRef(Array.from({ length: 12 }, () => ({
    ProductName: "",
    ProductID: "",
    Trademark: "",
    ManufactureCountry: "",
    Quantity: "",
    QuantityUnit: "",
  })));

  const fetchDocument = async () => {
    let RequestParams = {
      RequestType: "GetTransitionDocument",
      ProjectID: ProjectID,
      DocumentID: SelectedRow.current.children[1].innerText
    }
    await axios.get(API_URL, {params: RequestParams})
    .then((response) => {
      if (!response.data.StatusCode){
        response.data.Data.Items.map((item, index) => {
          ItemsList.current[index].ProductName = item.Product_Name;
          ItemsList.current[index].ProductID = item.Product_ID;
          ItemsList.current[index].Trademark = item.Trademark;
          ItemsList.current[index].ManufactureCountry = item.Manufacture_Country;
          ItemsList.current[index].Quantity = item.Quantity;
          ItemsList.current[index].QuantityUnit = item.Quantity_Unit;
        })
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
          setStores(response.data.Data);
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
                  <th>الكود</th>
                  <th>العلامة التجارية</th>
                  <th>بلد الصنع</th>
                  <th>الكمية</th>
                  <th>الوحدة</th>
                </tr>
              </thead>
              <tbody>
              {ItemsList.current.map((item, index) => (
                <TransitionDocumentItem ItemsList={ItemsList} Index={index}/>
              ))}
              </tbody>
            </table>
          </div>
          <div>
            <button onClick={(event) => EditDocument(event)}>تعديل</button>
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