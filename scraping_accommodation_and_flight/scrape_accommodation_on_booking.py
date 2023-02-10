import time

from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, ElementNotInteractableException,
    StaleElementReferenceException, NoSuchElementException
)

from utils import helper_functions


def get_year_month_and_day_from_string(date_string: str, date_string_format: str) -> (date, int, int, int):
    date_object = datetime.strptime(date_string, date_string_format).date()

    year = date_object.year
    month = date_object.month
    day = date_object.day

    return date_object, year, month, day


def get_nr_months_between_dates(date_1: date, date_2: date) -> int:
    return (date_1.year - date_2.year) * 12 + (date_1.month - date_2.month)


if __name__ == '__main__':
    booking_months_limit = 15
    destination = 'Milano'
    start_date_str = '2023-02-13'
    end_date_str = '2023-02-20'
    nr_persons = '4'
    nr_rooms = '2'

    start_date_obj, year_at_start_date, month_at_start_date, day_at_start_date = get_year_month_and_day_from_string(
        date_string=start_date_str,
        date_string_format='%Y-%m-%d'
    )
    end_date_obj, year_at_end_date, month_at_end_date, day_at_end_date = get_year_month_and_day_from_string(
        date_string=end_date_str,
        date_string_format='%Y-%m-%d'
    )
    today = date.today()
    year_now, month_now, day_now = today.year, today.month, today.day

    # Check the given dates are valid, the following conditions must be fulfilled:
    # 1. start_date <= end_date
    # 2. start_date >= today date
    # 3. end_date >= today date
    try:
        if start_date_obj < today or start_date_obj > end_date_obj \
                or end_date_obj < today:
            raise ValueError
    except ValueError as exc:
        print('Invalid dates, please enter valid start and end dates!')
        raise

    # On booking the number of persons and rooms must be in the range of [1, 30]
    nr_persons = int(nr_persons)
    nr_rooms = int(nr_rooms)
    try:
        if not 1 <= nr_persons <= 30 or not 1 <= nr_rooms <= 30:
            raise ValueError
    except ValueError as exc:
        print(f'Please enter valid integer numbers from the [1, 30] range, for the number of persons and rooms!')
        raise

    # NOTE: On booking, an user can search for accommodation only starting from the current month
    #       up until 15 months later from the current month
    nr_months_between_now_and_start_date = get_nr_months_between_dates(start_date_obj, today)
    nr_months_between_start_and_end_dates = get_nr_months_between_dates(end_date_obj, start_date_obj)
    print(
        f"Months between today({today}) and start date({start_date_obj}): {nr_months_between_now_and_start_date}"
    )
    print(
        f"Months between start date({start_date_obj}) and end date({end_date_obj}): "
        f"{nr_months_between_start_and_end_dates}"
    )
    total_months = nr_months_between_now_and_start_date + nr_months_between_start_and_end_dates
    print(f"Total nr. of months between today's month and the end date's month is: {total_months}")

    try:
        if total_months > booking_months_limit:
            raise ValueError
    except ValueError:
        print(f"The start date ({start_date_obj}) and end date ({end_date_obj}) provided are not valid!\n\n"
              f"The gap between today's month ({today}) and the end date's month ({end_date_obj}) for your staying in "
              f"{destination} is too big, booking.com only allows searching for accommodations up until the next "
              f"{booking_months_limit} months starting from today's month.")
        raise

    url = 'https://www.booking.com/'
    driver = webdriver.Firefox(
        executable_path='../geckodriver.exe'
    )
    driver.get(url)
    time.sleep(5)

    """ Accept cookies """
    driver.find_element_by_xpath(
        "//button[contains(@data-gdpr-consent, 'accept') or contains(@id, 'onetrust-accept-btn-handler')]"
    ).click()
    time.sleep(2)

    """ Select destination """
    # Find the input for entering the destination
    destination_input = driver.find_element_by_xpath("//input[contains(@name, 'ss')]")
    # Add the destination in the input.
    destination_input.send_keys(destination)
    time.sleep(5)

    """ Select check-in and check-out dates """
    # Find the input for entering the dates for check-in and check-out
    driver.find_element_by_xpath("//div[contains(@class, 'xp__dates-inner')]").click()

    # Find the next button for the months (in case the start date or the end date for the accommodation is not
    # within the current month, then it is necessary to navigate to the right month)
    next_month_button = driver.find_element_by_xpath("//div[contains(@data-bui-ref, 'calendar-next')]")

    for i in range(nr_months_between_now_and_start_date):
        next_month_button.click()
    time.sleep(1)

    # Select the start date for the accommodation
    driver.find_element_by_xpath("//td[contains(@data-date, '" + start_date_str + "')]").click()
    time.sleep(1)

    for i in range(nr_months_between_start_and_end_dates - 1):
        next_month_button.click()
    time.sleep(1)

    # Select the end date for the accommodation
    driver.find_element_by_xpath("//td[contains(@data-date, '" + end_date_str + "')]").click()

    """ Select the number of persons """
    # Find the input for entering the number of persons and the number of rooms
    driver.find_element_by_xpath("//label[contains(@id, 'xp__guests__toggle')]").click()

    change_nr_of_adults_container = driver.find_element_by_xpath("//div[contains(@class, 'sb-group__field-adults')]")
    nr_adults_subtract_button = change_nr_of_adults_container.find_element_by_xpath(
        ".//button[contains(@class, 'bui-stepper__subtract-button')]"
    )
    nr_adults_addition_button = change_nr_of_adults_container.find_element_by_xpath(
        ".//button[contains(@class, 'bui-stepper__add-button')]"
    )

    if nr_persons == 1:
        nr_adults_subtract_button.click()
    elif nr_persons > 2:
        for idx in range(nr_persons - 2):
            nr_adults_addition_button.click()

    """ Select the number of rooms """
    change_nr_of_rooms_container = driver.find_element_by_xpath("//div[contains(@class, 'sb-group__field-rooms')]")
    nr_rooms_addition_button = change_nr_of_rooms_container.find_element_by_xpath(
        ".//button[contains(@class, 'bui-stepper__add-button')]"
    )

    for idx in range(nr_rooms - 1):
        nr_rooms_addition_button.click()

    """ Search results """
    # Click on the button to search for results
    driver.find_element_by_class_name('sb-searchbox__button').click()

    """ Get the accommodations details listed in the first 2 pages """
    # Wait until the list of hotels is loaded
    wait = WebDriverWait(driver, timeout=7)
    try:
        wait.until(EC.visibility_of_element_located((By.ID, 'search_results_table')))
    except TimeoutException:
        print('Timeout exceeded! Accommodations page did not load!')
        driver.close()
        raise
    else:
        try:
            driver.find_element_by_xpath(
                "//li[contains(@class, 'sort_category') and contains(@class, 'sort_review_score_and_price')]"
            ).click()
            time.sleep(1.2)
        except ElementNotInteractableException or NoSuchElementException:
            sortbar_dropdown_button = driver.find_element_by_xpath(
                "//button[contains(@data-testid, 'sorters-dropdown-trigger')]"
            )
            sortbar_dropdown_button.click()
            try:
                wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "//div[contains(@data-testid, 'sorters-dropdown')]")
                ))
            except TimeoutException:
                print('Timeout exceeded! Sorting options list did not load!')
            else:
                driver.find_element_by_xpath(
                    "//button[contains(@data-id, 'class_and_price')]"
                ).click()

        time.sleep(2)
        accommodations = []
        print()
        for page_idx in range(2):
            while True:
                try:
                    wait.until(EC.visibility_of_element_located((By.ID, 'search_results_table')))
                except StaleElementReferenceException:
                    print('The element is no longer attached to the DOM, we will try again!')
                    continue
                except TimeoutException:
                    print('Something went wrong while loading the accommodation results, continue to the next page!')
                    break
                else:
                    time.sleep(1.2)
                    accommodation_containers = driver.find_elements_by_xpath(
                        "//div[contains(@data-testid, 'property-card')]"
                    )

                    for container in accommodation_containers:
                        accommodation = {}

                        try:
                            accommodation_name_container = container.find_element_by_xpath(
                                ".//div[1]/div[2]/div/div[1]/div[1]/div/div[1]/div/h3/a"
                            )
                        except NoSuchElementException:
                            print('Could not find essential information, go to the next accommodation!')
                            print()
                            continue
                        else:
                            accommodation['url'] = accommodation_name_container.get_attribute('href')
                            accommodation['name'] = accommodation_name_container.find_element_by_xpath(
                                "./div[contains(@data-testid, 'title')]"
                            ).text
                            print(accommodation['url'])
                            print(accommodation['name'])

                        try:
                            accommodation_price = container.find_element_by_xpath(
                                ".//div[1]/div[2]/div/div[3]/div[2]/div/div[1]/span/div/span[2]"
                            ).text
                        except NoSuchElementException:
                            try:
                                accommodation_price = container.find_element_by_xpath(
                                    ".//div[1]/div[2]/div/div[2]/div[2]/div/div[1]/span/div/span[2]"
                                ).text
                            except NoSuchElementException:
                                print('Could not find essential information, go to the next accommodation!')
                                print()
                                continue
                        else:
                            accommodation['price'] = helper_functions.convert_string_to_int(accommodation_price)
                            print(accommodation['price'])

                        try:
                            accommodation_score = container.find_element_by_xpath(
                                ".//div[1]/div[2]/div/div[1]/div[2]/div/a/span/div/div[1]"
                            ).text
                        except NoSuchElementException:
                            accommodation['score'] = 2.5
                            print()
                        else:
                            accommodation['score'] = helper_functions.convert_string_to_float(accommodation_score)
                            print(accommodation['score'])

                        accommodations.append(accommodation)
                        print()
                    break

            time.sleep(1)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1500);")
            try:
                next_page_container = driver.find_element_by_xpath(
                    "//div[contains(@data-testid, 'pagination')]"
                )
                next_page_nav = next_page_container.find_element_by_tag_name('nav').find_element_by_tag_name('div')
                next_page_button = next_page_nav.find_elements_by_tag_name('div')[2]\
                    .find_element_by_tag_name('button')
                next_page_button.click()
            except NoSuchElementException:
                driver.find_element_by_xpath(
                    "//li[contains(@class, 'bui-pagination__item') \
                     and contains(@class, 'bui-pagination__item--disabled')]"
                )
            else:
                time.sleep(1.5)

        if len(accommodations) == 0:
            print('No accommodation was found!')

        sorted_accommodations = sorted(accommodations, reverse=True, key=lambda it: (it['price'], it['score']))
        print(sorted_accommodations)
        # print(len(sorted_accommodations))
        # print(sorted_accommodations)

    driver.close()
