import sys
import oracledb
import random
import oci
import re
import json
import datetime
from datetime import datetime,timedelta
from faker import Factory
from subjects import Subject
from products import Product

# Define the start and end dates
start_date = datetime(2024, 1, 30)
end_date = datetime(2024, 6, 28)
# Initialise an empty list to store the weekdays
weekdays = []

# OCI Gen AI set up
compartment_id = "<COMPARTMENT OCID>"
CONFIG_PROFILE = "DEFAULT"
config = oci.config.from_file('~/.oci/config', CONFIG_PROFILE)

# Service endpoint
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
##############################################################################################

listCallWeights = [d.get('weight', None) for d in Subject]
listProdWeights = [d.get('weight', None) for d in Product]

recs = int(sys.argv[1])
if recs == 0:
    recs=10 #Default number of new records

replacement=''
pattern1_end = r'Is there any other .*'
pattern2_end = r'Would you like me.*'
fake = Factory.create('en_AU')

current_date = start_date
while current_date <= end_date:
    # Check if the current day is a weekday (Monday to Friday)
    if current_date.weekday() < 5:  # Monday is 0 and Friday is 4
        weekdays.append(current_date.strftime('%Y-%m-%d'))
    # Move to the next day
    current_date += timedelta(days=1)

connection=oracledb.connect(
     config_dir="/home/user/wallet",
     user="<dbuser>",
     password="<dbpasswd>",
     dsn="<db_profile>",
     wallet_location="/home/user/wallet",
     wallet_password="<wallet_pwd>"
     )

print("Successfully connected to Oracle Database")
call_insert_sql = """INSERT INTO <tablename>  (ID, OPERATOR_ID, CHAT_CONTENT) VALUES (:i, :OPERATOR_ID, :CONTENT)"""
    
with connection.cursor() as cursor:
    # iterate for recs argument
    for i in range(recs):

        operatorid = random.randrange(65,85)
        # Email or Voice to text

        l_gender = random.choices(["Male", "Female"], [0.5, 0.5])[0]
        first_name = fake.first_name_male() if l_gender=="Male" else fake.first_name_female()
        last_name =  fake.last_name()
        contact_name=first_name+' '+last_name
        gender = l_gender
        
        contact_type = random.choices(["an email from ", "a phone call interaction between your call centre operator and customer "], [0.4, 0.6])[0]
        contact_mind = random.choices(["upset", "confused", "annoyed", "ameniable", "arguementitive", "friendly", "unstable", "forgetful", "unprepared"], [0.2, 0.1, 0.2, 0.1, 0.1, 0.1,0.1,0.05, 0.05])[0]
        contact_conclusion = random.choices([". Leave the matter unresolved", ". The operator resolves the matter"], [0.7, 0.3])[0]

        subject_index=random.choices(list(range(0,len(Subject))),listCallWeights)[0]
        product_index=random.choices(list(range(0,len(Product))),listProdWeights)[0]
        callSubject=Subject[subject_index]['complaint']
        callProduct=Product[product_index]['product']
    
        operator_service = ". The responding operator must by easy to engage, act with empathy, respect time, explain what to expect, try to resolve the situation and listen to customer needs. Don't include addresses.Use fake reference numbers and company names. "

        generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config=config, service_endpoint=endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10,240))
        generate_text_detail = oci.generative_ai_inference.models.GenerateTextDetails()
        llm_inference_request = oci.generative_ai_inference.models.CohereLlmInferenceRequest()

        l_prompt = '\"You are a Building Materials supplier. Generate ' + contact_type + contact_name +' who is '+ l_gender +' and is '+ contact_mind +'. ' 
        l_prompt = l_prompt+ 'The subject is regarding ' + callSubject +' for the product ' + callProduct + contact_conclusion
        llm_inference_request.prompt = l_prompt + operator_service + ". Refer to call centre operator as 'operator'. Respond in British English, stick to the subject and don't include greetings.\"\n Stop Sequences'"

        #print(l_prompt)
        llm_inference_request.max_tokens = 1000
        llm_inference_request.temperature = 0.5
        llm_inference_request.frequency_penalty = 1
        llm_inference_request.top_p = 0.75

        generate_text_detail.serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(model_id="ocid1.generativeaimodel.oc1.us-chicago-1.<serviceid>")
        generate_text_detail.inference_request = llm_inference_request
        generate_text_detail.compartment_id = compartment_id
        generate_text_response = generative_ai_inference_client.generate_text(generate_text_detail)
        print(llm_inference_request.prompt)

        comments = generate_text_response.data.inference_response.generated_texts[0].text
        comments = re.sub(r'^.*?: ', replacement, comments)

        comments = re.sub(pattern1_end, replacement, comments)
        comments = re.sub(pattern2_end, replacement, comments)

        jdoc=comments

        cursor.execute(call_insert_sql, [i, operatorid, jdoc])

        print(cursor.rowcount, "Rows Inserted")

        connection.commit()
