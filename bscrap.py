from bs4 import BeautifulSoup
import requests
from requests_file import FileAdapter
import lxml
import pandas
import sqlite3
from sqlalchemy import null

base_url = "https://recipes.fandom.com"
ingredients_headings=("Ingredients")
directions_headings=("Directions", "Instructions", "Method", "Steps", "Preparation")

def get_ingredients(url):
    recipe_text=requests.get(url).text
    soup = BeautifulSoup(recipe_text, 'lxml')
    ingredients=[]
    ingredients_heading=None
    for heading in ingredients_headings:
        try:
            ingredients_heading = soup.find('span', {"id": lambda x: x and x.startswith('Ingredients')}).find_parent()
        except AttributeError:
            continue
    if not ingredients_heading:
        ingredients="Ingredients not found"
        return ingredients
    next_sib = ingredients_heading
    while True:
        next_sib = next_sib.nextSibling
        if not next_sib:
            break
        tag_name = next_sib.name
        if (tag_name in ("ol", 'ul')):
            for li in next_sib.find_all('li'):
                ingredients.append(li.text)
        elif (tag_name == "h3"):
            subheading = next_sib.find('span', class_='mw-headline')
            ingredients.append(subheading.text)
        elif (tag_name == 'p'):
            ingredients_list=next_sib.text.split("\n")
            for ingredient in ingredients_list:
                if (ingredient!=""):
                    ingredients.append(ingredient)
        elif (tag_name in ('div', 'figure', None)):
            continue
        else:
            break
    return ingredients            

def get_directions(url):
    recipe_text=requests.get(url).text
    soup = BeautifulSoup(recipe_text, 'lxml')
    directions = []
    directions_heading=None
    for heading in (directions_headings):
        try:
            directions_heading = soup.find('span', {"id": lambda x: x and x.startswith(heading)}).find_parent()        
        except AttributeError:
            continue
    if not directions_heading:
        directions = "Directions not found"
        return directions
    next_sib = directions_heading
    while True:
        next_sib = next_sib.nextSibling
        if not next_sib:
            break
        tag_name=next_sib.name
        if (tag_name in ("ol", 'ul')):
            for li in next_sib.find_all('li'):
                directions.append(li.text)
        elif (tag_name == "p"):
            next_text = " ".join((next_sib.text).split())  #get rid of empty paragraphs
            splitter=(next_text).replace(". ", ".OCELOT-SPLEENS")
            directions_list=splitter.split("OCELOT-SPLEENS")  #Split paragraph by sentence
            for step in directions_list:
                if (step!=""):
                    directions.append(step)
        elif (tag_name == "h3"):
            subheading = next_sib.find('span', class_='mw-headline')
            if (subheading.text!="Other Links"):
                directions.append(subheading.text)
        elif (tag_name==None):
            continue
        else:
            break
    return directions

def get_categories(url):
    recipe_text=requests.get(url).text
    soup = BeautifulSoup(recipe_text, 'lxml')
    categories = []
    category_section= soup.find('div', class_='page-header__categories').find_all('a', {"title": lambda x: x and x.startswith('Category:')})
    for category in category_section:
        categories.append(category.text)
    return categories                                 

def parse_recipes(recipes): #TODO: parse one recipe at a time, and include serving, image and copyright info where present
    count = 0
    recipe_list=[]
    for recipe in recipes:
        link= recipe.find('a')
        title = link.get('title')
        if (title.startswith("Category:")):
            continue
        title = title.replace('Oriental', 'Asian') #modernize the titles        
        url = base_url+link.get('href')
        try:
            ingredients = get_ingredients(url)
        except:
            continue
        try:
            directions = get_directions(url)
        except:
            continue
        try:
            categories = get_categories(url)
        except:
            continue
        recipe_list.append([title, url, repr(ingredients), repr(directions), repr(categories)])
        count+=1
    print(f"{count} recipes parsed")
    return(recipe_list)

def save_to_db(df):
    print(f"Saving to database ..... dataframe: {df}")
    conn = sqlite3.connect("recipes2.db")
    cursor=conn.cursor()
    create_sql = "CREATE TABLE IF NOT EXISTS recipes (title TEXT, url TEXT, ingredients TEXT, directions TEXT, categories TEXT)"
    cursor.execute(create_sql)
    df.to_sql(name="recipes", con=conn, if_exists='append', index=False)
    conn.commit
    conn.close

def crawl_category(url, recipe_link_list):
    html_text = requests.get(url).text 
    soup = BeautifulSoup(html_text, 'lxml')
    recipe_link_items=soup.find_all('li', class_='category-page__member')
    for link_item in recipe_link_items:
        recipe_link_list.append(link_item)
    next_page=None
    next_page= soup.find('a', class_='category-page__pagination-next wds-button wds-is-secondary')        
    if next_page:
        crawl_category(next_page.get('href'), recipe_link_list)

recipe_links=[]
crawl_category('https://recipes.fandom.com/wiki/Category:Dinner_Recipes', recipe_links)
recipe_data=parse_recipes(recipe_links)
recipe_df = pandas.DataFrame (recipe_data, columns = ['Title', 'Url', 'Ingredients', 'Directions', 'Categories'])

#print(recipe_df)
#save_to_db(recipe_df)
#TODO: save to csv

######## TESTING
# ingredients = get_ingredients('https://recipes.fandom.com/wiki/Belgian_Endive,_Spinach,_and_Radicchio_Salad_with_Mustard_Vinaigrette')
# for ingredient in ingredients:
#     print(ingredient)
