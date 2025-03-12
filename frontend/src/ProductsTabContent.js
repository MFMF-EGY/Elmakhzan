import { useState, useEffect, useRef, createContext, useContext } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';

const ProductsTabContext = createContext();

function ProductsTabContent({ref}){
  const { ProjectID } = useContext(GlobalContext);
  const { StoreID } = useContext(GlobalContext);
  const [ SearchParam, setSearchParam ] = useState({
    ProductID: "",
    ProductName: "",
    Trademark: "",
    ManufactureCountry: "",
    PurchasePrice: "",
    WholesalePrice: "",
    RetailPrice: "",
    ProductQuantity: ""
  });
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
  }, [UpdateTab, ProjectID, StoreID]);

  const fetchProducts = async () => {
    var RequestParams = {RequestType:"SearchProducts", ProjectID:ProjectID, StoreID:StoreID};
    if (SearchParam.ProductID){ RequestParams.Product_ID = SearchParam.ProductID; }
    if (SearchParam.ProductName){ RequestParams.Product_Name = SearchParam.ProductName; }
    if (SearchParam.Trademark){ RequestParams.Trademark = SearchParam.Trademark; }
    if (SearchParam.ManufactureCountry){ RequestParams.Manufacture_Country = SearchParam.ManufactureCountry; }
    if (SearchParam.PurchasePrice){ RequestParams.Purchase_Price = SearchParam.PurchasePrice; }
    if (SearchParam.WholesalePrice){ RequestParams.Wholesale_Price = SearchParam.WholesalePrice; }
    if (SearchParam.RetailPrice){ RequestParams.Retail_Price = SearchParam.RetailPrice; }
    if (SearchParam.ProductQuantity){ RequestParams.Product_Quantity = SearchParam.ProductQuantity; }
    await axios.get('http://localhost:8000/apis/v1.0/commercial', {params: RequestParams})
      .then(
        (response)=>{
          if (!response.data.StatusCode)
            {setResponse(response.data.Data)}
          else
            {console.log(response.data)}
        })
      .catch((err)=>{console.log(err)});
  }
  return(
    <ProductsTabContext.Provider value={{ SearchParam, setSearchParam, UpdateTab, setUpdateTab, Response, setResponse, OpendForm, setOpendForm, AddProductFormRef,
      EditProductButtonRef, EditProductFormRef, SearchProductsFormRef, PrintProductsFormRef, SelectedRow, setSelectedRow }}>
      <div className="Tab-content" ref={ref}>
        <div className="Table-container">
          <table className="Table" id="Products-table">
            <thead>
              <tr>
                <th>م</th>
                <th>الكود</th>
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
          {OpendForm === "AddProductForm" ? <AddProductForm></AddProductForm> :
           OpendForm === "SearchProductsForm" ? <SearchProductsForm></SearchProductsForm> :
           OpendForm === "EditProductForm" && <EditProductForm></EditProductForm>}
        </div>
        <div className='Side-bar'>
          <button className="Sidebar-button" onClick={(event) => setOpendForm("AddProductForm")}>إضافة منتج</button>
          <button className="Sidebar-button" ref={EditProductButtonRef} 
            onClick={(event) => setOpendForm("EditProductForm")} disabled={SelectedRow?false:true}>تعديل منتج</button>
          <button className="Sidebar-button" onClick={(event) => setOpendForm("SearchProductsForm")}>بحث</button>
          <button className="Sidebar-button">طباعة المنتجات</button>
        </div>
      </div>
    </ProductsTabContext.Provider>
  );
}
function AddProductForm(){
  const { ProjectID, StoreID } = useContext(GlobalContext);
  const { UpdateTab, setUpdateTab, AddProductFormRef } = useContext(ProductsTabContext);
  const AddProductNameRef = useRef();
  const AddProductTrademarkRef = useRef();
  const AddProductManufactureCountryRef = useRef();
  const AddProductPurchasePriceRef = useRef();
  const AddProductWholesalePriceRef = useRef();
  const AddProductRetailPriceRef = useRef();
  const AddProductPartialQuantityPrecisionRef = useRef();

  const AddProduct = (event) => {
    var RequestParams = {RequestType:"AddProduct", ProjectID:ProjectID, StoreID:StoreID,
      ProductName: AddProductNameRef.current.value,
      Trademark: AddProductTrademarkRef.current.value,
      ManufactureCountry: AddProductManufactureCountryRef.current.value,
      PurchasePrice: AddProductPurchasePriceRef.current.value,
      WholesalePrice: AddProductWholesalePriceRef.current.value,
      RetailPrice: AddProductRetailPriceRef.current.value,
      PartialQuantityPrecision: AddProductPartialQuantityPrecisionRef.current.value
    };
    
    axios.get('http://localhost:8000/apis/v1.0/commercial', {params: RequestParams},)
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
          <input type="text" ref={AddProductNameRef}></input>
        </div>
        <div>
          <label>العلامة التجارية</label>
          <input type="text" ref={AddProductTrademarkRef}></input>
        </div>
        <div>
          <label>بلد التصنيع</label>
          <input type="text" ref={AddProductManufactureCountryRef}></input>
        </div>
        <div>
          <label>سعر الشراء</label>
          <input type="number" ref={AddProductPurchasePriceRef}></input>
        </div>
        <div>
          <label>سعر بيع الجملة</label>
          <input type="number" ref={AddProductWholesalePriceRef}></input>
        </div>
        <div>
          <label>سعر بيع التجزئة</label>
          <input type="number" ref={AddProductRetailPriceRef}></input>
        </div>
        <div>
          <label>عدد الخانات العشرية</label>
          <input type="number" ref={AddProductPartialQuantityPrecisionRef}></input>
        </div>
        <div>
          <button onClick={(event) => AddProduct(event)}>إضافة</button>
        </div>
      </div>
    </div>
  );
}

