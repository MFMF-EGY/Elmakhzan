from django.shortcuts import render
from django.http import JsonResponse
import json
import mysql.connector
from django.db import connections
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.db.backends.mysql.base import CursorWrapper

global SELLING_INVOICE_LENGTH, PURCHASE_INVOICE_LENGTH, REFUND_INVOICE_LENGTH, TRANSITION_DOCUMENT_LENGTH
SELLING_INVOICE_LENGTH = 12
PURCHASE_INVOICE_LENGTH = 12
REFUND_INVOICE_LENGTH = 12
TRANSITION_DOCUMENT_LENGTH = 12
ProjectDBStructure = open(settings.BASE_DIR / "API/project_db_setup.sql").read().split(";")
# MainDBConnector = mysql.connector.connect(
#     host = "localhost",
#     user = "root",
#     password = "000600",
#     database = "MainDB",
#     ssl_disabled = True,
#     collation = "utf8mb4_unicode_ci", charset = "utf8mb4"
# )

connections.databases["MainDB"] = {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'MainDB',
    'HOST': 'localhost',
    'PORT': '3306',
    'USER': 'root',
    'PASSWORD': '000600',
    'OPTIONS': {
        'collation': 'utf8mb4_unicode_ci',
        'charset': 'utf8mb4'
    },
    'AUTOCOMMIT': False,
    'TIME_ZONE': settings.TIME_ZONE,
    'CONN_HEALTH_CHECKS': False,
    'CONN_MAX_AGE': 0,
    'ATOMIC_REQUESTS': False,
}
ProjectsDBsConnectors = {}
MainDBCursor = connections["MainDB"].cursor()

