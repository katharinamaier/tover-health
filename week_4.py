# import necessary packages
import requests
from bs4 import BeautifulSoup
import pandas as pd


# defining variables and parsing websites
url = "https://www.tover.care/ie/tovertafel-pixie/games"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

name = "h3.teaser-game__title"
device = "div.teaser-game__support"
effect_list = "ul.meta__list"
level_list = "div.meta__level"
level = "div.meta__star.meta__star--active"

data = {
    "name" : [],
    "device" : [],
    "effect" : [],
    "level" : []
}


# finding the game titles
name_data = soup.select(name)

for i in name_data:
    data["name"].append(i.text)



# finding the devices
device_data = soup.select(device)
device_data_clean = []

for i in range(len(device_data)):
    devices = device_data[i].select("span")
    device_data_clean.append(devices[0].text)

for i in range(len(device_data_clean)):
    devices = []
    if "1" in device_data_clean[i]:
        devices.append("1")
    if "2" in device_data_clean[i]:
        devices.append("2")
    if "3" in device_data_clean[i]:
        devices.append("3")
    if "Pixie" in device_data_clean[i]:
        devices.append("Pixie")
    if "Lab" in device_data_clean[i]:
        devices.append("Lab")

    data["device"].append(devices)



# finding game effects
effect_data = soup.select(effect_list)

for i in range(len(effect_data)):
    effects = []
    effect_names = effect_data[i].select("div")
    for j in range(len(effect_names)):
        effects.append(effect_names[j].text)
    data["effect"].append(effects)



# finding game levels
lvl_data = soup.select(level_list)
lvl_data_clean = []

for i in range(len(lvl_data)):
    lvl =  lvl_data[i].select(level)
    data["level"].append(len(lvl))




df = pd.DataFrame.from_dict(data)
print(df)

