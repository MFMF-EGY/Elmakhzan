create database Elfarid_Metal CHARACTER SET utf8 COLLATE utf8_general_ci;
use Elfarid_Metal;
create table Debt_Accounts(
    Person_ID int NOT NULL AUTO_INCREMENT,
    Person_Name varchar(100) UNIQUE,
    Debt_Balance float(20,2) default 0,
    PRIMARY KEY (Person_ID)
);

create table Products_Table(
    Product_ID int NOT NULL AUTO_INCREMENT,
    Product_Name varchar(50),
    Trademark varchar(50),
    Manufacture_Country varchar(50),
    Purchase_Price int,
    Wholesale_Price int,
    Retail_Price int,
    Partial_Quantity_Precision int,
    PRIMARY KEY (Product_ID)
);

create table Product_Quantity_Table(
    Store_ID int,
    Product_ID int,
    Quantity float
);

create table Stores_Table(
    Store_ID int NOT NULL AUTO_INCREMENT,
    Store_Name varchar(50) UNIQUE,
    PRIMARY KEY (Store_ID)
);

create table Selling_Invoices(
    Invoice_ID int NOT NULL AUTO_INCREMENT,
    Store_ID int,
    Client_ID int,
    DateTime datetime default CURRENT_TIMESTAMP,
    Total_Price int,
    Paid int,
    Transferred_To_Account int,
    PRIMARY KEY (Invoice_ID)
);
create table Selling_Items(
    Invoice_ID int NOT NULL,
    Product_ID int,
    Quantity int,
    Selling_Price int
);
create table Refund_Invoices(
    Invoice_ID int NOT NULL AUTO_INCREMENT,
    Store_ID int,
    Client_ID int,
    DateTime datetime default CURRENT_TIMESTAMP,
    Total_Price int,
    PRIMARY KEY (Invoice_ID)
);
create table Refund_Items(
    Invoice_ID int NOT NULL,
    Product_ID int,
    Quantity int,
    Refund_Price int
);

create table Purchase_Invoices(
    Invoice_ID int NOT NULL AUTO_INCREMENT,
    Store_ID int,
    Seller_ID int,
    DateTime datetime default CURRENT_TIMESTAMP,
    Total_Price int,
    Paid int,
    Subtracted_From_Account int,
    PRIMARY KEY (Invoice_ID)
);
create table Purchase_Items(
    Invoice_ID int NOT NULL,
    Product_ID int,
    Quantity int,
    Purchase_Price int
);
create table Transition_Documents(
    Document_ID int NOT NULL AUTO_INCREMENT,
    DateTime datetime default CURRENT_TIMESTAMP,
    Source_Store_ID int,
    Destination_Store_ID int,
    PRIMARY KEY (Document_ID)
);
create table Transition_Items(
    Document_ID int NOT NULL,
    Product_ID int,
    Quantity int
);
create table Products_Quantity_Adjustments(
    Operation_ID int NOT NULL AUTO_INCREMENT,
    Store_ID int,
    DateTime datetime default CURRENT_TIME,
    Product_ID int,
    Previous_Quantity float,
    Current_Quantity float,
    Notes TEXT,
    PRIMARY KEY (Operation_ID)
);
create table Accounts_Operations(
    Process_ID int NOT NULL AUTO_INCREMENT,
    Person_ID int NOT NULL,
    Description TINYTEXT,
    Required_Amount float,
    Paid float,
    Added_To_Account float,
    Debt_Balance float,
    PRIMARY KEY (Process_ID)
);
# drop database Elfarid_Metal