import mysql.connector
import pandas as pd
from generate_data_library import generate_refund
from generate_data_library import generate_transaction
from generate_data_library import generate_user
import subprocess
import threading


class install_req_libraries():
    def __new__(cls):
        cmd_run = subprocess.run(["powershell","-Command","pip install -r requirements.txt"],capture_output=True)
        print(cmd_run.stdout.decode("utf-8"))
        
class get_database:
    def __new__(cls,dataB):
        db = mysql.connector.connect(host = "localhost" , user = "root" , password =  "Enter_LocalDataBase_Password" , database = dataB)
        return db
    
class get_products_table():
    def __new__(cls):
        return pd.read_csv("dataset/product_table.csv")

class add_users():
    def __new__(cls):
        print("Generating users Data")
        db = get_database("website")
        generate_user.generate_user_data(db)
        
class add_transactions():
    def __new__(cls):
        print("Generating transaction Data")
        db = get_database("website")
        products_table = get_products_table()
        generate_transaction.generate_transaction_data(db,products_table)
        
class add_refund():
    def __new__(cls):
        print("Generating refunds Data")
        db = get_database("website")
        generate_refund.generate_refund_data(db)