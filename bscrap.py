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
categories=('Breakfast_Recipes', 'Brunch_Recipes', 'Dessert_Recipes', 'Dinner_Recipes', 
            'Lunch_Recipes', 'Main_Dish_Recipes', 'Salad_Recipes', 'Side_Dish_Recipes',
            'Soup_Recipes', 'Stew_Recipes', 'Vegetarian_Recipes', 'Smoothie_Recipes',
            'Condiment_Recipes')
category_base_url = 'https://recipes.fandom.com/wiki/Category:'
#TODO: crawl all categories
#To crawl one category, insert the link below:
category_link='https://recipes.fandom.com/wiki/Category:Dessert_Recipes'


def get_ingredients(soup):
    ingredients=[]
    ingredients_heading=None
    for heading in ingredients_headings:
        try:
            ingredients_heading = soup.find('span', {"id": lambda x: x and x.startswith(heading)}).find_parent()
        except AttributeError:
            continue
    if not ingredients_heading:
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

def get_directions(soup):
    directions = []
    directions_heading=None
    for heading in (directions_headings):
        try:
            directions_heading = soup.find('span', {"id": lambda x: x and x.startswith(heading)}).find_parent()        
        except AttributeError:
            continue
    if not directions_heading:
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

def get_categories(soup):
    categories = []
    category_section= soup.find('div', class_='page-header__categories').find_all('a', {"title": lambda x: x and x.startswith('Category:')})
    for category in category_section:
        categories.append(category.text)
    return categories

def get_title(soup):
    title = soup.find('h1', class_='page-header__title').text.strip()
    title = title.replace('Oriental', 'Asian') #modernize the titles
    return title                              

def parse_recipes(recipe_links): #TODO: include serving, image and copyright info where present
    count = 0
    recipe_list=[]
    for link in recipe_links:
        recipe_text=requests.get(link).text
        soup = BeautifulSoup(recipe_text, 'lxml')
        categories = get_categories(soup) #TODO: check for already-crawled categories and skip
        title = get_title(soup)     
        ingredients = get_ingredients(soup)
        directions = get_directions(soup)
        recipe_list.append([title, link, repr(ingredients), repr(directions), repr(categories)])
        count+=1
    print(f"{count} recipes parsed")
    return(recipe_list)

def save_to_db(df):
    conn = sqlite3.connect("recipes.db")
    cursor=conn.cursor()
    create_sql = "CREATE TABLE IF NOT EXISTS recipes (title TEXT, url TEXT, ingredients TEXT, directions TEXT, categories TEXT)"
    cursor.execute(create_sql)
    df.to_sql(name="recipes", con=conn, if_exists='append', index=False)
    conn.commit
    conn.close

#traverse all pages in category starting with category_url and add all recipe urls in them to recipe_links list
def crawl_category(category_url, recipe_link_list): 
    html_text = requests.get(category_url).text 
    soup = BeautifulSoup(html_text, 'lxml')
    category_page_links=soup.find_all('li', class_='category-page__member')
    for link_item in category_page_links:
        link= link_item.find('a')
        title = link.get('title')
        if (title.startswith("Category:")):
               continue
        recipe_link_list.append(base_url+link.get('href'))
    next_page=None
    next_page= soup.find('a', class_='category-page__pagination-next wds-button wds-is-secondary')        
    if next_page:
        crawl_category(next_page.get('href'), recipe_links)

recipe_links=[]
crawl_category(category_link, recipe_links)
recipe_data=parse_recipes(recipe_links)
recipe_df = pandas.DataFrame (recipe_data, columns = ['Title', 'Url', 'Ingredients', 'Directions', 'Categories'])
#TODO: remove duplicates

############ OUTPUT #############
#print(recipe_df)
save_to_db(recipe_df)
recipe_df.to_csv('recipes.csv', mode='a', index=False)

############ TESTING ##############
# ingredients = get_ingredients('https://recipes.fandom.com/wiki/Belgian_Endive,_Spinach,_and_Radicchio_Salad_with_Mustard_Vinaigrette')
# for ingredient in ingredients:
#     print(ingredient)
