import pickle

from bs4 import BeautifulSoup
from selenium import webdriver
import re
import pandas as pd
import logging
import datetime
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def create_pickle(date):
    pick_w = open(date + '.pkl', 'wb')


def get_num_pages(driver):
    delay = 10
    try:
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.CLASS_NAME, "re-Pagination")))

        pages = int(driver.find_element_by_class_name("re-Pagination")
                    .find_element_by_class_name("sui-MoleculePagination").find_elements_by_tag_name('li')[-2].text)
        print("total pages obtained: ", pages)
        # time.sleep(5)
        return pages
    except:
        print("error taking num pages")
        exit(1)


def first_scroll_slowly_until_end(driver):
    cnt = 0
    found = False
    timeout = time.time() + 60

    total_pages = None

    while not found and time.time() < timeout:
        cnt += 1000
        driver.execute_script("window.scrollTo(0, " + str(cnt) + ");")
        try:
            driver.find_element_by_class_name("re-Pagination")
            found = True

            total_pages = get_num_pages(driver)
        except:
            pass

    if not found:
        print("error, end of page not detected")
        exit(1)

    return driver.page_source, total_pages


def scroll_slowly_until_end(driver):
    cnt = 0
    found = False
    timeout = time.time() + 40

    while not found and time.time() < timeout:
        cnt += 200
        time.sleep(0.1)
        driver.execute_script("window.scrollTo(0, " + str(cnt) + ");")
        try:
            driver.find_element_by_class_name("re-Pagination")
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

    # print("total entries found:", len(entries_in_page))

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
                print("no proper link:", data_href[:12])
        else:
            print("no link detected")

    print("total links detected:", len(links))
    return links


def extract_info(link):
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    driver.get(link)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    price = soup.find('span', class_="re-DetailHeader-price").text.split()[0]
    if '.' in price:
        price = int(price.replace('.', ''))

    neigh = soup.find('h1', class_="re-DetailHeader-propertyTitle").text
    if 'Piso de alquiler en ' in neigh:
        neigh = neigh.replace('Piso de alquiler en ', '')

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

    print("price: " + str(price) + " rooms: " + str(rooms) + " restrooms: " + str(restrooms) + " sqrt_meters: "
          + str(sqrt_met) + " neighbourhood: " + neigh)

    ########################################
    # TODO: YOU CAN ADD HERE MORE ATTRIBUTES

    # description = soup.find('p', class_="fc-DetailDescription").text
    # ...

    ########################################

    driver.close()

    dict_ = {"price": price, "rooms": rooms, "restrooms": restrooms, "sqrt_meters": sqrt_met,
             "neighbourhood": neigh, "link": link}

    return dict_


def click_popup(driver):
    delay = 10
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located
                                           ((By.XPATH, '//*[@id="App"]/div[4]/div/div/div/footer/div/button[2]')))
        btn_cookie = driver.find_element_by_xpath('//*[@id="App"]/div[4]/div/div/div/footer/div/button[2]')
        btn_cookie.click()
        print("Popup clicked")

        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="App"]/div[2]/div[1]/div[4]/main/div/div[3]/section')))

    except TimeoutException:
        print("Loading took too much time!")


def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)

    date = datetime.date.today().strftime("%d-%m-%Y")

    pickle_exists = os.path.isfile(date + '.pkl')
    db = {}

    if pickle_exists:
        pickle_file = open(date + '.pkl', 'rb')
        db = pickle.load(pickle_file)
        pickle_file.close()

    print("Database init:", db)

    first_page = True
    total_pages = 999
    actual_page = 1

    while actual_page < total_pages:

        print("Reading page " + str(actual_page) + " of " + str(total_pages))
        print("Percent: " + str((actual_page * 100) / total_pages) + "%")

        # scroll through page and return the HTML source
        if first_page:
            url = 'https://www.fotocasa.es/es/alquiler/pisos/barcelona-capital/todas-las-zonas/l?latitude=41.3854&' \
                  'longitude=2.17754&combinedLocationIds=724,9,8,232,376,8019,0,0,0'
            driver.get(url)

            click_popup(driver)

            content, total_pages = first_scroll_slowly_until_end(driver)
        else:
            url = 'https://www.fotocasa.es/es/alquiler/pisos/barcelona-capital/todas-las-zonas/l/' + str(actual_page) \
                  + '?combinedLocationIds=724%2C9%2C8%2C232%2C376%2C8019%2C0%2C0%2C0&latitude=41.3854&longitude=2.17754'

            driver.get(url)

            content = scroll_slowly_until_end(driver)

        soup = BeautifulSoup(content, "html.parser")

        links = extract_flat_links(soup)

        for link in links:
            if link not in db.keys():
                dict_ = extract_info(link)
                db[dict_['link']] = dict_

            else:
                print("link already in DB, skipping")

        first_page = False
        actual_page += 1

        with open(date + '.pkl', 'wb') as pickle_file:
            # update of pickle file
            pickle.dump(db, pickle_file)

    flats = db.values()
    # final dataframe of all flats
    df = pd.DataFrame(flats)

    # export of the dataframe to a csv file
    df.to_csv(r'./' + date + "-fotocasa.csv", sep='*', index=False)
    print("CSV created")
    exit(0)


if __name__ == "__main__":
    for i in range(10):
        try:
            main()
        except:
            print("Reboot!", i)
            continue
    print('end of loop')
