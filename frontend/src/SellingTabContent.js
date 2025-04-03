import { useState, useEffect, useRef, createContext, useContext } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';
import { InvoiceItem } from './ItemComponents.js';
import { API_URL } from './App.js';

const SellingTabContext = createContext();

function SellingTabContent({ref}){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const [ SearchParam, setSearchParam ] = useState({
    InvoiceID: "",
    ClientName: "",
    DataTime: "",
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
    let RequestParams = {
      RequestType:"SearchInvoices",
      InvoiceType:"Selling",
      ProjectID:ProjectID,
      StoreID:StoreID
    };
    if (SearchParam.InvoiceID){ RequestParams.Invoice_ID = SearchParam.InvoiceID; }
    if (SearchParam.ClientName){ RequestParams.Seller_Name = SearchParam.SellerName; }
    if (SearchParam.DataTime){ RequestParams.Data_Time = SearchParam.DataTime; }
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
      RequestType: "DeleteSellingInvoice",
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
    <SellingTabContext.Provider value={{ SearchParam, setSearchParam, UpdateTab, setUpdateTab, InvoicesList,
      setInvoicesList, OpendForm, setOpendForm, SelectedRow, EditInvoiceButtonRef, DeleteInvoiceButtonRef }}>
      <div className="Tab-content" ref={ref}>
        <div className="Table-container">
          <table className="Table" id="Selling-table">
            <thead>
              <tr>
                <th>م</th>
                <th>الكود</th>
                <th>اسم العميل</th>
                <th>الوقت والتاريخ</th>
                <th>المبلغ المطلوب</th>
                <th>المبلغ المدفوع</th>
                <th>المضاف لحساب الدين</th>
              </tr>
            </thead>
            <tbody>
              <SellingInvoicesTableBody/>
            </tbody> 
          </table>
          {OpendForm === "CreateInvoiceForm" ? <CreateInvoiceForm/> :
           OpendForm === "SearchInvoiceForm" ? <SearchInvoiceForm/> :
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
    </SellingTabContext.Provider> 
  );
}
function SearchInvoiceForm(){
  return ("")
}
function CreateInvoiceForm(){
  const { ProjectID, StoreID } = useContext(GlobalContext);
  const { UpdateTab, setUpdateTab, setOpendForm } = useContext(SellingTabContext);
  
  const ClientNameFieldRef = useRef();
  const TotalPriceFieldRef = useRef();
  const PaidFieldRef = useRef();
  const AddToAccountFieldRef = useRef();
  const Itemslist = useRef(Array.from({ length: 12 }, () => ({
    ProductName: "",
    ProductID: "",
    Trademark: "",
    ManufactureCountry: "",
    Quantity: "",
    QuantityUnit: "",
    UnitPrice: "",
    Price: ""
  })));

  const createInvoice = async (event) => {
    var RequestParams = {
      RequestType: "Sell",
      ProjectID: ProjectID,
      StoreID: StoreID,
      ClientName: ClientNameFieldRef.current.value,
      Orders: Itemslist.current.map((item) => (item.ProductID !== "" && item.Quantity !== "" && item.UnitPrice !== "" ? {
        ProductID: item.ProductID,
        Quantity: item.Quantity,
        UnitPrice: item.UnitPrice,
      }: null)),
      Paid: PaidFieldRef.current.value
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

  return(
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={(event) => setOpendForm("")}>X</button>
        </div>
        <div>
          <div>
            <label>اسم العميل</label>
            <input type="text" ref={ClientNameFieldRef}></input>
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
                <th>بلد التصنيع</th>
                <th>الكمية</th>
                <th>الوحدة</th>
                <th>سعر الوحدة</th>
                <th>السعر</th>
              </tr>
            </thead>
            <tbody>
              {Itemslist.current.map((item, index) => (
                  <InvoiceItem ItemsList={Itemslist} Index={index}/>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <div>
            <label>اجمالي المبلغ</label>
            <input type="text" ref={TotalPriceFieldRef} />
          </div>
          <div>
            <label>المدفوع</label>
            <input type="text" ref={PaidFieldRef} />
          </div>
          <div>
            <label>المضاف لحساب الدين</label>
            <input type="text" ref={AddToAccountFieldRef} />
          </div>
        </div>
        <div>
          <button onClick={(event) => createInvoice(event)}>إنشاء</button>
        </div>
      </div>
    </div>
  )
}

function EditInvoiceForm(){
  const { ProjectID, StoreID } = useContext(GlobalContext);
  const { UpdateTab, setUpdateTab, setOpendForm, SelectedRow } = useContext(SellingTabContext);
  const [ Loading , setLoading ] = useState(true);
  const [ InvoiceInfo, setInvoiceInfo ] = useState({});
  const ClientNameFieldRef = useRef();
  const TotalPriceFieldRef = useRef();
  const PaidFieldRef = useRef();
  const TransferredToAccountFieldRef = useRef();
  const Itemslist = useRef(Array.from({ length: 12 }, () => ({
    ProductName: "",
    ProductID: "",
    Trademark: "",
    ManufactureCountry: "",
    Quantity: "",
    QuantityUnit: "",
    UnitPrice: "",
    Price: ""
  })));

  const fetchInvoice = async () => {
    var RequestParams = {
      RequestType: "GetInvoice",
      InvoiceType: "Selling",
      ProjectID: ProjectID,
      InvoiceID: SelectedRow.current.children[1].innerText
    }
    await axios.get(API_URL, {params: RequestParams})
      .then((response) => {
        if (!response.data.StatusCode){
          response.data.Data.Items.map((item, index) => {
            Itemslist.current[index].ProductName = item.Product_Name;
            Itemslist.current[index].ProductID = item.Product_ID;
            Itemslist.current[index].Trademark = item.Trademark;
            Itemslist.current[index].ManufactureCountry = item.Manufacture_Country;
            Itemslist.current[index].Quantity = item.Quantity;
            Itemslist.current[index].QuantityUnit = item.Quantity_Unit;
            Itemslist.current[index].UnitPrice = item.Unit_Price;
            Itemslist.current[index].Price = item.Quantity * item.Unit_Price;
          });
          setInvoiceInfo({
            InvoiceID: response.data.Data.Invoice_ID,
            ClientName: response.data.Data.Client_Name,
            TotalPrice: response.data.Data.Total_Price,
            Paid: response.data.Data.Paid,
            TransferredToAccount: response.data.Data.Transferred_To_Account
          });
          setLoading(false);
        }else{
          console.log(response.data);
          setLoading("error");
        }
      })
      .catch((error) => {
        console.log(error);
        setLoading("error");
      })
  }

  const editInvoice = async (event) => {
    var RequestParams = {
      RequestType: "EditSellingInvoice",
      ProjectID: ProjectID,
      InvoiceID: InvoiceInfo.InvoiceID,
      ClientName: ClientNameFieldRef.current.value,
      Orders: Itemslist.current.map((item) => (item.ProductID !== "" && item.Quantity !== "" && item.UnitPrice !== "" ? {
        ProductID: item.ProductID,
        Quantity: item.Quantity,
        UnitPrice: item.UnitPrice,
      }: null)),
      Paid: PaidFieldRef.current.value
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
    fetchInvoice();
  },[])

  return(
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={(event) => setOpendForm("")}>X</button>
        </div>
        {Loading === false?
          <>
          <div>
            <div>
              <label>الكود</label>
              <input type="text" value={InvoiceInfo.InvoiceID} disabled />
            </div>
            <div>
              <label>اسم العميل</label>
              <input type="text" defaultValue={InvoiceInfo.ClientName} ref={ClientNameFieldRef}></input>
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
                  <th>بلد التصنيع</th>
                  <th>الكمية</th>
                  <th>الوحدة</th>
                  <th>سعر الوحدة</th>
                  <th>السعر</th>
                </tr>
              </thead>
              <tbody>
                {Itemslist.current.map((item, index) => (
                    <InvoiceItem ItemsList={Itemslist} Index={index}/>
                ))}
              </tbody>
            </table>
          </div>
          <div>
            <div>
              <label>اجمالي المبلغ</label>
              <input type="text" defaultValue={InvoiceInfo.TotalPrice} ref={TotalPriceFieldRef}></input>
            </div>
            <div>
              <label>المدفوع</label>
              <input type="text" defaultValue={InvoiceInfo.Paid} ref={PaidFieldRef}></input>
            </div>
            <div>
              <label>المضاف لحساب الدين</label>
              <input type="text" defaultValue={InvoiceInfo.TransferredToAccount} ref={TransferredToAccountFieldRef}></input>
            </div>
          </div>
          <div>
            <button onClick={(event) => editInvoice(event)}>تعديل</button>
          </div>
        </>
      : Loading === "error"? "error" : "loading..."}
      </div>
    </div>
  )
}

function SellingInvoicesTableBody(){
  const { InvoicesList, SelectedRow, EditInvoiceButtonRef, DeleteInvoiceButtonRef } = useContext(SellingTabContext);
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
        <td>{invoice.Client_Name}</td>
        <td>{invoice.DateTime}</td>
        <td>{invoice.Total_Price}</td>
        <td>{invoice.Paid}</td>
        <td>{invoice.Transferred_To_Account}</td>
      </tr>
    ))
  );
}
export default SellingTabContent;