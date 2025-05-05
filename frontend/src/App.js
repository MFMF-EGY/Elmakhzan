import React, { useState, useEffect, useRef, createContext, useContext, useCallback, use } from 'react';
import './App.css';
import axios from 'axios';
import MainTableTabContent from './MainTableTabContent.js';
import ProductsTabContent from './ProductsTabContent.js';
import SellingTabContent from './SellingTabContent.js';
import PurchaseTabContent from './PurchaseTabContent.js';
import TransitionTabContent from './TransitionTabContent.js';
import DebtsAccountsTabContent from './DebtsAccountsTabContent.js';
import QuantityAdjustmentsTabContent from './QuantityAdjustmentsTabContent.js';

export const API_URL = 'http://0.0.0.0:8000/apis/v1.0/commercial';
export const GlobalContext = createContext();
const FormsContext = createContext();

function App() {
  const [ ProjectID, setProjectID] = useState(null);
  const [ StoreID, setStoreID ] = useState(null);
  const [ FormSelector, setFormSelector] = useState(null);
  const [ ProjectStoreChanged, setProjectStoreChanged ] = useState(false);
  const MainTableTabContentRef = useRef();
  const SellingTabContentRef = useRef();
  const PurchaseTabContentRef = useRef();
  const TransitionTabContentRef = useRef();
  const ProductsTabContentRef = useRef();
  const DebtsAccountsTabContentRef = useRef();
  const QuantityAdjustmentsTabContentRef = useRef();
  const CurrentTabContent = useRef(MainTableTabContentRef);

  useEffect(() => {
    CurrentTabContent.current = MainTableTabContentRef;
  }, [ProjectID, StoreID]);

  const changeTab = (event, TargetTabContent) => {
    document.getElementsByClassName("Active-tab")[0].classList.remove("Active-tab");
    CurrentTabContent.current.current.style.display = "none";
    TargetTabContent.current.style.display = "inline-flex";
    event.target.classList.add("Active-tab");
    CurrentTabContent.current = TargetTabContent;
  }

  return (
    <GlobalContext.Provider value={{ StoreID, setStoreID, ProjectID, setProjectID }}>
      <div className="App">
        <header className="App-header">
          <ProjectStoreSelect value={ProjectStoreChanged} GlobalContext={{ProjectID, setProjectID, StoreID, setStoreID}} setFormSelector={setFormSelector}/>
        </header>
        <main>
        { (ProjectID && StoreID) &&
          <>
            <div>
              <ul className="Tab-bar">
                <li className="Tab Active-tab" onClick={(event) => changeTab(event,MainTableTabContentRef)}>القائمة الرئيسية</li>
                <li className="Tab" onClick={(event) => changeTab(event,SellingTabContentRef)}>فواتير البيع</li>
                <li className="Tab" onClick={(event) => changeTab(event,PurchaseTabContentRef)}>فواتير الشراء</li>
                <li className="Tab" onClick={(event) => changeTab(event,TransitionTabContentRef)}>مستندات التحويل</li>
                <li className="Tab" onClick={(event) => changeTab(event,ProductsTabContentRef)}>قائمة المنتجات</li>
                <li className="Tab" onClick={(event) => changeTab(event,DebtsAccountsTabContentRef)}>حسابات الديون</li>
                <li className="Tab" onClick={(event) => changeTab(event,QuantityAdjustmentsTabContentRef)}>تعديل الكميات</li>
              </ul>
            </div>
            <div className="Tab-contents">
              <MainTableTabContent ref={MainTableTabContentRef}/>
              <SellingTabContent ref={SellingTabContentRef}/>
              <PurchaseTabContent ref={PurchaseTabContentRef}/>
              <TransitionTabContent ref={TransitionTabContentRef}/>
              <ProductsTabContent ref={ProductsTabContentRef}/>
              <DebtsAccountsTabContent ref={DebtsAccountsTabContentRef}/>
              <QuantityAdjustmentsTabContent ref={QuantityAdjustmentsTabContentRef}/>
            </div>
            <div className="Form-container" ></div>
          </>
        }
        <FormsContext.Provider value={{FormSelector, setFormSelector, ProjectStoreChanged, setProjectStoreChanged}}>
          { (FormSelector === "CreateProjectForm") && <CreateProjectForm/> }
          { (FormSelector === "CreateStoreForm") && <CreateStoreForm/> }
        </FormsContext.Provider>
        </main>
      </div>
    </GlobalContext.Provider>
  );
}


