
# %%
# importing the required libraries
import time
import random
import uuid
import pandas as pd

# %%
# defining the function generate_new_row
def generate_new_row():
    # random user id
    user_id = str(uuid.uuid4())
    
    # random email id
    user_email = str(''.join(random.choices('abcireubgurgbe',k=5))) + str(random.randint(1000,99999)) + "@gmil.com"
    
    # random user name
    user_name  = str(''.join(random.choices("ABC",k=1))) + str(''.join(random.choices("ibruegbieiurgeriuger", k = 4)))
    
    # random source
    source     = random.choice(['LinkedIn', 'Email', 'Instagram', 'Facebook', 'Organic', "Not Available"])
    
    # random prime customers with a probability of 2/7 
    is_prime   = random.choice([1, 1, 0, 0, 0, 0, 0])
    
    # current time as random time
    signup_time = str(pd.datetime.now())
    
    # returning the user details
    return user_id, user_email, user_name,  source, is_prime, signup_time
    
# %%

def generate_user_data(db):
    cursor = db.cursor()
    while True:
        command = "INSERT INTO users values" + str(generate_new_row())
        cursor.execute(command)
        db.commit()
        time.sleep(random.random())