# Enable dictionary fetches for Django cursor
CursorWrapper.dictfetchall = lambda self: [
    dict(zip([col[0] for col in self.description], row))
    for row in self.fetchall()
]
CursorWrapper.dictfetchone = lambda self: (
    dict(zip([col[0] for col in self.description], self.fetchone()))
    if self.rowcount > 0 else None
)
def SetupProjectsDBsConnectors():
    MainDBCursor.execute("SELECT Project_ID FROM Projects_Table;")
    ProjectsIDs = MainDBCursor.fetchall()
    for ProjectID in ProjectsIDs:
        connections.databases[f"Project{ProjectID[0]}"] = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': f"Project{ProjectID[0]}",
            'HOST': 'localhost',
            'PORT': '3306',
            'USER': 'root',
            'PASSWORD': '000600',
            'OPTIONS': {
                'collation': 'utf8mb4_unicode_ci',
                'charset': 'utf8mb4'
            },
            'AUTOCOMMIT': False,
            'TIME_ZONE': settings.TIME_ZONE,
            'CONN_HEALTH_CHECKS': False,
            'CONN_MAX_AGE': 0,
            'ATOMIC_REQUESTS': False,
        }
        ProjectsDBsConnectors[ProjectID[0]] = 1

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
        #TODO: Check if project has unique name
        ProjectName, ProjectDescription = RequestList["ProjectName"], RequestList["ProjectDescription"]
        MainDBCursor.execute("INSERT INTO Projects_Table(Project_Name,Project_Description) VALUES ('%s','%s')" % (ProjectName,ProjectDescription))
        MainDBCursor.execute("SELECT LAST_INSERT_ID();")
        ProjectID = MainDBCursor.fetchone()[0]
        MainDBCursor.execute(f"CREATE DATABASE Project{ProjectID};")
        
        connections.databases[f"Project{ProjectID}"] = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': f"Project{ProjectID}",
            'HOST': 'localhost',
            'PORT': '3306',
            'USER': 'root',
            'PASSWORD': '000600',
            'OPTIONS': {
                'collation': 'utf8mb4_unicode_ci',
                'charset': 'utf8mb4'
            },
            'AUTOCOMMIT': False,
            'TIME_ZONE': settings.TIME_ZONE,
            'CONN_HEALTH_CHECKS': False,
            'CONN_MAX_AGE': 0,
            'ATOMIC_REQUESTS': False,
        }
        NewDBCursor = connections[f"Project{ProjectID}"].cursor()
        for query in ProjectDBStructure:
            NewDBCursor.execute(query)
        connections[f"Project{ProjectID}"].commit()
        NewDBCursor.close()
        connections["MainDB"].commit()
        MainDBCursor.execute("USE MainDB;")
        SetupProjectsDBsConnectors()
        return {"StatusCode":0,"Data":"OK"}
    def GetProjects(RequestList):
        MainDBCursor.execute("SELECT * FROM Projects_Table;")
        return {"StatusCode":0,"Data":MainDBCursor.dictfetchall()}
    def CreateAccount(ProjectDBConnector, Cursor, RequestList):
        PersonName = RequestList["PersonName"]
        Cursor.execute(f"INSERT INTO Accounts(Name) VALUES ('{PersonName}');")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}

    def AddStore(ProjectDBConnector, Cursor, RequestList):
        StoreName, StoreAddress = RequestList["StoreName"], RequestList["StoreAddress"]
        Cursor.execute("Select Product_ID from Products_Table;\n")
        ProductsIDs = Cursor.dictfetchall()
        Cursor.execute(f"INSERT INTO Stores_Table(Store_Name, Store_Address) VALUES ('{StoreName}','{StoreAddress}');\n")
        for ProductID in ProductsIDs:
            Cursor.execute(f"INSERT INTO Product_Quantity_Table VALUES (LAST_INSERT_ID(),'{ProductID["Product_ID"]}',0);\n")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    
    def GetStores(Cursor):
        Cursor.execute("SELECT * FROM Stores_Table;")
        return {"StatusCode":0,"Data":Cursor.dictfetchall()}
    
    def AddProduct(ProjectDBConnector, Cursor, RequestList):
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
            Cursor.execute(f"INSERT INTO Product_Quantity_Table(Store_ID,Product_ID,Quantity) VALUES ({StoreID},LAST_INSERT_ID(),0)")
        ProjectDBConnector.commit()
        return {"StatusCode": 0,"Data": "OK"}
    def EditProductInfo(ProjectDBConnector, Cursor, RequestList):
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
        ProductQuantities = Cursor.dictfetchall()
        ProductInfo["Product_Quantity_Table"] = ProductQuantities
        return {"StatusCode": 0,"Data": ProductInfo}
    def GetProductsQuantities(Cursor, RequestList, ProductsIDs):
        StoreID = RequestList["StoreID"]
        Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Store_ID={StoreID} AND Product_ID IN ({','.join(map(str, ProductsIDs))});")
        ProductQuantities = Cursor.fetchall()
        return {"StatusCode":0,"Data":ProductQuantities}
    def Sell(ProjectDBConnector, Cursor, RequestList, Orders, RequiredAmount):
        StoreID, ClientName, Paid = RequestList["StoreID"], RequestList["ClientName"], RequestList["Paid"]

        # For every ordered product check if product has sufficient quantity
        for Order in Orders:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Order['ProductID']} AND Store_ID={StoreID}")
            AvailableQuantity = Cursor.fetchone()[0]
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
    def Purchase(ProjectDBConnector, Cursor, RequestList, Orders, TotalPrice):
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
    def EditSellingInvoice(ProjectDBConnector, Cursor, RequestList, StoreID, Orders, TotalPrice):
        InvoiceID, ClientName, Paid = RequestList["InvoiceID"], RequestList["ClientName"], RequestList["Paid"]
        
        # For every ordered product
        for Order in Orders:
            # Check if store has sufficient quantity
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Order['ProductID']} AND Store_ID={StoreID}")
            AvailableQuantity = Cursor.fetchone()[0]
            Cursor.execute(f"SELECT Quantity FROM Selling_Items WHERE Invoice_ID={InvoiceID} AND Product_ID={Order['ProductID']}")
            InvoicePreviousQuantity = Cursor.fetchone()[0]
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
    def EditPurchaseInvoice(ProjectDBConnector, Cursor, RequestList, StoreID, Orders, TotalPrice):
        InvoiceID, SellerName, Paid = RequestList["InvoiceID"], RequestList["SellerName"], RequestList["Paid"]
        
        # For every ordered product
        for Order in Orders:
            Cursor.execute(f"SELECT Quantity FROM Purchase_Items WHERE Invoice_ID={InvoiceID} AND Product_ID={Order['ProductID']}")
            
            # Subtract the previous quantity from the store
            InvoicePreviousQuantity = Cursor.fetchone()[0]
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
    def EditTransitionDocument(ProjectDBConnector, Cursor, RequestList, Orders):
        DocumentID = RequestList["DocumentID"]
        SourceStoreID, DestinationStoreID = RequestList["SourceStoreID"], RequestList["DestinationStoreID"]
        for Order in Orders:
            Cursor.execute(f"SELECT Quantity FROM Transition_Items WHERE Document_ID={DocumentID} AND Product_ID={Order['ProductID']}")
            DocumentPreviousQuantity = Cursor.fetchone()[0]
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {DocumentPreviousQuantity} WHERE Product_ID = {Order['ProductID']} AND Store_ID = {SourceStoreID}")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {DocumentPreviousQuantity} WHERE Product_ID = {Order['ProductID']} AND Store_ID = {DestinationStoreID}")
        Cursor.execute(f"DELETE FROM Transition_Items WHERE Document_ID={DocumentID};")
        Cursor.execute(f"UPDATE Transition_Documents SET Source_Store_ID='{SourceStoreID}',Destination_Store_ID='{DestinationStoreID}' WHERE Document_ID={DocumentID};")
        for Order in Orders:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Order['ProductID']} AND Store_ID={SourceStoreID}")
            AvailableQuantity = Cursor.fetchone()[0]
            if AvailableQuantity < Order["Quantity"]:
                return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Order['ProductID']}
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Order['Quantity']} WHERE Product_ID = {Order['ProductID']} AND Store_ID = {SourceStoreID}")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {Order['Quantity']} WHERE Product_ID = {Order['ProductID']} AND Store_ID = {DestinationStoreID}")
            Cursor.execute(f"INSERT INTO Transition_Items VALUES ('{DocumentID}','{Order["ProductID"]}','{Order["Quantity"]}');\n")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}
    def DeletePurchaseInvoice(ProjectDBConnector, Cursor, RequestList, StoreID):
        InvoiceID = RequestList["InvoiceID"]
        Cursor.execute(f"SELECT Product_ID,Quantity FROM Purchase_Items WHERE Invoice_ID={InvoiceID};")
        Items = Cursor.fetchall()
        for Item in Items:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Item[0]} AND Store_ID={StoreID};")
            if Cursor.fetchone()[0] < Item[1]:
                return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Item[0]}
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Item[1]} WHERE Product_ID={Item[0]} AND Store_ID={StoreID};")
        Cursor.execute(f"DELETE FROM Purchase_Items WHERE Invoice_ID={InvoiceID};")
        Cursor.execute(f"DELETE FROM Purchase_Invoices WHERE Invoice_ID={InvoiceID};")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}

    def DeleteSellingInvoice(ProjectDBConnector, Cursor, RequestList, StoreID):
        InvoiceID = RequestList["InvoiceID"]
        Cursor.execute(f"SELECT Product_ID,Quantity FROM Selling_Items WHERE Invoice_ID={InvoiceID};")
        Items = Cursor.fetchall()
        for Item in Items:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Item[0]} AND Store_ID={StoreID};")
            if Cursor.fetchone()[0] < Item[1]:
                return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Item[0]}
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {Item[1]} WHERE Product_ID={Item[0]} AND Store_ID={StoreID};")
        Cursor.execute(f"DELETE FROM Selling_Items WHERE Invoice_ID={InvoiceID};")
        Cursor.execute(f"DELETE FROM Selling_Invoices WHERE Invoice_ID={InvoiceID};")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}

    def DeleteRefundInvoice(ProjectDBConnector, Cursor, RequestList, StoreID):
        InvoiceID = RequestList["InvoiceID"]
        Cursor.execute(f"SELECT Product_ID,Quantity FROM Refund_Items WHERE Invoice_ID={InvoiceID};")
        Items = Cursor.fetchall()
        for Item in Items:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Item[0]} AND Store_ID={StoreID};")
            if Cursor.fetchone()[0] < Item[1]:
                return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Item[0]}
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Item[1]} WHERE Product_ID={Item[0]} AND Store_ID={StoreID};")
        Cursor.execute(f"DELETE FROM Refund_Items WHERE Invoice_ID={InvoiceID};")
        Cursor.execute(f"DELETE FROM Refund_Invoices WHERE Invoice_ID={InvoiceID};")
        ProjectDBConnector.commit()
        return {"StatusCode":0,"Data":"OK"}

    def DeleteTransitionDocument(ProjectDBConnector, Cursor, RequestList):
        DocumentID = RequestList["DocumentID"]
        Cursor.execute(f"SELECT Source_Store_ID,Destination_Store_ID FROM Transition_Documents WHERE Document_ID={DocumentID};")
        SourceStoreID, DestinationStoreID = Cursor.fetchone()
        Cursor.execute(f"SELECT Product_ID,Quantity FROM Transition_Items WHERE Document_ID={DocumentID};")
        Items = Cursor.fetchall()
        for Item in Items:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Item[0]} AND Store_ID={DestinationStoreID};")
            if Cursor.fetchone()[0] < Item[1]:
                return {"StatusCode":ErrorCodes.InsufficientQuantity,"ProductID":Item[0]}
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Item[1]} WHERE Product_ID={Item[0]} AND Store_ID={DestinationStoreID};")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {Item[1]} WHERE Product_ID={Item[0]} AND Store_ID={SourceStoreID};")
        Cursor.execute(f"DELETE FROM Transition_Items WHERE Document_ID={DocumentID};")
        Cursor.execute(f"DELETE FROM Transition_Documents WHERE Document_ID={DocumentID};")
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
    def Transit(ProjectDBConnector, Cursor, RequestList, Products):
        SourceStoreID, DestinationStoreID = RequestList["SourceStoreID"], RequestList["DestinationStoreID"]
        for Product in Products:
            Cursor.execute(f"SELECT Quantity FROM Product_Quantity_Table WHERE Product_ID={Product['ProductID']} AND Store_ID={SourceStoreID};")
            if (ExistingQuantity := Cursor.fetchone()) == None:
                return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
            if ExistingQuantity[0] < Product['Quantity']:
                return {"StatusCode": ErrorCodes.InsufficientQuantity,"ProductID": Product['ProductID']}
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity - {Product['Quantity']} WHERE Product_ID={Product['ProductID']} AND Store_ID={SourceStoreID};")
            Cursor.execute(f"UPDATE Product_Quantity_Table SET Quantity = Quantity + {Product['Quantity']} WHERE Product_ID={Product['ProductID']} AND Store_ID={DestinationStoreID};")
        Cursor.execute(f"INSERT INTO Transition_Documents(Source_Store_ID,Destination_Store_ID) VALUES ('{SourceStoreID}','{DestinationStoreID}');\n")
        for Product in Products:
            Cursor.execute(f"INSERT INTO Transition_Items(Document_ID,Product_ID,Quantity) VALUES ("
                           f"LAST_INSERT_ID(),'{Product['ProductID']}','{Product['Quantity']}');\n")
        ProjectDBConnector.commit()
        return {"StatusCode": 0,"Data": "OK"}
    
    def SearchProducts(Cursor, RequestList: dict):
        StoreID = RequestList["StoreID"]
        Filters = list(RequestList.keys())
        Filters.remove("RequestType")
        Filters.remove("ProjectID")
        Filters.remove("StoreID")
        Sql = f"SELECT * FROM Products_Table JOIN Product_Quantity_Table ON Products_Table.Product_ID = Product_Quantity_Table.Product_ID AND Product_Quantity_Table.Store_ID = {StoreID} " 
        if Filters:
            Sql += f"WHERE Products_Table.{Filters[0]} LIKE '%{RequestList[Filters[0]]}%' "
        for Filter in Filters[1:]:
            Sql += "AND "
            value = RequestList[Filter]
            Sql += f"Products_Table.{Filter} LIKE '%{value}%' "
        Cursor.execute(Sql)
        return {"StatusCode":0,"Data":Cursor.dictfetchall()}
    
    def SearchInvoices(Cursor, RequestList):
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
        return {"StatusCode":0,"Data":Cursor.dictfetchall()}
    
    def SearchTransitionDocuments(Cursor, RequestList):
        StoreID = RequestList["StoreID"]
        Filters = list(RequestList.keys())
        Filters.remove("RequestType")
        Filters.remove("ProjectID")
        Filters.remove("StoreID")
        Sql = f"SELECT Document_ID,DateTime,Source_Store_ID,Source_Store.Store_Name AS Source_Store_Name,Destination_Store_ID,Destination_Store.Store_Name AS Destination_Store_Name FROM Transition_Documents " \
              f"JOIN Stores_Table AS Source_Store ON Transition_Documents.Source_Store_ID = Source_Store.Store_ID " \
              f"JOIN Stores_Table AS Destination_Store ON Transition_Documents.Destination_Store_ID = Destination_Store.Store_ID " \
              f"WHERE Transition_Documents.Source_Store_ID = {StoreID} OR Transition_Documents.Destination_Store_ID = {StoreID} "
        
        for Filter in Filters:
            Sql += f"{Filter}='{RequestList[Filter]}'"
            Sql += " AND "
        print(Sql)
        Cursor.execute(Sql[:-5])
        return {"StatusCode":0,"Data":Cursor.dictfetchall()}
    
    def GetInvoice(Cursor, RequestList):
        InvoiceType = RequestList["InvoiceType"]
        InvoiceID = RequestList["InvoiceID"]
        Cursor.execute(f"SELECT * FROM {InvoiceType}_Invoices WHERE Invoice_ID={InvoiceID};")
        if (InvoiceInfo := Cursor.dictfetchone()) == {}:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        Cursor.execute(f"SELECT * FROM {InvoiceType}_Items JOIN Products_Table ON {InvoiceType}_Items.Product_ID = Products_Table.Product_ID WHERE Invoice_ID={InvoiceID};")
        InvoiceInfo["Items"] = Cursor.dictfetchall()
        return {"StatusCode":0,"Data":InvoiceInfo}
    
    def GetTransitionDocument(Cursor, RequestList):
        DocumentID = RequestList["DocumentID"]
        Cursor.execute(f"SELECT Document_ID,DateTime,Source_Store_ID,Source_Store.Store_Name AS Source_Store_Name,Destination_Store_ID,Destination_Store.Store_Name AS Destination_Store_Name FROM Transition_Documents " \
              f"JOIN Stores_Table AS Source_Store ON Transition_Documents.Source_Store_ID = Source_Store.Store_ID " \
              f"JOIN Stores_Table AS Destination_Store ON Transition_Documents.Destination_Store_ID = Destination_Store.Store_ID " \
              f"WHERE Transition_Documents.Document_ID = {DocumentID}")
        if (DocumentInfo := Cursor.dictfetchone()) == {}:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"DocumentID"}
        Cursor.execute(f"SELECT * FROM Transition_Items JOIN Products_Table ON Transition_Items.Product_ID = Products_Table.Product_ID WHERE Document_ID={DocumentID}")
        DocumentInfo["Items"] = Cursor.dictfetchall()
        return {"StatusCode":0,"Data":DocumentInfo}
    
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
                case "RequestType" | "InvoiceType" | "ProjectID" | "StoreID":
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
def GetOrders(Cursor, RequestList: dict):
    i = 0
    Orders = []
    OrdersIDs = []
    TotalPrice = Decimal()
    while True:
        if i > PURCHASE_INVOICE_LENGTH:
            return {"StatusCode": ErrorCodes.ExceededMaximum, "Variable": "Orders"} , 0
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
        if (RequiredPrecision := Cursor.fetchone()) == None:
            return {"StatusCode":ErrorCodes.NonexistantProduct,"Variable":f"Orders[{i}][ProductID]"}, 0
        QuantityPrecision = len(str(Order["Quantity"])) - str(float(Order["Quantity"])).find(".") - 1
        if QuantityPrecision > RequiredPrecision[0]:
            return {"StatusCode":ErrorCodes.InvalidPrecision,"Data":""}, 0
        if not Order["ProductID"] in OrdersIDs:
            Orders.append(Order)
            OrdersIDs.append(Order["ProductID"])
        else:
            return {"StatusCode":ErrorCodes.RedundantValue,"Variable":f"Orders[{i}]"}, 0
        i += 1
    return Orders, TotalPrice

