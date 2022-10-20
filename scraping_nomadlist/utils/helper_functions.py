import time

from selenium import webdriver


def load_dynamic_page(url, cool_down, browser_driver_path):
    # Retrieve the Web Page
    firefox = webdriver.Firefox(
        executable_path=browser_driver_path
    )
    get_height_string = 'return document.body.scrollHeight'
    scroll_command_string = 'window.scrollTo(0, document.body.scrollHeight);'

    # Gradually loading the dynamic content listed on nomadlist.com
    firefox.get(url)
    time.sleep(cool_down)
    prev_h = firefox.execute_script(get_height_string)
    check = True

    while check:
        firefox.execute_script(scroll_command_string)
        time.sleep(cool_down)
        curr_h = firefox.execute_script(get_height_string)
        check = (prev_h != curr_h)
        prev_h = curr_h

    firefox.execute_script(scroll_command_string)
    web_page = firefox.page_source
    firefox.close()

    return web_page


def extract_text(s):
    new_string = ""

    for c in s:
        if c.isalpha():
            new_string = new_string + c
        elif c.isspace():
            new_string = new_string + c

    return new_string.lstrip()


def format_cost(string_cost):
    new_cost = ''

    for c in string_cost:
        if c.isdigit():
            new_cost = new_cost + c

    new_cost = float(new_cost)

    return new_cost


def format_temperature(temp):
    new_temp = 0

    for c in temp:
        if c.isdigit():
            new_temp = new_temp * 10 + int(c)

    return new_temp


def format_humidity(humidity_text):
    new_humidity = 0

    for c in humidity_text:
        if c.isdigit():
            new_humidity = new_humidity * 10 + int(c)

    return new_humidity
