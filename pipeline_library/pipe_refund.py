# %%
import pandas as pd
import datetime
import mysql.connector
from pandas.core.common import SettingWithCopyWarning
import warnings
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)


# %%
def createConnection(dataB):
    db = mysql.connector.connect(host = "localhost" , user = "root", password = "Enter_LocalDataBase_Password" , database = dataB)
    return db

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
def extract_refund_data(db, start, end):
    cursor = db.cursor()
    
    command  = f"select * from refund_detail where ticket_raise_time between '{start}' and '{end}';"
    cursor.execute(command)
    data = cursor.fetchall()
    
    return pd.DataFrame.from_records(data,columns=["ticket_id" , 
                                                   "user_name", 
                                                   "transaction_id", 
                                                   "transaction_amount", 
                                                   "ticket_raise_time"])
    
    

# %%
def extract_valid_refund_data(db, start, end):
    cursor = db.cursor()
    
    command  = f"select transaction_id from valid_refund where ticket_raise_time between '{start}' and '{end}';"
    cursor.execute(command)
    data = cursor.fetchall()
    
    return pd.DataFrame.from_records(data, columns= ['transaction_id'])["transaction_id"].to_list()
    

# %%
def transform_refund_data(refund_request_data, refund_issued_TID, transaction_data):
    
    ## Validation of Requested refund's Transaction ID 
    ## Validation of transaction is been done in last 48 hours or not.
    refund_request_valid_TID = transaction_data.merge(refund_request_data , on = "transaction_id", how = "left" )
    refund_request_valid_TID = refund_request_valid_TID[refund_request_valid_TID.ticket_id.isnull() == False]
    
    ## Validation of Request if it's already proccesed or not
    refund_request_notissued = refund_request_valid_TID[~(refund_request_valid_TID.transaction_id.isin(refund_issued_TID))]
    refund_request_notissued.reset_index(inplace = True, drop = True)
    
    ## Invalid Transaction ID Data
    refund_request_invalid_TID = refund_request_data[~(refund_request_data.ticket_id.isin(refund_request_valid_TID.ticket_id))]
    refund_request_invalid_TID.reset_index(inplace = True, drop = True)
    refund_request_invalid_TID["refund_reject_reason"] = None
    refund_request_invalid_TID.loc[:,"refund_reject_reason"] = "Invalid Transaction ID or Transaction ID expired"
    
    ## Invalid Refund because Transaction ID already Processed
    refund_request_invalid_issued = refund_request_valid_TID[refund_request_valid_TID.transaction_id.isin(refund_issued_TID)]
    refund_request_invalid_issued.reset_index(inplace = True, drop=  True)
    refund_request_invalid_issued["refund_reject_reason"] = None
    refund_request_invalid_issued.loc[:,"refund_reject_reason"] = "Refund Already Processed"
    refund_request_invalid_issued = refund_request_invalid_issued.loc[:,refund_request_invalid_TID.columns]
    
    ## Combining Invalid Data
    invalid_request =  pd.concat([refund_request_invalid_TID,refund_request_invalid_issued])
    invalid_request.reset_index(inplace = True, drop = True)
    
    
    return refund_request_notissued,invalid_request
    
    
    

# %%
def load_valid_refund_data(db , valid_refund_request_data):
    cursor = db.cursor()
    
    valid_refund_columns = ["ticket_id", "transaction_id" , "user_id" , "price" , "ticket_raise_time"]
    valid_refund_data = valid_refund_request_data.loc[:,valid_refund_columns]
    
    # valid_refund_data = valid_refund_data.to_records(index = False)
    valid_refund_data = [tuple((row[0],row[1],row[2],int(row[3]), str(row[4]))) for row in valid_refund_data.to_records(index=False)]
    
    command = "insert into valid_refund (ticket_id, transaction_id , user_id , price , ticket_raise_time) values (%s, %s, %s, %s, %s)"

    cursor.executemany(command, valid_refund_data)
    db.commit()
    print("------------------------------Valid Refund Loaded to DataBase----------------------------")
    

# %%
def load_invalid_refund_data(invalid_request):
    
    invalid_data_csv = pd.read_csv("invalid_refund_request/invalid_refund_data.csv")
    data = invalid_request.merge(invalid_data_csv,on = 'ticket_id' ,how = "outer")
    data.to_csv("./invalid_refund_request/invalid_refund_data.csv")
    print("------------------------------Invalid Refund Loaded to CSV-------------------------------")
    

# %%
def pipeline_to_validate_refund_request(db):
    cursor = db.cursor()
    print("\n==================================Loading Refund Data====================================")
    current_time = datetime.datetime.now()
    current_time_30 = current_time - datetime.timedelta(minutes=30)
    current_time_48 = current_time - datetime.timedelta(hours=48)
    
    current_time = str(current_time)
    current_time_30 = str(current_time_30)
    current_time_48 = str(current_time_48)
    
    #Extraction
    transaction_data = extract_transaction_data(db, current_time_48, current_time)
    refund_request_data = extract_refund_data(db,current_time_30,current_time)
    refund_issued_TID = extract_valid_refund_data(db,current_time_48,current_time)
    
    #Transformation
    refund_request_notissued,invalid_request = transform_refund_data(refund_request_data,refund_issued_TID,transaction_data)
    
    #Load
    load_valid_refund_data(db,refund_request_notissued)
    load_invalid_refund_data(invalid_request)
    print("====================================Load Success=========================================\n")
    
