from recipe_scrapers import scrape_me
from website.models import *
from website.nutrition import *

def scrape_recipe(website):
    scraper = scrape_me(website,wild_mode=True)

    title = scraper.title()
    
    try:
        if scraper.cook_time() == 0 or scraper.cook_time() == None:
            cooktime = 0
        else:
            cooktime = scraper.cook_time()
    except: cooktime = 0
        
    try:
        if scraper.prep_time() == 0 or scraper.prep_time() == None:
            preptime = 0
        else: 
            preptime = scraper.prep_time()
    except: preptime = 0
    
    try:
        yeild = int(''.join(i for i in scraper.yields() if i.isdigit()))
        if yeild == 0 or yeild == None:
            yeild = 1
    except: yeild = 1
    
    ings = scraper.ingredients()
    inst=scraper.instructions().split('\n')
    img = scraper.image()
    
        
    return [[title, img, yeild, cooktime, preptime], [ings], [inst]]


def make_dish(title, img, yeild):
    newdish = Dish(
        name = title,
        pictureURL = img,
        numServings = yeild,
    )
    db.session.add(newdish)
    db.session.commit()
    
    newid = db.session.query(Dish).filter(Dish.name == title).first().id
    
    return newid


def make_recipe(nutrition, dishid):
    newrec = Recipe(
        dishfk = dishid,
        qty = nutrition['servingqty'],
        measurement = nutrition['servingunit'],
        ing = nutrition['foodname'],
        fat_total = nutrition['totalFat'],
        weight = nutrition['weight'],
        fat_sat = nutrition['satFat'],
        fat_trans = nutrition['transFat'],
        cholesterol = nutrition['cholesterol'],
        sodium = nutrition['sodium'],
        potassium = nutrition['potassium'],
        carb_total = nutrition['totalCarb'],
        carb_fiber = nutrition['fiber'],
        carb_sugar = nutrition['sugar'],
        protein = nutrition['protein'],
        calories = nutrition['calories'],
        pictureURL = nutrition['picURL'],
    )
    db.session.add(newrec)
    db.session.commit()

def make_steps(step, dishid, i):
    newstep = Steps(
        dishfk=dishid,
        step_num = i,
        step_text = step
    )
    db.session.add(newstep)
    db.session.commit()