function SearchProductsForm(){
  const { SearchParam, setSearchParam, UpdateTab, setUpdateTab, SearchProductsFormRef } = useContext(ProductsTabContext);
  const SearchProductsIdRef = useRef(null);
  const SearchProductsNameRef = useRef(null);
  const SearchProductsTrademarkRef = useRef(null);
  const SearchProductsManufactureCountryRef = useRef(null);
  const SearchProductsPurchasePriceRef = useRef(null);
  const SearchProductsWholesalePriceRef = useRef(null);
  const SearchProductsRetailPriceRef = useRef(null);
  const SearchProducts = (event) => {
    setSearchParam({
      ProductID: SearchProductsIdRef.current.value,
      ProductName: SearchProductsNameRef.current.value,
      Trademark: SearchProductsTrademarkRef.current.value,
      ManufactureCountry: SearchProductsManufactureCountryRef.current.value,
      PurchasePrice: SearchProductsPurchasePriceRef.current.value,
      WholesalePrice: SearchProductsWholesalePriceRef.current.value,
      RetailPrice: SearchProductsRetailPriceRef.current.value
    });
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
          <input type="text" defaultValue={SearchParam.ProductID} ref={SearchProductsIdRef}></input>
        </div>
        <div>
          <label>اسم المنتج</label>
          <input type="text" defaultValue={SearchParam.ProductName} ref={SearchProductsNameRef}></input>
        </div>
        <div>
          <label>العلامة التجارية</label>
          <input type="text" defaultValue={SearchParam.Trademark} ref={SearchProductsTrademarkRef}></input>
        </div>
        <div>
          <label>بلد التصنيع</label>
          <input type="text" defaultValue={SearchParam.ManufactureCountry} ref={SearchProductsManufactureCountryRef}></input>
        </div>
        <div>
          <label>سعر الشراء</label>
          <input type="number" defaultValue={SearchParam.PurchasePrice} ref={SearchProductsPurchasePriceRef}></input>
        </div>
        <div>
          <label>سعر بيع الجملة</label>
          <input type="number" defaultValue={SearchParam.WholesalePrice} ref={SearchProductsWholesalePriceRef}></input>
        </div>
        <div>
          <label>سعر بيع التجزئة</label>
          <input type="number" defaultValue={SearchParam.RetailPrice} ref={SearchProductsRetailPriceRef}></input>
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
    var RequestParams = {RequestType:"EditProductInfo", StoreID:StoreID,
      ProductID:EditProductID.current.value,
      ProductName:EditProductName.current.value,
      Trademark:EditProductTrademark.current.value,
      ManufactureCountry:EditProductManufactureCountry.current.value,
      PurchasePrice:EditProductPurchasePrice.current.value,
      WholesalePrice:EditProductWholesalePrice.current.value,
      RetailPrice:EditProductRetailPrice.current.value,
      PartialQuantityPrecision:EditProductPartialQuantityPrecision.current.value
    };
    axios.get('http://localhost:8000/apis/v1.0/commercial', {params: RequestParams})
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
      Response.map((product, index) => (
        <tr onClick={(event)=>{
          if (SelectedRow){SelectedRow.classList.remove("Selected-row");}
          setSelectedRow(event.currentTarget);
        }}>
          <td>{index + 1}</td>
          <td>{product.Product_ID}</td>
          <td>{product.Product_Name}</td>
          <td>{product.Trademark}</td>
          <td>{product.Manufacture_Country}</td>
          <td>{product.Purchase_Price}</td>
          <td>{product.Wholesale_Price}</td>
          <td>{product.Retail_Price}</td>
          <td>{product.Quantity}</td>
        </tr>
      ))
    )
  }catch{return ""}

}
export default ProductsTabContent;
      