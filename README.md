# GenAI_DataGenerator
Data Generator powered by AI and written to OracleDB

Using OCI GenAI service to create "call centre" chat records.

Pre requsites:
- Oracle Database (Recommend Autonomous 23ai)
- Credentials for API Services
- OCID for GenAI Services in tenancy

### Subjects.py 
Contains call centre "subject"

### Products.py
Contains product names/types IF required


Prompt is generated with:
random.choices(["an email from ", "a phone call interaction between your call centre operator and customer "], [0.4, 0.6])[0]
random.choices(["upset", "confused", "annoyed", "ameniable", "arguementitive", "friendly", "unstable", "forgetful", "unprepared"], [0.2, 0.1, 0.2, 0.1, 0.1, 0.1,0.1,0.05, 0.05])[0]
random.choices([". Leave the matter unresolved", ". The operator resolves the matter"], [0.7, 0.3])[0]

". The responding operator must by easy to engage, act with empathy, respect time, explain what to expect, try to resolve the situation and listen to customer needs. Don't include addresses.Use fake reference numbers and company names. "
"You are a Building Materials supplier. Generate " + contact_type + contact_name + " who is "+ l_gender +" and is " + contact_mind + ". " 
"The subject is regarding " + callSubject + " for the product " + callProduct
"Refer to call centre operator as 'operator'.\"\n Stop Sequences'"

