import { useState, useEffect, useRef, createContext, useContext } from 'react';
import axios from 'axios';
import { GlobalContext } from './App.js';

const SellingTabContext = createContext();

function SellingTabContent({ref}){
  useEffect(() => {

  })
  const addInvoice = (event) => {
    event.preventDefault();
    console.log('Add Invoice');
  }
  const editInvoice = (event) => {
    event.preventDefault();
    console.log('Edit Invoice');
  }
  const deleteInvoice = (event) => {
    event.preventDefault();
    console.log('Delete Invoice');
  }
  return(
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
      </table>
    </div>
    <div className='Side-bar'>
      <button className="Sidebar-button" onClick={(event) => addInvoice(event)}>إضافة فاتورة</button>
      <button className="Sidebar-button" onClick={(event) => editInvoice(event)}>تعديل فاتورة</button>
      <button className="Sidebar-button" onClick={(event) => deleteInvoice(event)}>حذف فاتورة</button>
      <button className="Sidebar-button">بحث</button>
      <button className="Sidebar-button">طباعة فاتورة</button>
    </div>

    </div>
  );
}

export default SellingTabContent;