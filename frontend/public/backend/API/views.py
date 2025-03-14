from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

import sys
import json
import enum
import mysql.connector
from datetime import datetime
from decimal import Decimal

ProjectDBConnector = mysql.connector.connect(
    host="localhost",
    user="root",
    password="000600",
    database="Elfarid_Metal",
    ssl_disabled= True,
    collation="utf8mb4_unicode_ci", charset="utf8mb4"
)
global Cursor
global GeneratedSql
global StoreID
Cursor = ProjectDBConnector.cursor(dictionary=True)
GeneratedSql = ""
StoreID = 0
class ErrorCodes:
    InvalidDataType = 1
    MissingVariables = 2
    EmptyValue = 3
    InvalidValue = 4
    DuplicateValue = 5
    ValueNotFound = 6
    InsufficientQuantity = 7
    ExcessQuantity = 8
    UnregisteredStore = 9
    UnregisteredProduct = 10
    UnregisteredPerson = 11
    InvalidPrecision = 12
    InvalidFilter = 13
#TODO: Enhance error handling
def isintstr(value):
    try:
        int(value)
        return True
    except:
        return False

class ProcessRequest:

    def CreateAccount(RequestList):
        PersonName = RequestList["PersonName"]
        Cursor.execute(f"INSERT INTO Accounts(Name) VALUES ('{PersonName}');")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}

    def AddStore(RequestList):
        StoreName = RequestList["StoreName"]
        Cursor.execute("Select Product_ID from Products_Table;\n")
        ProductsIDs = Cursor.fetchall()
        Cursor.execute(f"INSERT INTO Stores_Table(Store_Name) VALUES ('{StoreName}');\n")
        for ProductID in ProductsIDs:
            Cursor.execute(f"INSERT INTO Product_Quantity_Table VALUES (LAST_INSERT_ID(),'{ProductID["Product_ID"]}',0);\n")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}

    def AddProduct(RequestList):
        ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, PartialQuantityPrecision = (
            RequestList["ProductName"], RequestList["Trademark"],
            RequestList["ManufactureCountry"], RequestList["PurchasePrice"], RequestList["WholesalePrice"],
            RequestList["RetailPrice"], RequestList["PartialQuantityPrecision"])
        #Check if Product already exist with the same trademark
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_Name='{ProductName}' AND Trademark='{Trademark}';")
        if Cursor.fetchone():
            return {"StatusCode":ErrorCodes.DuplicateValue,"Data":""}
        Cursor.execute(f"SELECT Store_ID from Stores_Table;")
        StoresIDs = Cursor.fetchall()
        Cursor.execute(
            f"INSERT INTO Products_Table(Product_Name,Trademark,Manufacture_Country,Purchase_Price,Wholesale_Price,"
            f"Retail_Price,Partial_Quantity_Precision) VALUES ('{ProductName}','{Trademark}','{ManufactureCountry}',{PurchasePrice},{WholesalePrice},"
            f"{RetailPrice},{PartialQuantityPrecision});")
        for StoreID in StoresIDs:
            Cursor.execute(f"INSERT INTO Product_Quantity_Table(Store_ID,Product_ID,Quantity) VALUES ({StoreID["Store_ID"]},LAST_INSERT_ID(),0)")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def EditProductInfo(RequestList):
        ProductID, ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, PartialQuantityPrecision = (
            RequestList["ProductID"], RequestList["ProductName"], RequestList["Trademark"],
            RequestList["ManufactureCountry"], RequestList["PurchasePrice"], RequestList["WholesalePrice"],
            RequestList["RetailPrice"], RequestList["PartialQuantityPrecision"])
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_ID={ProductID};")
        if Cursor.fetchone() is None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        Cursor.execute(
            f"UPDATE Products_Table SET Product_Name = '{ProductName}', Trademark = '{Trademark}', "
            f"Manufacture_Country = '{ManufactureCountry}', Purchase_Price={PurchasePrice}, Wholesale_Price="
            f"{WholesalePrice}, Retail_Price={RetailPrice}, Partial_Quantity_Precision={PartialQuantityPrecision} WHERE Product_ID={ProductID} ")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def GetProductInfo(RequestList):
        ProductID = RequestList['ProductID']
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_ID={ProductID};")
        ProductInfo = Cursor.fetchone()
        if ProductInfo is None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        Cursor.execute("SELECT Store_ID,Quantity FROM Product_Quantity_Table;")
        ProductQuantities = Cursor.fetchall()
        ProductInfo["Product_Quantity_Table"] = ProductQuantities
        return {"StatusCode":0,"Data":ProductInfo}
    def Sell(RequestList):
        StoreID = RequestList["StoreID"]
        ClientID = RequestList["ClientID"]
        Orders = RequestList["Orders"]
        Paid = RequestList["Paid"]
        TotalPrice = Decimal()
        DuplicationChecker = {}
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.UnregisteredPerson,"Data":""}
        # For every ordered product check if product exist, has sufficient quantity, and inserted once
        for Order in Orders:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Order['ProductID']} AND Store_ID={StoreID}")
            ExistingQuantity = Cursor.fetchone()
            if ExistingQuantity is None:
                return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            elif ExistingQuantity["Quantity"] < Order["Quantity"]:
                return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Order['ProductID']}
            if Order["ProductID"] in DuplicationChecker:
                return {"StatusCode":ErrorCodes.DuplicateValue,"Data":""}
            else:
                DuplicationChecker[Order["ProductID"]] = 0
            TotalPrice += Order["Price"]
        if RequestList["Paid"]>TotalPrice:
            return {"StatusCode":ErrorCodes.ExcessQuantity,"Data":"Paid amount is more than invoice total price"}
        # TODO: Automatically add the remain to debt account if paid amount is less than total price
        #elif RequestList["Paid"]<TotalPrice:
        #    Amount = TotalPrice - RequestList["Paid"]
        #    ProcessRequest('{"RequestType":"AddToAccount","PersonID":"%s","Description":"CONCAT(\'فاتورة بيع #S-\',@Invoice_ID)","Amount":"%s"}' % (ClientID, Amount))

        Cursor.execute(f"INSERT INTO Selling_Invoices(Store_Id,Client_ID,Total_Price,Paid,Transferred_To_Account) "
                       f"VALUES ('{StoreID}','{ClientID}','{TotalPrice}','{Paid}',{TotalPrice-Paid});")
        Cursor.execute("SET @Invoice_ID = LAST_INSERT_ID();")
        for Order in Orders:
            Cursor.execute(f"INSERT INTO Selling_Items VALUES (@Invoice_ID,'{Order["ProductID"]}','{Order["Quantity"]}','{Order["Price"]}');\n")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Order['Quantity']} WHERE "
                           f"Store_ID = {StoreID} AND Product_ID = {Order['ProductID']}")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def Purchase(RequestList):
        StoreID = RequestList["StoreID"]
        SellerID = RequestList["SellerID"]
        Orders = RequestList["Orders"]
        Paid = RequestList["Paid"]
        TotalPrice = Decimal()
        DuplicationChecker = {}
        Cursor.execute(f"SELECT Person_ID FROM Debt_Accounts WHERE Person_ID = {SellerID}")
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.UnregisteredPerson,"Data":""}
        # For every ordered product check if product exist, and inserted once
        for Order in Orders:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Order['ProductID']} AND Store_ID={StoreID}")
            ExistingQuantity = Cursor.fetchone()
            if ExistingQuantity is None:
                return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            if Order["ProductID"] in DuplicationChecker:
                return {"StatusCode":ErrorCodes.DuplicateValue,"Data":""}
            else:
                DuplicationChecker[Order["ProductID"]] = 0
            TotalPrice += Order["Price"]
        if RequestList["Paid"]>TotalPrice:
            return {"StatusCode":ErrorCodes.ExcessQuantity,"Data":"Paid amount is more than invoice total price"}
        # TODO: Automatically subtract the remain from debt account if paid amount is less than total price
        #elif RequestList["Paid"]<TotalPrice:
        #    Amount = TotalPrice - RequestList["Paid"]
        #    ProcessRequest('{"RequestType":"AddToAccount","PersonID":"%s","Description":"CONCAT(\'فاتورة بيع #S-\',@Invoice_ID)","Amount":"%s"}' % (ClientID, Amount))
        Cursor.execute(f"INSERT INTO Purchase_Invoices(Store_Id,Seller_ID,Total_Price,Paid,Subtracted_From_Account) VALUES ('{StoreID}','{SellerID}','{TotalPrice}',{Paid},{TotalPrice-Paid});")
        Cursor.execute("SET @Invoice_ID = LAST_INSERT_ID();")
        for Order in Orders:
            Cursor.execute(
                f"INSERT INTO Purchase_Items VALUES (@Invoice_ID,'{Order["ProductID"]}','{Order["Quantity"]}','{Order["Price"]}');\n")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {Order['Quantity']} WHERE "
                           f"Store_ID = {StoreID} AND Product_ID = {Order['ProductID']}")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def Refund(RequestList):
        StoreID = RequestList["StoreID"]
        ClientID = RequestList["ClientID"]
        Orders = RequestList["Orders"]
        TotalPrice = Decimal()
        DuplicationChecker = {}
        Cursor.execute(f"SELECT Person_ID FROM Debt_Accounts WHERE Person_ID = {ClientID}")
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.UnregisteredPerson,"Data":""}
        # For every ordered product check if product exist, and inserted once
        for Order in Orders:
            Cursor.execute(
                f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Order['ProductID']} AND Store_ID={StoreID}")
            ExistingQuantity = Cursor.fetchone()
            if ExistingQuantity is None:
                return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            if Order["ProductID"] in DuplicationChecker:
                return {"StatusCode":ErrorCodes.DuplicateValue,"Data":""}
            else:
                DuplicationChecker[Order["ProductID"]] = 0
            TotalPrice += Order["Price"]
        Cursor.execute(
            f"INSERT INTO Refund_Invoices VALUES ('{StoreID}','{ClientID}','{TotalPrice}');")
        Cursor.execute("SET @Invoice_ID = LAST_INSERT_ID();")
        for Order in Orders:
            Cursor.execute(f"INSERT INTO Refund_Items VALUES (@Invoice_ID,'{Order["ProductID"]}','{Order["Quantity"]}','{Order["Price"]}');\n")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {Order['Quantity']} WHERE "
                           f"Store_ID = {StoreID} AND Product_ID = {Order['ProductID']}")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def AddToAccount(RequestList):
        PersonID = RequestList["PersonID"]
        Description = RequestList["Description"]
        Amount = RequestList["Amount"]
        Cursor.execute(f"SELECT Person_ID FROM Debt_Accounts WHERE Person_ID = {PersonID}")
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.UnregisteredPerson,"Data":""}
        Cursor.execute(f"INSERT INTO Accounts_Operations('Person_ID','Description','Required') VALUES ('{PersonID}','{Description}','{Amount}')\n")
        Cursor.execute(f"SET @Old_Balance = (SELECT Balance FROM Accounts WHERE Person_ID = {PersonID});\n")
        Cursor.execute(f"UPDATE Accounts SET Balance = @Old_Balance+{Amount} WHERE Person_ID = {PersonID};\n")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def DeductFromAccount(RequestList):
        PersonID = RequestList["PersonID"]
        Description = RequestList["Description"]
        Amount = RequestList["Amount"]
        Cursor.execute(f"SELECT Person_ID FROM Debt_Accounts WHERE Person_ID = {PersonID}")
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.UnregisteredPerson,"Data":""}
        Cursor.execute(
            f"INSERT INTO Accounts_Operations('Person_ID','Description','Required') VALUES ('{PersonID}','{Description}','{Amount}')\n")
        Cursor.execute(f"SET @Old_Balance = (SELECT Balance FROM Accounts WHERE Person_ID = {PersonID});\n")
        Cursor.execute(f"UPDATE Accounts SET Balance = @Old_Balance-{Amount} WHERE Person_ID = {PersonID};\n")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def Transit(RequestList):
        Products = RequestList["Products"]
        SourceStoreID = RequestList["SourceStoreID"]
        DestinationStoreID = RequestList["DestinationStoreID"]
        for Product in Products:
            Cursor.execute(f"SELECT Quantity FROM Products_Quantity_Table WHERE Product_ID={Product['ProductID']} AND Store_ID={SourceStoreID};")
            ExistingQuantity = Cursor.fetchone()
            if not ExistingQuantity:
                return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            if ExistingQuantity < Product['Quantity']:
                return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Product['ProductID']}
        Cursor.execute(f"INSERT INTO Transition_Documents(Source_Store_ID,Destination_Store_ID) VALUES ('{SourceStoreID}','{DestinationStoreID}');\n")

        for Product in Products:
            Cursor.execute(f"INSERT INTO Transition_Items(Document_ID,Product_ID,Quantity) VALUES ("
                           f"LAST_INSERT_ID(),'{Product['ProductID']}','{Product['Quantity']}');\n")
        return {"StatusCode":0,"Data":"OK"}
    def SearchProducts(RequestList: dict):
        StoreID = RequestList["StoreID"]
        Filters = list(RequestList.keys())
        Filters.remove("RequestType")
        Filters.remove("StoreID")
        Sql = f"SELECT * FROM Products_Table JOIN Product_Quantity_Table ON Products_Table.Product_ID = Product_Quantity_Table.Product_ID AND Product_Quantity_Table.Store_ID = {StoreID} " 
        if Filters:
            Sql += "WHERE "
        for Filter in Filters:
            value = RequestList[Filter]
            Sql += f"{Filter} LIKE '%{value}%' "
        Cursor.execute(Sql)
        return {"StatusCode":0,"Data":Cursor.fetchall()}
    def SearchInvoices(RequestList):
        InvoiceType = RequestList["InvoiceType"]
        StoreID = RequestList["StoreID"]
        Filters = list(RequestList.keys())
        Filters.remove("RequestType")
        Filters.remove("StoreID")
        Sql = f"SELECT * FROM {InvoiceType}_Invoices WHERE Store_ID={StoreID}"
        Filters.remove("InvoiceType")
        if Filters:
            Sql += " AND "
        for Filter in Filters:
            key = list(Filter.keys())[0]
            value = Filter[key]
            Sql += f"{key}='{value}'"
        Cursor.execute(Sql)
        Response = str(Cursor.fetchall())
        return {"StatusCode":0,"Data":Response}
    def SearchTransitionDocuments(RequestList):
        InvoiceType = RequestList["InvoiceType"]
        StoreID = RequestList["StoreID"]
        Filters = list(RequestList.keys())
        Filters.remove("RequestType")
        Filters.remove("StoreID")
        Sql = f"SELECT * FROM Transition_Documents WHERE Source_Store_ID={StoreID} OR Destination_Store_ID={StoreID} "
        if Filters:
            Sql += "AND "
        for Filter in Filters:
            key = list(Filter.keys())[0]
            value = Filter[key]
            Sql += f"{key}='{value}'"
        Cursor.execute(Sql)
        Response = str(Cursor.fetchall())
        return {"StatusCode":0,"Data":Response}
    def GetInvoiceItems(RequestList):
        #TODO: Add StoreID
        InvoiceType = RequestList["InvoiceType"]
        InvoiceID = RequestList["InvoiceID"]
        Cursor.execute(f"SELECT * FROM {InvoiceType}_Items WHERE Invoice_ID={InvoiceID};")
        return {"StatusCode":0,"Data":Cursor.fetchall()}
    def GetTransitionDocumentItems(RequestList):
        DocumentID = RequestList["DocumentID"]
        Cursor.execute(f"SELECT * FROM Transition_Items WHERE Invoice_ID={DocumentID};")
        return {"StatusCode":0,"Data":Cursor.fetchall()}
    def AdjustProductQuantity(RequestList):
        StoreID, ProductID, CurrentQuantity, Notes = (
            RequestList["StoreID"], RequestList["ProductID"], RequestList["CurrentQuantity"], RequestList["Notes"])
        Cursor.execute(f"SELECT * FROM Stores_Table WHERE Store_ID={StoreID};")
        if Cursor.fetchone() is None: return {"StatusCode":ErrorCodes.UnregisteredStore,"Data":""}
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_ID={ProductID};")
        if Cursor.fetchone() is None: return {"StatusCode":ErrorCodes.UnregisteredProduct,"Data":""}
        Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Store_ID={StoreID} AND Product_ID={ProductID};")
        PreviousQuantity = Cursor.fetchone()['Quantity']
        Cursor.execute(f"INSERT INTO Products_Quantity_Adjustments(Store_ID,Product_ID,Previous_Quantity,"
                       f"Current_Quantity,Notes) VALUES ({StoreID},{ProductID},{PreviousQuantity},{CurrentQuantity},"
                       f"'{Notes}');")
        Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity={CurrentQuantity} WHERE Store_ID={StoreID} AND Product_ID={ProductID};")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}

