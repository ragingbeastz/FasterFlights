from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
import requests
import json

shared_data = {
    'DestinationAirportName': '',
    'DepartureDate': '',
    'ReturnDate': '',
    'ResultsDeparture': [],
    'ResultsReturn': []
}


def returnAllCountries():  # To get destination country
    list = []
    for country in getAllAirports():
        if country['country']['name'] not in list:
            list.append(country['country']['name'])
    list.remove('United Kingdom')
    list.sort()
    return list

def getAllAirports():
    url = "https://www.ryanair.com/api/views/locate/5/airports/en/active"
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    stringList = response.text
    airportsList = json.loads(stringList)
    return airportsList

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



def getCountryCodebyCountryName(name):

    for country in getAllAirports():
        if country['country']['name'] == name:
            return country['country']['code']

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


class DatePicker(BoxLayout):
    def __init__(self, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (300, 44)

        # Spinner for day selection
        self.day_spinner = Spinner(
            text='01',
            values=[f'{i:02d}' for i in range(1, 32)],
            size_hint=(None, None),
            size=(100, 44)
        )

        # Spinner for month selection
        self.month_spinner = Spinner(
            text='01',
            values=[f'{i:02d}' for i in range(1, 13)],
            size_hint=(None, None),
            size=(100, 44)
        )

        # Spinner for year selection
        self.year_spinner = Spinner(
            text='2024',
            values=[str(i) for i in range(2023, 2031)],
            size_hint=(None, None),
            size=(100, 44)
        )

        self.add_widget(self.day_spinner)
        self.add_widget(self.month_spinner)
        self.add_widget(self.year_spinner)

    def get_selected_date(self):
        return f"{self.year_spinner.text}-{self.month_spinner.text}-{self.day_spinner.text}"

