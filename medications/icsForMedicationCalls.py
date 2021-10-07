import json, requests, os
from datetime import datetime
from datetime import timedelta

"""
Program to extract the next call in date for perscriptions 
in the notion database and create an ics file to save in the 
calendar
"""
lastKey = ""
lastAuthName = ""
#modules
def auth(auth_name):
    global lastAuthName, lastKey
    if auth_name == lastAuthName:
        key = lastKey
    else:
        with open("medications/key.txt") as file:
            data = file.read()
            keys = json.loads(data)
        key = keys[auth_name]
        lastAuthName = auth_name
        lastKey = key
    return key

def query_db(id, data, auth_name):
    headers = {
        'Authorization': f'Bearer {auth(auth_name)}',
        'Notion-Version': '2021-05-13',
        'Content-Type': 'application/json',
        }
    response = requests.post(f'https://api.notion.com/v1/databases/{id}/query', headers=headers, data=data)
    return response

def write_to_page(id, auth_name):
    headers = {
        'Authorization': f'Bearer {auth(auth_name)}',
        'Content-Type': 'application/json',
        'Notion-Version': '2021-05-13',
    }

    data = json.dumps({"properties":{"need to export":{"checkbox":False}}})
    response = requests.patch(f'https://api.notion.com/v1/pages/{id}', headers=headers, data=data)
#    print(response.status_code)
    return response

def write_reminder(Task_Name, StartDate, auth_name):
    url = "https://api.notion.com/v1/pages/"

    payload = json.dumps({"parent":{"database_id":"a692f980e9d4444481a12f8f75c2243e"},"properties":{"Task Name":{"title":[{"text":{"content":Task_Name}}]},"Due Date":{"date":{"start":StartDate}},"Context":{"multi_select":[{"name":"Jeremy"},{"name":"Medications"}]},"Project":{"relation":[{"id":"cf7c7d28-8bc5-4f1e-8c19-ab2b91a7cdc7"}]}}})
    headers = {
    'Authorization': f'Bearer {auth(auth_name)}',
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

#    print(response.text)
#    print(response.status_code)
    return response

def notification(Name=None, Reminder=None, Uncheck=None, ErrMsg=None): 
    with open('medications/log_'+datetime.today().strftime("%m%d%Y")+".txt", 'a') as log:
        if not (Name == None):
            #file write / screen write
            print(datetime.today().strftime("%x %X"), file=log)
            print(datetime.today().strftime("%x %X"))
            print(50*"*", file=log)
            print(50*"*")
            print("*  " + str(Name), file=log)
            print("*  " + str(Name))
            print(50*"*", file=log)
            print(50*"*")
            print("*  ✅ ics created", file=log)
            print("*  ✅ ics created")
        elif Reminder:
            print("*  ✅ Reminder created and added to Notion", file=log)
            print("*  ✅ Reminder created and added to Notion")
        elif Reminder == False:
            print("*  ❌ Reminder NOT created", file=log)
            print("*  ❌ Reminder NOT created")
            print("*  ❌ " + str(ErrMsg), file=log)
            print("*  ❌ " + str(ErrMsg))
        elif Uncheck:
            print("*  ✅ Unchecked in Notion", file=log)
            print("*  ✅ Unchecked in Notion")
            print(50*"*", file=log)
            print(50*"*")
            print(file=log)
            print()            
        elif Uncheck == False:
            print("*  ❌ NOT unchecked in Notion", file=log)
            print("*  ❌ NOT unchecked in Notion")
            print("*  ❌ " + str(ErrMsg), file=log)
            print("*  ❌ " + str(ErrMsg))
            print(50*"*", file=log)
            print(50*"*")
            print(file=log)
            print()


dbID = 'bc865f6372e145a5b95e7c10cb1ebd25'
data = '{"filter":{"or":[{"property":"need to export","checkbox":{"equals":true}}]},"sorts":[{"property":"Call In Refill","direction":"ascending"}]}'
query = query_db(dbID,data,'notion')
queryJSON = json.loads(query.text)
count = len(queryJSON['results'])

if count == 0:
    print('No medications found in Notion.  Please check the export field and re-run this program')
    quit()
else:
    with open('medications/call_for_medication.ics', 'w') as my_file:
        my_file.write('BEGIN:VCALENDAR\nVERSION:2.0\n')
        for i in range(count):
            startdate = datetime.strptime(queryJSON['results'][i]['properties']['Call In Refill']['formula']['date']['start'],"%Y-%m-%d")
            enddate = startdate + timedelta(days=1)
            MedName = queryJSON['results'][i]['properties']['Name of Medication']['title'][0]['plain_text']
            TaskName = "Call to Order " + MedName
            PickupDate = datetime.strptime(queryJSON['results'][i]['properties']['Pickup Refill']['formula']['date']['start'],"%Y-%m-%d").strftime("%m/%d/%Y")
            my_file.write('BEGIN:VEVENT\n')
            my_file.write('SUMMARY:' + TaskName +"\n")
            my_file.write('LOCATION:' + queryJSON['results'][i]['properties']['Pharmacy']['select']['name']+"\n")
            my_file.write('DESCRIPTION:' + "Call " + queryJSON['results'][i]['properties']['Pharmacy']['select']['name'] + " to request a refill of " + queryJSON['results'][i]['properties']['Name of Medication']['title'][0]['plain_text'] + " to be picked up on " + PickupDate + "\n")
            my_file.write('DTSTART;VALUE=DATE:'+ str(startdate.strftime("%Y%m%d")) +"\n")
            my_file.write('DTEND;VALUE=DATE:'+ str(enddate.strftime("%Y%m%d")) +"\n")
            my_file.write('END:VEVENT\n')
            notification(Name=str(MedName)+" - "+str(i+1)+" of "+str(count))
            
            #create a page for each reminder to the task list for database a4e2f92bc25947cb915e6ef5f8ba7979(Task Name, Due Date, Context = Jeremy, Medications, Project = Medical)
            reminder = write_reminder(TaskName,startdate.strftime("%Y%m%d"),'notion')
            if reminder.status_code == 200:
                notification(Reminder=True)
            else:
                notification(Reminder=False, ErrMsg=reminder.reason)
                
            
            #uncheck the need to export field in notion medicine page
            writePage = write_to_page(queryJSON['results'][i]['id'], 'notion')   
            if writePage.status_code == 200:
                notification(Uncheck=True)
            else:
                notification(Uncheck=False, ErrMsg=writePage.reason)

        my_file.write('END:VCALENDAR')
    os.system('open medications/call_for_medication.ics')