import { useState, useEffect, useContext } from 'react';
import logo from './logo.svg';
import './App.css';
import axios from 'axios';

var StoreID = 1;
var Response;
function App() {
  const [ StoreIDGet, setStoreID ] = useState(1);
  useEffect(() => {
    StoreID = StoreIDGet;
  })

  return (
    <div className="App">
      <header className="App-header">
        <h1 className='Project-title'>الفريد ميتال</h1>
      </header>
      <main>
      <div>
        <ul className="Tab-bar">
          <li className="Tab Active-tab" onClick={(event) => ChangeTab(event,"Main-list")}>القائمة الرئيسية</li>
          <li className="Tab" onClick={(event) => ChangeTab(event,"Selling-operations")}>عمليات البيع</li>
          <li className="Tab" onClick={(event) => ChangeTab(event,"Purchase-operations")}>عمليات الشراء</li>
          <li className="Tab" onClick={(event) => ChangeTab(event,"Transition-operations")}>عمليات التحويل</li>
          <li className="Tab" onClick={(event) => ChangeTab(event,"Products-list")}>قائمة المنتجات</li>
          <li className="Tab" onClick={(event) => ChangeTab(event,"Debts-accounts")}>حسابات الديون</li>
        </ul>
      </div>
      <div className="Tab-contents">
        <div className="Tab-content" id="Main-list" >
          
        </div>
        <SellingTabContent></SellingTabContent>
        <div className="Tab-content" id="Purchase-operations" >
          <text>Purchase operations</text>
        </div>
        <div className="Tab-content" id="Transition-operations" ></div>
        <ProductsTabContent></ProductsTabContent>
        <div className="Tab-content" id="Debts-accounts" ></div>
      </div>
      </main>
    </div>
  );
}
var Current_tab_content = "Main-list";
function ChangeTab(event,Target_tab_content){
  document.getElementsByClassName("Active-tab")[0].classList.remove("Active-tab");
  document.getElementById(Current_tab_content).style.display = "none";
  document.getElementById(Target_tab_content).style.display = "inline-flex";
  event.target.classList.add("Active-tab");
  Current_tab_content = Target_tab_content;

}

function SellingTabContent(){
  return(
    <div className="Tab-content" id="Selling-operations">
      <div className="Table-container">
        <table className="Table" id="Selling-table">
          <tr>
            <th>م</th>
            <th>الرقم التعريفي</th>
            <th>اسم العميل</th>
            <th>الوقت والتاريخ</th>
            <th>المبلغ المطلوب</th>
            <th>المبلغ المدفوع</th>
            <th>المضاف لحساب الدين</th>
          </tr>
          <tr>
            <td>1</td>
            <td>520</td>
          </tr>
          <tr>
            <td>2</td>
            <td>555</td>
          </tr>
        </table>
      </div>
      <div className='Side-bar'>
        <button className="Sidebar-button" onClick={(event) => AddInvoice(event)}>إضافة فاتورة</button>
        <button className="Sidebar-button" onClick={(event) => EditInvoice(event)}>تعديل فاتورة</button>
        <button className="Sidebar-button" onClick={(event) => DeleteInvoice(event)}>حذف فاتورة</button>
        <button className="Sidebar-button">بحث</button>
        <button className="Sidebar-button">طباعة فاتورة</button>
      </div>

    </div>
  );
}
function AddInvoice(event){
  console.log("Add Invoice");
}
function EditInvoice(event){
  console.log("Edit Invoice");
}
function DeleteInvoice(event){
  console.log("Delete Invoice");
}

