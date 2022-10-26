from bs4 import BeautifulSoup
import requests
from requests_file import FileAdapter
import lxml
import pandas
import sqlite3
from sqlalchemy import null

base_url = "https://recipes.fandom.com"

def get_ingredients(url):
    recipe_text=requests.get(url).text
    soup = BeautifulSoup(recipe_text, 'lxml')
    ingredients=[]
    try:
        ingredients_heading = soup.find('span', {"id": lambda x: x and x.startswith('Ingredients')}).find_parent()
    except AttributeError:
        return null
    next_sib = ingredients_heading.nextSibling
    while True:
        next_sib = next_sib.nextSibling
        try:
            tag_name = next_sib.name
        except AttributeError:
            break
        if (tag_name == "ul"):
            for li in next_sib.find_all('li'):
                ingredients.append(li.text)
        elif (tag_name == "h3"):
            clean_h3 = next_sib.text[:-2]
            ingredients.append(clean_h3)
        elif (tag_name == 'p'):
            clean_paragraph = next_sib.text.replace('\n', '')
            if clean_paragraph!='':
                ingredients.append(clean_paragraph)
        elif (tag_name=='div'):
            continue
        elif (tag_name=='figure'):
            continue
        elif (tag_name==None):
            continue
        elif (tag_name == "h2"):
            break
        else:
            break
    return ingredients            

def get_directions(url):
    recipe_text=requests.get(url).text
    soup = BeautifulSoup(recipe_text, 'lxml')
    directions = []
    directions_heading=None
    for heading in ("Directions", "Instructions", "Method"):
        try:
            directions_heading = soup.find('span', {"id": lambda x: x and x.startswith(heading)}).find_parent()        
        except AttributeError:
            continue
    if not directions_heading:
        directions = "Not found"
        return directions
    next_sib = directions_heading
    while True:
        next_sib = next_sib.nextSibling
        if not next_sib:
            break
        tag_name=next_sib.name
        if (tag_name == "ol" or tag_name == 'ul'):
            for li in next_sib.find_all('li'):
                directions.append(li.text)
        elif (tag_name == "p"):
            next_text = " ".join((next_sib.text).split())  #get rid of empty paragraphs
            splitter=(next_text).replace(". ", ".OCELOT-SPLEENS")
            directions_list=splitter.split("OCELOT-SPLEENS")  #Split paragraph by sentence without removing periods.
            for step in directions_list:
                if (step!=""):  #get rid of empty lines
                    directions.append(step)
        elif (tag_name == "h3"):
            clean_h3 = next_sib.text[:-2]
            if (clean_h3!="Other Links"):
                directions.append(clean_h3)
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

def parse_recipes(recipes):
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

def save_to_db(recipe_list):
    df = pandas.DataFrame (recipe_list, columns = ['Title', 'Url', 'Ingredients', 'Directions', 'Categories'])
    print(df)

    conn = sqlite3.connect("recipes2.db")
    cursor=conn.cursor()
    create_sql = "CREATE TABLE IF NOT EXISTS recipes (title TEXT, url TEXT, ingredients TEXT, directions TEXT, categories TEXT)"
    cursor.execute(create_sql)

    df.to_sql(name="recipes", con=conn, if_exists='append', index=False)
    conn.commit
    conn.close

def crawl_category(url):
    html_text = requests.get(url).text 
    soup = BeautifulSoup(html_text, 'lxml')
    recipes = soup.find_all('li', class_='category-page__member')
    recipe_list=parse_recipes(recipes)
    save_to_db(recipe_list)
    print(f"saved {url} recipes to database")
    next_page=None
    next_page= soup.find('a', class_='category-page__pagination-next wds-button wds-is-secondary')        
    if not next_page:
        return recipe_list
    else:
        crawl_category(next_page.get('href'))

#TODO: Next category: Dinner recipes in 'by course'
crawl_category('https://recipes.fandom.com/wiki/Category:Brunch_Recipes')
