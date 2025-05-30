import { useState, useEffect, useRef, createContext, useContext, use } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';
import { InvoiceItem } from './ItemComponents.js'
import ItemsListEditor from './ItemsListEditor.js';
import { API_URL } from './App.js';

const PurchaseTabContext = createContext();

function PurchaseTabContent({ref}){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const [ SearchParam, setSearchParam ] = useState({
    InvoiceID: "",
    SellerName: "",
    DateTime: "",
    TotalPrice: "",
    Paid:""
  });
  const [ UpdateTab, setUpdateTab ] = useState(0);
  const [ InvoicesList, setInvoicesList] = useState([]);
  const [ OpendForm, setOpendForm ] = useState(null);
  
  const EditInvoiceButtonRef = useRef(null);
  const DeleteInvoiceButtonRef = useRef(null);
  
  const SelectedRow = useRef(null);

  useEffect(() => {
    if (SelectedRow.current){SelectedRow.current.classList.remove("Selected-row");}
    SelectedRow.current = null;
    EditInvoiceButtonRef.current.disabled = true;
    DeleteInvoiceButtonRef.current.disabled = true;
    setOpendForm(null); 
    fetchInvoices();
  }, [UpdateTab, ProjectID, StoreID]);

  const fetchInvoices = async () => {
    var RequestParams = {
      RequestType:"SearchInvoices",
      InvoiceType:"Purchase",
      ProjectID:ProjectID, StoreID:StoreID
    };
    if (SearchParam.InvoiceID){ RequestParams.Invoice_ID = SearchParam.InvoiceID; }
    if (SearchParam.SellerName){ RequestParams.Seller_Name = SearchParam.SellerName; }
    if (SearchParam.DateTime){ RequestParams.Date_Time = SearchParam.DateTime; }
    if (SearchParam.TotalPrice){ RequestParams.Total_Price = SearchParam.TotalPrice; }
    if (SearchParam.Paid){ RequestParams.Paid = SearchParam.Paid; }
    await axios.get(API_URL, {params: RequestParams})
      .then(
        (response)=>{
          if (!response.data.StatusCode)
            {setInvoicesList(response.data.Data)}
          else
            {console.log(response.data)}
        })
      .catch((err)=>{console.log(err)});
  }
  const deleteInvoice = async (InvoiceID) => {
    var RequestParams = {
      RequestType: "DeletePurchaseInvoice",
      ProjectID: ProjectID, 
      InvoiceID: InvoiceID
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
    <PurchaseTabContext.Provider value={{ SearchParam, setSearchParam, UpdateTab, setUpdateTab, InvoicesList,
      setInvoicesList, OpendForm, setOpendForm, SelectedRow, EditInvoiceButtonRef, DeleteInvoiceButtonRef }}>
      <div className="Tab-content" ref={ref}>
        <div className="Table-container">
          <table className="Table" id="Invoices-table">
            <thead>
              <tr>
                <th>م</th>
                <th>الكود</th>
                <th>اسم البائع</th>
                <th>الوقت والتاريخ</th>
                <th>إجمالي المبلغ</th>
                <th>المدفوع</th>
              </tr>
            </thead>
            <tbody>
              <PurchaseInvoicesTableBody/>
            </tbody>
          </table>
          {OpendForm === "CreateInvoiceForm" ? <CreateInvoiceForm/> :
           OpendForm === "SearchInvoicesForm" ? <SearchInvoicesForm/> :
           OpendForm === "EditInvoiceForm" && <EditInvoiceForm/>}
        </div>
        <div className='Side-bar'>
          <button className="Sidebar-button" onClick={(event) => setOpendForm("CreateInvoiceForm")}>إنشاء فاتورة</button>
          <button className="Sidebar-button" ref={EditInvoiceButtonRef} 
            onClick={(event) => setOpendForm("EditInvoiceForm")}>تعديل فاتورة</button>
          <button className="Sidebar-button" ref={DeleteInvoiceButtonRef}
            onClick={(event) => deleteInvoice(SelectedRow.current.children[1].innerText)}>حذف فاتورة</button>
          <button className="Sidebar-button" onClick={(event) => setOpendForm("SearchInvoicesForm")}>بحث</button>
          <button className="Sidebar-button">طباعة فاتورة</button>
        </div>
      </div>
    </PurchaseTabContext.Provider>
  );
}

function CreateInvoiceForm(){
  const { ProjectID, StoreID } = useContext(GlobalContext);
  const { UpdateTab, setUpdateTab, setOpendForm } = useContext(PurchaseTabContext);
  
  const [ InvoiceInfo, setInvoiceInfo ] = useState({
    SellerName: "",
    TotalPrice: "",
    Paid: ""
  });
  const [ ItemsList, setItemsList ] = useState(Array.from({ length: 12 }, () => ({
    ProductName: "",
    ProductID: "",
    Trademark: "",
    ManufactureCountry: "",
    Quantity: "",
    QuantityUnit: "",
    UnitPrice: "",
    Price: ""
  })));
  const [ ValidationChecker, setValidationChecker ] = useState(Array.from({ length: 12 }, () => undefined));
  const [ SelectedItemIndex, setSelectedItemIndex ] = useState(null);
  const ExistingQuantities = useRef([]);

  const createInvoice = async (event) => {
    var RequestParams = {
      RequestType: "Purchase",
      ProjectID: ProjectID,
      StoreID: StoreID,
      SellerName: InvoiceInfo.SellerName,
      Orders: ItemsList.map((item) => (item.ProductID !== "" && item.Quantity !== "" && item.UnitPrice !== "" ? {
        ProductID: item.ProductID,
        Quantity: item.Quantity,
        UnitPrice: item.UnitPrice,
      }: null)),
      Paid: InvoiceInfo.Paid
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setUpdateTab(UpdateTab + 1);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }

  useEffect(() => {
    InvoiceInfo.TotalPrice = ItemsList.reduce((acc, item) => acc + (Number(item.Price)),0);
  }, [ItemsList]);

  return(
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={(event) => setOpendForm("")}>X</button>
        </div>
        <div>
          <div>
            <label>اسم البائع</label>
            <input type="text"
            onChange={(event) =>{
              setInvoiceInfo({
                ...InvoiceInfo,
                SellerName: event.target.value
              });
            }}/>
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
                <th>سعر الوحدة</th>
                <th>السعر</th>
              </tr>
            </thead>
            <tbody>
              {ItemsList.map((item, index) => (
                <InvoiceItem 
                  ItemsList={ItemsList}
                  setItemsList={setItemsList}
                  setSelectedItemIndex={setSelectedItemIndex}
                  ExistingQuantities={ExistingQuantities.current}
                  isQuantitySufficient={true}
                  Index={index}
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
              QuantityUnit: "",
              UnitPrice: "",
              Price: ""
            }} 
          />
        </div>
        <div>
          <div>
            <label>المبلغ الكلي</label>
            <input type="number"
              value={InvoiceInfo.TotalPrice}
              readOnly
            />
          </div>
          <div>
            <label>المدفوع</label>
            <input
              type="number"
              className={InvoiceInfo.Paid > InvoiceInfo.TotalPrice || InvoiceInfo.Paid === 0 || InvoiceInfo.Paid < 0 ? "Invalid-field-data" : ""}
              value={InvoiceInfo.Paid}
              onChange={(event) => {
                setInvoiceInfo({
                  ...InvoiceInfo,
                  Paid: event.target.value
                });
              }}
            />
          </div>
        </div>
        <div>
          <button
            className="Form-submit"
            onClick={(event) => createInvoice(event)}
            disabled={
              ValidationChecker.includes(false) || !ValidationChecker.includes(true) || InvoiceInfo.SellerName === "" || InvoiceInfo.Paid === "" ||
              InvoiceInfo.Paid <= 0 || InvoiceInfo.Paid > InvoiceInfo.TotalPrice
            }
          >إنشاء</button>
        </div>
      </div>
    </div>
  )
}

function SearchInvoicesForm(){
  return ("")
}

function EditInvoiceForm(){
  const { ProjectID, StoreID } = useContext(GlobalContext);
  const { UpdateTab, setUpdateTab, CreateInvoiceFormRef, setOpendForm, SelectedRow } = useContext(PurchaseTabContext);
  const [ Loading , setLoading ] = useState(true);
  const [ InvoiceInfo, setInvoiceInfo ] = useState({
    InvoiceID: "",
    SellerName: "",
    TotalPrice: "",
    Paid: ""
  });
  const [ ItemsList, setItemsList ] = useState(Array.from({ length: 12 }, () => ({
    ProductName: "",
    ProductID: "",
    Trademark: "",
    ManufactureCountry: "",
    Quantity: "",
    QuantityUnit: "",
    UnitPrice: "",
    Price: ""
  })));
  const [ ValidationChecker, setValidationChecker ] = useState(Array.from({ length: 12 }, () => undefined));
  const [ SelectedItemIndex, setSelectedItemIndex ] = useState(null);
  const ExistingQuantities = useRef([]);

  const fetchInvoice = async () => {
    var RequestParams = {
      RequestType: "GetInvoice",
      InvoiceType: "Purchase",
      ProjectID: ProjectID,
      InvoiceID: SelectedRow.current.children[1].innerText
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          let ItemsList = Array.from({ length: 12 }, () => ({
            ProductName: "",
            ProductID: "",
            Trademark: "",
            ManufactureCountry: "",
            Quantity: "",
            QuantityUnit: "",
            UnitPrice: "",
            Price: ""
          }));
          response.data.Data.Items.forEach((item, index) => {
            ItemsList[index] = {
              ProductName: item.Product_Name,
              ProductID: item.Product_ID,
              Trademark: item.Trademark,
              ManufactureCountry: item.Manufacture_Country,
              Quantity: item.Quantity,
              QuantityUnit: item.Quantity_Unit,
              UnitPrice: item.Unit_Price,
              Price: item.Quantity * item.Unit_Price
            }
          });
          setItemsList(ItemsList);
          setValidationChecker(Array.from({ length: 12 }, (_, index) => index < response.data.Data.Items.length ? true : undefined));
          setInvoiceInfo({
            InvoiceID: response.data.Data.Invoice_ID,
            SellerName: response.data.Data.Seller_Name,
            TotalPrice: response.data.Data.Total_Price,
            Paid: response.data.Data.Paid,
          });
          fetchExistingQuantites(ItemsList);
        } else {
          console.log(response.data);
          setLoading("error");
        }
      })
      .catch((error) => {
        console.log(error);
        setLoading("error");
      })
  }

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
          setLoading(false)
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

  const editInvoice = async (event) => {
    var RequestParams = {
      RequestType: "EditPurchaseInvoice",
      ProjectID: ProjectID,
      InvoiceID: InvoiceInfo.InvoiceID,
      SellerName: InvoiceInfo.SellerName,
      Orders: ItemsList.map((item) => (item.ProductID !== "" && item.Quantity !== "" && item.UnitPrice !== "" ? {
        ProductID: item.ProductID,
        Quantity: item.Quantity,
        UnitPrice: item.UnitPrice,
      }: null)),
      Paid: InvoiceInfo.Paid
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          setUpdateTab(UpdateTab + 1);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => console.log(error))
  }
  
  useEffect(() => {
    InvoiceInfo.TotalPrice = ItemsList.reduce((acc, item) => acc + (Number(item.Price)),0);
  }, [ItemsList]);

  useEffect(() => {
    fetchInvoice();
  }, [])

  return(
    <div className='Form-container' ref={CreateInvoiceFormRef}>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={(event) => setOpendForm("")}>X</button>
        </div>
        {Loading === false?
          <>
          <div>
            <div>
              <label>الكود</label>
              <input type="text" value={InvoiceInfo.InvoiceID} readOnly />
            </div>
            <div>
              <label>اسم البائع</label>
              <input type="text" value={InvoiceInfo.SellerName}
                onChange={(event) =>{
                  setInvoiceInfo({
                    ...InvoiceInfo,
                    SellerName: event.target.value
                  });
                }}
              />
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
                  <th>سعر الوحدة</th>
                  <th>السعر</th>
                </tr>
              </thead>
              <tbody>
                {ItemsList.map((item, index) => (
                  <InvoiceItem 
                    ItemsList={ItemsList}
                    setItemsList={setItemsList}
                    setSelectedItemIndex={setSelectedItemIndex}
                    ExistingQuantities={ExistingQuantities.current}
                    isQuantitySufficient={true}
                    Index={index}
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
                QuantityUnit: "",
                UnitPrice: "",
                Price: ""
              }} 
            />
          </div>
          <div>
            <div>
              <label>المبلغ الكلي</label>
              <input type="number" value={InvoiceInfo.TotalPrice} readOnly/>
            </div>
            <div>
              <label>المدفوع</label>
              <input 
                type="number"
                className={InvoiceInfo.Paid > InvoiceInfo.TotalPrice || InvoiceInfo.Paid === 0 || InvoiceInfo.Paid < 0 ? "Invalid-field-data" : ""}
                value={InvoiceInfo.Paid}
                onChange={(event) => {
                  setInvoiceInfo({
                    ...InvoiceInfo,
                    Paid: event.target.value
                  });
                }}
              />
            </div>
          </div>
          <div>
            <button
              className="Form-submit"
              onClick={(event) => editInvoice(event)}
              disabled={
                ValidationChecker.includes(false) || !ValidationChecker.includes(true) || InvoiceInfo.SellerName === "" || InvoiceInfo.Paid === "" ||
                InvoiceInfo.Paid <= 0 || InvoiceInfo.Paid > InvoiceInfo.TotalPrice
              }
            >تعديل</button>
          </div>
        </>
      : Loading === "error"? "error" : "loading..."}
      </div>
    </div>
  )
}

function PurchaseInvoicesTableBody(){
  const { InvoicesList, SelectedRow, EditInvoiceButtonRef, DeleteInvoiceButtonRef } = useContext(PurchaseTabContext);
  const selectRow = (event) => {
    if (SelectedRow.current){SelectedRow.current.classList.remove("Selected-row");}
    SelectedRow.current = event.currentTarget;
    SelectedRow.current.classList.add("Selected-row");
    EditInvoiceButtonRef.current.disabled = false;
    DeleteInvoiceButtonRef.current.disabled = false;
  }

  return (
    InvoicesList.map((invoice, index) => (
      <tr onClick={(event)=>selectRow(event)}>
        <td>{index + 1}</td>
        <td>{invoice.Invoice_ID}</td>
        <td>{invoice.Seller_Name}</td>
        <td>{invoice.DateTime}</td>
        <td>{invoice.Total_Price}</td>
        <td>{invoice.Paid}</td>

      </tr>
    ))
  );
}
export default PurchaseTabContent;