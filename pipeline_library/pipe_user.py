# %%
import mysql.connector
import datetime
import pandas as pd

# %%
def getDataBase(dataB):
    db = mysql.connector.connect(host = "localhost" , user = "root" , password =  "Enter_LocalDataBase_Password" , database = dataB)
    return db

# %%
def setDefaultZero():
    db = getDataBase("website")
    cursor = db.cursor()
    cols = ["Email", "Facebook", "Instagram" , "LinkedIn", "Organic"]
    for col in cols:
        command = f"alter table signup_summary modify {col} int default 0"
        cursor.execute(command)
        command = f"alter table signup_summary modify prime_from_{col} int default 0"
        cursor.execute(command)
        db.commit()

# %%
def extract_users_data(db,start,end):
    cursor = db.cursor()
    
    print(f"Extracting data from time {str(start)} to {str(end)}")
    command = f"select * from users where signup_time between '{start}' AND '{end}'; "
    cursor.execute(command)
    data = cursor.fetchall()
    return data

# %%
def transform_user_data(df_user, start_time, end_time):
    
    # Dealing with not available values
    df_user.source.replace("Not Available", "Organic", inplace=True)
    
    src_list = ["Email", "Facebook", "Instagram" , "LinkedIn", "Organic"]
    #
    source_total_data = []
    for src in src_list:
        if(src in df_user.source.value_counts().index):
            source_total_data.append(df_user.source.value_counts()[src])
        else:
            source_total_data.append(0)
    
    #
    source_prime_data = []
    for src in src_list:
        if(src in df_user.source[df_user.is_prime == 1].value_counts().index ):
            source_prime_data.append(df_user.source[df_user.is_prime == 1].value_counts()[src])
        else:
            source_prime_data.append(0)
    
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    data_tuple_summary = (start_time,end_time,*source_total_data, *source_prime_data)
    
    return data_tuple_summary
   
    
    

# %%
def load_user_data(db,new_data):
    cursor = db.cursor()
    
    command = "INSERT INTO signup_summary values{val}".format(val = tuple(new_data))
    cursor.execute(command)
    db.commit()
    
    print("------------------------------User Summary Loaded to DataBase----------------------------")

# %%
def pipeline_to_update_user_summary(db):
    print("\n==================================Loading User Data====================================")
    cursor = db.cursor()
    #Time frame
    end = datetime.datetime.now()
    start = end - datetime.timedelta(minutes=5)
    # Extract
    userdata = extract_users_data(db,start,end)
    data = pd.DataFrame.from_records(userdata, columns=["user_id" , "user_email" , "user_name" , "source", "is_prime", "signup_time"])
    
    # Transform
    new_data = transform_user_data(data,start,end)
    
    # Load
    load_user_data(db,new_data)
    print("====================================Load Success=========================================\n")
    
