import requests, json
from . import db
from .models import Dish


def auth(auth_name):
    with open("website/key.txt") as file:
        data = file.read()
        keys = json.loads(data)
    key = keys[auth_name]
    return key
    
    
def get_supplies():
    url = "https://api.notion.com/v1/databases/ac64bba17a8e4a3aa696543024c86206/query"
    
    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer ' + auth('notion')
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    jsonResponse = json.loads(response.text)
    
    return jsonResponse

def get_menu():
    url = "https://api.notion.com/v1/databases/79e5cfd9b9654ca492ed8290557c37da/query"
    
    payload = ""
    headers = {
    'Content-Type': 'application/json',
    'Notion-Version': '2021-05-13',
    'Authorization': 'Bearer ' + auth('notion')
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    jsonResponse = json.loads(response.text)

    with open("menu.json",'w') as file:
        file.write(json.dumps(jsonResponse))
    
    # menu = []
    for i in range(len(jsonResponse['results'])):
        id = jsonResponse['results'][i]['id']
        name = jsonResponse['results'][i]['properties']['Name']['title'][0]['text']['content']
        # littlemenu = {}
        # littlemenu['id'] = id
        # littlemenu['name'] = name
        # menu.append(littlemenu)
        
        if Dish.query.filter_by(notionID=id).first():
            pass
        else:
            item = Dish(notionID=id, item=name)
            db.session.add(item)
            db.session.commit()
    
    # return menu

def get_meals():
    pass