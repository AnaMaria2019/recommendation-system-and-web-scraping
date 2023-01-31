"""
    LOGIC PROCESS:
        The scope of this Python script is to extract the best option of flight from
        'momondo.ro', where the destination city and the trip's start and end date are provided.
"""


import time
from datetime import date, datetime

from selenium import webdriver
from bs4 import BeautifulSoup


def get_data_from_flight_container(flight_container):
    flight_depart_time = flight_container.find('span', {'class': 'depart-time'}).get_text()
    flight_depart_time = flight_depart_time.replace('\n', '')

    flight_arrival_time = flight_container.find('span', {'class': 'arrival-time'}).get_text()
    flight_arrival_time = flight_arrival_time.replace('\n', '')

    airports_names_container = flight_container\
        .find('div', {'class': 'bottom'})\
        .find_all('span', {'class': 'airport-name'})
    from_airport_name = airports_names_container[0].get_text().replace('\n', ' ')
    to_airport_name = airports_names_container[1].get_text().replace('\n', ' ')

    return flight_depart_time, flight_arrival_time, from_airport_name, to_airport_name


def get_airlines_names(flight_container):
    airlines = flight_container.find('span', {'class': 'codeshares-airline-names'}).get_text()
    if ',' in airlines:
        airlines_names = airlines.split(', ')
        flight_1_airline, flight_2_airline = airlines_names[0], airlines_names[1]
    else:
        flight_1_airline, flight_2_airline = airlines, airlines

    return flight_1_airline, flight_2_airline


def get_price_from_flight_container(flight_container):
    price_container = flight_container.find('span', id=lambda x: x and x.endswith('-price-text'))
    price = price_container.get_text().replace('\n', '')

    return price


def get_booking_link_for_flight(flight_container):
    link = flight_container.find('a', id=lambda x: x and x.endswith('-booking-link'))
    href = link['href']
    booking_link = "https://www.momondo.ro/" + href

    return booking_link


def are_dates_valid(from_date_str: str, to_date_str: str) -> bool:
    from_date_obj = datetime.strptime(from_date_str, '%Y-%m-%d').date()
    to_date_obj = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    today_date_obj = date.today()

    if from_date_obj < today_date_obj or from_date_obj > to_date_obj\
            or to_date_obj < today_date_obj:
        return False

    return True


if __name__ == '__main__':
    """ Retrieve the Web Page """
    from_airport = 'BUH'
    to_airport = 'MIL'
    from_date = '2023-03-03'
    to_date = '2023-03-05'

    # Check the given dates are valid, the following conditions must be fulfilled:
    # 1. start_date <= end_date
    # 2. start_date >= today date
    # 3. end_date >= today date
    try:
        if not are_dates_valid(from_date_str=from_date, to_date_str=to_date):
            raise ValueError
    except ValueError as exc:
        print('Invalid dates, please enter valid start and end dates!')
        raise

    url = f'https://www.momondo.ro/flight-search/{from_airport}-{to_airport}/{from_date}/{to_date}?sort=bestflight_a'
    driver = webdriver.Firefox(
        executable_path='../geckodriver.exe'
    )
    driver.get(url)
    time.sleep(20)

    # Close pop-up window
    driver.find_element_by_xpath(
        "//div[contains(@class, 'dDYU-close')]"
    ).click()
    time.sleep(4)

    page = driver.page_source
    driver.close()

    soup = BeautifulSoup(page, 'html.parser')

    """ Find the container that holds the details on the flight option with 'Best' label attached to it """
    flights = soup.find_all('div', {'class': 'inner-grid keel-grid'})
    ind = 0
    curr_flight = flights[ind]
    best_flight_label = curr_flight.find('div', {'class': 'bfLabel bf-best'})

    while best_flight_label is None:
        ind += 1
        curr_flight = flights[ind]
        best_flight_label = curr_flight.find('div', {'class': 'bfLabel bf-best'})

    best_flight_option = curr_flight.find_all('div', {'class': 'result-column'})[0]
    flights_details = best_flight_option.find_all('div', {'class': 'section times'})

    flight_1 = flights_details[0]
    print('First flight details:')
    flight_1_depart_time, flight_1_arrival_time,\
        flight_1_from_airport, flight_1_to_airport = get_data_from_flight_container(flight_1)
    print(f'Depart time: {flight_1_depart_time}')
    print(f'Arrival time: {flight_1_arrival_time}')
    print(f'From Airport: {flight_1_from_airport}')
    print(f'To Airport: {flight_1_to_airport}')
    print()

    flight_2 = flights_details[1]
    print('Second flight details:')
    flight_2_depart_time, flight_2_arrival_time,\
        flight_2_from_airport, flight_2_to_airport = get_data_from_flight_container(flight_2)
    print(f'Depart time: {flight_2_depart_time}')
    print(f'Arrival time: {flight_2_arrival_time}')
    print(f'From Airport: {flight_2_from_airport}')
    print(f'To Airport: {flight_2_to_airport}')
    print()

    flight_1_airline_name, flight_2_airline_name = get_airlines_names(best_flight_option)
    print(f'Flight 1 airline name: {flight_1_airline_name}')
    print(f'Flight 2 airline name: {flight_2_airline_name}')
    print()

    best_flight_price = get_price_from_flight_container(curr_flight)
    provider_name = curr_flight.find('span', {'class': 'providerName'}).get_text().replace('\n', '')
    print(f'Price {best_flight_price} using the provider {provider_name}')

    booking_flight_link = get_booking_link_for_flight(curr_flight)
    print(f'Link to booking page: {booking_flight_link}')
