from django.shortcuts import render
from django.http import JsonResponse
import json
import mysql.connector
from datetime import datetime
from decimal import Decimal
from django.conf import settings

global SELLING_INVOICE_LENGTH, PURCHASE_INVOICE_LENGTH, REFUND_INVOICE_LENGTH, TRANSITION_DOCUMENT_LENGTH
SELLING_INVOICE_LENGTH = 12
PURCHASE_INVOICE_LENGTH = 12
REFUND_INVOICE_LENGTH = 12
TRANSITION_DOCUMENT_LENGTH = 12
ProjectDBStructure = open(settings.BASE_DIR / "API/project_db_setup.sql").read().split(";")
MainDBConnector = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "000600",
    database = "MainDB",
    ssl_disabled = True,
    collation = "utf8mb4_unicode_ci", charset = "utf8mb4"
)
ProjectsDBsConnectors = {}
MainDBCursor = MainDBConnector.cursor(dictionary = True, buffered = True)
def SetupProjectsDBsConnectors():
    MainDBCursor.execute("SELECT * FROM Projects_Table;")
    Projects = MainDBCursor.fetchall()
    for Project in Projects:
        ProjectsDBsConnectors[Project['Project_ID']] = mysql.connector.connect(
            host="localhost",
            user="root",
            password="000600",
            database=f"Project{Project['Project_ID']}",
            ssl_disabled=True,
            collation="utf8mb4_unicode_ci", charset="utf8mb4"
        )
SetupProjectsDBsConnectors()
global ProjectDBConnector
global GeneratedSql
global StoreID
GeneratedSql = ""
StoreID = 0
class ErrorCodes:
    InvalidDataType = 1
    MissingVariables = 2
    EmptyValue = 3
    RedundantValue = 4
    ValueNotFound = 5
    InsufficientQuantity = 6
    ExcessQuantity = 7
    NoStoresExist = 8
    UnregisteredStore = 9
    UnregisteredProduct = 10
    UnregisteredPerson = 11
    InvalidPrecision = 12
    InvalidFilter = 13
    ExceededMaximum = 14
    InvalidValue = 15
    NonexistantProduct = 16
#TODO: Enhance error handling
def isintstr(value):
    try:
        int(value)
        return True
    except:
        return False

