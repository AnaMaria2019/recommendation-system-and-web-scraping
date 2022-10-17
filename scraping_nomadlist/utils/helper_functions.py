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
