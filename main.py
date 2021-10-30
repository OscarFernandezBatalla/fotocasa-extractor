
from bs4 import BeautifulSoup
import requests
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

def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)



    url = 'https://www.fotocasa.es/es/alquiler/pisos/barcelona-capital/todas-las-zonas/l?latitude=41.3854&longitude=2.17754&combinedLocationIds=724,9,8,232,376,8019,0,0,0'
    driver.get(url)
    html = driver.page_source

    # page = requests.get(url)
    # soup = BeautifulSoup(page.content, 'html.parser')

    # soup = BeautifulSoup(html,"html.parser")
    # print(soup.find_all('title'))
    delay = 10
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="App"]/div[4]/div/div/div/footer/div/button[2]')))
        btn_cookie = driver.find_element_by_xpath('//*[@id="App"]/div[4]/div/div/div/footer/div/button[2]')
        btn_cookie.click()


        print("ready1")
        myElem = WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="App"]/div[2]/div[1]/div[4]/main/div/div[3]/section')))

        print("ready2")

        content = scroll_slowly_until_end(driver)

        soup = BeautifulSoup(content, "html.parser")

        entries_in_page = soup.find('section', class_='re-Searchresult').findChildren("div", recursive=False)
        # print(html)


        print(len(entries_in_page))
        for i in entries_in_page:
            print("\n\n")
            print(i)

    except TimeoutException:
        print("Loading took too much time!")

    # entries_in_page = soup.find('section', class_='re-Searchresult').findChildren("div", recursive=False)


    # print(entries_in_page[3])
    # for entry in entries_in_page:
    #




if __name__ == "__main__":
    main()
