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

class Komis(ObiektMapy):
    pass

class Pracownik(ObiektMapy):
    def __init__(self, nazwa, miejscowosc, komis):
        self.komis = komis
        super().__init__(nazwa, miejscowosc)

class Klient(ObiektMapy):
    def __init__(self, nazwa, miejscowosc, komis):
        self.komis = komis
        super().__init__(nazwa, miejscowosc)


def dodaj_przesuniecie(wspolrzedne):
    """Zwraca delikatnie przesunięte współrzędne, aby napisy się nie nakładały."""
    lat, lon = wspolrzedne
    ilosc = ilosc_markerow_na_lokalizacji[(lat, lon)]
    ilosc_markerow_na_lokalizacji[(lat, lon)] += 1

    przes_lat = 0.01 * (ilosc % 5)
    przes_lon = 0.01 * (ilosc // 5)

    return [lat + przes_lat, lon + przes_lon]

def dodaj_komis():
    nazwa = pole_nazwa.get()
    miejscowosc = pole_miejscowosc.get()
    if nazwa and miejscowosc:
        nowy_komis = Komis(nazwa, miejscowosc)
        lista_komisow.append(nowy_komis)
        lista_komisow_box.insert(END, nowy_komis.nazwa)
    wyczysc_pola()

def dodaj_pracownika():
    nazwa = pole_nazwa.get()
    miejscowosc = pole_miejscowosc.get()
    komis = pole_dodatkowe.get()
    if nazwa and miejscowosc and komis:
        nowy_pracownik = Pracownik(nazwa, miejscowosc, komis)
        lista_pracownikow.append(nowy_pracownik)
        lista_pracownikow_box.insert(END, nowy_pracownik.nazwa)
    wyczysc_pola()

def dodaj_klienta():
    nazwa = pole_nazwa.get()
    miejscowosc = pole_miejscowosc.get()
    komis = pole_dodatkowe.get()
    if nazwa and miejscowosc and komis:
        nowy_klient = Klient(nazwa, miejscowosc, komis)
        lista_klientow.append(nowy_klient)
        lista_klientow_box.insert(END, nowy_klient.nazwa)
    wyczysc_pola()

def wyczysc_pola():
    pole_nazwa.delete(0, END)
    pole_miejscowosc.delete(0, END)
    if pole_dodatkowe:
        pole_dodatkowe.delete(0, END)

def usun_markery():
    global wszystkie_markery, ilosc_markerow_na_lokalizacji
    for marker in wszystkie_markery:
        marker.delete()
    wszystkie_markery = []
    ilosc_markerow_na_lokalizacji.clear()

def pokaz_komisy():
    usun_markery()
    mapa.set_zoom(6)
    for k in lista_komisow:
        k.marker = mapa.set_marker(k.wspolrzedne[0], k.wspolrzedne[1], text=k.nazwa)
        wszystkie_markery.append(k.marker)

def pokaz_pracownikow():
    usun_markery()
    mapa.set_zoom(6)
    for p in lista_pracownikow:
        wsp = dodaj_przesuniecie(p.wspolrzedne)
        p.marker = mapa.set_marker(wsp[0], wsp[1], text=p.nazwa)
        wszystkie_markery.append(p.marker)

def pokaz_klientow_dla_komisu():
    usun_markery()
    komis_nazwa = pole_klienci_komis.get()
    for k in lista_klientow:
        if k.komis == komis_nazwa:
            wsp = dodaj_przesuniecie(k.wspolrzedne)
            k.marker = mapa.set_marker(wsp[0], wsp[1], text=k.nazwa)
            wszystkie_markery.append(k.marker)

def pokaz_pracownikow_dla_komisu():
    usun_markery()
    komis_nazwa = pole_pracownicy_komis.get()
    for p in lista_pracownikow:
        if p.komis == komis_nazwa:
            wsp = dodaj_przesuniecie(p.wspolrzedne)
            p.marker = mapa.set_marker(wsp[0], wsp[1], text=p.nazwa)
            wszystkie_markery.append(p.marker)

def pokaz_formularz(typ):
    for widget in ramka_formularza.winfo_children():
        widget.destroy()

    Label(ramka_formularza, text="Nazwa").grid(row=0, column=0)
    global pole_nazwa
    pole_nazwa = Entry(ramka_formularza)
    pole_nazwa.grid(row=0, column=1)

    Label(ramka_formularza, text="Miejscowość").grid(row=1, column=0)
    global pole_miejscowosc
    pole_miejscowosc = Entry(ramka_formularza)
    pole_miejscowosc.grid(row=1, column=1)

    global pole_dodatkowe
    pole_dodatkowe = None

    if typ != "komis":
        Label(ramka_formularza, text="Komis").grid(row=2, column=0)
        pole_dodatkowe = Entry(ramka_formularza)
        pole_dodatkowe.grid(row=2, column=1)

    if typ == "komis":
        Button(ramka_formularza, text="Dodaj komis", command=dodaj_komis).grid(row=3, column=0, columnspan=2)
    elif typ == "pracownik":
        Button(ramka_formularza, text="Dodaj pracownika", command=dodaj_pracownika).grid(row=3, column=0, columnspan=2)
    elif typ == "klient":
        Button(ramka_formularza, text="Dodaj klienta", command=dodaj_klienta).grid(row=3, column=0, columnspan=2)
