from recipe_scrapers import scrape_me



def scrape_recipe(website):
    scraper = scrape_me(website,wild_mode=True)

    title = scraper.title()
    totaltime = scraper.total_time()
    ing = scraper.ingredients()
    inst=scraper.instructions()
    img = scraper.image()
    scraper.host()
    scraper.links()
    nutrients=scraper.nutrients() 
    yeild=scraper.yields()
    print(title, totaltime, yeild)
    print(ing)
    print(inst)
    print(img)
    print(nutrients)


# scrape_recipe('https://iwashyoudry.com/garlic-parmesan-pork-chop-recipe/')
scrape_recipe('https://www.foodnetwork.com/recipes/food-network-kitchen/5-ingredient-instant-pot-mac-and-cheese-3649854')