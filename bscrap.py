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
    try:
        directions_heading = soup.find('span', {"id": lambda x: x and x.startswith('Directions')}).find_parent()
    except AttributeError:
        return null
    next_sib = directions_heading.nextSibling
    while True:
        next_sib = next_sib.nextSibling
        try:
            tag_name = next_sib.name
        except AttributeError:
            break
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
        elif (tag_name == "h2"):
            break
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
        title = title.replace('Oriental', 'Asian') #modernize the titles
        if (title.startswith("Category:")):
            continue
        url = base_url+link.get('href')
        ingredients = []
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

html_text = requests.get('https://recipes.fandom.com/wiki/Category:Dessert_Recipes?from=Sock-It-To-Me+Coffee+Cake').text 
soup = BeautifulSoup(html_text, 'lxml')
recipes = soup.find_all('li', class_='category-page__member')
recipe_list = parse_recipes(recipes)

#TODO: wrap in a function that crawls all pages in a category. Next category: Dinner recipes in 'by course'
next_page= soup.find('a', class_='category-page__pagination-next wds-button wds-is-secondary')
print(f"Next page: {next_page.get('href')}")#TODO: except attribute error (break when reaching last page)

df = pandas.DataFrame (recipe_list, columns = ['Title', 'Url', 'Ingredients', 'Directions', 'Categories'])
print(df)

conn = sqlite3.connect("recipes.db")
cursor=conn.cursor()
create_sql = "CREATE TABLE IF NOT EXISTS recipes (title TEXT, url INTEGER, ingredients TEXT, directions TEXT, categories TEXT)"
cursor.execute(create_sql)

df.to_sql(name="recipes", con=conn, if_exists='append', index=False)
conn.commit
conn.close