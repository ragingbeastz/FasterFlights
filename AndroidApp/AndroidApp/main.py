from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp, sp
from kivy.clock import Clock

import External
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        countries = External.returnAllCountries()

        # Create a GridLayout with vertical orientation
        layout = GridLayout(cols=1, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Create buttons for each country and add them to the GridLayout
        for country in countries:
            btn = Button(text=country, size_hint_y=None, height=dp(100), font_size=sp(20))
            btn.bind(on_press=self.on_button_press)
            layout.add_widget(btn)

        # Create a ScrollView and add the GridLayout to it
        scroll_view = ScrollView(size_hint=(1, 1), size=(dp(Window.width), dp(Window.height)))  # Adjust size_hint to (1, 1) to fill the parent
        scroll_view.add_widget(layout)

        # Add the ScrollView to the screen
        self.add_widget(scroll_view)



    def on_button_press(self, instance):
        # Switch to the second screen
        self.manager.current = 'dateselection'
        # Update the label on the second screen
        External.shared_data['DestinationAirportName'] = instance.text
        self.manager.get_screen('dateselection').update_label(f'You selected {instance.text}')

class DateSelection(Screen):
    def __init__(self, **kwargs):
        super(DateSelection, self).__init__(**kwargs)
        self.Return = False
        self.ReturnExists = False
        self.layout = FloatLayout()

        # Create and position the label
        self.label = Label(text='Second Screen', font_size=24,
                           size_hint=(None, None), size=(200, 50),
                           pos_hint={'center_x': 0.5, 'top': 1})

        self.labelDeparture = Label(text='Departure Date:', font_size=24,
                                 size_hint=(None, None), size=(200, 50),
                                 pos_hint={'x': 0, 'center_y': 0.5})
        # Create and position the date picker
        self.date_picker = External.DatePicker(size_hint=(None, None), size=(200, 100),
                                      pos_hint={'center_x': 0.5, 'center_y': 0.5})

        # Create and position the back button
        back_button = Button(text='Back', size_hint=(1, None), size=(200, 70),
                             pos_hint={'center_x': 0.5, 'y': 0})

        # Create and position the forward button
        forward_button = Button(text='Proceed', size_hint=(1, None), size=(200, 70),
                             pos_hint={'center_x': 0.5, 'y': 0.09})

        self.return_button = Button(text='Add Return?', size_hint=(1, None), size=(200, 70),
                                pos_hint={'center_x': 0.5, 'y': 0.18})

        self.return_button.bind(on_press=self.addReturn)
        back_button.bind(on_press=self.go_back)
        forward_button.bind(on_press=self.go_forward)

        # Add widgets to the layout
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.date_picker)
        self.layout.add_widget(self.labelDeparture)
        self.layout.add_widget(self.return_button)
        self.layout.add_widget(forward_button)
        self.layout.add_widget(back_button)

        self.add_widget(self.layout)
    def update_label(self, text):
        text = text + ". Please select a date:"
        self.label.text = text

    def addReturn(self, instance):
        self.Return = True
        self.layout.remove_widget(self.return_button)
        # Create and position the date picker
        self.labelReturn = Label(text='Return Date:', font_size=24,
                           size_hint=(None, None), size=(200, 50),
                           pos_hint={'x': 0, 'y': 0.4})

        self.date_pickerReturn = External.DatePicker(size_hint=(None, None), size=(200, 100),
                                               pos_hint={'center_x': 0.5, 'y': 0.4})
        self.add_widget(self.labelReturn)
        self.add_widget(self.date_pickerReturn)
        self.ReturnExists = True

    def load_flight_information(self, dt):
        #self.manager.get_screen('loading').getFlightInformation()
        Loading.getFlightInformation()
        self.manager.get_screen('resultsDeparture').update()

    def go_forward(self, instance):
        # Here you can use self.date_picker.get_selected_date() to get the selected date
        External.shared_data['DepartureDate'] = self.date_picker.get_selected_date()
        self.manager.current = 'loading'


        if self.ReturnExists:
            External.shared_data['ReturnDate'] = self.date_pickerReturn.get_selected_date()
            Clock.schedule_once(self.load_flight_information, 0.1)

        else:
            Clock.schedule_once(self.load_flight_information, 0.1)

        self.manager.current = 'resultsDeparture'



    def go_back(self, instance):
        # Here you can use self.date_picker.get_selected_date() to get the selected date
        if self.Return:
            self.remove_widget(self.labelReturn)
            self.remove_widget(self.date_pickerReturn)
            self.layout.add_widget(self.return_button)
            self.Return = False

        self.manager.current = 'main'