const ProjectStoreSelect = React.memo(({value, GlobalContext, setFormSelector}) =>{
  const { ProjectID, setProjectID } = GlobalContext
  const { StoreID, setStoreID } = GlobalContext;
  const [projects, setProjects] = useState([]);
  const [stores, setStores] = useState([]);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await axios.get(API_URL + '?RequestType=GetProjects');
        if (!response.data.StatusCode) {
          setProjects(response.data.Data);
        }
      } catch (error) {
        console.log(error);
      }
    };
    fetchProjects();
  }, [value]);

  useEffect(() => {
    fetchStores();
  }, [value, ProjectID]);

  const fetchStores = async () => {
    if (ProjectID) {
      try {
        const response = await axios.get(API_URL + "?RequestType=GetStores&ProjectID="+ProjectID);
        if (!response.data.StatusCode) {
          setStores(response.data.Data);
        }
      } catch (error) {
        console.log(error);
      }
    }
  };
  
  const selectProject = (event) => {
    setProjectID(event.target.value);
    setStoreID(null);
  }
  
  return(
    <div>
      <select id="Project-select" defaultValue={""} onChange={(event) => {selectProject(event)}}>
        <option value="" disabled hidden>اختر مشروع</option>
        {projects.map((project) => (
          <option key={project.Project_ID} value={project.Project_ID}>{project.Project_Name}</option>
        ))}
      </select>
      <button onClick={(event) => {setFormSelector("CreateProjectForm")}}>إنشاء مشروع</button>
      { ProjectID && (
        <>
        <select id="Store-select" value={StoreID ? StoreID : ""} onChange={(event) => {setStoreID(event.target.value)}}>
          <option value="" disabled hidden>اختر مخزن</option>
          {stores.map((store) => (
            <option key={store.Store_ID} value={store.Store_ID}>{store.Store_Name}</option>
          ))}
        </select>
        <button onClick={(event) => {setFormSelector("CreateStoreForm")}}>أضف مخزن</button>
        </>
      )}
      
    </div>
  );
}, (prevProps, nextProps) => prevProps.value === nextProps.value && prevProps.GlobalContext === nextProps.GlobalContext);

function CreateProjectForm(){
  const { setFormSelector } = useContext(FormsContext);
  const { ProjectStoreChanged, setProjectStoreChanged } = useContext(FormsContext);
  const { ProjectID, setProjectID } = useContext(GlobalContext);
  const ProjectNameRef = useRef();
  const ProjectDescriptionRef = useRef()
  const createProject = async (event) => {
    var RequestParms = {
      RequestType: "CreateProject",
      ProjectName: ProjectNameRef.current.value,
      ProjectDescription: ProjectDescriptionRef.current.value
    }
    await axios.get(API_URL,{params: RequestParms})
    .then(() => {
      setFormSelector("");
      setProjectStoreChanged(!ProjectStoreChanged);
    })
    .catch((error) => console.log(error))
  }
  return(
    <div className='Form-container'>
      <div className="Form">
        <div>
          <button className="Form-close" onClick={(event) => setFormSelector("")}>X</button>
        </div>
        <div>
          <label>اسم المشروع</label>
          <input type="text" ref={ProjectNameRef}></input>
        </div>
        <div>
          <label>الوصف</label>
          <input type="text" ref={ProjectDescriptionRef}></input>
        </div>
        <div>
          <button onClick={(event) => createProject(event)}>إنشاء</button>
        </div>
      </div>
    </div>
  );
}

function CreateStoreForm(){
  const { setFormSelector } = useContext(FormsContext);
  const { ProjectStoreChanged, setProjectStoreChanged } = useContext(FormsContext);
  const { ProjectID, setProjectID } = useContext(GlobalContext);
  const StoreNameRef = useRef();
  const StoreAddressRef = useRef()
  const addStore = async (event) => {
    var RequestParms = {
      RequestType: "AddStore",
      ProjectID: ProjectID,
      StoreName: StoreNameRef.current.value,
      StoreAddress: StoreAddressRef.current.value
    }
    await axios.get(API_URL,{params: RequestParms})
    .then((response) => {
      if (!response.data.StatusCode){
        setFormSelector("");
        setProjectStoreChanged(!ProjectStoreChanged);
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
          <button className="Form-close" onClick={(event) => setFormSelector("")}>X</button>
        </div>
        <div>
          <label>اسم المخزن</label>
          <input type="text" ref={StoreNameRef}></input>
        </div>
        <div>
          <label>العنوان</label>
          <input type="text" ref={StoreAddressRef}></input>
        </div>
        <div>
          <button onClick={(event) => addStore(event)}>إنشاء</button>
        </div>
      </div>
    </div>
  );
}
export default App;
