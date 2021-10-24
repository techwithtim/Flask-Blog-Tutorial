import requests
import json

def get_food_item(item):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"    

    payload='query='+item
    headers = {
    'x-app-id': '9b92ba02',
    'x-app-key': 'a8e4036769b4268c11f0fb1a50e7ec3c',
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    fulljson = json.loads(response.text)
    
    # return json.dumps(fulljson)
    with open('fulljson.json','w') as jsonfull:
        jsonfull.write(json.dumps(fulljson))
    
    nutrition = parse_results(fulljson)
    
    with open('nutrition.json','w') as jsonfile:
        jsonfile.write(json.dumps(nutrition))
    return nutrition

def parse_results(fulljson):
    full_nutrition = {}
    
    full_nutrition['foodname'] = fulljson['foods'][0]['food_name']
    full_nutrition['servingqty'] = fulljson['foods'][0]['serving_qty']
    full_nutrition['servingunit'] = fulljson['foods'][0]['serving_unit']
    #weight
    if 'serving_weight_grams' not in fulljson['foods'][0]: full_nutrition['weight'] = 0
    elif fulljson['foods'][0]['serving_weight_grams'] is None: full_nutrition['weight'] = 0
    else: full_nutrition['weight'] = round(fulljson['foods'][0]['serving_weight_grams'],1)
    
    #calories
    if 'nf_calories' not in fulljson['foods'][0]: full_nutrition['calories'] = 0
    elif fulljson['foods'][0]['nf_calories'] is None: full_nutrition['calories'] = 0
    else: full_nutrition['calories'] = round(fulljson['foods'][0]['nf_calories'],1)
    
    #calories from fat
    if 'nf_total_fat' not in fulljson['foods'][0]: full_nutrition['calFat'] = 0
    elif fulljson['foods'][0]['nf_total_fat'] is None: full_nutrition['calFat'] = 0
    else: full_nutrition['calFat'] = round((fulljson['foods'][0]['nf_total_fat'])*9,1)
    
    #total fat
    if 'nf_total_fat' not in fulljson['foods'][0]: full_nutrition['totalFat'] = 0
    elif fulljson['foods'][0]['nf_total_fat'] is None: full_nutrition['totalFat'] = 0
    else: full_nutrition['totalFat'] = round(fulljson['foods'][0]['nf_total_fat'],1)
    
    #Saturated fat
    if 'nf_saturated_fat' not in fulljson['foods'][0]: full_nutrition['satFat'] = 0
    elif fulljson['foods'][0]['nf_saturated_fat'] is None: full_nutrition['satFat'] = 0
    else: full_nutrition['satFat'] = round(fulljson['foods'][0]['nf_saturated_fat'],1)
    
    #trans fat
    if 'nf_trans_fatty_acid' not in fulljson['foods'][0]: full_nutrition['transFat'] = 0
    elif fulljson['foods'][0]['nf_trans_fatty_acid'] is None: full_nutrition['cholesterol'] = 0
    else: full_nutrition['transFat'] = round(fulljson['foods'][0]['nf_trans_fatty_acid'],1)
    
    #cholesterol
    if 'nf_cholesterol' not in fulljson['foods'][0]: full_nutrition['cholesterol'] = 0
    elif fulljson['foods'][0]['nf_cholesterol'] is None: full_nutrition['cholesterol'] = 0
    else: full_nutrition['cholesterol'] = round(fulljson['foods'][0]['nf_cholesterol'],1)
    
    #sodium
    if 'nf_sodium' not in fulljson['foods'][0]: full_nutrition['sodium'] = 0
    elif fulljson['foods'][0]['nf_sodium'] is None: full_nutrition['sodium'] = 0
    else: full_nutrition['sodium'] = round(fulljson['foods'][0]['nf_sodium'],1)
    
    #Total Carbs
    if 'nf_total_carbohydrate' not in fulljson['foods'][0]: full_nutrition['totalCarb'] = 0
    elif fulljson['foods'][0]['nf_total_carbohydrate'] is None: full_nutrition['totalCarb'] = 0
    else: full_nutrition['totalCarb'] = round(fulljson['foods'][0]['nf_total_carbohydrate'],1)
    
    #Fiber
    if 'nf_dietary_fiber' not in fulljson['foods'][0]: full_nutrition['fiber'] = 0
    elif fulljson['foods'][0]['nf_dietary_fiber'] is None: full_nutrition['fiber'] = 0
    else: full_nutrition['fiber'] = round(fulljson['foods'][0]['nf_dietary_fiber'],1)
    
    #sugar
    if 'nf_sugars' not in fulljson['foods'][0]: full_nutrition['sugar'] = 0
    elif fulljson['foods'][0]['nf_sugars'] is None: full_nutrition['sugar'] = 0
    else: full_nutrition['sugar'] = round(fulljson['foods'][0]['nf_sugars'],1)
    
    #protein
    if 'nf_protein' not in fulljson['foods'][0]: full_nutrition['protein'] = 0
    elif fulljson['foods'][0]['nf_protein'] is None: full_nutrition['protein'] = 0
    else: full_nutrition['protein'] = round(fulljson['foods'][0]['nf_protein'],1)
    
    #potassium
    if 'nf_potassium' not in fulljson['foods'][0]: full_nutrition['potassium'] = 0
    elif fulljson['foods'][0]['nf_potassium'] is None: full_nutrition['potassium'] = 0
    else: full_nutrition['potassium'] = round(fulljson['foods'][0]['nf_potassium'],1)
    
    full_nutrition['picURL'] = fulljson['foods'][0]['photo']['thumb']
    
    return full_nutrition

def nutrition_single(ings):
    allnutrition = {}
    weight = 0
    fat_total = 0
    fat_sat = 0
    fat_trans = 0
    cholesterol = 0
    sodium = 0
    potassium = 0
    carb_total = 0
    carb_fiber = 0
    carb_sugar = 0
    protein = 0
    calories = 0
    calories_fat = 0
    
    for ing in ings:
        weight = weight + round(ing.weight)
        fat_total = fat_total + round(ing.fat_total)
        fat_sat = fat_sat + round(ing.fat_sat)
        fat_trans = fat_trans + round(ing.fat_trans)
        cholesterol = cholesterol + round(ing.cholesterol)
        sodium = sodium + round(ing.sodium)
        potassium = potassium + round(ing.potassium)
        carb_total = carb_total + round(ing.carb_total)
        carb_fiber = carb_fiber + round(ing.carb_fiber)
        carb_sugar = carb_sugar + round(ing.carb_sugar)
        protein = protein + round(ing.protein)
        calories = calories + round(ing.calories)
        calories_fat= round(fat_total*9)
    
    allnutrition['fat_total'] = fat_total
    allnutrition['weight'] = weight
    allnutrition['fat_sat'] = fat_sat
    allnutrition['fat_trans'] = fat_trans
    allnutrition['cholesterol'] = cholesterol
    allnutrition['sodium'] = sodium
    allnutrition['potassium'] = potassium
    allnutrition['carb_total'] = carb_total
    allnutrition['carb_fiber'] = carb_fiber
    allnutrition['carb_sugar'] = carb_sugar
    allnutrition['protein'] = protein
    allnutrition['calories'] = calories
    allnutrition['calories_fat'] = calories_fat
    
    return allnutrition

if __name__ == '__main__':
    eat = get_food_item("30 oz van camps pork and beans")
    with open('fulljson.json','w') as jsonfull:
        jsonfull.write(eat)