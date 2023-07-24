
# importing the required libraries
import time
import random
import uuid
import pandas as pd


# %%
# function to generate refund requests.
def generate_all_refund(transactions):
    # randomly generating the ticket id using uuid
    ticket_id = "TICKET-" + str(uuid.uuid4())
    
    # selecting any random transaction id from the transaction id list
    random_index = random.randint(0,len(transactions)-1)
    transaction_id = transactions[random_index][0]
    transaction_amount = transactions[random_index][1]
    
    # creating a random user name of 5 characters
    user_name  = str(''.join(random.choices("ABC",k=1))) + str(''.join(random.choices("ibruegbieiurgeriuger", k = 4)))
    
    refund_status = "NEW"
    
    # current time as the ticket raise time
    ticket_raise_time = str(pd.datetime.now())
    
    # Adding error in 20 percent of the refund request.

    random_error = random.choice([1,1,1,1,0])
    
    # if the random error is 0, then manipulate the transaction id
    if random_error == 0:        
        if random.choice([0,1,0,0,0]) == 0:    
            transaction_id = transaction_id.replace('0', 's') # A user may enter wrong transaction id so creating some false result
        else:
            transaction_amount = transaction_amount + 100
    
    # return the values
    return ticket_id, user_name, transaction_id, transaction_amount, ticket_raise_time

#%% 


# %%
def generate_refund_data(db):
    cursor = db.cursor()
    while True:
        # get the updated transaction_ids and price from the updated transactions table.
        command = "SELECT transaction_id, price FROM transaction"
        cursor.execute(command)
        transactions = cursor.fetchall()
        
        # generating 10 refund request every 10-20 seconds
        for i in range(10):
            command = "INSERT INTO refund_detail values" + str(generate_all_refund(transactions))
            cursor.execute(command)
            db.commit()
            time.sleep(random.randint(10,20))

# %%



