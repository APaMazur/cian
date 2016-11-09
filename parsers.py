#coding:utf8
import requests
from bs4 import BeautifulSoup
import re
import math


def clearHTML(data):
    return re.sub('<[^>]*>', '', data)



#number of rooms
def rooms(data):
    room = data.findAll('div', {'class':'object_descr_title'})
    for value in room:
        if re.search('([0-9]+)\-комн\. кв\.', clearHTML(str(value))) != None:
            room = re.search('([0-9]+)\-комн\. кв\.', clearHTML(str(value))).group(1)
        else:
            room = '-'
    return {
        'Rooms':room
    }
#print rooms(data)

#price
def price(data):
    pr = data.findAll('div', {'class':'object_descr_price'})
    for value in pr:
         value = clearHTML(str(value))
    if len(pr) > 0:
        pr = value
        pr = clearHTML(str(pr)).replace('\n', '').replace('\t', '').split(' ')
        pr = "".join([i for i in pr if i.isdigit()][-3:])
        if pr < 1000000:
            pr = pr * 1000
        return {
            'Price':pr
        }
    else:
        return {
            'Price': '-'
        }
#print price(data)

def information(data):
    infor = data.findAll('table', {'class': 'object_descr_props flat sale', 'style': 'float:left'})
    if len(infor) > 0:
        infor = clearHTML(str(infor[0])).replace('\n', '').replace('\t', '').replace(' ', '').replace('\xc2\xa0', '')

        #area of flat
        if re.search('Общаяплощадь\:([0-9]+(,[0-9]+)?)м', infor) != None:
            totsp = re.search('Общаяплощадь\:([0-9]+(,[0-9])?)м', infor).group(1)
        else:
            totsp = '-'

        #living area
        if re.search('Жилаяплощадь\:([0-9]+(,[0-9]+)?)м', infor) != None:
            livesp = re.search('Жилаяплощадь\:([0-9]+(,[0-9])?)м', infor).group(1)
        else:
            livesp = '-'

        #area of kitchen
        if re.search('Площадькухни\:([0-9]+(,[0-9]+)?)м', infor) != None:
            kitsp = re.search('Площадькухни\:([0-9]+(,[0-9])?)м', infor).group(1)
        else:
            kitsp = '-'

        #type of house
        #ATTENTION ne rabotaet, esli net brick i posle idet ne Tip,  a Visota potolkov
        type = re.search('Типдома\:(новостройка|вторичка)(\,)?(монолитный|кирпичный|кирпично\-монолитный|.+)?(Тип)', infor)
        if type.group(1) == 'новостройка':
            new = 1
        elif type.group(1) == None:
            new = '-'
        else:
            new = 0


        brick = type.group(3)
        if brick == 'монолитный' or brick == 'кирпичный' or brick == 'кирпично-монолитный':
            brick = 1
        elif brick == '' or brick == 'дом':
            brick = 'none'
        else:
            brick = 0

        #telephone
        if re.search('Телефон', infor) != None:
            if re.search('Телефон\:да', infor) != None:
                tel = 1
            else:
                 tel = 0
        else:
            tel = '-'

        #balcony
        if re.search('Балкон\:(.+)Лифт', infor) != None:
            bal = re.search('Балкон\:(.+)Лифт', infor).group(1)
            if bal == '-' or bal == '' or bal == 'нет':
                bal = 0
            else:
                bal = 1
        else:
            bal = '-'

        #floors
        if re.search('Этаж\:([0-9]+)\/([0-9]+)', infor) != None:
            floors = re.search('Этаж\:([0-9]+)\/([0-9]+)', infor)
            floor = floors.group(1)
            nfloors = floors.group(2)
        else:
            floor = '-'
            nfloors = '-'


        return {
            'Totsp':totsp,
            'Livesp':livesp,
            'Kitsp':kitsp,
            'Brick':brick,
            'Tel':tel,
            'Bal':bal,
            'Floor':floor,
            'Nfloors':nfloors,
            'New':new
        }
    else:
        return {
            'Totsp': '-',
            'Livesp': '-',
            'Kitsp': '-',
            'Brick': '-',
            'Tel': '-',
            'Bal': '-',
            'Floor': '-',
            'Nfloors': '-',
            'New': '-'
        }

#print information(data)

#distance to the metro
def metrdist(data):
    if len(data.findAll('span', {'class':'object_item_metro_comment'})) != 0:
        mdist = data.findAll('span', {'class':'object_item_metro_comment'})

        mdist = clearHTML(str(mdist[0])).replace('\n', '').replace('\t', '').replace(' ', '')
        if re.search('([0-9]+)мин(\.)?(пешком|)', mdist) != None:
            mdist = re.search('([0-9]+)мин(\.)?(пешком|)', mdist)
            if mdist.group(3) == 'пешком':
                walk = 1
            else:
                walk = 0
            md = mdist.group(1)
        else:
            md = '-'
            walk = '-'
    else:
            md = '-'
            walk = '-'
    return {
        'Metrdist':md,
        'Walk':walk
    }
#print metrdist(data)


def Coords(data):
    if data.findAll('div', {'class':'map_info_button_extend'}) != None:
        map = data.findAll('div', {'class':'map_info_button_extend'})
        map = re.split('&amp|center=|%2C', str(map))
        coords_list = []
        for item in map:
            if item[0].isdigit():
                coords_list.append(item)
        if len(coords_list) > 1:
            lat = float(coords_list[0])
            lon = float(coords_list[1])
        else:
            lat = '-'
            lon = '-'
    else:
        lat = '-'
        lon = '-'
    return lat, lon

#distance to the center
def dist(data):
    if Coords(data)[0] != '-':
        a = 55.755831
        b = 37.617673
        latitude = 111.134861111 * (a - Coords(data)[0])
        longitude = 111.321377778 * (b * math.cos(math.radians(a)) - Coords(data)[1] * math.cos(math.radians(Coords(data)[0])))
        d = math.sqrt(latitude ** 2 + longitude ** 2)
        d = round(d, 1)
    else:
        d = '-'
    return {
        'Dist':d
    }
#print dist(data)

def pars(data):
    return dict(rooms(data).items() + price(data).items() + information(data).items() + metrdist(data).items() + dist(data).items())
#print pars(data)
