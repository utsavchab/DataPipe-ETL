# %%
import pandas as pd
import datetime
import mysql.connector

# %%
def getDataBase(dataB):
    db = mysql.connector.connect(host = "localhost" , user = "root" , password =  "Enter_LocalDataBase_Password" , database = dataB)
    return db

# %%
# set Default value of attributes of transaction table to zero
def setDefaultZero():
    db = getDataBase("website")
    cursor = db.cursor()
    columns = ['Air Conditioner', 'Microwave', 'Refrigrator', 'Haier', 'LG', 'Samsung', 'Whirlpool', 
            'sales_from_Air Conditioner', 'sales_from_Microwave', 'sales_from_Refrigrator', 
            'sales_from_Haier', 'sales_from_LG', 'sales_from_Samsung', 'sales_from_Whirlpool']
    for col in columns:
        command = f"alter table transaction_summary modify {col} int default 0"
        cursor.execute(command)
        db.commit()


# %%
def extract_product_data():
    data = pd.read_csv("dataset/product_table.csv")
    return data

# %%
def extract_transaction_data(db, start_time, end_time):
    
    # create database cursor
    cursor = db.cursor()
    
    print("Extracting transactions between {} and {}".format(str(start_time),str(end_time)))
    
    # command to extract the data of last 5 minutes.
    command = f"SELECT * FROM transaction WHERE transaction_time BETWEEN '{start_time}' AND '{end_time}'"
    
    # execute the command and return the results.
    cursor.execute(command)
    data = cursor.fetchall()
    
    # return the dataframe
    return pd.DataFrame.from_records(data, columns= ['transaction_id',
                                                     'user_id',
                                                     'product_id',
                                                     'transaction_time',
                                                     'price'])

# %%
def transform_transaction_data(latest_transaction_data,product_data,start,end):
    
    #combining data
    data = latest_transaction_data.merge(product_data , on = "product_id" , how = "left")
    data["product_company"] = data.product_name.apply(lambda x: x[0:x.find(" ")])
    
    # Units Sold by Category
    data_dict = {}
    data_dict.update(dict(data.groupby("product_category")["transaction_id"].count()))
    
    # Units Sold by Company
    data_dict.update(dict(data.groupby("product_company")["transaction_id"].count()))
    
    # Sales by category
    sales_by_category = dict(data.groupby("product_category")["price"].sum())
    for keys in sales_by_category.keys():
        data_dict["sales_from_"+keys] = sales_by_category[keys]
    
    # Sales by company
    sales_by_company = dict(data.groupby("product_company")["price"].sum())
    for key in sales_by_company.keys():
        data_dict["sales_from_"+key] = sales_by_company[key]
        
    data_dict["start_time"] = str(start)
    data_dict["end_time"] = str(end)
    return data_dict
    
    
    
    

# %%
def load_transaction_summary(db,result_dict):
    cursor = db.cursor()
    # command = "INSERT INTO transaction_summary {col} values {val}".format(col= tuple((data.keys())),
                                                                    #  val= tuple(data.values()))
                                                                       
    command = "INSERT INTO transaction_summary( {col}) values{val}".format(col= ', '.join(result_dict.keys()),
                                                                       val= tuple(result_dict.values()))
    
    command = command.replace('sales_from_Air Conditioner', '`sales_from_Air Conditioner`')
    command = command.replace(' Air Conditioner', '`Air Conditioner`')
    
    cursor.execute(command)
    db.commit()
    print("---------------------------Transaction Summary Loaded to DataBase-------------------------")
    

# %%
def pipeline_to_update_transaction_summary(db,product_data):
    print("\n==================================Loading Transaction Data====================================")
    current_time = datetime.datetime.now()
    current_minus_10 = current_time - datetime.timedelta(minutes=10)
    
    # Extract
    latest_transaction_data = extract_transaction_data(db=db,
                                                       start_time = current_minus_10,
                                                       end_time = current_time)
    
    # Transform
    summarized_data = transform_transaction_data(latest_transaction_data,product_data,current_minus_10,current_time)
    
    # Load
    load_transaction_summary(db,summarized_data)
    print("====================================Load Success=========================================\n")
    
