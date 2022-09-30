from bs4 import BeautifulSoup
import requests
from requests_file import FileAdapter
import lxml

urlstart = 'href="'
urlend = '" title'
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
        elif (tag_name == "h2"):
            break
        elif (tag_name==None):
            continue
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
        if (tag_name == "ol"):
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

html_text = requests.get('https://recipes.fandom.com/wiki/Category:Main_Dish_Recipes').text 
soup = BeautifulSoup(html_text, 'lxml')
recipes = soup.find_all('li', class_='category-page__member')

count = 0

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
    print(title)
    print(url)
    print(ingredients)
    print(directions)
    count+=1

print(f"{count} recipes parsed")