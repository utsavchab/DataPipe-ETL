
# %%
# importing the required libraries
import time
import random
import uuid
import pandas as pd




# %%
#function to Generate New Transactions.

def generate_new_transaction(users,products_table):
    
    # generating random transaction id
    transaction_id = "TI-" + str(uuid.uuid4())
    
    # selecting a random user id 
    user_id = users[random.randint(0,len(users))][0]
    
    # selecting a random product_id using the CSV file
    random_product = random.randint(0, products_table.shape[0]-1)
    product_id = products_table.iloc[random_product]['product_id']
    
    # current time will be transaction time
    transaction_time = str(pd.datetime.now())
    
    # extracting price of the product using the CSV file
    price = products_table.iloc[random_product]['product_price']
    
    return transaction_id, user_id, product_id, transaction_time, price

# %%
def generate_transaction_data(db,products_table):
    cursor = db.cursor()
    while True:
        
        command = "SELECT user_id FROM users"
        cursor.execute(command)
        users = cursor.fetchall() 
        
        # creating the new random transaction
        for i in range(25):
            command = "INSERT INTO transaction values" + str(generate_new_transaction(users,products_table))
            cursor.execute(command)
            db.commit()
            time.sleep(random.randint(0,4))
