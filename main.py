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
            return [52.23, 21.01]

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



def edytuj_komis():
    zaznaczony = lista_komisow_box.curselection()
    if not zaznaczony:
        return
    indeks = zaznaczony[0]
    komis = lista_komisow[indeks]

    edycja_okno = Toplevel(okno)
    edycja_okno.title("Edytuj komis")

    Label(edycja_okno, text="Nazwa").grid(row=0, column=0)
    entry_nazwa = Entry(edycja_okno)
    entry_nazwa.insert(0, komis.nazwa)
    entry_nazwa.grid(row=0, column=1)

    Label(edycja_okno, text="Miejscowość").grid(row=1, column=0)
    entry_miejsc = Entry(edycja_okno)
    entry_miejsc.insert(0, komis.miejscowosc)
    entry_miejsc.grid(row=1, column=1)

    def zapisz():
        komis.nazwa = entry_nazwa.get()
        komis.miejscowosc = entry_miejsc.get()
        komis.wspolrzedne = komis.pobierz_wspolrzedne()
        lista_komisow_box.delete(indeks)
        lista_komisow_box.insert(indeks, komis.nazwa)
        edycja_okno.destroy()

    Button(edycja_okno, text="Zapisz", command=zapisz).grid(row=2, column=0, columnspan=2)

def usun_komis():
    zaznaczony = lista_komisow_box.curselection()
    if not zaznaczony:
        return
    indeks = zaznaczony[0]
    del lista_komisow[indeks]
    lista_komisow_box.delete(indeks)

def edytuj_pracownika():
    zaznaczony = lista_pracownikow_box.curselection()
    if not zaznaczony:
        return
    indeks = zaznaczony[0]
    pracownik = lista_pracownikow[indeks]

    edycja_okno = Toplevel(okno)
    edycja_okno.title("Edytuj pracownika")

    Label(edycja_okno, text="Nazwa").grid(row=0, column=0)
    entry_nazwa = Entry(edycja_okno)
    entry_nazwa.insert(0, pracownik.nazwa)
    entry_nazwa.grid(row=0, column=1)

    Label(edycja_okno, text="Miejscowość").grid(row=1, column=0)
    entry_miejsc = Entry(edycja_okno)
    entry_miejsc.insert(0, pracownik.miejscowosc)
    entry_miejsc.grid(row=1, column=1)

    Label(edycja_okno, text="Komis").grid(row=2, column=0)
    entry_komis = Entry(edycja_okno)
    entry_komis.insert(0, pracownik.komis)
    entry_komis.grid(row=2, column=1)

    def zapisz():
        pracownik.nazwa = entry_nazwa.get()
        pracownik.miejscowosc = entry_miejsc.get()
        pracownik.komis = entry_komis.get()
        pracownik.wspolrzedne = pracownik.pobierz_wspolrzedne()
        lista_pracownikow_box.delete(indeks)
        lista_pracownikow_box.insert(indeks, pracownik.nazwa)
        edycja_okno.destroy()

    Button(edycja_okno, text="Zapisz", command=zapisz).grid(row=3, column=0, columnspan=2)

def usun_pracownika():
    zaznaczony = lista_pracownikow_box.curselection()
    if not zaznaczony:
        return
    indeks = zaznaczony[0]
    del lista_pracownikow[indeks]
    lista_pracownikow_box.delete(indeks)

def edytuj_klienta():
    zaznaczony = lista_klientow_box.curselection()
    if not zaznaczony:
        return
    indeks = zaznaczony[0]
    klient = lista_klientow[indeks]

    edycja_okno = Toplevel(okno)
    edycja_okno.title("Edytuj klienta")

    Label(edycja_okno, text="Nazwa").grid(row=0, column=0)
    entry_nazwa = Entry(edycja_okno)
    entry_nazwa.insert(0, klient.nazwa)
    entry_nazwa.grid(row=0, column=1)

    Label(edycja_okno, text="Miejscowość").grid(row=1, column=0)
    entry_miejsc = Entry(edycja_okno)
    entry_miejsc.insert(0, klient.miejscowosc)
    entry_miejsc.grid(row=1, column=1)

    Label(edycja_okno, text="Komis").grid(row=2, column=0)
    entry_komis = Entry(edycja_okno)
    entry_komis.insert(0, klient.komis)
    entry_komis.grid(row=2, column=1)

    def zapisz():
        klient.nazwa = entry_nazwa.get()
        klient.miejscowosc = entry_miejsc.get()
        klient.komis = entry_komis.get()
        klient.wspolrzedne = klient.pobierz_wspolrzedne()
        lista_klientow_box.delete(indeks)
        lista_klientow_box.insert(indeks, klient.nazwa)
        edycja_okno.destroy()

    Button(edycja_okno, text="Zapisz", command=zapisz).grid(row=3, column=0, columnspan=2)