def getTransitedProducts(Cursor, RequestList: dict):
    i = 0
    Products = []
    while True:
        if i > PURCHASE_INVOICE_LENGTH:
            return {"StatusCode": ErrorCodes.ExceededMaximum, "Variable": "Products"}
        Product = {}
        if (Para := RequestList.get(f"Orders[{i}][ProductID]")) != None:
            if not isintstr(Para):
                return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":f"Products[{i}][ProductID]"}
            Product["ProductID"] = Para
            print(Para)
        if (Para := RequestList.get(f"Orders[{i}][Quantity]")) != None:
            if not isintstr(Para):
                return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":f"Products[{i}][Quantity]"}
            if float(Para) <= 0:
                return {"StatusCode":ErrorCodes.InvalidValue,"Variable":f"Products[{i}][Quantity]"}
            Product["Quantity"] = Decimal(Para)
        if not Product:
            break
        elif len(Product.keys()) < 2:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":f"Products[{i}]"}
        Cursor.execute(f"SELECT Partial_Quantity_Precision FROM Products_Table WHERE Product_ID={Product['ProductID']};")
        if (RequiredPrecision := Cursor.fetchone()) == None:
            return {"StatusCode":ErrorCodes.NonexistantProduct,"Variable":f"Products[{i}][ProductID]"}
        QuantityPrecision = len(str(Product["Quantity"])) - str(float(Product["Quantity"])).find(".") - 1
        if QuantityPrecision > RequiredPrecision[0]:
            return {"StatusCode": ErrorCodes.InvalidPrecision, "Data": ""}
        Products.append(Product)
        i += 1
    return Products
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
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if len(PersonName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable": "PersonName"}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        return ProcessRequest.CreateAccount(ProjectDBConnector, Cursor, RequestList)
    def AddStore(RequestList):
        try:
            ProjectID, StoreName = RequestList["ProjectID"], RequestList["StoreName"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}

        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        
        if len(StoreName) == 0:return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"StoreName"}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        return ProcessRequest.AddStore(ProjectDBConnector, Cursor, RequestList)
    
    def GetStores(RequestList):
        try:
            ProjectID = RequestList["ProjectID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectID = int(ProjectID)
        if ProjectsDBsConnectors.get(ProjectID) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        Cursor = connections[f"Project{ProjectID}"].cursor()
        return ProcessRequest.GetStores(Cursor)
    
    def AddProduct(RequestList):
        try:
            ProjectID = RequestList["ProjectID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType, "Variable":"ProjectID"}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
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
        return ProcessRequest.AddProduct(ProjectDBConnector, Cursor, RequestList)
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
        if ProjectsDBsConnectors.get(int(ProjectID)) == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
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
        return ProcessRequest.EditProductInfo(ProjectDBConnector, Cursor, RequestList)
    def GetProductInfo(RequestList):
        try:
            ProjectID, ProductID = RequestList["ProjectID"], RequestList["ProductID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":"ProjectID"}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"ProjectID"}
        if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
 
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = connections[f"Project{ProjectID}"].cursor()
        return ProcessRequest.GetProductInfo(Cursor, RequestList)
    
    def GetProductsQuantities(RequestList):
        try:
            ProjectID, StoreID = RequestList["ProjectID"], RequestList["StoreID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        i = 0
        ProductsIDs = []
        while True:
            if (ProductID := RequestList.get(f"ProductsIDs[{i}]")) == None: break
            if not isintstr(ProductID): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":f"ProductsIDs[{i}]"}
            ProductsIDs.append(ProductID)
            i+=1
        if len(ProductsIDs) == 0: return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"ProductsIDs"}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        Cursor = connections[f"Project{ProjectID}"].cursor()
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        return ProcessRequest.GetProductsQuantities(Cursor, RequestList, ProductsIDs)
    
    def Sell(RequestList):
        try:
            ProjectID, StoreID, ClientName, Paid = (
                RequestList["ProjectID"],RequestList["StoreID"], RequestList["ClientName"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(ClientName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"ClientName"}
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if int(Paid) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        Orders, RequiredAmount = GetOrders(Cursor, RequestList)
        if isinstance(Orders, dict):
            return Orders
        if len(Orders) == 0:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        RequestList["Paid"] = Decimal(Paid)
        if RequestList["Paid"] > RequiredAmount:
            return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"Paid"}
        return ProcessRequest.Sell(ProjectDBConnector, Cursor, RequestList, Orders, RequiredAmount)
    def Purchase(RequestList):
        try:
            ProjectID, StoreID, SellerName, Paid = (
                RequestList["ProjectID"], RequestList["StoreID"], RequestList["SellerName"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables, "Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(SellerName) == 0: return {"StatusCode": ErrorCodes.EmptyValue, "Variable": "SellerName"}
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":"Paid"}
        if int(Paid) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"Paid"}
        Orders, TotalPrice = GetOrders(Cursor, RequestList)
        if isinstance(Orders, dict):
            return Orders
        if len(Orders) == 0:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        RequestList["Paid"] = Decimal(Paid)
        if RequestList["Paid"] > TotalPrice:
            return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"Paid"}
        return ProcessRequest.Purchase(ProjectDBConnector, Cursor, RequestList, Orders, TotalPrice)
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
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}

        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT Store_ID FROM Selling_Invoices WHERE Invoice_ID={InvoiceID};")
        if (StoreID := Cursor.fetchone()) == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
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
        return ProcessRequest.EditSellingInvoice(ProjectDBConnector, Cursor, RequestList, StoreID[0], Orders, TotalPrice)
    def EditPurchaseInvoice(RequestList):
        try:
            ProjectID, InvoiceID, SellerName, Paid = (
                RequestList["ProjectID"], RequestList["InvoiceID"], RequestList["SellerName"], RequestList["Paid"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}

        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        
        Cursor.execute(f"SELECT Store_ID FROM Purchase_Invoices WHERE Invoice_ID={InvoiceID};")
        if (StoreID := Cursor.fetchone()) == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        if not isintstr(Paid): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if len(SellerName) == 0: return {"StatusCode":ErrorCodes.EmptyValue,"Variable":"SellerName"}
        if int(Paid) < 0: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        Orders, TotalPrice = GetOrders(Cursor, RequestList)
        if isinstance(Orders, dict):
            return Orders
        if len(Orders) == 0:
            return {"StatusCode":ErrorCodes.MissingVariables,"Variable":"Orders"}
        RequestList["Paid"] = Decimal(Paid)
        if RequestList["Paid"] > TotalPrice:
            return {"StatusCode":ErrorCodes.InvalidValue,"Variable": "Paid"}
        return ProcessRequest.EditPurchaseInvoice(ProjectDBConnector, Cursor, RequestList, StoreID[0], Orders, TotalPrice)
    
    def EditRefundInvoice(RequestList):
        # TODO: review this
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
    
    def EditTransitionDocument(RequestList):
        try:
            ProjectID, DocumentID, SourceStoreID, DestinationStoreID = (RequestList["ProjectID"],
                RequestList["DocumentID"], RequestList["SourceStoreID"], RequestList["DestinationStoreID"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Variable": "ProjectID"}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        if SourceStoreID == DestinationStoreID:
            return {"StatusCode": ErrorCodes.InvalidValue,"Variable": "StoresIDs"}
        if not isintstr(SourceStoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT Store_ID FROM Stores_Table WHERE Store_ID={SourceStoreID};")
        if Cursor.fetchone() == None:
            return {"StatusCode": ErrorCodes.ValueNotFound, "Variable": "SourceStoreID"}
        if not isintstr(DestinationStoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT Store_ID FROM Stores_Table WHERE Store_ID={DestinationStoreID};")
        if Cursor.fetchone() == None:
            return {"StatusCode": ErrorCodes.ValueNotFound, "Variable": "DestinationStoreID"}
        Cursor.execute(f"SELECT Document_ID FROM Transition_Documents WHERE Document_ID={DocumentID}")
        if Cursor.fetchone() == None:
            return {"StatusCode": ErrorCodes.ValueNotFound, "Variable": "DocumentID"}
        Orders = getTransitedProducts(Cursor, RequestList)
        if isinstance(Orders, dict):
            return Orders
        if len(Orders) == 0:
            return {"StatusCode": ErrorCodes.MissingVariables, "Variable": "Products"}
        return ProcessRequest.EditTransitionDocument(ProjectDBConnector, Cursor, RequestList, Orders)
    
    def DeletePurchaseInvoice(RequestList):
        try:
            ProjectID, InvoiceID = RequestList["ProjectID"], RequestList["InvoiceID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}

        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        Cursor.execute(f"SELECT Store_ID FROM Purchase_Invoices WHERE Invoice_ID={InvoiceID};")
        if (StoreID := Cursor.fetchone()) == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        return ProcessRequest.DeletePurchaseInvoice(ProjectDBConnector, Cursor, RequestList, StoreID[0])
    def DeleteSellingInvoice(RequestList):
        try:
            ProjectID, InvoiceID = RequestList["ProjectID"], RequestList["InvoiceID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        Cursor.execute(f"SELECT Store_ID FROM Selling_Invoices WHERE Invoice_ID={InvoiceID};")
        if (StoreID := Cursor.fetchone()) == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"InvoiceID"}
        return ProcessRequest.DeleteSellingInvoice(ProjectDBConnector, Cursor, RequestList, StoreID[0])
    def DeleteRefundInvoice(RequestList):
        pass
    def DeleteTransitionDocument(RequestList):
        try:
            ProjectID, DocumentID = RequestList["ProjectID"], RequestList["DocumentID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(DocumentID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        Cursor.execute(f"SELECT Document_ID FROM Transition_Documents WHERE Document_ID={DocumentID};")
        if Cursor.fetchone() == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"DocumentID"}
        return ProcessRequest.DeleteTransitionDocument(ProjectDBConnector, Cursor, RequestList)
    
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
            ProjectID, SourceStoreID, DestinationStoreID = (RequestList["ProjectID"],
                RequestList["SourceStoreID"], RequestList["DestinationStoreID"])
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Variable": "ProjectID"}
        ProjectDBConnector = connections[f"Project{ProjectID}"]
        Cursor = ProjectDBConnector.cursor()
        if SourceStoreID == DestinationStoreID:
            return {"StatusCode": ErrorCodes.InvalidValue,"Variable": "StoresIDs"}
        if not isintstr(SourceStoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT Store_ID FROM Stores_Table WHERE Store_ID={SourceStoreID};")
        if Cursor.fetchone() == None:
            return {"StatusCode": ErrorCodes.ValueNotFound, "Variable": "SourceStoreID"}
        if not isintstr(DestinationStoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor.execute(f"SELECT Store_ID FROM Stores_Table WHERE Store_ID={DestinationStoreID};")
        if Cursor.fetchone() == None:
            return {"StatusCode": ErrorCodes.ValueNotFound, "Variable": "DestinationStoreID"}
        Products = getTransitedProducts(Cursor, RequestList)
        if isinstance(Products, dict):
            return Products
        if len(Products) == 0:
            return {"StatusCode": ErrorCodes.MissingVariables, "Variable": "Products"}
        return ProcessRequest.Transit(ProjectDBConnector, Cursor, RequestList, Products)
    def SearchProducts(RequestList):
        try:
            ProjectID, StoreID = RequestList["ProjectID"], RequestList["StoreID"]
        except:
            return {"StatusCode": ErrorCodes.MissingVariables, "Data": ""}
        if not isintstr(ProjectID): return {"StatusCode": ErrorCodes.InvalidDataType, "Variable": "ProjectID"}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None:
            print(ProjectsDBsConnectors)
            return {"StatusCode": ErrorCodes.ValueNotFound, "Variable": "ProjectID"}
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

        #ProjectDBConnector = ProjectsDBsConnectors[ProjectID]
        #Cursor = ProjectDBConnector.cursor(dictionary=True, buffered=True)
        Cursor = connections[f"Project{ProjectID}"].cursor()
        return ProcessRequest.SearchProducts(Cursor, RequestList)
    def SearchInvoices(RequestList):
        try:
            ProjectID, InvoiceType, StoreID = RequestList["ProjectID"], RequestList["InvoiceType"], RequestList["StoreID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}

        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
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
        Cursor = connections[f"Project{ProjectID}"].cursor()
        return ProcessRequest.SearchInvoices(Cursor, RequestList)
    def SearchTransitionDocuments(RequestList):
        try:
            ProjectID, StoreID = RequestList["ProjectID"], RequestList["StoreID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":"ProjectID"}
        if not isintstr(StoreID): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable":"StoreID"}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        Cursor = connections[f"Project{ProjectID}"].cursor()
        Cursor.execute(f"SELECT Store_ID FROM Stores_Table WHERE Store_ID={StoreID};")
        if Cursor.fetchone() == None:
            return {"StatusCode":ErrorCodes.ValueNotFound,"Variable":"StoreID"}
        for Filter in RequestList.keys():
            match Filter:
                case "Document_ID" | "Source_Store_ID" | "Destination_Store_ID" | "Product_ID" | "Quantity":
                    if not isintstr(RequestList[Filter]): return {"StatusCode":ErrorCodes.InvalidDataType,"Variable": Filter}
                case "DateTime":
                    if not datetime.strptime(RequestList[Filter], "%y-%m-%d %H-%M-%S"): return {"StatusCode":ErrorCodes.InvalidValue,"Variable":"DateTime"}
                case "RequestType" | "InvoiceType" | "ProjectID"| "StoreID":
                    pass
                case _:
                    return {"StatusCode":ErrorCodes.InvalidFilter,"Variable":Filter}
        return ProcessRequest.SearchTransitionDocuments(Cursor, RequestList)
    
    def GetInvoice(RequestList):
        try:
            ProjectID, InvoiceType, InvoiceID = RequestList["ProjectID"], RequestList["InvoiceType"], RequestList["InvoiceID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}

        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(InvoiceID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if not InvoiceType in ValidInvoiceTypes: return {"StatusCode":ErrorCodes.InvalidValue,"Data":""}
        Cursor = connections[f"Project{ProjectID}"].cursor()
        return ProcessRequest.GetInvoice(Cursor, RequestList)
    
    def GetTransitionDocument(RequestList):
        try:
            ProjectID, DocumentID = RequestList["ProjectID"], RequestList["DocumentID"]
        except:
            return {"StatusCode":ErrorCodes.MissingVariables,"Data":""}
        if not isintstr(ProjectID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        if ProjectsDBsConnectors.get(int(ProjectID)) == None: return {"StatusCode":ErrorCodes.ValueNotFound,"Data":""}
        if not isintstr(DocumentID): return {"StatusCode":ErrorCodes.InvalidDataType,"Data":""}
        Cursor = connections[f"Project{ProjectID}"].cursor()
        
        return ProcessRequest.GetTransitionDocument(Cursor, RequestList)
    
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
        Cursor.execute(f"SELECT Partial_Quantity_Precision FROM Products_Table WHERE Product_ID={ProductID};")
        RequiredPrecision = Cursor.fetchone()["Partial_Quantity_Precision"]
        QuantityPrecision = len(str(CurrentQuantity)) - str(CurrentQuantity).index(".") - 1
        if QuantityPrecision > RequiredPrecision: return {"StatusCode":ErrorCodes.InvalidPrecision,"Data":""}
        return ProcessRequest.AdjustProductQuantity(RequestList)
def SanatizeRequest(RequestList):
    if isinstance(RequestList, list):
        for i in range(len(RequestList)):
            RequestList[i] = SanatizeRequest(RequestList[i])
    elif isinstance(RequestList, dict):
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
        case "GetProductsQuantities":
            Response = CheckValidation.GetProductsQuantities(RequestList)
        case "Sell":
            Response = CheckValidation.Sell(RequestList)
        case "Purchase":
            Response = CheckValidation.Purchase(RequestList)
        case "Refund":
            Response = CheckValidation.Refund(RequestList)
        case "Transit":
            Response = CheckValidation.Transit(RequestList)
        case "EditPurchaseInvoice":
            Response = CheckValidation.EditPurchaseInvoice(RequestList)
        case "EditSellingInvoice":
            Response = CheckValidation.EditSellingInvoice(RequestList)
        case "EditRefundInvoice":
            Response = CheckValidation.EditRefundInvoice(RequestList)
        case "EditTransitionDocument":
            Response = CheckValidation.EditTransitionDocument(RequestList)
        case "DeletePurchaseInvoice":
            Response = CheckValidation.DeletePurchaseInvoice(RequestList)
        case "DeleteSellingInvoice":
            Response = CheckValidation.DeleteSellingInvoice(RequestList)
        case "DeleteRefundInvoice":
            Response = CheckValidation.DeleteRefundInvoice(RequestList)
        case "DeleteTransitionDocument":
            Response = CheckValidation.DeleteTransitionDocument(RequestList)
        case "AddToAccount":
            Response = CheckValidation.AddToAccount(RequestList)
        case "DeductFromAccount":
            Response = CheckValidation.DeductFromAccount(RequestList)
        case "SearchProducts":
            Response = CheckValidation.SearchProducts(RequestList)
        case "SearchInvoices":
            Response = CheckValidation.SearchInvoices(RequestList)
        case "SearchTransitionDocuments":
            Response = CheckValidation.SearchTransitionDocuments(RequestList)
        case "GetInvoice":
            Response = CheckValidation.GetInvoice(RequestList)
        case "GetTransitionDocument":
            Response = CheckValidation.GetTransitionDocument(RequestList)
        case "AdjustProductQuantity":
            Response = CheckValidation.AdjustProductQuantity(RequestList)
        case _:
            Response = {"StatusCode": ErrorCodes.InvalidValue,"Variable": "RequestType"}
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



