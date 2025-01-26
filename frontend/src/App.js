import logo from './logo.svg';
import './App.css';
import axios from 'axios';



function App() {
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
  return(
    <div className="Tab-content" id="Products-list">
      <div className="Table-container">
        <table className="Table" id="Products-table">
          <tr>
            <th>م</th>
            <th>الرقم التعريفي</th>
            <th>اسم المنتج</th>
            <th>الكمية</th>
            <th>السعر</th>
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
        <button className="Sidebar-button" onClick={(event) => AddProduct(event)}>إضافة منتج</button>
        <button className="Sidebar-button" onClick={(event) => EditProduct(event)}>تعديل منتج</button>
        <button className="Sidebar-button" onClick={(event) => DeleteProduct(event)}>حذف منتج</button>
        <button className="Sidebar-button">بحث</button>
        <button className="Sidebar-button">طباعة المنتجات</button>
      </div>
    </div>
  );
  function LoadProducts(event){
    axios.get('http://localhost:8000/apis/v1.0/commercial', {params:{RequestType:"GetProductInfo",ProductID:12}},
    ).then((response) => {console.log(response.data);}).catch((error) => {console.log(error);});
  }
  function AddProduct(event){
    console.log("Add Product");
  }
  function EditProduct(event){
    console.log("Edit Product");
  }
  function DeleteProduct(event){
    console.log("Delete Product");
  }
}
export default App;
