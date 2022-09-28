from bs4 import BeautifulSoup
import requests
from requests_file import FileAdapter
import lxml

urlstart = 'href="'
urlend = '" title'
base_url = "https://recipes.fandom.com"

    
def get_ingreds(url):
    recipe_text=requests.get(url).text
    soup = BeautifulSoup(recipe_text, 'lxml')
    try:
        ingreds_heading = soup.find('span', {"id": lambda x: x and x.startswith('Ingredients')}).find_parent()
    except AttributeError:
        return
    next_sib = ingreds_heading.nextSibling
    while True:
        next_sib = next_sib.nextSibling
        try:
            tag_name = next_sib.name
        except AttributeError:
            break
           # print("Attribute Error")
           # tag_name = ""
        if (tag_name == "ul"):
            print(next_sib.text)
        elif (tag_name == "h3"):
            clean_h3 = next_sib.text[:-2] #TODO fix hardcoded nonsense
            print(clean_h3)
        elif (tag_name == "h2"):
            print ("*****")
            break
        elif (tag_name==None):
            continue
        else:
            break
            
    

html_text = requests.get('https://recipes.fandom.com/wiki/Category:Main_Dish_Recipes').text 
soup = BeautifulSoup(html_text, 'lxml')
recipes = soup.find_all('li', class_='category-page__member')

for recipe in recipes:
    for link in recipe.find_all('a'):
        title = link.get('title')
        if (title.startswith("Category:")):
            continue
        url = base_url+link.get('href')
        print(title)
        print(url)
        get_ingreds(url)
 