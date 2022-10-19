import requests
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime, date
from googletrans import Translator

""" Helper functions """


def string_to_int(s):
    n = 0
    for c in s:
        if c.isdigit():
            n = n * 10 + int(c)
        elif c == ',':
            break

    return n


# print(string_to_int('4.837,25 lei'))  # => 4837


def string_to_float(s):
    new_string = ''
    for c in s:
        if c == ',':
            new_string += '.'
        else:
            new_string += c

    return float(new_string)


# print(string_to_float('9,6'))  # => 9.6

translator = Translator()
months = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}

destination = 'vienna'
start_date = '2020-08-20'
end_date = '2020-08-22'
nr_persons = '2'
nr_rooms = '1'

start_date_year = datetime.strptime(start_date, '%Y-%m-%d').year
start_date_month = datetime.strptime(start_date, '%Y-%m-%d').month
start_date_day = datetime.strptime(start_date, '%Y-%m-%d').day
# print(start_date_year, start_date_month, start_date_day)

end_date_year = datetime.strptime(end_date, '%Y-%m-%d').year
end_date_month = datetime.strptime(end_date, '%Y-%m-%d').month
end_date_day = datetime.strptime(end_date, '%Y-%m-%d').day
# print(end_date_year, end_date_month, end_date_day)

today_year = date.today().year
today_month = date.today().month
today_day = date.today().day
# print(today_year, today_month, today_day)

url = 'https://www.booking.com/'

opts = webdriver.FirefoxOptions()
opts.headless = True
driver = webdriver.Firefox()
driver.get(url)

# Accept cookies.
time.sleep(5)
driver.find_element_by_xpath(
    "//button[contains(@data-gdpr-consent, 'accept') or contains(@id, 'onetrust-accept-btn-handler')]"
).click()

# Find the input for entering the destination.
destination_input = driver.find_element_by_id('ss')
# Add the destination in the input.
destination_input.send_keys(destination)

# Find the input for entering the dates for check-in and check-out.
driver.find_element_by_xpath("//div[contains(@class, 'xp__dates-inner')]").click()
# driver.find_element_by_xpath("//div[contains(@data-bui-ref, 'calendar-content')]").click()

if today_year == start_date_year:
    current_month = True
    for m in range(today_month, start_date_month):
        current_month = False

        button_1 = driver.find_element_by_xpath("//div[contains(@data-bui-ref, 'calendar-next')]")
        button_1.click()
        # time.sleep(1)

    if current_month and start_date_day >= today_day:
        driver.find_element_by_xpath("//td[contains(@data-date, '" + start_date + "')]").click()
    elif not current_month:
        driver.find_element_by_xpath("//td[contains(@data-date, '" + start_date + "')]").click()

    time.sleep(1)

    if end_date_month - start_date_month in [0, 1]:
        driver.find_element_by_xpath("//td[contains(@data-date, '" + end_date + "')]").click()
    else:
        for m in range(start_date_month, end_date_month):
            driver.find_element_by_xpath("//div[contains(@data-bui-ref, 'calendar-next')]").click()
            # time.sleep(1.5)
        driver.find_element_by_xpath("//td[contains(@data-date, '" + end_date + "')]").click()
else:
    for m in range(12 - start_date_month + 1):
        driver.find_element_by_xpath("//div[contains(@data-bui-ref, 'calendar-next')]").click()
        # time.sleep(1.5)

    # Pe Booking se pot cauta cazari pana in anul urmator maxim septembrie. De verificat daca utilizatorul a introdus
    # start_date si end_date ce se incadreaza in aceste conditii.

    """
    for y in range(start_date_year - today_year - 2):
        for m in range(12):
            driver.find_element_by_xpath("//div[contains(@data-bui-ref, 'calendar-next')]").click()
            time.sleep(3)
    """

    for m in range(start_date_month):
        driver.find_element_by_xpath("//div[contains(@data-bui-ref, 'calendar-next')]").click()
        # time.sleep(1.5)
    driver.find_element_by_xpath("//td[contains(@data-date, '" + start_date + "')]").click()

    if end_date_month - start_date_month in [0, 1]:
        driver.find_element_by_xpath("//td[contains(@data-date, '" + end_date + "')]").click()
    else:
        for m in range(start_date_month, end_date_month):
            driver.find_element_by_xpath("//div[contains(@data-bui-ref, 'calendar-next')]").click()
            # time.sleep(1)
        driver.find_element_by_xpath("//td[contains(@data-date, '" + end_date + "')]").click()

