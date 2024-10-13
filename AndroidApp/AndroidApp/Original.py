import requests
import json
from datetime import datetime
import pandas as pd


def is_valid_date(date_str):
    try:
        # Try to parse the date string using the specified format
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        # If a ValueError is raised, the format is incorrect
        return False
def getAllAirports():
    url = "https://www.ryanair.com/api/views/locate/5/airports/en/active"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    stringList = response.text
    airportsList = json.loads(stringList)

    return airportsList

def returnAllCountries(): #To get destination country

    list = []
    for country in getAllAirports():
        if country['country']['name'] not in list:
            list.append(country['country']['name'])

    list.sort()
    count = 0
    string = ""
    for country in list:
        string += country + ", "
        count += 1
        if count == 5:
            string += "\n"
            count = 0

    string += "\n"
    print(string)
def getCountryCodebyCountryName(name):

    for country in getAllAirports():
        if country['country']['name'] == name:
            return country['country']['code']

    return getCountryCodebyCountryName(input("Enter a valid country name:"))

def getAirports(countrycode):
    url = "https://www.ryanair.com/api/views/locate/5/airports/en/active"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    stringList = response.text
    airportsList = json.loads(stringList)

    AirportsList = []
    for airport in airportsList:
        if airport['country']['code'] == countrycode:
            AirportsList.append(airport)

    return AirportsList

def getFlightInfo(fromCode, toCode, startDate, currency = "GBP"):
    url = "https://www.ryanair.com/api/farfnd/v4/oneWayFares/{fromCode}/{toCode}/cheapestPerDay?outboundMonthOfDate={startDate}&currency={currency}"
    url = url.format(fromCode=fromCode, toCode=toCode, startDate=startDate, currency=currency)

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    departures = json.loads(response.text)

    fares = departures['outbound']['fares']

    for fare in fares:

        if fare['arrivalDate'] == None:
            continue

        elif fare['day'] == startDate:
            arrivaldate = fare['arrivalDate']
            departuredate = fare['departureDate']


            arrivalDay, arrivalTime = arrivaldate.split('T')
            departureDate, departureTime = departuredate.split('T')

            price = fare['price']['value']

            output = {
                "Exists" : True,
                "departureDate": departureDate,
                "departureTime": departureTime,
                "arrivalDate": arrivalDay,
                "arrivalTime": arrivalTime,
                "price": price
            }


            return output

    output = {
        "Exists": False,
        "departureDate": "N/A",
        "departureTime": "N/A",
        "arrivalDate": "N/A",
        "arrivalTime": "N/A",
        "price": "N/A"
    }
    return output


print("\n Welcome to the better Ryanair Search Engine for UK Residents \n")
returnAllCountries()
name = input("Enter Country:")
countrycode = getCountryCodebyCountryName(name)

unitedKingdomAirports = getAirports("gb")
destinationAirportsList = getAirports(countrycode)

valid = False
while not valid:
    departureDate = input("Enter departure date yyyy-mm-dd:")
    valid = is_valid_date(departureDate)

valid = False
while not valid:
    returnDate = input("Enter return date yyyy-mm-dd:")
    valid = is_valid_date(returnDate)

rows_departure = []
rows_arrival = []

for origin in unitedKingdomAirports:
    for destination in destinationAirportsList:
        bestFlight = getFlightInfo(origin['code'], destination['code'], departureDate)

        if bestFlight['Exists']:

            row = {
                'Origin': origin['name'],
                'Destination': destination['name'],
                'Departure Date': bestFlight['departureDate'],
                'Departure Time': bestFlight['departureTime'],
                'Arrival Date': bestFlight['arrivalDate'],
                'Arrival Time': bestFlight['arrivalTime'],
                'Price': bestFlight['price']
            }

            rows_departure.append(row)

for origin in destinationAirportsList:
    for destination in unitedKingdomAirports:
        bestFlight = getFlightInfo(origin['code'], destination['code'], returnDate)

        if bestFlight['Exists']:

            row = {
                'Origin': origin['name'],
                'Destination': destination['name'],
                'Departure Date': bestFlight['departureDate'],
                'Departure Time': bestFlight['departureTime'],
                'Arrival Date': bestFlight['arrivalDate'],
                'Arrival Time': bestFlight['arrivalTime'],
                'Price': bestFlight['price']
            }

            rows_arrival.append(row)

df_outbound = pd.DataFrame(rows_departure)
df_return = pd.DataFrame(rows_arrival)


output_file = 'flights' + name + '.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df_outbound.to_excel(writer, sheet_name='Outbound Flights', index=False)
    df_return.to_excel(writer, sheet_name='Return Flights', index=False)

print("Done")
