import sys
import json
import enum
import mysql.connector
from datetime import datetime

DataBaseConnector = mysql.connector.connect(
    host="localhost",
    user="root",
    password="000600",
    database="Elfarid_Metal",
    collation="utf8mb4_unicode_ci", charset="utf8mb4"
)
global Cursor
global GeneratedSql
global StoreID
Cursor = DataBaseConnector.cursor(dictionary=True)
GeneratedSql = ""
StoreID = 0
class ErrorCodes(enum.Enum):
    InvalidDataType = enum.auto()
    MissingVariables = enum.auto()
    EmptyValue = enum.auto()
    InvalidValue = enum.auto()
    DuplicateName = enum.auto()
    ValueNotFound = enum.auto()


class ProcessRequest:

    #TODO: Sanitizing user input to prevent sql injection
    #TODO: Defining error codes
    def CreateAccount(RequestList):
        PersonName = RequestList["PersonName"]
        Cursor.execute(f"INSERT INTO Accounts(Name) VALUES ('{PersonName}');")
        DataBaseConnector.commit()
        return (0,"OK")

    def AddStore(RequestList):
        global Cursor
        StoreName = RequestList["StoreName"]
        Cursor.execute("Select Product_ID from Products_Table;\n")
        ProductsIDs = Cursor.fetchall()
        Cursor.execute(f"INSERT INTO Stores_Table(Store_Name) VALUES ('{StoreName}');\n")
        for ProductID in ProductsIDs:
            Cursor.execute(f"INSERT INTO Product_Quantity_Table VALUES (LAST_INSERT_ID(),'{ProductID["Product_ID"]}',0);\n")
        DataBaseConnector.commit()
        return (0,"OK")

    def AddProduct(RequestList):
        #Check if Product already exist with the same trademark
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_Name='{RequestList['ProductName']}' AND Trademark='{RequestList['Trademark']}';")
        if Cursor.fetchone():
            return (ErrorCodes.DuplicateName,"Product already exist with the same trademark")
        Cursor.execute(f"SELECT Store_ID from Stores_Table;")
        StoresIDs = Cursor.fetchall()
        Cursor.execute(
            f"INSERT INTO Products_Table(Product_Name,Trademark,Manufacture_Country,Purchase_Price,Wholesale_Price,"
            f"Retail_Price) VALUES ('{RequestList['ProductName']}','{RequestList['Trademark']}','{RequestList['ManufactureCountry']}',{RequestList['PurchasePrice']},{RequestList['WholesalePrice']},"
            f"{RequestList['RetailPrice']});")
        for StoreID in StoresIDs:
            Cursor.execute(f"INSERT INTO Product_Quantity_Table(Store_ID,Product_ID,Quantity) VALUES ({StoreID["Store_ID"]},LAST_INSERT_ID(),0)")
        DataBaseConnector.commit()
        return (0,"OK")
    def EditProductInfo(RequestList):
        ProductID, ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice = (
            RequestList["ProductID"], RequestList["ProductName"], RequestList["Trademark"],
            RequestList["ManufactureCountry"], RequestList["PurchasePrice"], RequestList["WholesalePrice"],
            RequestList["RetailPrice"])
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_ID={ProductID};")
        if Cursor.fetchone() is None:
            return (ErrorCodes.ValueNotFound,f"There is no product with id {ProductID}")
        Cursor.execute(
            f"UPDATE Products_Table SET Product_Name = '{ProductName}', Trademark = '{Trademark}', "
            f"Manufacture_Country = '{ManufactureCountry}', Purchase_Price={PurchasePrice}, Wholesale_Price="
            f"{WholesalePrice}, Retail_Price={RetailPrice} WHERE Product_ID={ProductID} ")
        DataBaseConnector.commit()
        return (0,"OK")
    def GetProductInfo(RequestList):
        ProductID = RequestList['ProductID']
        Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_ID={ProductID};")
        ProductInfo = Cursor.fetchone()
        if ProductInfo is None:
            return (ErrorCodes.ValueNotFound,f"There is no product which id is {ProductID}")
        Cursor.execute("SELECT Store_ID,Quantity FROM Product_Quantity_Table;")
        ProductQuantities = Cursor.fetchall()
        ProductInfo["Product_Quantity_Table"] = ProductQuantities
        return ProductInfo
    def Sell(RequestList):
            ClientID = RequestList["ClientID"]
            Orders = RequestList["Orders"]
            TotalPrice = 0
            for Order in Orders:
                Cursor.execute(f"SELECT Quantity_Store{StoreID} FROM Products_Table WHERE Product_ID={Order['ProductID']}")
                ExistingQuantity = Cursor.fetchall()[0][0]
                if ExistingQuantity < Order["Quantity"]:
                    pass
                TotalPrice += Order["Price"]
                GeneratedSql += (f"INSERT INTO Selling_Operations(Invoice_ID,Product_ID,Quantity,Selling_Price) VALUES "
                                 f"(@Invoice_ID,'{Order["ProductID"]}','{Order["Quantity"]}',"
                                 f"'{Order["Price"]}');\n")
            GeneratedSql = "SET @Invoice_ID = LAST_INSERT_ID();\n" + GeneratedSql
            GeneratedSql = f"INSERT INTO Selling_Invoices(Store_Id,Client_ID,Total_Price) VALUES ('{StoreID}','{ClientID}','{TotalPrice}');\n" + GeneratedSql
            if RequestList["Paid"]>TotalPrice:
                return "ER"
            elif RequestList["Paid"]<TotalPrice:
                Amount = TotalPrice - RequestList["Paid"]
                GeneratedSql += ProcessRequest('{"RequestType":"AddToAccount","PersonID":"%s","Description":"CONCAT(\'فاتورة بيع #S-\',@Invoice_ID)","Amount":"%s"}' % (ClientID, Amount))
    def Purchase(RequestList):
            SellerID = RequestList["SellerID"]
            Orders = RequestList["Orders"]
            TotalPrice = 0
            for Order in Orders:
                TotalPrice += Order["Price"]
                GeneratedSql += (f"INSERT INTO Purchase_Operations(Invoice_ID,Product_ID,Quantity,Purchase_Price) "
                                 f"VALUES (@Invoice_ID,'{Order["ProductID"]}','{Order["Quantity"]}',"
                                 f"'{Order["Price"]}');\n")
            GeneratedSql = "SET @Invoice_ID = LAST_INSERT_ID();\n" + GeneratedSql
            GeneratedSql = f"INSERT INTO Purchase_Invoices(Store_Id,Seller_ID,Total_Price) VALUES ('{StoreID}','{SellerID}','{TotalPrice}');\n" + GeneratedSql
            if RequestList["Paid"]<TotalPrice:
                Amount = TotalPrice - RequestList["Paid"]
                GeneratedSql+=ProcessRequest(f'{"RequestType":"DeductFromAccount","PersonID":{SellerID},"Description":"CONCAT(\'فاتورة شراء #P-\',@Invoice_ID)","Amount":{Amount}}')
    def Refund(RequestList):
            ClientID = RequestList["ClientID"]
            Orders = RequestList["Orders"]
            TotalPrice = 0
            for Order in Orders:
                TotalPrice += Order["Price"]
                GeneratedSql += (f"INSERT INTO Refund_Operations(Invoice_ID,Product_ID,Quantity,Refund_Price) VALUES ("
                                 f"LAST_INSERT_ID(),'{Order["ProductID"]}','{Order["Quantity"]}','{Order["Price"]}');\n")
            GeneratedSql += f"INSERT INTO Refund_Invoices(Store_Id,Client_ID,Total_Price) VALUES ('{StoreID}','{ClientID}','{TotalPrice}');\n"

    def AddToAccount(RequestList):
            PersonID = RequestList["PersonID"]
            Description = RequestList["Description"]
            Amount = RequestList["Amount"]
            #Description variable is left without quotes to enable using sql statement
            GeneratedSql = f"INSERT INTO Accounts_Operations('Person_ID','Description','Required') VALUES ({PersonID},{Description},{Amount})\n"
            GeneratedSql += f"SET @Old_Balance = (SELECT Balance FROM Accounts WHERE Person_ID = {PersonID});\n"
            GeneratedSql += f"UPDATE Accounts SET Balance = @Old_Balance+{Amount} WHERE Person_ID = {PersonID};\n"
    def DeductFromAccount(RequestList):
            PersonName = RequestList["PersonName"]
            Description = RequestList["Description"]
            Amount = RequestList["Amount"]
            GeneratedSql = f"SET @PersonID = (SELECT Person_ID FROM Accounts WHERE Person_Name = '{PersonName}')"
            # Description variable is left without quotes to enable using sql statement
            GeneratedSql += f"INSERT INTO Accounts_Operations('Person_ID','Operation_Description','Amount') VALUES (@PersonID,{Description},{Amount})\n"
            GeneratedSql += f"SET @Old_Balance = (SELECT Balance FROM Accounts WHERE Person_ID = @PersonID);\n"
            GeneratedSql += f"UPDATE Accounts SET Balance = @Old_Balance-{Amount} WHERE Person_ID = @PersonID;\n"

    def Transit(RequestList):
            GeneratedSql = f"INSERT INTO Transition_Documents(Source_Store_ID,Destination_Store_ID) VALUES ('{RequestList['SourceStoreID']}','{RequestList['DestinationStoreID']}');\n"
            Products = RequestList["Products"]
            for Product in Products:
                GeneratedSql += (f"INSERT INTO Transition_Operations(Document_ID,Product_ID,Quantity) VALUES ("
                                 f"LAST_INSERT_ID(),'{Product['ProductID']}','{Product['Quantity']}');\n")
    def GetHistory(RequestList):
            Tables = RequestList["Tables"]
            Timelapse = RequestList["Timelapse"]
            DateTables = ["Purchase_Invoices","Selling_Invoices","Refund_Invoices","Transition_Documents"]
            for Table in Tables:
                if Table not in DateTables:
                    return "ER"
                GeneratedSql += f"SELECT * FROM {Table} WHERE Store_ID={StoreID} AND DateTime BETWEEN '{Timelapse[0]}' AND '{Timelapse[1]}';\n"
            Cursor.execute(GeneratedSql)
            Response = Cursor.fetchall()
            return Response

