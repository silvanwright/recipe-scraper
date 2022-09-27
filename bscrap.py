from bs4 import BeautifulSoup
import requests
import lxml
import re

urlstart = "href=\""
urlend = "\" title"

def get_url(str):
    idx1 = str.index(urlstart)
    idx2 = str.index(urlend)
    url = str[idx1+len(urlstart): idx2]
    print(url)

print(urlstart)
print(urlend)

html_text = requests.get('https://recipes.fandom.com/wiki/Category:Main_Dish_Recipes').text
soup = BeautifulSoup(html_text, 'lxml')
recipes = soup.find_all('li', class_='category-page__member')

get_url('member-link" href="/wiki/Outdoor_Beef_and_Rice_Skillet" title="Outdoor Beef and Rice Skillet">Outdoor Beef and Rice Skillet</a> </li>')