class ProcessRequest:
    def CreateProject(RequestList):
        ProjectName, ProjectDescription = RequestList["ProjectName"], RequestList["ProjectDescription"]
        MainDBCursor.execute("INSERT INTO Projects_Table(Project_Name,Project_Description) VALUES ('%s','%s')" % (ProjectName,ProjectDescription))
        MainDBCursor.execute("SELECT LAST_INSERT_ID();")
        ProjectID = MainDBCursor.fetchone()['LAST_INSERT_ID()']
        MainDBCursor.execute(f"CREATE DATABASE Project{ProjectID};")
        NewDBConnector = mysql.connector.connect(
            host="localhost",
            user="root",
            password="000600",
            database=f"Project{ProjectID}",
            ssl_disabled=True,
            collation="utf8mb4_unicode_ci", charset="utf8mb4"
        )
        NewDBCursor = NewDBConnector.cursor(dictionary=True, buffered=True)
        for query in ProjectDBStructure:
            NewDBCursor.execute(query)
        NewDBConnector.commit()
        NewDBCursor.close()
        NewDBConnector.close()
        MainDBConnector.commit()
        MainDBCursor.execute("USE MainDB;")
        SetupProjectsDBsConnectors()
        return {"StatusCode":0,"Data":"OK"}
    def GetProjects(RequestList):
        MainDBCursor.execute("SELECT * FROM Projects_Table;")
        return {"StatusCode":0,"Data":MainDBCursor.fetchall()}
    def CreateAccount(RequestList):
        PersonName = RequestList["PersonName"]
        Cursor.execute(f"INSERT INTO Accounts(Name) VALUES ('{PersonName}');")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}

    def AddStore(RequestList):
        StoreName, StoreAddress = RequestList["StoreName"], RequestList["StoreAddress"]
        Cursor.execute("Select Product_ID from Products_Table;\n")
        ProductsIDs = Cursor.fetchall()
        Cursor.execute(f"INSERT INTO Stores_Table(Store_Name, Store_Address) VALUES ('{StoreName}','{StoreAddress}');\n")
        for ProductID in ProductsIDs:
            Cursor.execute(f"INSERT INTO Product_Quantity_Table VALUES (LAST_INSERT_ID(),'{ProductID["Product_ID"]}',0);\n")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    
    def GetStores(RequestList):
        Cursor.execute("SELECT * FROM Stores_Table;")
        return {"StatusCode":0,"Data":Cursor.fetchall()}
    
    def AddProduct(RequestList):
        ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, QuantityUnit, PartialQuantityPrecision = (
            RequestList["ProductName"], RequestList["Trademark"],
            RequestList["ManufactureCountry"], RequestList["PurchasePrice"], RequestList["WholesalePrice"],
            RequestList["RetailPrice"], RequestList["QuantityUnit"], RequestList["PartialQuantityPrecision"])
        #Check if Product already exist with the same trademark
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_Name='{ProductName}' AND Trademark='{Trademark}';")
        if Cursor.fetchone():
            return {"StatusCode":ErrorCodes.RedundantValue,"Data":""}
        Cursor.execute(f"SELECT Store_ID from Stores_Table;")
        StoresIDs = Cursor.fetchall()
        Cursor.execute(
            f"INSERT INTO Products_Table(Product_Name,Trademark,Manufacture_Country,Purchase_Price,Wholesale_Price,"
            f"Retail_Price,Quantity_Unit,Partial_Quantity_Precision) VALUES ('{ProductName}','{Trademark}','{ManufactureCountry}',"
            f"{PurchasePrice},{WholesalePrice},{RetailPrice},'{QuantityUnit}',{PartialQuantityPrecision});")
        for StoreID in StoresIDs:
            Cursor.execute(f"INSERT INTO Product_Quantity_Table(Store_ID,Product_ID,Quantity) VALUES ({StoreID["Store_ID"]},LAST_INSERT_ID(),0)")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def EditProductInfo(RequestList):
        ProductID, ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, QuantityUnit, PartialQuantityPrecision = (
            RequestList["ProductID"], RequestList["ProductName"], RequestList["Trademark"],
            RequestList["ManufactureCountry"], RequestList["PurchasePrice"], RequestList["WholesalePrice"],
            RequestList["RetailPrice"], RequestList["QuantityUnit"], RequestList["PartialQuantityPrecision"])
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_ID={ProductID};")
        if Cursor.fetchone() is None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        Cursor.execute(
            f"UPDATE Products_Table SET Product_Name = '{ProductName}', Trademark = '{Trademark}', "
            f"Manufacture_Country = '{ManufactureCountry}', Purchase_Price={PurchasePrice}, Wholesale_Price="
            f"{WholesalePrice}, Retail_Price={RetailPrice}, Quantity_Unit='{QuantityUnit}', Partial_Quantity_Precision = {PartialQuantityPrecision} WHERE Product_ID={ProductID};")
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
    def Sell(RequestList, Orders, RequiredAmount):
        StoreID, ClientName, Paid = RequestList["StoreID"], RequestList["ClientName"], RequestList["Paid"]

        # For every ordered product check if product has sufficient quantity
        for Order in Orders:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Order['ProductID']} AND Store_ID={StoreID}")
            AvailableQuantity = Cursor.fetchone()["Quantity"]
            if AvailableQuantity < Order["Quantity"]:
                return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Order['ProductID']}

        Cursor.execute(f"INSERT INTO Selling_Invoices(Store_Id,Client_Name,Total_Price,Paid,Transferred_To_Account) "
                       f"VALUES ('{StoreID}','{ClientName}','{RequiredAmount}','{Paid}',{RequiredAmount - Paid});")
        Cursor.execute("SET @Invoice_ID = LAST_INSERT_ID();")
        for Order in Orders:
            Cursor.execute(f"INSERT INTO Selling_Items VALUES (@Invoice_ID,'{Order["ProductID"]}','{Order["Quantity"]}','{Order["UnitPrice"]}');\n")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Order['Quantity']} WHERE "
                           f"Store_ID = {StoreID} AND Product_ID = {Order['ProductID']}")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def Purchase(RequestList, Orders, TotalPrice):
        StoreID, SellerName, Paid = RequestList["StoreID"], RequestList["SellerName"], RequestList["Paid"]
        Cursor.execute(f"INSERT INTO Purchase_Invoices(Store_Id,Seller_Name,Total_Price,Paid,Subtracted_From_Account) VALUES ('{StoreID}','{SellerName}','{TotalPrice}',{Paid},{TotalPrice-Paid});")
        Cursor.execute("SET @Invoice_ID = LAST_INSERT_ID();")
        for Order in Orders:
            Cursor.execute(
                f"INSERT INTO Purchase_Items(Invoice_ID,Product_ID,Quantity,Unit_Price) VALUES (@Invoice_ID,'{Order["ProductID"]}','{Order["Quantity"]}','{Order["UnitPrice"]}');\n")
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
                return {"StatusCode":ErrorCodes.RedundantValue,"Data":""}
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
    def EditSellingInvoice(RequestList, StoreID, Orders, TotalPrice):
        InvoiceID, ClientName, Paid = RequestList["InvoiceID"], RequestList["ClientName"], RequestList["Paid"]
        
        # For every ordered product
        for Order in Orders:
            # Check if store has sufficient quantity
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Order['ProductID']} AND Store_ID={StoreID}")
            AvailableQuantity = Cursor.fetchone()["Quantity"]
            Cursor.execute(f"SELECT Quantity FROM Selling_Items WHERE Invoice_ID={InvoiceID} AND Product_ID={Order['ProductID']}")
            InvoicePreviousQuantity = Cursor.fetchone()
            if InvoicePreviousQuantity != None:
                InvoicePreviousQuantity = InvoicePreviousQuantity["Quantity"]
                if AvailableQuantity < Order["Quantity"] - InvoicePreviousQuantity:
                    return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Order['ProductID']}
                # Return the previous quantity to the store
                Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {InvoicePreviousQuantity} WHERE Product_ID = {Order['ProductID']} AND Store_ID = {StoreID}")
        
        Cursor.execute(f"UPDATE Selling_Invoices SET Client_Name='{ClientName}',Total_Price='{TotalPrice}',Paid='{Paid}',Transferred_To_Account='{TotalPrice - Paid}' WHERE Invoice_ID={InvoiceID};")
        Cursor.execute(f"DELETE FROM Selling_Items WHERE Invoice_ID='{InvoiceID}';")
        for Order in Orders:
            Cursor.execute(f"INSERT INTO Selling_Items VALUES ('{InvoiceID}','{Order["ProductID"]}','{Order["Quantity"]}','{Order["UnitPrice"]}');\n")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Order['Quantity']} WHERE "
                           f"Store_ID = {StoreID} AND Product_ID = {Order['ProductID']}")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def EditPurchaseInvoice(RequestList, StoreID, Orders, TotalPrice):
        InvoiceID, SellerName, Paid = RequestList["InvoiceID"], RequestList["SellerName"], RequestList["Paid"]
        
        # For every ordered product
        for Order in Orders:
            Cursor.execute(f"SELECT Quantity FROM Purchase_Items WHERE Invoice_ID={InvoiceID} AND Product_ID={Order['ProductID']}")
            if (InvoicePreviousQuantity := Cursor.fetchone()) != None:
                # Subtract the previous quantity from the store
                InvoicePreviousQuantity = InvoicePreviousQuantity["Quantity"]
                Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {InvoicePreviousQuantity} WHERE Product_ID = {Order['ProductID']} AND Store_ID = {StoreID}")
        Cursor.execute(f"UPDATE Purchase_Invoices SET Seller_Name='{SellerName}',Total_Price='{TotalPrice}',Paid='{Paid}',Subtracted_From_Account='{TotalPrice - Paid}' WHERE Invoice_ID={InvoiceID};")
        Cursor.execute(f"DELETE FROM Purchase_Items WHERE Invoice_ID='{InvoiceID}';")
        for Order in Orders:
            Cursor.execute(f"INSERT INTO Purchase_Items VALUES ('{InvoiceID}','{Order["ProductID"]}','{Order["Quantity"]}','{Order["UnitPrice"]}');\n")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {Order['Quantity']} WHERE "
                           f"Store_ID = {StoreID} AND Product_ID = {Order['ProductID']}")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def EditRefundInvoice(RequestList, Orders, TotalPrice):
        pass
    def DeletePurchaseInvoice(RequestList, StoreID):
        InvoiceID = RequestList["InvoiceID"]
        Cursor.execute(f"SELECT * FROM Purchase_Items WHERE Invoice_ID={InvoiceID};")
        Items = Cursor.fetchall()
        for Item in Items:
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Item['Quantity']} WHERE Product_ID={Item['Product_ID']} AND Store_ID={StoreID};")
        Cursor.execute(f"DELETE FROM Purchase_Items WHERE Invoice_ID={InvoiceID};")
        Cursor.execute(f"DELETE FROM Purchase_Invoices WHERE Invoice_ID={InvoiceID};")
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
        Filters.remove("ProjectID")
        Filters.remove("StoreID")
        Sql = f"SELECT * FROM Products_Table JOIN Product_Quantity_Table ON Products_Table.Product_ID = Product_Quantity_Table.Product_ID AND Product_Quantity_Table.Store_ID = {StoreID} " 
        if Filters:
            Sql += "WHERE "
        for Filter in Filters:
            value = RequestList[Filter]
            Sql += f"Products_Table.{Filter} LIKE '%{value}%' "
        Cursor.execute(Sql)
        return {"StatusCode":0,"Data":Cursor.fetchall()}
    def SearchInvoices(RequestList):
        InvoiceType = RequestList["InvoiceType"]
        StoreID = RequestList["StoreID"]
        Filters = list(RequestList.keys())
        Filters.remove("RequestType")
        Filters.remove("ProjectID")
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
        Response = Cursor.fetchall()
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
    def GetInvoice(RequestList):
        InvoiceType = RequestList["InvoiceType"]
        InvoiceID = RequestList["InvoiceID"]
        Cursor.execute(f"SELECT * FROM {InvoiceType}_Invoices WHERE Invoice_ID={InvoiceID};")
        InvoiceInfo = Cursor.fetchone()
        Cursor.execute(f"SELECT * FROM {InvoiceType}_Items JOIN Products_Table ON {InvoiceType}_Items.Product_ID = Products_Table.Product_ID WHERE Invoice_ID={InvoiceID};")
        InvoiceInfo["Items"] = Cursor.fetchall()
        return {"StatusCode":0,"Data":InvoiceInfo}
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
                    pass
                case "Quantity":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Selling_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "RequestType" | "InvoiceType" | "ProjectID" | "StoreID":
                    pass
                case _:
                    return {"StatusCode":ErrorCodes.InvalidFilter,"Data":""}
        return 0
    def PurchaseInvoices(RequestList):
        for Filter in RequestList.keys():
            match Filter:
                case "Invoice_ID" | "Seller_Name":
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
                case "RequestType" | "InvoiceType" | "ProjectID" |"StoreID":
                    pass
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
                case "RequestType" | "InvoiceType" | "ProjectID" | "StoreID":
                    pass
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
                case "RequestType" | "InvoiceType" | "ProjectID" | "StoreID":
                    pass
                case _:
                    return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return 0
