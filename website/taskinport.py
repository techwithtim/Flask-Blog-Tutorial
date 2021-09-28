import requests
from website.models import Tasks, Projects
from . import db
from json import loads, dumps
import random

def getNextTasks(nextcursor):
    url = "https://api.notion.com/v1/databases/a692f980e9d4444481a12f8f75c2243e/query"

    payload = dumps({
    "start_cursor": nextcursor
    })
    headers = {
    'Authorization': 'Bearer secret_E56vtGLhJHUK1o7WerXlnUaZHcbHnnlyFiMuPPwU1bz',
    'Content-Type': 'application/json',
    'Notion-Version': '2021-08-16'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    jsonResponse = loads(response.text)
    
    with open('fulljson'+str(random.randrange(20, 50, 3))+'.json', 'w') as file:
        file.write(dumps(jsonResponse))
    
    return jsonResponse

def parsejsonMakeTask(json):    
    import datetime
    for i in range(len(json['results'])):
        projectid = getdbid(json['results'][i]['properties']['Project']['relation'][0]['id'])
        
        try:
            start = json['results'][i]['properties']["Due Date"]['date']['start']
            if "T" in start:
                data = start[0:start.find('T')]
                duedate = datetime.datetime.strptime(data,"%Y-%m-%d")
            else:
                duedate = datetime.datetime.strptime(start,"%Y-%m-%d")
        except Exception:
            duedate = datetime.datetime.strptime('2021-12-31',"%Y-%m-%d")
        
        newtask = Tasks(
            item = json['results'][i]['properties']["Task Name"]['title'][0]['text']['content'],
            checked = json['results'][i]['properties']['Done']['checkbox'],
            userid = 1,
            duedate = duedate,
            project = projectid
        )
        db.session.add(newtask)
        db.session.commit()

def get_tasks():
    url = "https://api.notion.com/v1/databases/a692f980e9d4444481a12f8f75c2243e/query"

    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer secret_E56vtGLhJHUK1o7WerXlnUaZHcbHnnlyFiMuPPwU1bz'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    jsonResponse = loads(response.text)
    
    with open('fulljson.json', 'w') as file:
        file.write(dumps(jsonResponse))
    
    return jsonResponse

def projectname(id):

    url = "https://api.notion.com/v1/pages/" + id

    payload={}
    headers = {
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer secret_E56vtGLhJHUK1o7WerXlnUaZHcbHnnlyFiMuPPwU1bz'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = loads(response.text)
    
    name = data['properties']["Project Name"]['title'][0]['text']['content']
  
    return name

def getdbid(notion):
    
    count = db.session.query(Projects.id, Projects.notionid).filter(Projects.notionid == notion).count()
    
    if count > 0:
        projectid = db.session.query(Projects.id, Projects.notionid).filter(Projects.notionid == notion).first()
        return projectid[0]

def notionidupdate():
    url = "https://api.notion.com/v1/databases/eff25566ca524f7faa287b79e5175186/query"

    payload = ""
    headers = {
    'Authorization': 'Bearer secret_E56vtGLhJHUK1o7WerXlnUaZHcbHnnlyFiMuPPwU1bz',
    'Content-Type': 'application/json',
    'Notion-Version': '2021-08-16'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    jsonResponse = loads(response.text)
    
    for i in range(len(jsonResponse['results'])):
        id = jsonResponse['results'][i]['id']
        name = jsonResponse['results'][i]['properties']["Project Name"]['title'][0]['text']['content']

        count = db.session.query(Projects).filter(Projects.name == name).count()
        if count > 0:
            record = db.session.query(Projects).filter(Projects.name == name).first()
            record.notionid = id
            db.session.commit()

        