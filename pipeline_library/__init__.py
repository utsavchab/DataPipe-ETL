import mysql.connector
import pandas as pd
from pipeline_library import pipe_refund
from pipeline_library import pipe_transaction
from pipeline_library import pipe_user

class get_database:
    def __new__(cls,dataB):
        db = mysql.connector.connect(host = "localhost" , user = "root" , password =  "Enter_LocalDataBase_Password" , database = dataB)
        return db
class get_products_table():
    def __new__(cls):
        return pd.read_csv("dataset/product_table.csv")
    
class pipeline_user_data():
    def __new__(cls,db):
        pipe_user.pipeline_to_update_user_summary(db)
        
class pipeline_transaction_data():
    def __new__(cls,db,products_table):
        pipe_transaction.pipeline_to_update_transaction_summary(db,products_table)
        
class pipeline_refund_data():
    def __new__(cls,db):
        pipe_refund.pipeline_to_validate_refund_request(db)
    