function ProductsTabContent(){
  const [ ProductID, setProductID ] = useState("");
  const [ ProductName, setProductName ] = useState("");
  const [ Trademark, setTrademark ] = useState("");
  const [ ManufactureCountry, setManufactureCountry ] = useState("");
  const [ PurchasePrice, setPurchasePrice ] = useState("");
  const [ WholesalePrice, setWholesalePrice ] = useState("");
  const [ RetailPrice, setRetailPrice ] = useState("");
  const [ ProductQuantity, setProductQuantity ] = useState("");
  const [ AddedProduct, setAddedProduct ] = useState(true);
  const [Response, setResponse] = useState([]);

  useEffect(() => {
    if (AddedProduct){
      var Request = {RequestType:"SearchProducts", StoreID:StoreID};
      if (ProductID){ Request.ProductID = ProductID; }
      if (ProductName){ Request.ProductName = ProductName; }
      if (Trademark){ Request.Trademark = Trademark; }
      if (ManufactureCountry){ Request.ManufactureCountry = ManufactureCountry; }
      if (PurchasePrice){ Request.PurchasePrice = PurchasePrice; }
      if (WholesalePrice){ Request.WholesalePrice = WholesalePrice; }
      if (RetailPrice){ Request.RetailPrice = RetailPrice; }
      if (ProductQuantity){ Request.ProductQuantity = ProductQuantity; }
      axios.get('http://localhost:8000/apis/v1.0/commercial', {params: Request})
        .then((response)=>{setResponse(response.data)})
        .catch((err)=>{console.log(err)});
      setAddedProduct(false);
    }
  });
  // useEffect(() => {
  //   Request = {RequestType:"SearchProducts", StoreID:StoreID};
  //   if (ProductID){ Request.ProductID = ProductID; }
  //   if (ProductName){ Request.ProductName = ProductName; }
  //   if (Trademark){ Request.Trademark = Trademark; }
  //   if (ManufactureCountry){ Request.ManufactureCountry = ManufactureCountry; }
  //   if (PurchasePrice){ Request.PurchasePrice = PurchasePrice; }
  //   if (WholesalePrice){ Request.WholesalePrice = WholesalePrice; }
  //   if (RetailPrice){ Request.RetailPrice = RetailPrice; }
  //   if (ProductQuantity){ Request.ProductQuantity = ProductQuantity; }

  //   Response = axios.get('http://localhost:8000/apis/v1.0/commercial', {params: Request})
  //     .catch((error) => {console.log(error);});
  //   console.log(Response.data);
  //   //setAddedProduct(false);
  // }, [ProductID, ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, ProductQuantity, AddedProduct]);

  return(
    <div className="Tab-content" id="Products-list">
      <div className="Table-container">
        <table className="Table" id="Products-table">
          <thead>
            <tr>
              <th>م</th>
              <th>الرقم التعريفي</th>
              <th>اسم المنتج</th>
              <th>العلامة التجارية</th>
              <th>بلد التصنيع</th>
              <th>سعر الشراء</th>
              <th>سعر بيع الجملة</th>
              <th>سعر بيع التجزئة</th>
              <th>الكمية</th>
            </tr>
          </thead>
          <tbody>
            <FetchProducts></FetchProducts>
          </tbody>
        </table>
        <AddProductForm></AddProductForm>
      </div>
      <div className='Side-bar'>
        <button className="Sidebar-button" onClick={(event) => ShowAddProductForm(event)}>إضافة منتج</button>
        <button className="Sidebar-button" onClick={(event) => ShowEditProductForm(event)}>تعديل منتج</button>
        <button className="Sidebar-button">بحث</button>
        <button className="Sidebar-button">طباعة المنتجات</button>
      </div>
    </div>
  );
  function FetchProducts(){
    try{
      console.log(Response.Data);
    return Object.keys(Response.Data).map((key, index) => (
      <tr>
        <td>{index + 1}</td>
        <td>{Response.Data[key].Product_ID}</td>
        <td>{Response.Data[key].Product_Name}</td>
        <td>{Response.Data[key].Trademark}</td>
        <td>{Response.Data[key].Manufacture_Country}</td>
        <td>{Response.Data[key].Purchase_Price}</td>
        <td>{Response.Data[key].Wholesale_Price}</td>
        <td>{Response.Data[key].Retail_Price}</td>
        <td>{Response.Data[key].Quantity}</td>
      </tr>
    ))}
    catch{return ""}

  }
  function ShowAddProductForm(event){
    document.getElementById("Add-product-form").style.display = "block";
  }
  function ShowEditProductForm(event){
    console.log("Edit Product");
  }


  function AddProductForm(){

    return(
      <div className="Form-container" id="Add-product-form">
        <div className="Form">
          <div>
            <button className='Form-close' onClick={(event) => CloseForm(event)}>X</button>
          </div>
          <div>
            <label>اسم المنتج</label>
            <input type="text" id="Add-product-name"></input>
          </div>
          <div>
            <label>العلامة التجارية</label>
            <input type="text" id="Add-product-trademark"></input>
          </div>
          <div>
            <label>بلد التصنيع</label>
            <input type="text" id="Add-product-manufacture-country"></input>
          </div>
          <div>
            <label>سعر الشراء</label>
            <input type="number" id="Add-product-purchase-price"></input>
          </div>
          <div>
            <label>سعر بيع الجملة</label>
            <input type="number" id="Add-product-wholesale-price"></input>
          </div>
          <div>
            <label>سعر بيع التجزئة</label>
            <input type="number" id="Add-product-retail-price"></input>
          </div>
          <div>
            <label>عدد الخانات العشرية</label>
            <input type="number" id="Add-product-partial-quantity-precision"></input>
          </div>
          <div>
            <button onClick={(event) => AddProduct(event)}>إضافة</button>
          </div>
        </div>
      </div>
    );
    function AddProduct(event){
      Request = {RequestType:"AddProduct", StoreID:StoreID,
        ProductName:document.getElementById("Add-product-name").value,
        Trademark:document.getElementById("Add-product-trademark").value,
        ManufactureCountry:document.getElementById("Add-product-manufacture-country").value,
        PurchasePrice:document.getElementById("Add-product-purchase-price").value,
        WholesalePrice:document.getElementById("Add-product-wholesale-price").value,
        RetailPrice:document.getElementById("Add-product-retail-price").value,
        PartialQuantityPrecision:document.getElementById("Add-product-partial-quantity-precision").value
      };

      
      axios.get('http://localhost:8000/apis/v1.0/commercial', {params: Request},)
        .then()
        .catch((error) => {console.log(error);});
      setAddedProduct(true);
      console.log(AddedProduct);
    
    }
  
    function CloseForm(event){
      document.getElementsByClassName("Form-container")[0].style.display = "none";
    }
  }
}


export default App;