class Loading(Screen):
    def __init__(self, **kwargs):
        super(Loading, self).__init__(**kwargs)#

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.label = Label(text='Loading...')
        layout.add_widget(self.label)
        self.add_widget(layout)

    @staticmethod
    def getFlightInformation():
        unitedKingdomAirports = External.getAirports("gb")
        destinationAirportsList = External.getAirports(External.getCountryCodebyCountryName(External.shared_data['DestinationAirportName']))

        resultsDeparture = []
        resultsReturn = []

        for origin in unitedKingdomAirports:
            for destination in destinationAirportsList:
                bestFlight = External.getFlightInfo(origin['code'], destination['code'], External.shared_data['DepartureDate'])

                flight = {
                    'Exists': bestFlight['Exists'],
                    'Origin': origin['name'],
                    'Destination': destination['name'],
                    'Departure Date': bestFlight['departureDate'],
                    'Departure Time': bestFlight['departureTime'],
                    'Arrival Date': bestFlight['arrivalDate'],
                    'Arrival Time': bestFlight['arrivalTime'],
                    'Price': bestFlight['price']
                }

                resultsDeparture.append(flight)

        if External.shared_data['ReturnDate'] != '':
            for origin in destinationAirportsList:
                for destination in unitedKingdomAirports:
                    bestFlight = External.getFlightInfo(origin['code'], destination['code'],
                                                        External.shared_data['ReturnDate'])

                    flight = {
                        'Exists': bestFlight['Exists'],
                        'Origin': origin['name'],
                        'Destination': destination['name'],
                        'Departure Date': bestFlight['departureDate'],
                        'Departure Time': bestFlight['departureTime'],
                        'Arrival Date': bestFlight['arrivalDate'],
                        'Arrival Time': bestFlight['arrivalTime'],
                        'Price': bestFlight['price']
                    }

                    resultsReturn.append(flight)

            External.shared_data['ResultsReturn'] = resultsReturn

        External.shared_data['ResultsDeparture'] = resultsDeparture




class ResultsDeparture(Screen):
    def __init__(self, **kwargs):
        super(ResultsDeparture, self).__init__(**kwargs)

        # Initialize GridLayout with 3 columns and set size_hint_y to None
        self.grid_layout = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        # Create a ScrollView to handle scrolling
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.grid_layout)

        self.add_widget(scroll_view)

    def viewReturnFlights(self, instance):
        self.manager.current = 'resultsReturn'
        self.manager.get_screen('resultsReturn').update()

    def backToMainMenu(self, instance):
        External.shared_data = {
            'DestinationAirportName': '',
            'DepartureDate': '',
            'ReturnDate': '',
            'ResultsDeparture': [],
            'ResultsReturn': []
        }

        self.manager.current = 'main'

    def update(self):
        self.grid_layout.clear_widgets()

        departureFlights = []
        for flight in External.shared_data['ResultsDeparture']:#
            if flight['Exists'] == True:
                departureFlights.append(flight)

        for flight in departureFlights:
            print(flight)


        departureFlights.sort(key=lambda x: float(x['Price']))
        for flight in departureFlights:
            if flight['Exists'] == True:
                textInfo = f"Origin: {flight['Origin']}\nDestination: {flight['Destination']}\nDeparture Date: {flight['Departure Date']}\nDeparture Time: {flight['Departure Time']}\nArrival Date: {flight['Arrival Date']}\nArrival Time: {flight['Arrival Time']}\nPrice: {flight['Price']}"
                label = Label(
                    text=textInfo,
                    size_hint_x=None,  # Ensure the width is fixed
                    width=(Window.width / 3) - 20,  # Adjust width for three columns and padding
                    size_hint_y=None,  # Ensure height is fixed
                    height=150,  # Adjust height if necessary
                    text_size=(Window.width / 3 - 20, None)  # Allow text to wrap
                )
                self.grid_layout.add_widget(label)

        if External.shared_data['ReturnDate'] != '':
            ReturnsButton = Button(text='View Return Flights', size_hint=(1, None), size=(200, 70),
                             pos_hint={'center_x': 0.5, 'y': 0})
            ReturnsButton.bind(on_press=self.viewReturnFlights)

            self.add_widget(ReturnsButton)

        BackButton = Button(text='Return to Main Menu', size_hint=(1, None), size=(200, 70),
                            pos_hint={'center_x': 0.5, 'y': 0.1})

        BackButton.bind(on_press=self.backToMainMenu)
        self.add_widget(BackButton)




