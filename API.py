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
Cursor = DataBaseConnector.cursor()

class ErrorCodes(enum.Enum):
    InvalidDataType = enum.auto()
    MissingVariables = enum.auto()
    EmptyValue = enum.auto()
    InvalidValue = enum.auto()
    DuplicateName = enum.auto()


def GenerateSql(Request: str):
    RequestList = json.loads(Request)
    RequestType = RequestList["RequestType"]
    GeneratedSql = ""
    StoreID = 1
    #TODO: Add IsValidFunction
    #TODO: Sanitizing user input to prevent sql injection
    #TODO: Defining error codes
    match (RequestType):
        case "CreateAccount":
            PersonName = RequestList["PersonName"]
            GeneratedSql += f"INSERT INTO Accounts(Name,Balance) VALUES ('{PersonName}',0);"
        case "AddStore":
            StoreName=RequestList["StoreName"]
            GeneratedSql = (f"INSERT INTO Stores_Table(Store_Name) VALUES ('{StoreName}');\n"
                            f"SET @Sql = CONCAT('ALTER TABLE Products_Table ADD Quantity_Store',LAST_INSERT_ID(),' int default 0');\n"
                            f"PREPARE STMT FROM @Sql;\n"
                            f"EXECUTE STMT;\n"
                            f"DEALLOCATE PREPARE STMT;")
        case "AddProduct":
            Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_Name='{RequestList['ProductName']}';")
            if Cursor.fetchone():
                return "ER"
            Cursor.execute(
                f"INSERT INTO Products_Table(Product_Name,Trademark,Manufacture_Country,Purchase_Price,Wholesale_Price,"
                f"Retail_Price) VALUES ('{RequestList['ProductName']}','{RequestList['Trademark']}','{RequestList['ManufactureCountry']}',{RequestList['PurchasePrice']},{RequestList['WholesalePrice']},"
                f"{RequestList['RetailPrice']});")
            DataBaseConnector.commit()
        case "EditProductInfo":
            Cursor.execute(f"SELECT * FROM Products_Table WHERE Product_ID={RequestList['ProductID']};")
            if Cursor.fetchone() is None:
                return "ER"
            Cursor.execute(
                f"UPDATE Products_Table SET Product_Name = '{RequestList['ProductName']}', Trademark = '{RequestList['Trademark']}', Manufacture_Country = '{RequestList['ManufactureCountry']}', Purchase_Price={RequestList['PurchasePrice']}, Wholesale_Price={RequestList['WholesalePrice']}, Retail_Price={RequestList['RetailPrice']} WHERE Product_ID={RequestList['ProductID']} ")
            DataBaseConnector.commit()
        case "GetProductInfo":
            Cursor.execute(f"SELECT Product_Name,Purchase_Price,Wholesale_Price,Retail_Price,Quantity_Store{StoreID} FROM Products_Table WHERE Product_ID={RequestList['ProductID']};")
            Response = Cursor.fetchone()
            if Response is None:
                return "ER"
            return Response
        case "Sell":
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
                GeneratedSql += GenerateSql('{"RequestType":"AddToAccount","PersonID":"%s","Description":"CONCAT(\'فاتورة بيع #S-\',@Invoice_ID)","Amount":"%s"}' % (ClientID, Amount))
        case "Purchase":
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
                GeneratedSql+=GenerateSql(f'{"RequestType":"DeductFromAccount","PersonID":{SellerID},"Description":"CONCAT(\'فاتورة شراء #P-\',@Invoice_ID)","Amount":{Amount}}')
        case "Refund":
            ClientID = RequestList["ClientID"]
            Orders = RequestList["Orders"]
            TotalPrice = 0
            for Order in Orders:
                TotalPrice += Order["Price"]
                GeneratedSql += (f"INSERT INTO Refund_Operations(Invoice_ID,Product_ID,Quantity,Refund_Price) VALUES ("
                                 f"LAST_INSERT_ID(),'{Order["ProductID"]}','{Order["Quantity"]}','{Order["Price"]}');\n")
            GeneratedSql += f"INSERT INTO Refund_Invoices(Store_Id,Client_ID,Total_Price) VALUES ('{StoreID}','{ClientID}','{TotalPrice}');\n"

        case "AddToAccount":
            PersonID = RequestList["PersonID"]
            Description = RequestList["Description"]
            Amount = RequestList["Amount"]
            #Description variable is left without quotes to enable using sql statement
            GeneratedSql = f"INSERT INTO Accounts_Operations('Person_ID','Description','Required') VALUES ({PersonID},{Description},{Amount})\n"
            GeneratedSql += f"SET @Old_Balance = (SELECT Balance FROM Accounts WHERE Person_ID = {PersonID});\n"
            GeneratedSql += f"UPDATE Accounts SET Balance = @Old_Balance+{Amount} WHERE Person_ID = {PersonID};\n"
        case "DeductFromAccount":
            PersonName = RequestList["PersonName"]
            Description = RequestList["Description"]
            Amount = RequestList["Amount"]
            GeneratedSql = f"SET @PersonID = (SELECT Person_ID FROM Accounts WHERE Person_Name = '{PersonName}')"
            # Description variable is left without quotes to enable using sql statement
            GeneratedSql += f"INSERT INTO Accounts_Operations('Person_ID','Operation_Description','Amount') VALUES (@PersonID,{Description},{Amount})\n"
            GeneratedSql += f"SET @Old_Balance = (SELECT Balance FROM Accounts WHERE Person_ID = @PersonID);\n"
            GeneratedSql += f"UPDATE Accounts SET Balance = @Old_Balance-{Amount} WHERE Person_ID = @PersonID;\n"

        case "Transit":
            GeneratedSql = f"INSERT INTO Transition_Documents(Source_Store_ID,Destination_Store_ID) VALUES ('{RequestList['SourceStoreID']}','{RequestList['DestinationStoreID']}');\n"
            Products = RequestList["Products"]
            for Product in Products:
                GeneratedSql += (f"INSERT INTO Transition_Operations(Document_ID,Product_ID,Quantity) VALUES ("
                                 f"LAST_INSERT_ID(),'{Product['ProductID']}','{Product['Quantity']}');\n")
        case "GetHistory":
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
    return GeneratedSql