def GetOrders(RequestList: dict):
    i = 0
    Orders = []
    OrdersIDs = []
    TotalPrice = Decimal()
    while True:
        if i > PURCHASE_INVOICE_LENGTH:
            return {"StatusCode":ErrorCodes.ExceededMaximum,"Variable":"Orders"} , 0
        Order = {}
        if (Para := RequestList.get(f"Orders[{i}][ProductID]")) != None:
            if not isintstr(Para):
                return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":f"Orders[{i}][ProductID]"}, 0
            Order["ProductID"] = Para
        if (Para := RequestList.get(f"Orders[{i}][Quantity]")) != None:
            if not isintstr(Para):
                return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":f"Orders[{i}][Quantity]"}, 0
            if float(Para) <= 0:
                return {"StatusCode":ErrorCodes.InvalidValue,"Variable":f"Orders[{i}][Quantity]"}, 0
            Order["Quantity"] = Decimal(Para)
        if (Para := RequestList.get(f"Orders[{i}][UnitPrice]")) != None:
            if not isintstr(Para):
                return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":f"Orders[{i}][UnitPrice]"}, 0
            if float(Para) < 0:
                return {"StatusCode":ErrorCodes.InvalidValue,"Variable":f"Orders[{i}][UnitPrice]"}, 0
            Order["UnitPrice"] = float(Para)
        if not Order:
            break
        elif len(Order.keys()) < 3:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":f"Orders[{i}]"}, 0
        TotalPrice += Decimal(Order["UnitPrice"]) * Decimal(Order["Quantity"])
        
        Cursor.execute(f"SELECT Partial_Quantity_Precision FROM Products_Table WHERE Product_ID={Order['ProductID']};")
        if (RequiredPrecision := Cursor.fetchone().get("Partial_Quantity_Precision")) == None:
            print(RequiredPrecision)
            return {"StatusCode":ErrorCodes.NonexistantProduct,"Variable":f"Orders[{i}][ProductID]"}, 0
        QuantityPrecision = len(str(Order["Quantity"])) - str(float(Order["Quantity"])).find(".") - 1
        if QuantityPrecision > RequiredPrecision:
            print(Order["Quantity"])
            print(QuantityPrecision)
            print(RequiredPrecision)
            return {"StatusCode":ErrorCodes.InvalidPrecision,"Data":""}, 0
        if not Order["ProductID"] in OrdersIDs:
            Orders.append(Order)
            OrdersIDs.append(Order["ProductID"])
        else:
            return {"StatusCode":ErrorCodes.RedundantValue,"Variable":f"Orders[{i}]"}, 0
        i += 1
    return Orders, TotalPrice
    