# Find the input for entering the number of persons and the number of rooms.
driver.find_element_by_xpath("//label[contains(@id, 'xp__guests__toggle')]").click()

if int(nr_persons) < 2:
    driver.find_element_by_xpath(
        "//div[contains(@class, 'sb-group__field-adults')]//button[contains(@class, 'bui-stepper__subtract-button')]"
    ).click()
elif int(nr_persons) > 2:
    for p in range(int(nr_persons) - 2):
        driver.find_element_by_xpath(
            "//div[contains(@class, 'sb-group__field-adults')]//button[contains(@class, 'bui-stepper__add-button')]"
        ).click()
        # time.sleep(1)

if int(nr_rooms) > 1:
    for r in range(int(nr_rooms) - 1):
        driver.find_element_by_xpath(
            "//div[contains(@class, 'sb-group__field-rooms')]//button[contains(@class, 'bui-stepper__add-button')]"
        ).click()
        # time.sleep(1)

# Click on the button to search for results.
driver.find_element_by_class_name('sb-searchbox__button').click()

# Wait until the list of hotels is loaded.
wait = WebDriverWait(driver, timeout=5)
wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'sr-hotel__title')))

try:
    driver.find_element_by_xpath(
        "//li[contains(@class, 'sort_category') and contains(@class, 'sort_review_score_and_price')]"
    ).click()
    time.sleep(1.2)
except ElementNotInteractableException:
    driver.find_element_by_id('sortbar_dropdown_button').click()
    driver.find_element_by_xpath(
        "//li[contains(@class, 'sort_category') and contains(@class, 'sort_review_score_and_price')]"
    ).click()
    time.sleep(1.2)

accommodations = []
nr = 0
for i in range(2):
    while True:
        try:
            wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'sr-hotel__title')))
        except StaleElementReferenceException:
            print("The element is no longer attached to the DOM, continue with the next page!")
            continue
        except TimeoutException:
            break
        else:
            time.sleep(1.2)
            """
            acc_names = driver.find_elements_by_class_name('sr-hotel__name')
            for name in acc_names:
                print(name.text)
            """
            accommodation_containers = driver.find_elements_by_class_name('sr_item_content')

            for container in accommodation_containers:
                accommodation = {}
                attributes_found = 0

                try:
                    acc_h3 = container.find_element_by_class_name('sr-hotel__title')
                except NoSuchElementException:
                    continue
                else:
                    attributes_found += 1
                    accommodation['url'] = acc_h3.find_element_by_class_name('hotel_name_link').get_attribute('href')

                try:
                    acc_name = container.find_element_by_class_name('sr-hotel__name')
                except NoSuchElementException:
                    continue
                else:
                    attributes_found += 1
                    accommodation['name'] = acc_name.text

                try:
                    acc_price = container.find_element_by_class_name('bui-price-display__value')
                except NoSuchElementException:
                    continue
                else:
                    attributes_found += 1
                    accommodation['price'] = string_to_int(acc_price.text)

                try:
                    acc_score = container.find_element_by_class_name('bui-review-score__badge')
                except NoSuchElementException:
                    accommodation['score'] = 2.5
                else:
                    attributes_found += 1
                    accommodation['score'] = string_to_float(acc_score.text)

                if attributes_found == 4:
                    nr += 1
                    print(f"Accommodation {nr}: name - {accommodation['name']}, price - {accommodation['price']}, score - {accommodation['score']}")

                accommodations.append(accommodation)

            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1500);")
            try:
                last_page = driver.find_element_by_xpath(
                    "//li[contains(@class, 'bui-pagination__next-arrow')]"
                ).click()
                # time.sleep(1.5)
            except NoSuchElementException:
                driver.find_element_by_xpath(
                    "//li[contains(@class, 'bui-pagination__item') \
                     and contains(@class, 'bui-pagination__item--disabled')]"
                )
                break
            """else:
                time.sleep(1.5)"""
            break

sorted_accommodations = sorted(accommodations, reverse=True, key=lambda it: (it['price'], it['score']))
# print(len(sorted_accommodations))
# print(sorted_accommodations)
# driver.close()