class SearchFiltersValidation:
    def SellingInvoices(RequestList):
        for Filter in RequestList.keys():
            match Filter:
                case "Invoice_ID" | "Client_ID":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "DateTime":
                    if not isinstance(RequestList[Filter],str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                    if not datetime.strptime(RequestList[Filter],"%y-%m-%d %H-%M-%S"): return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
                case "Total_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Paid":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Transferred_To_Account":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Product_ID":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Product_Name":
                    if not isintstr(RequestList[Filter],str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Quantity":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Selling_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "RequestType" | "InvoiceType" | "StoreID":
                    pass
                case _:
                    return {"StatusCode":ErrorCodes.InvalidFilter,"Data":""}
        return 0
    def PurchaseInvoices(RequestList):
        for Filter in RequestList.keys():
            match Filter:
                case "Invoice_ID" | "Seller_ID":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "DateTime":
                    if not isinstance(RequestList[Filter],str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                    if not datetime.strptime(RequestList[Filter],"%y-%m-%d %H-%M-%S"): return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
                case "Total_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Paid":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Transferred_To_Account":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Product_ID":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Product_Name":
                    if not isinstance(RequestList[Filter],str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Quantity":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Purchase_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case _:
                    return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return 0
    def RefundInvoices(RequestList):
        for Filter in RequestList.keys():
            match Filter:
                case "Invoice_ID" | "Client_ID":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "DateTime":
                    if not isinstance(RequestList[Filter],str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                    if not datetime.strptime(RequestList[Filter],"%y-%m-%d %H-%M-%S"): return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
                case "Total_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Paid":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Transferred_To_Account":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Product_ID":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Product_Name":
                    if not isinstance(RequestList[Filter],str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Quantity":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Refund_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case _:
                    return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return 0
    def TransitionDocuments(Filters):
        for Filter in Filters:
            match Filter:
                case "Document_ID" | "Source_Store_ID" | "Destination_Store_ID" | "Product_ID" | "Quantity":
                    if not isintstr(Filters[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "DateTime":
                    if not isinstance(Filters[Filter], str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                    if not datetime.strptime(Filters[Filter], "%y-%m-%d %H-%M-%S"): return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
                case _:
                    return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return 0

ValidHistoryTables = ["Selling_Invoices","Refund_Invoices","Purchase_Invoices","Transition_Documents","Accounts_Operations"]
ValidInvoiceTypes = ["Selling","Refund","Purchase"]
class CheckValidation:
    def __init__(self):
        pass
    def CreateAccount(RequestList):
        try:
            PersonName=RequestList["PersonName"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isinstance(PersonName,str):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(PersonName) == 0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "PersonName"}
        return ProcessRequest.CreateAccount(RequestList)
    def AddStore(RequestList):
        try:
            StoreName=RequestList["StoreName"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isinstance(StoreName,str):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(StoreName)==0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"StoreName"}
        return ProcessRequest.AddStore(RequestList)
    def AddProduct(RequestList):
        try:
            ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, PartialQuantityPrecision =(
                RequestList["ProductName"], RequestList["Trademark"], RequestList["ManufactureCountry"],
                RequestList["PurchasePrice"],RequestList["WholesalePrice"], RequestList["RetailPrice"], RequestList["PartialQuantityPrecision"]
            )
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isinstance(ProductName,str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(Trademark,str):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(ManufactureCountry, str):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(PurchasePrice):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(WholesalePrice):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(RetailPrice):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(ProductName)==0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "ProductName"}
        if len(Trademark)==0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"Trademark"}
        if len(ManufactureCountry)==0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ManufactureCountry"}
        if int(PurchasePrice) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if int(WholesalePrice) < 0:return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if int(RetailPrice) < 0:return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if int(PartialQuantityPrecision) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return ProcessRequest.AddProduct(RequestList)
    def EditProductInfo(RequestList):
        try:
            ProductID, ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, PartialQuantityPrecision = (
                RequestList["ProductID"], RequestList["ProductName"], RequestList["Trademark"],
                RequestList["ManufactureCountry"], RequestList["PurchasePrice"], RequestList["WholesalePrice"],
                RequestList["RetailPrice"], RequestList["PartialQuantityPrecision"]
            )
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(ProductName, str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(Trademark, str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(ManufactureCountry, str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(PurchasePrice): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(WholesalePrice): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(RetailPrice): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(ProductName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ProductName"}
        if len(Trademark) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "Trademark"}
        if len(ManufactureCountry) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "ManufactureCountry"}
        if PurchasePrice < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if WholesalePrice < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if RetailPrice < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if PartialQuantityPrecision < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return ProcessRequest.EditProductInfo(RequestList)
    def GetProductInfo(RequestList):
        try:
            ProductID = RequestList["ProductID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        return ProcessRequest.GetProductInfo(RequestList)

    def Sell(RequestList):
        try:
            StoreID, ClientID, Orders, Paid = (
                RequestList["StoreID"], RequestList["ClientID"], RequestList["Orders"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(ClientID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        try:
            RequestList["Orders"] = json.loads(Orders)
        except:
            return {"StatusCOde":ErrorCodes.InvalidValue,"Data":""}
        if not isinstance(RequestList["Orders"], list): return {"StatusCode": ErrorCodes.InvalidDataType, "Data": ""}
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if Paid < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        for Order in RequestList["Orders"]:
            try:
                ProductID, Quantity, Price = Order["ProductID"], Order["Quantity"], Order["Price"]
            except:
                return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
            if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if not isintstr(Quantity): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if not isintstr(Price): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if Quantity <= 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            if Price < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            Cursor.execute(f"SELECT Partial_Quantity_Precision FROM Products_Table WHERE Product_ID={ProductID};")
            RequiredPrecision = Cursor.fetchone()["Partial_Quantity_Precision"]
            QuantityPrecision = len(str(Quantity)) - str(Quantity).index(".") - 1
            if QuantityPrecision > RequiredPrecision:
                return {"StatusCode":ErrorCodes.InvalidPrecision,"Data":""}
        return ProcessRequest.Sell(RequestList)
    def Purchase(RequestList):
        try:
            StoreID, SellerID, Orders, Paid = (
                RequestList["StoreID"], RequestList["SellerID"], RequestList["Orders"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(SellerID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        try:
            RequestList["Orders"] = json.loads(Orders)
        except:
            return {"StatusCOde":ErrorCodes.InvalidValue,"Data":""}
        if not isinstance(Orders, list): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if Paid < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        for Order in Orders:
            try:
                ProductID, Quantity, Price = Order["ProductID"], Order["Quantity"], Order["Price"]
            except:
                return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
            if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if not isintstr(Quantity): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if not isintstr(Price): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if Quantity <= 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            if Price < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            Cursor.execute(f"SELECT Partial_Quantity_Precision FROM Products_Table WHERE Product_ID={ProductID};")
            RequiredPrecision = Cursor.fetchone()["Partial_Quantity_Precision"]
            QuantityPrecision = len(str(Quantity)) - str(Quantity).index(".") - 1
            if QuantityPrecision > RequiredPrecision:
                return {"StatusCode":ErrorCodes.InvalidPrecision,"Data":""}
        return ProcessRequest.Purchase(RequestList)
    def Refund(RequestList):
        try:
            StoreID, ClientID , Orders = RequestList["StoreID"], RequestList["ClientID"], RequestList["Orders"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(ClientID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(Orders,list): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        for Order in Orders:
            try:
                ProductID, Quantity, Price = Order["ProductID"], Order["Quantity"], Order["Price"]
            except:
                return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
            if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if not isintstr(Quantity,float): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if not isintstr(Price,float): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if Quantity <= 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            if Price<0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            Cursor.execute(f"SELECT Partial_Quantity_Precision FROM Products_Table WHERE Product_ID={ProductID};")
            RequiredPrecision = Cursor.fetchone()["Partial_Quantity_Precision"]
            QuantityPrecision = len(str(Quantity)) - str(Quantity).index(".") - 1
            if QuantityPrecision > RequiredPrecision:
                return {"StatusCode":ErrorCodes.InvalidPrecision,"Data":""}
        return ProcessRequest.Refund(RequestList)

    def AddToAccount(RequestList):
        try:
            PersonID, Description, Amount = RequestList["PersonID"], RequestList["Description"], RequestList["Amount"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(PersonID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(Description,str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(Amount,float): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if PersonID<0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if len(Description)==0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if Amount<=0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return ProcessRequest.AddToAccount(RequestList)
    def DeductFromAccount(RequestList):
        try:
            PersonID, Description, Amount = RequestList["PersonID"], RequestList["Description"], RequestList["Amount"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(PersonID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(Description,str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(Amount,float): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(Description)==0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if Amount <= 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return ProcessRequest.DeductFromAccount(RequestList)
    def Transit(RequestList):
        try:
            SourceStoreID, DestinationStoreID, Products = (RequestList["SourceStoreID"],
                RequestList["DestinationStoreID"], RequestList["Products"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(SourceStoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(DestinationStoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(Products,list): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(Products)==0: return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        for Product in Products:
            if not isinstance(Product,dict): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            try:
                ProductID, Quantity = Product["ProductID"], Product["Quantity"]
            except:
                return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
            if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if not (isintstr(Quantity) or isinstance(Quantity,float)): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
            if Quantity <= 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            Cursor.execute(f"SELECT Partial_Quantity_Precision FROM Products_Table WHERE Product_ID={ProductID};")
            RequiredPrecision = Cursor.fetchone()["Partial_Quantity_Precision"]
            QuantityPrecision = len(str(Quantity)) - str(Quantity).index(".") - 1
            if QuantityPrecision > RequiredPrecision:
                return {"StatusCode":ErrorCodes.InvalidPrecision,"Data":""}
        return ProcessRequest.Transit(RequestList)
    def SearchProducts(RequestList):
        try:
            StoreID = RequestList["StoreID"]
        except:
            return {"StatusCode": ErrorCodes.MissingVariables, "Data": ""}
        if not isintstr(StoreID): return {"StatusCode": ErrorCodes.InvalidDataType, "Data": ""}
        for Filter in RequestList.keys():
            match Filter:
                case "Product_ID" | "Product_Name" | "Trademark" | "Manufacture_Country":
                    if not isinstance(RequestList[Filter],str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Purchase_Price" | "Wholesale_Price" | "Retail_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Partial_Quantity_Precision":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "RequestType" | "StoreID":
                    pass
                case _:
                    return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return ProcessRequest.SearchProducts(RequestList)
    def SearchInvoices(RequestList):
        try:
            InvoiceType, StoreID = RequestList["InvoiceType"], RequestList["StoreID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isinstance(InvoiceType,str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        match InvoiceType:
            case "Selling":
                Error = SearchFiltersValidation.SellingInvoices(RequestList)
            case "Purchase":
                Error = SearchFiltersValidation.PurchaseInvoices(RequestList)
            case "Refund":
                Error = SearchFiltersValidation.RefundInvoices(RequestList)
            case _:
                return {"StatusCode":ErrorCodes.InvalidValue,"Parameter":InvoiceType}
        if Error:
            return Error
        return ProcessRequest.SearchInvoices(RequestList)
    def SearchTransitionDocuments(RequestList):
        try:
            Filters = RequestList["Filters"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isinstance(Filters, dict): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Error = SearchFiltersValidation.TransitionDocuments(Filters)
        if Error:
            return Error
        else:
            return ProcessRequest.SearchTransitionDocuments(RequestList)
    def GetInvoiceItems(RequestList):
        try:
            InvoiceType, InvoiceID = RequestList["InvoiceType"], RequestList["InvoiceID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isinstance(InvoiceType,str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not InvoiceType in ValidInvoiceTypes: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return ProcessRequest.GetInvoiceItems(RequestList)
    def GetTransitionDocumentItems(RequestList):
        try:
            DocumentID = RequestList["DocumentID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(DocumentID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        return ProcessRequest.GetTransitionDocumentItems(RequestList)
    def AdjustProductQuantity(RequestList):
        try:
            StoreID, ProductID, CurrentQuantity, Notes = (
                RequestList["StoreID"], RequestList["ProductID"], RequestList["CurrentQuantity"], RequestList["Notes"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(CurrentQuantity): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isinstance(Notes, str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT Partial_Quantity_Precision FROM Products_Table WHERE Product_ID={ProductID};")
        RequiredPrecision = Cursor.fetchone()["Partial_Quantity_Precision"]
        QuantityPrecision = len(str(CurrentQuantity)) - str(CurrentQuantity).index(".") - 1
        if QuantityPrecision > RequiredPrecision: return {"StatusCode":ErrorCodes.InvalidPrecision,"Data":""}
        return ProcessRequest.AdjustProductQuantity(RequestList)
def SanatizeRequest(RequestList):
    if isinstance(RequestList,list):
        for i in range(len(RequestList)):
            RequestList[i] = SanatizeRequest(RequestList[i])
    elif isinstance(RequestList,dict):
        for key in RequestList.keys():
            RequestList[key] = SanatizeRequest(RequestList[key])
    elif isinstance(RequestList, str):
        RequestList = RequestList.replace("'","''")
    return RequestList
def StartRequestProcessing(Request):
    RequestList = Request.GET.dict()
    RequestList = SanatizeRequest(RequestList)
    RequestType = RequestList["RequestType"]
    match RequestType:
        case "CreateAccount":
            Response = CheckValidation.CreateAccount(RequestList)
        case "AddStore":
            Response = CheckValidation.AddStore(RequestList)
        case "AddProduct":
            Response = CheckValidation.AddProduct(RequestList)
        case "EditProductInfo":
            Response = CheckValidation.EditProductInfo(RequestList)
        case "GetProductInfo":
            Response = CheckValidation.GetProductInfo(RequestList)
        case "Sell":
            Response = CheckValidation.Sell(RequestList)
        case "Purchase":
            Response = CheckValidation.Purchase(RequestList)
        case "Refund":
            Response = CheckValidation.Refund(RequestList)
        case "AddToAccount":
            Response = CheckValidation.AddToAccount(RequestList)
        case "DeductFromAccount":
            Response = CheckValidation.DeductFromAccount(RequestList)
        case "Transit":
            Response = CheckValidation.Transit(RequestList)
        case "SearchProducts":
            Response = CheckValidation.SearchProducts(RequestList)
        case "SearchInvoices":
            Response = CheckValidation.SearchInvoices(RequestList)
        case "SearchTransitionDocuments":
            Response = CheckValidation.SearchTransitionDocuments(RequestList)
        case "GetInvoiceItems":
            Response = CheckValidation.GetInvoiceItems(RequestList)
        case "GetTransitionDocumentItems":
            Response = CheckValidation.GetTransitionDocumentItems(RequestList)
        case "AdjustProductQuantity":
            Response = CheckValidation.AdjustProductQuantity(RequestList)
    print(str(Response))
    Response = JsonResponse(Response)
    Response["Access-Control-Allow-Origin"] = "*"
    return Response
    #return JsonResponse(Response)

def test(Request):
    #r=StartRequestProcessing('{"Re":"ghl\'","h":[1,2,3],"i":{"g":"\'"}}')
    #r = StartRequestProcessing('{"RequestType":"SearchInvoices","InvoiceType":"Purchase","Filters":[{"Invoice_ID":1}]}')
    #r = StartRequestProcessing('{"RequestType":"SearchTransitionDocuments","Filters":[{"Document_ID":1}]}')
    #ProcessRequest('{"RequestType":"EditProductInfo","ProductID":2,"ProductName":"Combination Wrench",'
    #               '"Trademark":"King Tools","ManufactureCountry":"China","PurchasePrice":5,"WholesalePrice":60,'
    #               '"RetailPrice":65}')
    #r= StartRequestProcessing('{"RequestType":"GetProductInfo","ProductID":12}')
    #r=StartRequestProcessing('{"RequestType":"AddProduct","ProductName":"Combination Wrench","Trademark":"King Tools","ManufactureCountry":"China","PurchasePrice":20,"WholesalePrice":30,"RetailPrice":35,"PartialQuantityPrecision":0}')
    #r= StartRequestProcessing('{"RequestType":"Sell","StoreID":1,"ClientID":1,"Orders":[{"ProductID":12,"Quantity":2.0,"Price":9.0}],"Paid":8}')
    #r= StartRequestProcessing('{"RequestType":"Purchase","StoreID":1,"SellerID":1,"Orders":[{"ProductID":12,"Quantity":4,"Price":9}],"Paid":9}')
    #ProcessRequest('{"RequestType":"Refund","ClientID":5,"Orders":[{"ProductID":5,"Quantity":4,"Price":9},{"ProductID":5,"Quantity":4,"Price":9}]}')
    #ProcessRequest('{"RequestType":"Transit","SourceStoreID":0,"DestinationStoreID":1,"Products":[{"ProductID":1,"Quantity":2},{"ProductID":2,"Quantity":2},{"ProductID":6,"Quantity":2}]}')
    #r = StartRequestProcessing('{"RequestType":"AdjustProductQuantity","StoreID":1,"ProductID":1,"CurrentQuantity":25.0,"Notes":"قيمة أولية"}')
    pass



