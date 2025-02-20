import { useState, useEffect, useRef, createContext, useContext } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';

const ProductsTabContext = createContext();

function ProductsTabContent(){
  const { StoreID } = useContext(GlobalContext);
  const [ ProductID, setProductID ] = useState("");
  const [ ProductName, setProductName ] = useState("");
  const [ Trademark, setTrademark ] = useState("");
  const [ ManufactureCountry, setManufactureCountry ] = useState("");
  const [ PurchasePrice, setPurchasePrice ] = useState("");
  const [ WholesalePrice, setWholesalePrice ] = useState("");
  const [ RetailPrice, setRetailPrice ] = useState("");
  const [ ProductQuantity, setProductQuantity ] = useState("");
  const [ UpdateTab, setUpdateTab ] = useState(0);
  const [ Response, setResponse] = useState([]);

  const [ OpendForm, setOpendForm ] = useState(null);
  const AddProductFormRef = useRef(null);
  const EditProductButtonRef = useRef(null);
  const EditProductFormRef = useRef(null);
  const SearchProductsFormRef = useRef(null);
  const PrintProductsFormRef = useRef(null);

  const [SelectedRow, setSelectedRow] = useState(null);
  

  useEffect(() => {
    if (SelectedRow){SelectedRow.classList.remove("Selected-row");}
    setSelectedRow(null);
    setOpendForm(null); 
    fetchProducts();
  }, [UpdateTab]);
  useEffect(() => {
    if (OpendForm){OpendForm.current.style.display = "block";}
  });
  const fetchProducts = () => {
    var Request = {RequestType:"SearchProducts", StoreID:StoreID};
    if (ProductID){ Request.Product_ID = ProductID; }
    if (ProductName){ Request.Product_Name = ProductName; }
    if (Trademark){ Request.Trademark = Trademark; }
    if (ManufactureCountry){ Request.Manufacture_Country = ManufactureCountry; }
    if (PurchasePrice){ Request.Purchase_Price = PurchasePrice; }
    if (WholesalePrice){ Request.Wholesale_Price = WholesalePrice; }
    if (RetailPrice){ Request.Retail_Price = RetailPrice; }
    if (ProductQuantity){ Request.Product_Quantity = ProductQuantity; }
    axios.get('http://localhost:8000/apis/v1.0/commercial', {params: Request})
      .then((response)=>{setResponse(response.data)})
      .catch((err)=>{console.log(err)});
  }
  return(
    <ProductsTabContext.Provider value={{ ProductID, setProductID, ProductName, setProductName, Trademark, setTrademark, ManufactureCountry,
      setManufactureCountry, PurchasePrice, setPurchasePrice, WholesalePrice, setWholesalePrice, RetailPrice, setRetailPrice,
      ProductQuantity, setProductQuantity, UpdateTab, setUpdateTab, Response, setResponse, OpendForm, setOpendForm, AddProductFormRef,
      EditProductButtonRef, EditProductFormRef, SearchProductsFormRef, PrintProductsFormRef, SelectedRow, setSelectedRow }}>
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
              <ProductsTableBody/>
            </tbody>
          </table>
          <AddProductForm></AddProductForm>
          <SearchProductsForm></SearchProductsForm>
          <EditProductForm></EditProductForm>
        </div>
        <div className='Side-bar'>
          <button className="Sidebar-button" onClick={(event) => setOpendForm(AddProductFormRef)}>إضافة منتج</button>
          <button className="Sidebar-button" ref={EditProductButtonRef} 
            onClick={(event) => setOpendForm(EditProductFormRef)} disabled={SelectedRow?false:true}>تعديل منتج</button>
          <button className="Sidebar-button" onClick={(event) => setOpendForm(SearchProductsFormRef)}>بحث</button>
          <button className="Sidebar-button">طباعة المنتجات</button>
        </div>
      </div>
    </ProductsTabContext.Provider>
  );
}
function AddProductForm(){
  const { StoreID, UpdateTab, setUpdateTab, AddProductFormRef } = useContext(ProductsTabContext);
  const AddProduct = (event) => {
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
      .then((response)=>{
        if (!response.data.StatusCode){
          setUpdateTab(UpdateTab + 1);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => {console.log(error);});
  
  }
  return(
    <div className="Form-container" id="Add-product-form" ref={AddProductFormRef}>
      <div className="Form">
        <div>
          <button className='Form-close' onClick={(event) => {AddProductFormRef.current.style.display = "none";}}>X</button>
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
}

function SearchProductsForm(){
  const { ProductID, setProductID, ProductName, setProductName, Trademark, setTrademark,
    ManufactureCountry, setManufactureCountry, PurchasePrice, setPurchasePrice, WholesalePrice, setWholesalePrice,
    RetailPrice, setRetailPrice, UpdateTab, setUpdateTab, SearchProductsFormRef } = useContext(ProductsTabContext);
  const SearchProductsIdRef = useRef(null);
  const SearchProductsNameRef = useRef(null);
  const SearchProductsTrademarkRef = useRef(null);
  const SearchProductsManufactureCountryRef = useRef(null);
  const SearchProductsPurchasePriceRef = useRef(null);
  const SearchProductsWholesalePriceRef = useRef(null);
  const SearchProductsRetailPriceRef = useRef(null);
  const SearchProducts = (event) => {
    setProductID(SearchProductsIdRef.current.value);
    setProductName(SearchProductsNameRef.current.value);
    setTrademark(SearchProductsTrademarkRef.current.value);
    setManufactureCountry(SearchProductsManufactureCountryRef.current.value);
    setPurchasePrice(SearchProductsPurchasePriceRef.current.value);
    setWholesalePrice(SearchProductsWholesalePriceRef.current.value);
    setRetailPrice(SearchProductsRetailPriceRef.current.value);
    setUpdateTab(UpdateTab + 1);
  }
  return(
    <div className="Form-container" ref={SearchProductsFormRef}>
      <div className="Form">
        <div>
          <button className='Form-close' onClick={(event) => {SearchProductsFormRef.current.style.display = "none";}}>X</button>
        </div>
        <div>
          <label>الرقم التعريفي</label>
          <input type="text" defaultValue={ProductID} ref={SearchProductsIdRef}></input>
        </div>
        <div>
          <label>اسم المنتج</label>
          <input type="text" defaultValue={ProductName} ref={SearchProductsNameRef}></input>
        </div>
        <div>
          <label>العلامة التجارية</label>
          <input type="text" defaultValue={Trademark} ref={SearchProductsTrademarkRef}></input>
        </div>
        <div>
          <label>بلد التصنيع</label>
          <input type="text" defaultValue={ManufactureCountry} ref={SearchProductsManufactureCountryRef}></input>
        </div>
        <div>
          <label>سعر الشراء</label>
          <input type="number" defaultValue={PurchasePrice} ref={SearchProductsPurchasePriceRef}></input>
        </div>
        <div>
          <label>سعر بيع الجملة</label>
          <input type="number" defaultValue={WholesalePrice} ref={SearchProductsWholesalePriceRef}></input>
        </div>
        <div>
          <label>سعر بيع التجزئة</label>
          <input type="number" defaultValue={RetailPrice} ref={SearchProductsRetailPriceRef}></input>
        </div>
        <div>
          <button onClick={(event) => SearchProducts(event)}>ابحث</button>
        </div>
      </div>
    </div>
  );
}

function EditProductForm(){
  const { StoreID, UpdateTab, setUpdateTab, Response, SelectedRow, EditProductFormRef } = useContext(ProductsTabContext);
  const EditProductID = useRef(null);
  const EditProductName = useRef(null);
  const EditProductTrademark = useRef(null);
  const EditProductManufactureCountry = useRef(null);
  const EditProductPurchasePrice = useRef(null);
  const EditProductWholesalePrice = useRef(null);
  const EditProductRetailPrice = useRef(null);
  const EditProductPartialQuantityPrecision = useRef(null);
  const EditProduct = (event) => {
    Request = {RequestType:"EditProductInfo", StoreID:StoreID,
      ProductID:EditProductID.current.value,
      ProductName:EditProductName.current.value,
      Trademark:EditProductTrademark.current.value,
      ManufactureCountry:EditProductManufactureCountry.current.value,
      PurchasePrice:EditProductPurchasePrice.current.value,
      WholesalePrice:EditProductWholesalePrice.current.value,
      RetailPrice:EditProductRetailPrice.current.value,
      PartialQuantityPrecision:EditProductPartialQuantityPrecision.current.value
    };
    axios.get('http://localhost:8000/apis/v1.0/commercial', {params: Request})
      .then((response)=>{
        if (!response.data.StatusCode){
          setUpdateTab(UpdateTab + 1);
        }else{
          console.log(response.data);
        }
      })
      .catch((error) => {console.log(error);});
  }

  useEffect(() => {
    if (SelectedRow){
      EditProductID.current.value = Response.Data[SelectedRow.rowIndex - 1].Product_ID;
      EditProductName.current.value = Response.Data[SelectedRow.rowIndex - 1].Product_Name;
      EditProductTrademark.current.value = Response.Data[SelectedRow.rowIndex - 1].Trademark;
      EditProductManufactureCountry.current.value = Response.Data[SelectedRow.rowIndex - 1].Manufacture_Country;
      EditProductPurchasePrice.current.value = Response.Data[SelectedRow.rowIndex - 1].Purchase_Price;
      EditProductWholesalePrice.current.value = Response.Data[SelectedRow.rowIndex - 1].Wholesale_Price;
      EditProductRetailPrice.current.value = Response.Data[SelectedRow.rowIndex - 1].Retail_Price;
      EditProductPartialQuantityPrecision.current.value = Response.Data[SelectedRow.rowIndex - 1].Partial_Quantity_Precision;
    }
  })

  return(
    <div className="Form-container" ref={EditProductFormRef}>
      <div className="Form">
        <div>
          <button className='Form-close' onClick={(event) => {EditProductFormRef.current.style.display = "none";}}>X</button>
        </div>
        <div>
          <label>الرقم التعريفي</label>
          <input type="text" ref={EditProductID} />
        </div>
        <div>
          <label>اسم المنتج</label>
          <input type="text" ref={EditProductName} />
        </div>
        <div>
          <label>العلامة التجارية</label>
          <input type="text" ref={EditProductTrademark} />
        </div>
        <div>
          <label>بلد التصنيع</label>
          <input type="text" ref={EditProductManufactureCountry} />
        </div>
        <div>
          <label>سعر الشراء</label>
          <input type="number" ref={EditProductPurchasePrice} />
        </div>
        <div>
          <label>سعر بيع الجملة</label>
          <input type="number" ref={EditProductWholesalePrice} />
        </div>
        <div>
          <label>سعر بيع التجزئة</label>
          <input type="number" ref={EditProductRetailPrice} />
        </div>
        <div>
          <label>عدد الخانات العشرية</label>
          <input type="number" ref={EditProductPartialQuantityPrecision} />
        </div>
        <div>
          <button onClick={(event) => EditProduct(event)}>تعديل</button>
        </div>
      </div>
    </div>
  );
}


function ProductsTableBody(){
  const { Response, SelectedRow, setSelectedRow } = useContext(ProductsTabContext);
  useEffect(() => {
    if (SelectedRow){SelectedRow.classList.add("Selected-row")};
  })
  try{
    return (
      Object.keys(Response.Data).map((key, index) => (
        <tr onClick={(event)=>{
          if (SelectedRow){SelectedRow.classList.remove("Selected-row");}
          setSelectedRow(event.currentTarget);
        }}>
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
      ))
    )
  }catch{return ""}

}
export default ProductsTabContent;
      