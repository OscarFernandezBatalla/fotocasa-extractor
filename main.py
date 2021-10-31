
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import pandas as pd
import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def scroll_slowly_until_end(driver):
    cnt = 0
    found = False
    timeout = time.time() + 60
    while not found and time.time() < timeout:
        cnt += 700
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, " + str(cnt) + ");")
        try:
            driver.find_element_by_class_name("re-Pagination")
            print("found!")
            found = True
        except:
            pass

    if not found:
        print("error, end of page not detected")
        exit(1)

    return driver.page_source


def extract_flat_links(soup):
    # found each flat AD
    entries_in_page = soup.find('section', class_='re-Searchresult').findChildren("div", recursive=False)

    # find the link of each flat
    links = []
    for entry in entries_in_page:
        link_raw = entry.find('a')
        if link_raw:
            data_href = link_raw['href']
            if data_href[:13] == "/es/alquiler/":
                link = "https://www.fotocasa.es" + data_href
                # print(link)
                links.append(link)
            else:
                print(data_href[:12])
                print("no proper link")
        else:
            print("no link detected")
    return links


def extract_info(link):
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    print(link)
    driver.get(link)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    price = soup.find('span', class_="re-DetailHeader-price").text.split()[0]
    if '.' in price:
        price = int(price.replace('.', ''))
    print(price)

    neigh = soup.find('h1', class_="re-DetailHeader-propertyTitle").text
    if 'Piso de alquiler en ' in neigh:
        neigh = neigh.replace('Piso de alquiler en ', '')
    print(neigh)

    features = [val.text for val in soup.find('ul', class_="re-DetailHeader-features").contents]

    rooms = None
    restrooms = None
    sqrt_met = None

    for feature in features:
        if 'hab' in feature:
            rooms = int(feature.split()[0])
        elif 'baño' in feature:
            restrooms = int(feature.split()[0])
        elif 'm²' in feature:
            sqrt_met = int(feature.split()[0])

    print("rooms", rooms)
    print("restrooms", restrooms)
    print("sqrt_met", sqrt_met)

    # description = soup.find('p', class_="fc-DetailDescription").text

    driver.close()


def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    url = 'https://www.fotocasa.es/es/alquiler/pisos/barcelona-capital/todas-las-zonas/l?latitude=41.3854&longitude=' \
          '2.17754&combinedLocationIds=724,9,8,232,376,8019,0,0,0'
    driver.get(url)
    delay = 10

    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located
                                           ((By.XPATH, '//*[@id="App"]/div[4]/div/div/div/footer/div/button[2]')))
        btn_cookie = driver.find_element_by_xpath('//*[@id="App"]/div[4]/div/div/div/footer/div/button[2]')
        btn_cookie.click()
        print("Pop up clicked")

        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="App"]/div[2]/div[1]/div[4]/main/div/div[3]/section')))

        # scroll through page and return the HTML source
        content = scroll_slowly_until_end(driver)
        soup = BeautifulSoup(content, "html.parser")

        links = extract_flat_links(soup)

        for link in links:
            extract_info(link)

    except TimeoutException:
        print("Loading took too much time!")


if __name__ == "__main__":
    main()
