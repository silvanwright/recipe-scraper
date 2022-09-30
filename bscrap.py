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
    ingredients_list=[]
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
            ingredients_list.append(next_sib.text)
        elif (tag_name == "h3"):
            clean_h3 = next_sib.text[:-2]
            ingredients_list.append(clean_h3)
        elif (tag_name == "h2"):
            break
        elif (tag_name==None):
            continue
        else:
            break
    return ingredients_list        

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
        if ((tag_name == "ol") or (tag_name == "p")):
            directions.append(next_sib.text)
        elif (tag_name == "h3"):
            clean_h3 = next_sib.text[:-2]
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

# for recipe in recipes[:5]:
    # for link in recipe.find('a'):
        # title = link.get('title')
        # if (title.startswith("Category:")):
            # continue
        # url = base_url+link.get('href')
        # print("*****"+title+"******")
        # print(url)
        # ingreds = []
        # try:
            # ingreds = get_ingreds(url)
        # except:
            # print("Ingreds not found")
            # continue
        # print("Ingredients")
        # print(ingreds)
        # try:
            # directions = get_directions(url)
        # except:
            # print("Directions not found")
            # continue
        # print("Directions")
        # print(directions)
        # print(f"{title} complete")
        # count+=1
# print(f"{count} recipes parsed")


 
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
    for ingredient in ingredients:
        print(ingredient)
    for step in directions:
        print(step)
    count+=1
print(f"{count} recipes parsed")