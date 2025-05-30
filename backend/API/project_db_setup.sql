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
    Purchase_Price float,
    Wholesale_Price float,
    Retail_Price float,
    Quantity_Unit varchar(20),
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
    Store_Address varchar(100),
    PRIMARY KEY (Store_ID)
);

create table Selling_Invoices(
    Invoice_ID int NOT NULL AUTO_INCREMENT,
    Store_ID int,
    Client_Name VARCHAR(50),
    DateTime datetime default CURRENT_TIMESTAMP,
    Total_Price float,
    Paid float,
    Transferred_To_Account float,
    PRIMARY KEY (Invoice_ID)
);

create table Selling_Items(
    Invoice_ID int NOT NULL,
    Product_ID int,
    Quantity float,
    Purchase_Price float,
    Unit_Price float
);

create table Refund_Invoices(
    Invoice_ID int NOT NULL AUTO_INCREMENT,
    Store_ID int,
    Client_Name VARCHAR(50),
    DateTime datetime default CURRENT_TIMESTAMP,
    Total_Price float,
    PRIMARY KEY (Invoice_ID)
);

create table Refund_Items(
    Invoice_ID int NOT NULL,
    Product_ID int,
    Quantity float,
    Unit_Price float
);

create table Purchase_Invoices(
    Invoice_ID int NOT NULL AUTO_INCREMENT,
    Store_ID int,
    Seller_Name VARCHAR(50),
    DateTime datetime default CURRENT_TIMESTAMP,
    Total_Price float,
    Paid float,
    Subtracted_From_Account float,
    PRIMARY KEY (Invoice_ID)
);
create table Purchase_Items(
    Invoice_ID int NOT NULL,
    Product_ID int,
    Quantity float,
    Unit_Price float
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
    Quantity float
);
create table Products_Quantities_Adjustments(
    Operation_ID int NOT NULL AUTO_INCREMENT,
    Store_ID int,
    Operation_Type varchar(20),
    Product_ID int,
    DateTime datetime default CURRENT_TIME,
    Quantity float,
    Note TEXT,
    PRIMARY KEY (Operation_ID)
);
create table Accounts_Operations(
    Process_ID int NOT NULL AUTO_INCREMENT,
    Person_ID int NOT NULL,
    Operation_Type varchar(20),
    Document_ID int,
    Description TINYTEXT,
    Required_Amount float,
    Paid float,
    Added_To_Account float,
    Debt_Balance float,
    PRIMARY KEY (Process_ID)
);