class ResultsReturn(Screen):
    def __init__(self, **kwargs):
        super(ResultsReturn, self).__init__(**kwargs)

        # Initialize GridLayout with 3 columns and set size_hint_y to None
        self.grid_layout = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        # Create a ScrollView to handle scrolling
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.grid_layout)

        self.add_widget(scroll_view)

    def viewDepartureFlights(self, instance):
        self.manager.current = 'resultsDeparture'
        self.manager.get_screen('resultsDeparture').update()

    def backToMainMenu(self, instance):
        External.shared_data = {
            'DestinationAirportName': '',
            'DepartureDate': '',
            'ReturnDate': '',
            'ResultsDeparture': [],
            'ResultsReturn': []
        }

        self.manager.current = 'main'

    def update(self):
        self.grid_layout.clear_widgets()

        returnFlights = []
        for flight in External.shared_data['ResultsReturn']:#
            if flight['Exists'] == True:
                returnFlights.append(flight)

        for flight in returnFlights:
            print(flight)


        returnFlights.sort(key=lambda x: float(x['Price']))
        for flight in returnFlights:
            if flight['Exists'] == True:
                textInfo = f"Origin: {flight['Origin']}\nDestination: {flight['Destination']}\nDeparture Date: {flight['Departure Date']}\nDeparture Time: {flight['Departure Time']}\nArrival Date: {flight['Arrival Date']}\nArrival Time: {flight['Arrival Time']}\nPrice: {flight['Price']}"
                label = Label(
                    text=textInfo,
                    size_hint_x=None,  # Ensure the width is fixed
                    width=(Window.width / 3) - 20,  # Adjust width for three columns and padding
                    size_hint_y=None,  # Ensure height is fixed
                    height=150,  # Adjust height if necessary
                    text_size=(Window.width / 3 - 20, None)  # Allow text to wrap
                )
                self.grid_layout.add_widget(label)

        DeparturesButton = Button(text='View Departure Flights', size_hint=(1, None), size=(200, 70),
                         pos_hint={'center_x': 0.5, 'y': 0})

        BackButton = Button(text='Return to Main Menu', size_hint=(1, None), size=(200, 70),
                                  pos_hint={'center_x': 0.5, 'y': 0.1})

        DeparturesButton.bind(on_press=self.viewDepartureFlights)
        BackButton.bind(on_press=self.backToMainMenu)

        self.add_widget(DeparturesButton)
        self.add_widget(BackButton)



class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(DateSelection(name='dateselection'))
        sm.add_widget(Loading(name='loading'))
        sm.add_widget(ResultsDeparture(name='resultsDeparture'))
        sm.add_widget(ResultsReturn(name='resultsReturn'))

        return sm

if __name__ == '__main__':
    MyApp().run()