class SearchFiltersValidation:
    def SellingInvoices(self,Filter):
        for key in Filter:
            match key:
                case "Invoice_ID" "Client_ID":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "DateTime":
                    if not isinstance(Filter[key],str): return (ErrorCodes.InvalidDataType,"")
                    if not datetime.strptime(Filter[key],"%y-%m-%d %H-%M-%S"): return (ErrorCodes.InvalidValue,"")
                case "Total_Price":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Paid":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Transferred_To_Account":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Product_ID":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Product_Name":
                    if not isinstance(Filter[key],str): return (ErrorCodes.InvalidDataType,"")
                case "Quantity":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Selling_Price":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
        return 0
    def PurchaseInvoices(self,Filter):
        for key in Filter:
            match key:
                case "Invoice_ID" "Seller_ID":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "DateTime":
                    if not isinstance(Filter[key],str): return (ErrorCodes.InvalidDataType,"")
                    if not datetime.strptime(Filter[key],"%y-%m-%d %H-%M-%S"): return (ErrorCodes.InvalidValue,"")
                case "Total_Price":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Paid":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Transferred_To_Account":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Product_ID":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Product_Name":
                    if not isinstance(Filter[key],str): return (ErrorCodes.InvalidDataType,"")
                case "Quantity":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Purchase_Price":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
        return 0
    def RefundInvoices(self,Filter):
        for key in Filter:
            match key:
                case "Invoice_ID" "Client_ID":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "DateTime":
                    if not isinstance(Filter[key],str): return (ErrorCodes.InvalidDataType,"")
                    if not datetime.strptime(Filter[key],"%y-%m-%d %H-%M-%S"): return (ErrorCodes.InvalidValue,"")
                case "Total_Price":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Paid":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Transferred_To_Account":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Product_ID":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Product_Name":
                    if not isinstance(Filter[key],str): return (ErrorCodes.InvalidDataType,"")
                case "Quantity":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "Refund_Price":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
        return 0
    def TransitionDocuments(self,Filter):
        for key in Filter:
            match key:
                case "Document_ID" "Source_Store_ID" "Destination_Store_ID" "Product_ID" "Quantity":
                    if not isinstance(Filter[key],int): return (ErrorCodes.InvalidDataType,"")
                case "DateTime":
                    if not isinstance(Filter[key], str): return (ErrorCodes.InvalidDataType, "")
                    if not datetime.strptime(Filter[key], "%y-%m-%d %H-%M-%S"): return (ErrorCodes.InvalidValue, "")
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
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(PersonName,str):return (ErrorCodes.InvalidDataType,"PersonName")
        if PersonName.len()==0:return (ErrorCodes.EmptyValue, "PersonName")
        return ProcessRequest.CreateAccount(RequestList)
    def AddStore(RequestList):
        try:
            StoreName=RequestList["StoreName"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(StoreName,str):return (ErrorCodes.InvalidDataType,"StoreName")
        if len(StoreName)==0:return (ErrorCodes.EmptyValue,"StoreName")
        return ProcessRequest.AddStore(RequestList)
    def AddProduct(RequestList):
        try:
            ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice =(
                RequestList["ProductName"], RequestList["Trademark"], RequestList["ManufactureCountry"],
                RequestList["PurchasePrice"],RequestList["WholesalePrice"], RequestList["RetailPrice"]
            )
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(ProductName,str): return (ErrorCodes.InvalidDataType,"ProductName")
        if not isinstance(Trademark,str):return (ErrorCodes.InvalidDataType,"Trademark")
        if not isinstance(ManufactureCountry, str):return (ErrorCodes.InvalidDataType, "ManufactureCountry")
        if not isinstance(PurchasePrice, int):return (ErrorCodes.InvalidDataType, "Trademark")
        if not isinstance(WholesalePrice, int):return (ErrorCodes.InvalidDataType, "WholesalePrice")
        if not isinstance(RetailPrice, int):return (ErrorCodes.InvalidDataType, "RetailPrice")
        if ProductName.len()==0: return (ErrorCodes.EmptyValue, "ProductName")
        if Trademark.len()==0:return (ErrorCodes.EmptyValue,"Trademark")
        if ManufactureCountry.len()==0:return (ErrorCodes.EmptyValue,"ManufactureCountry")
        if PurchasePrice < 0: return (ErrorCodes.InvalidValue, "PurchasePrice")
        if WholesalePrice<0:return (ErrorCodes.InvalidValue,"WholesalePrice")
        if RetailPrice<0:return (ErrorCodes.InvalidValue,"RetailPrice")
        return ProcessRequest.AddProduct(RequestList)
    def EditProductInfo(RequestList):
        try:
            ProductID, ProductName, Trademark, ManufactureCountry, PurchasePrice, WholesalePrice, RetailPrice = (
                RequestList["ProductID"], RequestList["ProductName"], RequestList["Trademark"],
                RequestList["ManufactureCountry"], RequestList["PurchasePrice"], RequestList["WholesalePrice"],
                RequestList["RetailPrice"]
            )
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(ProductID,int): return (ErrorCodes.InvalidDataType,"ProductID")
        if not isinstance(ProductName, str): return (ErrorCodes.InvalidDataType, "ProductName")
        if not isinstance(Trademark, str): return (ErrorCodes.InvalidDataType, "Trademark")
        if not isinstance(ManufactureCountry, str): return (ErrorCodes.InvalidDataType, "ManufactureCountry")
        if not isinstance(PurchasePrice, int): return (ErrorCodes.InvalidDataType, "Trademark")
        if not isinstance(WholesalePrice, int): return (ErrorCodes.InvalidDataType, "WholesalePrice")
        if not isinstance(RetailPrice, int): return (ErrorCodes.InvalidDataType, "RetailPrice")
        if ProductName.len() == 0: return (ErrorCodes.EmptyValue, "ProductName")
        if Trademark.len() == 0: return (ErrorCodes.EmptyValue, "Trademark")
        if ManufactureCountry.len() == 0: return (ErrorCodes.EmptyValue, "ManufactureCountry")
        if PurchasePrice < 0: return (ErrorCodes.InvalidValue, "PurchasePrice")
        if WholesalePrice < 0: return (ErrorCodes.InvalidValue, "WholesalePrice")
        if RetailPrice < 0: return (ErrorCodes.InvalidValue, "RetailPrice")
        return ProcessRequest.EditProductInfo(RequestList)
    def GetProductInfo(RequestList):
        try:
            ProductID = RequestList["ProductID"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(ProductID,int): return (ErrorCodes.InvalidDataType,"")
        return ProcessRequest.GetProductInfo(RequestList)

    def Sell(RequestList):
        try:
            ClientID, Orders, Paid = (
                RequestList["ClientID"], RequestList["Orders"], RequestList["Paid"])
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(ClientID, int): return (ErrorCodes.InvalidDataType,"ClientID")
        if not isinstance(Orders, list): return (ErrorCodes.InvalidDataType,"Orders")
        if not isinstance(Paid, int): return (ErrorCodes.InvalidDataType,"Paid")
        if Paid<0: return (ErrorCodes.InvalidValue,"Paid")
        for Order in Orders:
            try:
                ProductID, Quantity, Price = Order["ProductID"], Order["Quantity"], Order["Price"]
            except:
                return (ErrorCodes.MissingVariables,"")
            if not isinstance(ProductID, int): return (ErrorCodes.InvalidDataType,"ProductID")
            if not isinstance(Quantity, int): return (ErrorCodes.InvalidDataType,"Quantity")
            if not isinstance(Price, int): return (ErrorCodes.InvalidDataType,"Price")
            if Quantity<=0: return (ErrorCodes.InvalidValue,"Quantity")
            if Price<0: return (ErrorCodes.InvalidValue,"Price")
        return ProcessRequest.Sell(RequestList)
    def Purchase(RequestList):
        try:
            SellerID, Orders, Paid = (
                RequestList["SellerID"], RequestList["Orders"], RequestList["Paid"])
        except:
            return (ErrorCodes.MissingVariables, "")
        if not isinstance(SellerID, int): return (ErrorCodes.InvalidDataType, "ClientID")
        if not isinstance(Orders, list): return (ErrorCodes.InvalidDataType, "Orders")
        if not isinstance(Paid, int): return (ErrorCodes.InvalidDataType, "Paid")
        if Paid < 0: return (ErrorCodes.InvalidValue, "Paid")
        for Order in Orders:
            try:
                ProductID, Quantity, Price = Order["ProductID"], Order["Quantity"], Order["Price"]
            except:
                return (ErrorCodes.MissingVariables, "")
            if not isinstance(ProductID, int): return (ErrorCodes.InvalidDataType, "ProductID")
            if not isinstance(Quantity, int): return (ErrorCodes.InvalidDataType, "Quantity")
            if not isinstance(Price, int): return (ErrorCodes.InvalidDataType, "Price")
            if Quantity <= 0: return (ErrorCodes.InvalidValue, "Quantity")
            if Price < 0: return (ErrorCodes.InvalidValue, "Price")
        return ProcessRequest.Purchase(RequestList)
    def Refund(RequestList):
        try:
            ClientID , Orders = RequestList["ClientID"], RequestList["Orders"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(ClientID,int): return (ErrorCodes.InvalidDataType,"")
        if not isinstance(Orders,list): return (ErrorCodes.InvalidDataType,"")
        for Order in Orders:
            try:
                ProductID, Quantity, Price = Order["ProductID"], Order["Quantity"], Order["Price"]
            except:
                return (ErrorCodes.MissingVariables,"")
            if not isinstance(ProductID,int): return (ErrorCodes.InvalidDataType,"")
            if not isinstance(Quantity,int): return (ErrorCodes.InvalidDataType,"")
            if not isinstance(Price,int): return (ErrorCodes.InvalidDataType,"")
            if Quantity <= 0: return (ErrorCodes.InvalidValue,"")
            if Price<0: return (ErrorCodes.InvalidValue,"")
        return ProcessRequest.Refund(RequestList)

    def AddToAccount(RequestList):
        try:
            PersonID, Description, Amount = RequestList["PersonID"], RequestList["Description"], RequestList["Amount"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(PersonID,int): return (ErrorCodes.InvalidDataType,"")
        if not isinstance(Description,str): return (ErrorCodes.InvalidDataType,"")
        if not (isinstance(Amount,float) or isinstance(Amount,int)): return (ErrorCodes.InvalidDataType,"")
        if PersonID<0: return (ErrorCodes.InvalidValue,"")
        if len(Description)==0: return (ErrorCodes.InvalidValue,"")
        if Amount<=0: return (ErrorCodes.InvalidValue,"")
        return ProcessRequest.AddToAccount(RequestList)
    def DeductFromAccount(RequestList):
        try:
            PersonID, Description, Amount = RequestList["PersonID"], RequestList["Description"], RequestList["Amount"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(PersonID,int): return (ErrorCodes.InvalidDataType,"")
        if not isinstance(Description,str): return (ErrorCodes.InvalidDataType,"")
        if not (isinstance(Amount,float) or isinstance(Amount,int)): return (ErrorCodes.InvalidDataType,"")
        if len(Description)==0: return (ErrorCodes.InvalidValue,"")
        if Amount<=0: return (ErrorCodes.InvalidValue,"")
        return ProcessRequest.DeductFromAccount(RequestList)
    def Transit(RequestList):
        try:
            SourceStoreID, DestinationStoreID, Products = (RequestList["SourceStoreID"],
                RequestList["DestinationStoreID"], RequestList["Products"])
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(SourceStoreID,int): return (ErrorCodes.InvalidDataType,"")
        if not isinstance(DestinationStoreID,int): return (ErrorCodes.InvalidDataType,"")
        if not isinstance(Products,list): return (ErrorCodes.InvalidDataType,"")
        if len(Products)==0: return (ErrorCodes.MissingVariables,"")
        for Product in Products:
            if not isinstance(Product,dict): return (ErrorCodes.InvalidDataType,"")
            try:
                ProductID, Quantity = Product["ProductID"], Product["Quantity"]
            except:
                return (ErrorCodes.MissingVariables,"")
            if not isinstance(ProductID,int): return (ErrorCodes.InvalidDataType,"")
            if not (isinstance(Quantity,int) or isinstance(Quantity,float)): return (ErrorCodes.InvalidDataType,"")
            if Quantity<=0: return (ErrorCodes.InvalidValue,"")
        return ProcessRequest.Transit(RequestList)
    def SearchInvoice(RequestList):
        try:
            InvoiceType, Filter = RequestList["InvoiceType"], RequestList["Filter"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(InvoiceType,str): return (ErrorCodes.InvalidDataType,"")
        if not isinstance(Filter,dict): return (ErrorCodes.InvalidDataType,"")
        match InvoiceType:
            case "Selling":
                IsNotValidFilter = SearchFiltersValidation.SellingInvoices(Filter)
            case "Purchase":
                IsNotValidFilter = SearchFiltersValidation.PurchaseInvoices(Filter)
            case "Refund":
                IsNotValidFilter = SearchFiltersValidation.RefundInvoices(Filter)
            case _:
                return (ErrorCodes.InvalidValue,"Invalid InvoiceType")
        if IsNotValidFilter:
            return IsNotValidFilter
        # TODO: Implement this task
        #else:
        #   ProcessRequest.SearchInvoice(RequestList)
    def SearchTransitionDocument(RequestList):
        try:
            Filter = RequestList["Filter"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(Filter, dict): return (ErrorCodes.InvalidDataType, "")
        IsNotValidFilters = SearchFiltersValidation.TransitionDocuments(Filter)
        if IsNotValidFilters:
            return IsNotValidFilters
        else:
            pass
            # TODO: Implement this task
            # return ProcessRequest.SearchTransitionDocument(RequestList)
    def GetInvoiceItems(RequestList):
        try:
            InvoiceType, InvoiceID = RequestList["InvoiceType"], RequestList["InvoiceID"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(InvoiceType,str): return (ErrorCodes.InvalidDataType,"")
        if not isinstance(InvoiceID,int): return (ErrorCodes.InvalidDataType,"")
        if not InvoiceType in ValidInvoiceTypes: return (ErrorCodes.InvalidValue,"")
        #TODO: Implement this task
        #return ProcessRequest.GeInvoiceItems(RequestList)
    def GetTransitionItems(RequestList):
        try:
            DocumentID = RequestList["DocumentID"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(DocumentID,int): return (ErrorCodes.InvalidDataType,"")
        #TODO: Implement this task
        #return ProcessRequest.GetTransitionItems(RequestList)
def StartRequestProcessing(Request):
    RequestList = json.loads(Request)
    RequestType = RequestList["RequestType"]
    match RequestType:
        case "CreateAccount":
            return CheckValidation.CreateAccount(RequestList)
        case "AddStore":
            return CheckValidation.AddStore(RequestList)
        case "AddProduct":
            return CheckValidation.AddProduct(RequestList)
        case "EditProductInfo":
            return CheckValidation.EditProductInfo(RequestList)
        case "GetProductInfo":
            return CheckValidation.GetProductInfo(RequestList)
        case "Sell":
            return CheckValidation.Sell(RequestList)
        case "Purchase":
            return CheckValidation.Purchase(RequestList)
        case "Refund":
            return CheckValidation.Refund(RequestList)
        case "AddToAccount":
            return CheckValidation.AddToAccount(RequestList)
        case "DeductFromAccount":
            return CheckValidation.DeductFromAccount(RequestList)
        case "Transit":
            return CheckValidation.Transit(RequestList)
        case "SearchInvoice":
            return CheckValidation.SearchInvoice(RequestList)
        case "SearchTransitionDocument":
            return CheckValidation.SearchTransitionDocument(RequestList)
        case "GetInvoiceItems":
            return CheckValidation.GetInvoiceItems(RequestList)
        case "GetTransitionItems":
            return CheckValidation.GetInvoiceItems(RequestList)

def main():

    #r= StartRequestProcessing('{"RequestType":"AddStore","StoreName":"مخزن بلتان"}')
    #ProcessRequest('{"RequestType":"GetHistory","Tables":["Purchase_Invoices"],"Timelapse":["2024-09-06","2024-09-05"]}')
    #ProcessRequest('{"RequestType":"EditProductInfo","ProductID":2,"ProductName":"Combination Wrench",'
    #               '"Trademark":"King Tools","ManufactureCountry":"China","PurchasePrice":5,"WholesalePrice":60,'
    #               '"RetailPrice":65}')
    r= StartRequestProcessing('{"RequestType":"GetProductInfo","ProductID":12}')
    #r=GenerateSql('{"RequestType":"AddProduct","ProductName":"Combination Wrench","Trademark":"King Tools","ManufactureCountry":"China","PurchasePrice":20,"WholesalePrice":30,"RetailPrice":35}')
    #GenerateSql('{"RequestType":"Sell","ClientID":1,"Orders":[{"ProductID":1,"Quantity":4,"Price":9},{"ProductID":1,"Quantity":4,"Price":9}],"Paid":15}')
    #ProcessRequest('{"RequestType":"Purchase","SellerID":5,"Orders":[{"ProductID":5,"Quantity":4,"Price":9},{"ProductID":5,"Quantity":4,"Price":9}],"Paid":5}')
    #ProcessRequest('{"RequestType":"Refund","ClientID":5,"Orders":[{"ProductID":5,"Quantity":4,"Price":9},{"ProductID":5,"Quantity":4,"Price":9}]}')
    #ProcessRequest('{"RequestType":"Transit","SourceStoreID":0,"DestinationStoreID":1,"Products":[{"ProductID":1,"Quantity":2},{"ProductID":2,"Quantity":2},{"ProductID":6,"Quantity":2}]}')
    print(r)



if __name__ == "__main__":
    main()