ValidHistoryTables = ["Selling_Invoices","Refund_Invoices","Purchase_Invoices","Transition_Documents","Accounts_Operations"]
ValidInvoiceTypes = ["Selling","Refund","Purchase"]
class CheckValidation:
    def __init__(self):
        pass
    def CreateProject(RequestList):
        try:
            ProjectName, ProjectDescription = RequestList["ProjectName"], RequestList["ProjectDescription"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if len(ProjectName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ProjectName"}
        if len(ProjectDescription) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ProjectDescription"}
        return ProcessRequest.CreateProject(RequestList)
    def CreateAccount(RequestList):
        try:
            ProjectID, PersonName = RequestList["ProjectID"], RequestList["PersonName"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isinstance(PersonName,str): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(PersonName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "PersonName"}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.CreateAccount(RequestList)
    def AddStore(RequestList):
        try:
            ProjectID, StoreName = RequestList["ProjectID"], RequestList["StoreName"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectID = int(ProjectID)
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        
        if len(StoreName) == 0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"StoreName"}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.AddStore(RequestList)
    
    def GetStores(RequestList):
        try:
            ProjectID = RequestList["ProjectID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectID = int(ProjectID)
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.GetStores(RequestList)
    
    def AddProduct(RequestList):
        try:
            ProjectID = RequestList["ProjectID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType, "Variable":"ProjectID"}
        ProjectID = int(ProjectID)
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        Cursor.execute("SELECT COUNT(*) FROM Stores_Table;")
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.NoStoresExist,"Data":""}
        try:
            ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, QuantityUnit, PartialQuantityPrecision =(
                RequestList["ProductName"], RequestList["Trademark"], RequestList["ManufactureCountry"],
                RequestList["PurchasePrice"],RequestList["WholesalePrice"], RequestList["RetailPrice"],
                RequestList["QuantityUnit"], RequestList["PartialQuantityPrecision"]
            )
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(PurchasePrice):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(WholesalePrice):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(RetailPrice):return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(ProductName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "ProductName"}
        if len(Trademark) == 0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"Trademark"}
        if len(ManufactureCountry) == 0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ManufactureCountry"}
        if len(QuantityUnit) == 0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"QuantityUnit"}
        if int(PurchasePrice) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if int(WholesalePrice) < 0:return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if int(RetailPrice) < 0:return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if int(PartialQuantityPrecision) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return ProcessRequest.AddProduct(RequestList)
    def EditProductInfo(RequestList):
        try:
            ProjectID, ProductID, ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice, QuantityUnit, PartialQuantityPrecision = (
                RequestList["ProjectID"], RequestList["ProductID"], RequestList["ProductName"], RequestList["Trademark"],
                RequestList["ManufactureCountry"], RequestList["PurchasePrice"], RequestList["WholesalePrice"],
                RequestList["RetailPrice"], RequestList["QuantityUnit"], RequestList["PartialQuantityPrecision"]
            )
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":"ProjectID"}
        if (ProjectID := int(ProjectID)) not in ProjectsDBsConnectors.keys():
            return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT Product_ID FROM Products_Table WHERE Product_ID={ProductID};")
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.NonexistantProduct,"Variable":"ProductID"}
        if not isintstr(PurchasePrice): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(WholesalePrice): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(RetailPrice): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(ProductName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ProductName"}
        if len(Trademark) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "Trademark"}
        if len(ManufactureCountry) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "ManufactureCountry"}
        if int(PurchasePrice) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if int(WholesalePrice) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if int(RetailPrice) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if len(QuantityUnit) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"QuantityUnit"}
        if int(PartialQuantityPrecision) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        return ProcessRequest.EditProductInfo(RequestList)
    def GetProductInfo(RequestList):
        try:
            ProjectID, ProductID = RequestList["ProjectID"], RequestList["ProductID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":"ProjectID"}
        if (ProjectID := int(ProjectID)) not in ProjectsDBsConnectors.keys():
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"ProjectID"}
        if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.GetProductInfo(RequestList)

    def Sell(RequestList):
        try:
            ProjectID, StoreID, ClientName, Paid = (
                RequestList["ProjectID"],RequestList["StoreID"], RequestList["ClientName"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectID = int(ProjectID)
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(ClientName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ClientName"}
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if int(Paid) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        Orders, RequiredAmount = GetOrders(RequestList)
        if isinstance(Orders, dict):
            return Orders
        if len(Orders) == 0:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        RequestList["Paid"] = Decimal(Paid)
        if RequestList["Paid"] > RequiredAmount:
            return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"Paid"}
        return ProcessRequest.Sell(RequestList, Orders, RequiredAmount)
    def Purchase(RequestList):
        try:
            ProjectID, StoreID, SellerName, Paid = (
                RequestList["ProjectID"], RequestList["StoreID"], RequestList["SellerName"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables, "Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectID = int(ProjectID)
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(SellerName) == 0: return {"StatusCode": ErrorCodes.EmptyValue, "Variable": "SellerName"}
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":"Paid"}
        if int(Paid) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"Paid"}
        Orders, TotalPrice = GetOrders(RequestList)
        if isinstance(Orders, dict):
            return Orders
        if len(Orders) == 0:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        RequestList["Paid"] = Decimal(Paid)
        if RequestList["Paid"] > TotalPrice:
            return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"Paid"}
        return ProcessRequest.Purchase(RequestList, Orders, TotalPrice)
    def Refund(RequestList):
        try:
            ProjectID, StoreID, ClientID = (
                RequestList["ProjectID"], RequestList["StoreID"], RequestList["ClientID"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(ClientID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Orders = GetOrders(RequestList)
        if len(Orders) == 0:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        return ProcessRequest.Refund(RequestList, Orders)
    def EditSellingInvoice(RequestList):
        try:
            ProjectID, InvoiceID, ClientName, Paid = (
                RequestList["ProjectID"], RequestList["InvoiceID"], RequestList["ClientName"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if (ProjectID := int(ProjectID)) not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT Store_ID FROM Selling_Invoices WHERE Invoice_ID={InvoiceID};")
        if (StoreID := Cursor.fetchone()) == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        StoreID = StoreID["Store_ID"]
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(ClientName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ClientName"}
        if int(Paid) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        Orders, TotalPrice = GetOrders(RequestList)
        if isinstance(Orders, dict):
            return Orders
        if len(Orders) == 0:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        RequestList["Paid"] = Decimal(Paid)
        if RequestList["Paid"] > TotalPrice:
            return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"Paid"}
        return ProcessRequest.EditSellingInvoice(RequestList, StoreID, Orders, TotalPrice)
    def EditPurchaseInvoice(RequestList):
        try:
            ProjectID, InvoiceID, SellerName, Paid = (
                RequestList["ProjectID"], RequestList["InvoiceID"], RequestList["SellerName"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if (ProjectID := int(ProjectID)) not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        
        Cursor.execute(f"SELECT Store_ID FROM Purchase_Invoices WHERE Invoice_ID={InvoiceID};")
        if (StoreID := Cursor.fetchone()) == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        StoreID = StoreID["Store_ID"]
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(SellerName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"SellerName"}
        if int(Paid) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        Orders, TotalPrice = GetOrders(RequestList)
        if isinstance(Orders, dict):
            return Orders
        if len(Orders) == 0:
            print(Orders)
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        RequestList["Paid"] = Decimal(Paid)
        if RequestList["Paid"] > TotalPrice:
            return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"Paid"}
        return ProcessRequest.EditPurchaseInvoice(RequestList, StoreID, Orders, TotalPrice)
    def EditRefundInvoice(RequestList):
        try:
            ProjectID, InvoiceID, ClientID = (
                RequestList["ProjectID"], RequestList["InvoiceID"], RequestList["ClientID"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if (ProjectID := int(ProjectID)) not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT * FROM Refund_Invoices WHERE Invoice_ID={InvoiceID};")
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(ClientID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Orders = GetOrders(RequestList)
        if len(Orders) == 0:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        return ProcessRequest.EditRefundInvoice(RequestList, Orders)
    def DeletePurchaseInvoice(RequestList):
        try:
            ProjectID, InvoiceID = RequestList["ProjectID"], RequestList["InvoiceID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if (ProjectID := int(ProjectID)) not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        Cursor.execute(f"SELECT Store_ID FROM Purchase_Invoices WHERE Invoice_ID={InvoiceID};")
        if not (StoreID := Cursor.fetchone().get("Store_ID")):
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        return ProcessRequest.DeletePurchaseInvoice(RequestList, StoreID)
    def AddToAccount(RequestList):
        try:
            ProjectID, PersonID, Description, Amount = (
                RequestList["ProjectID"], RequestList["PersonID"], RequestList["Description"], RequestList["Amount"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(PersonID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        
        if not isintstr(Amount, float): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if PersonID<0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if len(Description)==0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if Amount<=0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.AddToAccount(RequestList)
    def DeductFromAccount(RequestList):
        try:
            ProjectID, PersonID, Description, Amount = (
                RequestList["ProjectID"], RequestList["PersonID"], RequestList["Description"], RequestList["Amount"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(PersonID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        
        if not isintstr(Amount, float): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(Description)==0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        if Amount <= 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.DeductFromAccount(RequestList)
    def Transit(RequestList):
        try:
            ProjectID, SourceStoreID, DestinationStoreID, Products = (RequestList["ProjectID"],
                RequestList["SourceStoreID"], RequestList["DestinationStoreID"], RequestList["Products"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
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
            ProjectID, StoreID = RequestList["ProjectID"], RequestList["StoreID"]
        except:
            return {"StatusCode": ErrorCodes.MissingVariables, "Data": ""}
        if not isintstr(ProjectID): return {"StatusCode": ErrorCodes.InvalidDataType, "Variable": "ProjectID"}
        if (ProjectID := int(ProjectID)) not in ProjectsDBsConnectors.keys(): return {"StatusCode": ErrorCodes.ValueNotFound, "Variable": "ProjectID"}
        if not isintstr(StoreID): return {"StatusCode": ErrorCodes.InvalidDataType, "Variable": "StoreID"}
        for Filter in RequestList.keys():
            match Filter:
                case "Product_ID" | "Product_Name" | "Trademark" | "Manufacture_Country":
                    pass
                case "Purchase_Price" | "Wholesale_Price" | "Retail_Price":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "Partial_Quantity_Precision":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
                case "RequestType" | "ProjectID" | "StoreID":
                    pass
                case _:
                    return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.SearchProducts(RequestList)
    def SearchInvoices(RequestList):
        try:
            ProjectID, InvoiceType, StoreID = RequestList["ProjectID"], RequestList["InvoiceType"], RequestList["StoreID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectID = int(ProjectID)
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
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
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.SearchInvoices(RequestList)
    def SearchTransitionDocuments(RequestList):
        try:
            ProjectID, Filters = RequestList["ProjectID"], RequestList["Filters"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isinstance(Filters, dict): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Error = SearchFiltersValidation.TransitionDocuments(Filters)
        if Error:
            return Error
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.SearchTransitionDocuments(RequestList)
    def GetInvoice(RequestList):
        try:
            ProjectID, InvoiceType, InvoiceID = RequestList["ProjectID"], RequestList["InvoiceType"], RequestList["InvoiceID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectID = int(ProjectID)
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not InvoiceType in ValidInvoiceTypes: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        Cursor.execute(f"SELECT Store_ID FROM {InvoiceType}_Invoices WHERE Invoice_ID={InvoiceID};")
        if not Cursor.fetchone():
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        return ProcessRequest.GetInvoice(RequestList)
    def GetTransitionDocumentItems(RequestList):
        try:
            ProjectID, DocumentID = RequestList["ProjectID"], RequestList["DocumentID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(DocumentID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        return ProcessRequest.GetTransitionDocumentItems(RequestList)
    def AdjustProductQuantity(RequestList):
        try:
            ProjectID, StoreID, ProductID, CurrentQuantity, Notes = (RequestList["ProjectID"],
                RequestList["StoreID"], RequestList["ProductID"], RequestList["CurrentQuantity"], RequestList["Notes"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectID not in ProjectsDBsConnectors.keys(): return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        global Cursor
        global ProjectDBConnector
        ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not isintstr(CurrentQuantity): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
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
        case "CreateProject":
            Response = CheckValidation.CreateProject(RequestList)
        case "GetProjects":
            Response = ProcessRequest.GetProjects(RequestList)
        case "CreateAccount":
            Response = CheckValidation.CreateAccount(RequestList)
        case "AddStore":
            Response = CheckValidation.AddStore(RequestList)
        case "AddProduct":
            Response = CheckValidation.AddProduct(RequestList)
        case "GetStores":
            Response = CheckValidation.GetStores(RequestList)
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
        case "EditPurchaseInvoice":
            Response = CheckValidation.EditPurchaseInvoice(RequestList)
        case "EditSellingInvoice":
            Response = CheckValidation.EditSellingInvoice(RequestList)
        case "EditRefundInvoice":
            Response = CheckValidation.EditRefundInvoice(RequestList)
        case "DeletePurchaseInvoice":
            Response = CheckValidation.DeletePurchaseInvoice(RequestList)
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
        case "GetInvoice":
            Response = CheckValidation.GetInvoice(RequestList)
        case "GetTransitionDocumentItems":
            Response = CheckValidation.GetTransitionDocumentItems(RequestList)
        case "AdjustProductQuantity":
            Response = CheckValidation.AdjustProductQuantity(RequestList)
        case _:
            Response = {"StatusCode":ErrorCodes.InvalidValue,"Variable":"RequestType"}
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



