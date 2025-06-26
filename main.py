from tkinter import *
import tkintermapview
import requests
from bs4 import BeautifulSoup
from collections import defaultdict


lista_komisow = []
lista_pracownikow = []
lista_klientow = []
wszystkie_markery = []


ilosc_markerow_na_lokalizacji = defaultdict(int)

class ObiektMapy:
    def __init__(self, nazwa, miejscowosc):
        self.nazwa = nazwa
        self.miejscowosc = miejscowosc
        self.wspolrzedne = self.pobierz_wspolrzedne()
        self.marker = None

    def pobierz_wspolrzedne(self):
        try:
            url = f"https://pl.wikipedia.org/wiki/{self.miejscowosc}"
            response = requests.get(url, timeout=5).text
            soup = BeautifulSoup(response, "html.parser")
            latitude = float(soup.select(".latitude")[1].text.replace(",", "."))
            longitude = float(soup.select(".longitude")[1].text.replace(",", "."))
            return [latitude, longitude]
        except Exception as e:
            print(f"Błąd pobierania współrzędnych dla {self.miejscowosc}: {e}")
            return [52.23, 21.01]  # Domyślna: Warszawa
