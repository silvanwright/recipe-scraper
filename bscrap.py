from bs4 import BeautifulSoup
import requests
import lxml

urlstart = 'href="'
urlend = '" title'
base_url = "https://recipes.fandom.com/"

def get_url(str):
    index1 = str.index(urlstart)
    index2 = str.index(urlend)
    url = str[index1+len(urlstart): index2]
    return base_url+url

html_text = requests.get('https://recipes.fandom.com/wiki/Category:Main_Dish_Recipes').text 
soup = BeautifulSoup(html_text, 'lxml')
recipes = soup.find_all('li', class_='category-page__member') #TODO: exclude category links

for recipe in recipes:
    url = get_url(str(recipe))
    print(url)