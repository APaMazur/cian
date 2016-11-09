import requests
import csv
import parsers
from bs4 import BeautifulSoup
import re

def clearHTML(data):
    return re.sub('<[^>]*>', '', data)

url = 'http://www.cian.ru/cat.php?deal_type=sale&district[0]=%s&engine_version=2&offer_type=flat&p=%s&room1=%s&room2=%s&room3=%s&room4=%s&room5=%s&room6=%s'

def getLinks():
    links = []
    prevLen = 0

    for dist in range(1, 348):
        for room in range(0, 6):
            a = []
            for j in range(0, room):
                a.append(0)
            a.append(1)
            for j in range(room+1, 6):
                a.append(0)

            for page in range(1, 31):
                page_url = url % tuple([dist, page] + a)
                search_page = requests.get(page_url).content
                search_page = BeautifulSoup(search_page, 'lxml')

                flat_urls = search_page.findAll('div', {'ng-class':"{'serp-item_removed': offer.remove.state, 'serp-item_popup-opened': isPopupOpen}"})
                flat_urls = re.split('http://www.cian.ru/sale/flat/|/" ng-class="', str(flat_urls))

                for link in flat_urls:
                    if link.isdigit():
                        if not link in links:
                            links.append(link)
                print 'Page ' + str(page) + ', room ' + str(room) + ', region ' + str(dist) + ' finished, ' + str(len(links)) + ' links collected'
                if len(links) == prevLen:
                    break
                prevLen = len(links)

    csvfile = open('/Users/anton/work/projects/cianFinal/results/links.csv', 'wb')
    linkswriter = csv.writer(csvfile, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
    linkswriter.writerow(links)
    csvfile.close()

    return links

def getLinksFromFile():
    links = []

    csvfile = open('/Users/anton/work/projects/cianFinal/results/links.csv', 'rb')
    reader = csv.reader(csvfile, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
    for link in reader:
        links.append(link)
    csvfile.close()

    if len(links) > 0:
        return links[0]
    else:
        return []

def parseData(links):
    data = []

    csvfile = open('/Users/anton/work/projects/cianFinal/results/pars.csv', 'rb')
    reader = csv.reader(csvfile, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        data.append(row)
    csvfile.close()

    csvfile = open('/Users/anton/work/projects/cianFinal/results/pars.csv', 'wb')
    flatwriter = csv.writer(csvfile, delimiter=';', quotechar=';', quoting=csv.QUOTE_MINIMAL)
    if len(data) > 0:
        for row in data:
            flatwriter.writerow(row)
    else:
        flatwriter.writerow(['N', 'Rooms', 'Price', 'Totsp', 'Livesp', 'Kitsp', 'Dist', 'Metrdist', 'Walk', 'Brick', 'Tel', 'Bal', 'Floor', 'Nfloors', 'New'])

    for number in range(len(data)-2 if len(data) > 1 else 0, len(links)-1):
        def parseLinkData():
            page = links[number+1]
            print 'Flat ' + str(number+2) + '/' + str(len(links)) + ' ' + str(page)
            flat_url = 'http://www.cian.ru/sale/flat/' + str(page) + '/'
            data = BeautifulSoup(requests.get(flat_url).content, 'lxml')
            res = dict(parsers.pars(data).items() + {'N':str(page)}.items())
            print res
            return res

        def writeLinkData2CSV(res):
            flatwriter.writerow([
                res['N'],
                res['Rooms'],
                res['Price'],
                res['Totsp'],
                res['Livesp'],
                res['Kitsp'],
                res['Dist'],
                res['Metrdist'],
                res['Walk'],
                res['Brick'],
                res['Tel'],
                res['Bal'],
                res['Floor'],
                res['Nfloors'],
                res['New']
            ])

        for iteration in range(0, 5):       # Broken pipe hotfix
            res = parseLinkData()
            if res['Price'] != '-':
                writeLinkData2CSV(res)
                break

    csvfile.close()

parseData(getLinks())
#parseData(getLinksFromFile())