def usun_klienta():
    zaznaczony = lista_klientow_box.curselection()
    if not zaznaczony:
        return
    indeks = zaznaczony[0]
    del lista_klientow[indeks]
    lista_klientow_box.delete(indeks)


okno = Tk()
okno.geometry("1200x800")
okno.title("Mapa Komisów Samochodowych")

panel_lewy = Frame(okno)
panel_lewy.grid(row=0, column=0, sticky=N)

Button(panel_lewy, text="Formularz: Komis", command=lambda: pokaz_formularz("komis")).grid(row=0, column=0, columnspan=2)
Button(panel_lewy, text="Formularz: Pracownik", command=lambda: pokaz_formularz("pracownik")).grid(row=1, column=0, columnspan=2)
Button(panel_lewy, text="Formularz: Klient", command=lambda: pokaz_formularz("klient")).grid(row=2, column=0, columnspan=2)

ramka_formularza = Frame(panel_lewy)
ramka_formularza.grid(row=3, column=0, columnspan=2, pady=10)

Button(panel_lewy, text="Pokaż wszystkie komisy", command=pokaz_komisy).grid(row=4, column=0, columnspan=2)
Button(panel_lewy, text="Pokaż wszystkich pracowników", command=pokaz_pracownikow).grid(row=5, column=0, columnspan=2)

Label(panel_lewy, text="Komis (dla klientów):").grid(row=6, column=0, columnspan=2)
pole_klienci_komis = Entry(panel_lewy)
pole_klienci_komis.grid(row=7, column=0, columnspan=2)
Button(panel_lewy, text="Pokaż klientów", command=pokaz_klientow_dla_komisu).grid(row=8, column=0, columnspan=2)

Label(panel_lewy, text="Komis (dla pracowników):").grid(row=9, column=0, columnspan=2)
pole_pracownicy_komis = Entry(panel_lewy)
pole_pracownicy_komis.grid(row=10, column=0, columnspan=2)
Button(panel_lewy, text="Pokaż pracowników", command=pokaz_pracownikow_dla_komisu).grid(row=11, column=0, columnspan=2)

Label(panel_lewy, text="Komisy").grid(row=12, column=0)
lista_komisow_box = Listbox(panel_lewy, height=5)
lista_komisow_box.grid(row=13, column=0, columnspan=2)
Button(panel_lewy, text="Edytuj komis", command=edytuj_komis).grid(row=14, column=0)
Button(panel_lewy, text="Usuń komis", command=usun_komis).grid(row=14, column=1)

Label(panel_lewy, text="Pracownicy").grid(row=15, column=0)
lista_pracownikow_box = Listbox(panel_lewy, height=5)
lista_pracownikow_box.grid(row=16, column=0, columnspan=2)
Button(panel_lewy, text="Edytuj pracownika", command=edytuj_pracownika).grid(row=17, column=0)
Button(panel_lewy, text="Usuń pracownika", command=usun_pracownika).grid(row=17, column=1)

Label(panel_lewy, text="Klienci").grid(row=18, column=0)
lista_klientow_box = Listbox(panel_lewy, height=5)
lista_klientow_box.grid(row=19, column=0, columnspan=2)
Button(panel_lewy, text="Edytuj klienta", command=edytuj_klienta).grid(row=20, column=0)
Button(panel_lewy, text="Usuń klienta", command=usun_klienta).grid(row=20, column=1)

panel_prawy = Frame(okno)
panel_prawy.grid(row=0, column=1)

mapa = tkintermapview.TkinterMapView(panel_prawy, width=800, height=800, corner_radius=0)
mapa.set_position(52.23, 21.01)
mapa.set_zoom(6)
mapa.pack(fill="both", expand=True)

okno.mainloop()