ValidHistoryTables = ["Selling_Invoices","Refund_Invoices","Purchase_Invoices","Transition_Documents","Accounts_Operations"]
class CheckValidation:
    def __init__(self):
        pass
    def CreateAccount(self,RequestList):
        try:
            PersonName=RequestList["PersonName"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(PersonName,str):return (ErrorCodes.InvalidDataType,"PersonName")
        if PersonName.len()==0:return (ErrorCodes.EmptyValue, "PersonName")
        return (0,"OK")
    def AddStore(self,RequestList):
        try:
            StoreName=RequestList["StoreName"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(StoreName,str):return (ErrorCodes.InvalidDataType,"StoreName")
        if StoreName.len()==0:return (ErrorCodes.EmptyValue,"StoreName")
        return (0,"OK")
    def AddProduct(self,RequestList):
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
        return (0,"OK")
    def EditProductInfo(self,RequestList):
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
        return (0,"OK")
    def GetProductInfo(self,RequestList):
        try:
            ProductID = RequestList["ProductID"]
        except:
            return (ErrorCodes.MissingVariables,"")
        

    def Sell(self,RequestList):
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
    def Purchase(self,RequestList):
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
    def Refund(self,RequestList):
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

    def AddToAccount(self,RequestList):
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
    def DeductFromAccount(self,RequestList):
        try:
            PersonID, Description, Amount = RequestList["PersonID"], RequestList["Description"], RequestList["Amount"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if not isinstance(PersonID,int): return (ErrorCodes.InvalidDataType,"")
        if not isinstance(Description,str): return (ErrorCodes.InvalidDataType,"")
        if not (isinstance(Amount,float) or isinstance(Amount,int)): return (ErrorCodes.InvalidDataType,"")
        if len(Description)==0: return (ErrorCodes.InvalidValue,"")
        if Amount<=0: return (ErrorCodes.InvalidValue,"")
    def Transit(self,RequestList):
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

    def GetHistory(self,RequestList):
        try:
            TableList, Timelapse = RequestList["TableList"], RequestList["Timelapse"]
        except:
            return (ErrorCodes.MissingVariables,"")
        if isinstance(TableList,list): return (ErrorCodes.InvalidDataType,"")
        if isinstance(Timelapse,list): return (ErrorCodes.InvalidDataType,"")
        if len(TableList)==0 or len(Timelapse)<2: return (ErrorCodes.InvalidValue,"")
        for Table in TableList:
            if isinstance(Table,str): return (ErrorCodes.InvalidDataType,"")
            if not Table in ValidHistoryTables: return (ErrorCodes.InvalidValue,"")
        for Datetime in Timelapse:
            if isinstance(Datetime,str): return (ErrorCodes.InvalidDataType,"")
            if datetime.strptime(Datetime,"%d-%m-%y %H-%M-%S"):return (ErrorCodes.InvalidValue,"")

def main():
    Request = ""
    RequestList = json.loads(Request)
    RequestType = RequestList["RequestType"]
    match RequestType:
        case "CreateAccount":
            CheckValidation.CreateAccount(RequestList)
            #TransformedValue = TransformRequest(RequestList)
        case "AddStore":CheckValidation.AddStore(RequestList)
        case "AddProduct":CheckValidation.AddProduct(RequestList)
        case "EditProductInfo":CheckValidation.EditProductInfo(RequestList)
        case "GetProductInfo":CheckValidation.GetProductInfo(RequestList)
        case "Sell":CheckValidation.Sell(RequestList)
        case "Purchase":CheckValidation.Purchase(RequestList)
        case "Refund":CheckValidation.Refund(RequestList)
        case "AddToAccount":CheckValidation.AddToAccount(RequestList)
        case "DeductFromAccount":CheckValidation.DeductFromAccount(RequestList)
        case "Transit":CheckValidation.Transit(RequestList)
        case "GetHistory":CheckValidation.GetHistory(RequestList)
    r= GenerateSql('{"RequestType":"AddStore","StoreName":"مخزن بلتان"}')
    #ProcessRequest('{"RequestType":"GetHistory","Tables":["Purchase_Invoices"],"Timelapse":["2024-09-06","2024-09-05"]}')
    #ProcessRequest('{"RequestType":"EditProductInfo","ProductID":2,"ProductName":"Combination Wrench",'
    #               '"Trademark":"King Tools","ManufactureCountry":"China","PurchasePrice":5,"WholesalePrice":60,'
    #               '"RetailPrice":65}')
    #ProcessRequest('{"RequestType":"GetProductInfo","ProductID":8}')
    #r=GenerateSql('{"RequestType":"AddProduct","ProductName":"Combination Wrench","Trademark":"King Tools","ManufactureCountry":"China","PurchasePrice":20,"WholesalePrice":30,"RetailPrice":35}')
    #GenerateSql('{"RequestType":"Sell","ClientID":1,"Orders":[{"ProductID":1,"Quantity":4,"Price":9},{"ProductID":1,"Quantity":4,"Price":9}],"Paid":15}')
    #ProcessRequest('{"RequestType":"Purchase","SellerID":5,"Orders":[{"ProductID":5,"Quantity":4,"Price":9},{"ProductID":5,"Quantity":4,"Price":9}],"Paid":5}')
    #ProcessRequest('{"RequestType":"Refund","ClientID":5,"Orders":[{"ProductID":5,"Quantity":4,"Price":9},{"ProductID":5,"Quantity":4,"Price":9}]}')
    #ProcessRequest('{"RequestType":"Transit","SourceStoreID":0,"DestinationStoreID":1,"Products":[{"ProductID":1,"Quantity":2},{"ProductID":2,"Quantity":2},{"ProductID":6,"Quantity":2}]}')
    print(r)
    for query in r.split("\n"):
        Cursor.execute(query)
    DataBaseConnector.commit()


if __name__ == "__main__":
    main()
