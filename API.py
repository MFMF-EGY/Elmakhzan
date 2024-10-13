import sys
import json

import mysql.connector

DataBaseConnector = mysql.connector.connect(
    host="localhost",
    user="root",
    password="000600",
    database="Elfarid_Metal",
    collation="utf8mb4_unicode_ci", charset="utf8mb4"
)

Cursor = DataBaseConnector.cursor(buffered=True)


def GenerateSql(Request: str):
    RequestList = json.loads(Request)
    RequestType = RequestList["RequestType"]
    GeneratedSql = ""
    StoreID = 1
    #TODO: Sanitizing user input to prevent sql injection
    #TODO: Defining error codes
    match (RequestType):
        case "AddStore":
            Cursor.execute(f"INSERT INTO Stores_Table(Store_Name) VALUES ('{RequestList["StoreName"]}');")
            DataBaseConnector.commit()
            Cursor.execute("SELECT LAST_INSERT_ID()")
            StoreID = Cursor.fetchone()[0]
            Cursor.execute(f"ALTER TABLE Products_Table ADD Quantity_Store{StoreID} int default 0;")
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
            ClientName, ClientID = RequestList["ClientName"], RequestList["ClientID"]
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
            GeneratedSql = f"INSERT INTO Selling_Invoices(Store_Id,Client_Name,Client_ID,Total_Price) VALUES ('{StoreID}','{ClientName}','{ClientID}','{TotalPrice}');\n" + GeneratedSql
            if RequestList["Paid"]>TotalPrice:
                return "ER"
            elif RequestList["Paid"]<TotalPrice:
                Amount = TotalPrice - RequestList["Paid"]
                GeneratedSql += GenerateSql('{"RequestType":"AddToAccount","PersonID":"%s","Description":"CONCAT(\'فاتورة بيع #S-\',@Invoice_ID)","Amount":"%s"}' % (ClientID, Amount))
        case "Purchase":
            SellerName, SellerID = RequestList["SellerName"], RequestList["SellerID"]
            Orders = RequestList["Orders"]
            TotalPrice = 0
            for Order in Orders:
                TotalPrice += Order["Price"]
                GeneratedSql += (f"INSERT INTO Purchase_Operations(Invoice_ID,Product_ID,Quantity,Purchase_Price) "
                                 f"VALUES (@Invoice_ID,'{Order["ProductID"]}','{Order["Quantity"]}',"
                                 f"'{Order["Price"]}');\n")
            GeneratedSql = "SET @Invoice_ID = LAST_INSERT_ID();\n" + GeneratedSql
            GeneratedSql = f"INSERT INTO Purchase_Invoices(Store_Id,Seller_Name,Seller_ID,Total_Price) VALUES ('{StoreID}','{SellerName}','{SellerID}','{TotalPrice}');\n" + GeneratedSql
            if RequestList["Paid"]<TotalPrice:
                Amount = TotalPrice - RequestList["Paid"]
                GeneratedSql+=GenerateSql(f'{"RequestType":"DeductFromAccount","PersonID":{SellerID},"Description":"CONCAT(\'فاتورة شراء #P-\',@Invoice_ID)","Amount":{Amount}}')
        case "Refund":
            ClientName, ClientID = RequestList["ClientName"], RequestList["ClientID"]
            Orders = RequestList["Orders"]
            TotalPrice = 0
            for Order in Orders:
                TotalPrice += Order["Price"]
                GeneratedSql += (f"INSERT INTO Refund_Operations(Invoice_ID,Product_ID,Quantity,Refund_Price) VALUES ("
                                 f"LAST_INSERT_ID(),'{Order["ProductID"]}','{Order["Quantity"]}','{Order["Price"]}');\n")
            GeneratedSql += f"INSERT INTO Refund_Invoices(Store_Id,Client_Name,Client_ID,Total_Price) VALUES ('{StoreID}','{ClientName}','{ClientID}','{TotalPrice}');\n"

        case "AddToAccount":
            PersonID = RequestList["PersonID"]
            Description = RequestList["Description"]
            Amount = RequestList["Amount"]
            #Description variable is left without quotes to enable using sql statement
            GeneratedSql = f"INSERT INTO Accounts_Operations('Person_ID','Description','Required') VALUES ({PersonID},{Description},{Amount})\n"
            GeneratedSql += f"SET @Old_Balance = (SELECT Balance FROM Accounts WHERE Person_ID = {PersonID});\n"
            GeneratedSql += f"UPDATE Accounts SET Balance = @Old_Balance+{Amount} WHERE Person_ID = {PersonID};\n"
        case "DeductFromAccount":
            PersonID = RequestList["PersonID"]
            Description = RequestList["Description"]
            Amount = RequestList["Amount"]
            # Description variable is left without quotes to enable using sql statement
            GeneratedSql = f"INSERT INTO Accounts_Operations('Person_ID','Operation_Description','Amount') VALUES ({PersonID},{Description},{Amount})\n"
            GeneratedSql += f"SET @Old_Balance = (SELECT Balance FROM Accounts WHERE Person_ID = {PersonID});\n"
            GeneratedSql += f"UPDATE Accounts SET Balance = @Old_Balance-{Amount} WHERE Person_ID = {PersonID};\n"

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


def main():
    #ProcessRequest('{"RequestType":"AddStore","StoreName":"مخزن بلتان"}')
    #ProcessRequest('{"RequestType":"GetHistory","Tables":["Purchase_Invoices"],"Timelapse":["2024-09-06","2024-09-05"]}')
    #ProcessRequest('{"RequestType":"EditProductInfo","ProductID":2,"ProductName":"Combination Wrench",'
    #               '"Trademark":"King Tools","ManufactureCountry":"China","PurchasePrice":5,"WholesalePrice":60,'
    #               '"RetailPrice":65}')
    #ProcessRequest('{"RequestType":"GetProductInfo","ProductID":8}')
    #ProcessRequest('{"RequestType":"AddProduct","ProductName":"Combination Wrench","Trademark":"King Tools","ManufactureCountry":"China","PurchasePrice":20,"WholesalePrice":30,"RetailPrice":35}')
    r=GenerateSql('{"RequestType":"Sell","ClientName":"mohamed","ClientID":5,"Orders":[{"ProductID":1,"Quantity":4,"Price":9},{"ProductID":1,"Quantity":4,"Price":9}],"Paid":15}')
    #ProcessRequest('{"RequestType":"Purchase","SellerName":"mohamed","SellerID":5,"Orders":[{"ProductID":5,"Quantity":4,"Price":9},{"ProductID":5,"Quantity":4,"Price":9}],"Paid":5}')
    #ProcessRequest('{"RequestType":"Refund","ClientName":"mohamed","ClientID":5,"Orders":[{"ProductID":5,"Quantity":4,"Price":9},{"ProductID":5,"Quantity":4,"Price":9}]}')
    #ProcessRequest('{"RequestType":"Transit","SourceStoreID":0,"DestinationStoreID":1,"Products":[{"ProductID":1,"Quantity":2},{"ProductID":2,"Quantity":2},{"ProductID":6,"Quantity":2}]}')
    print(r)
    for query in r.split("\n"):
        Cursor.execute(query)
    DataBaseConnector.commit()


if __name__ == "__main__":
    main()
