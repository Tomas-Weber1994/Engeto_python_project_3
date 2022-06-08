from bs4 import BeautifulSoup
import requests
import sys
import csv


def main():
    """
    Hlavní funkce, která řídí běh programu
    """
    url, jmeno_souboru = cmd_spusteni()
    soup = make_soup(url)
    url_uzemnich_celku = ziskej_url_uzemnich_celku(soup)
    vsechny_kody_obci, vsechny_nazvy_obci = ziskej_kody_a_nazvy_obci(soup)

    seznam_volebnich_vysledku = []
    for url in url_uzemnich_celku:   # Smyčka prochází všechny URL územních celků, které je nutné scrapovat.
        nazev_obce = ziskej_nazev_obce(url)
        kod_obce = najdi_odpovidajici_kod_obce(nazev_obce, vsechny_nazvy_obci, vsechny_kody_obci)
        pocty_opravnenych_volicu, pocty_vydanych_obalek, pocty_platnych_hlasu = scraping_hlavickovych_dat_jednotlivych_obci(url)
        seznam_kandidujicich_stran = scraping_nazvu_stran(url)
        hlasy_kandidujicich_stran = scraping_poctu_hlasu_stran(url)
        slovnik = vytvor_slovnik(kod_obce, nazev_obce, pocty_opravnenych_volicu, pocty_vydanych_obalek, pocty_platnych_hlasu, seznam_kandidujicich_stran, hlasy_kandidujicich_stran)
        seznam_volebnich_vysledku.append(slovnik)

    uloz_data_csv(seznam_volebnich_vysledku, jmeno_souboru)

    # Alternativně lze:
    # import pandas as pd
    # df = pd.DataFrame(seznam_volebnich_vysledku)
    # df.to_csv("volby.csv", sep=";", encoding="utf-8")


def cmd_spusteni() -> tuple:
    """
    Program je spouštěn pomocí příkazové řádky, přičemž je třeba zadat dva argumenty.
    Pokud uživatel argumenty nezadá, případně zadá jejich nesprávný počet, je upozorněn a program končí.
    """
    try:
        webova_stranka = sys.argv[1]
        ulozit_jako = sys.argv[2]
        return webova_stranka, ulozit_jako
    except IndexError:
        print("Nebyly zadány správně argumenty.")
        print("Pro správný běh programu je třeba zadat do příkazové řádky: python Election_Scraper.py <\"URL\"> <\"název souboru.csv\">")
        quit()
    # except: # Slouží pouze pro testování programu namísto výše uvedené klauzule except IndexError.
    #     webova_stranka = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100"
    #     ulozit_jako = "volby.csv"
    #     return webova_stranka, ulozit_jako


def make_soup(webova_adresa) -> BeautifulSoup:
    """
    Funkce posílá požadavek GET na zadané URL a vrací BS4 object. Pokud není URL validní, program končí.
    """
    try:
        odpoved = requests.get(webova_adresa)
        return BeautifulSoup(odpoved.text, features="html.parser")
    except:
        print("Nebylo zadáno validní URL, ukončuji program...")
        quit()


def ziskej_url_uzemnich_celku(soup) -> list:
    """
    Funkce vrací seznam URL všech územních celků (obcí nebo mětských částí) na základě primárního URL zadaného při spuštění programu.
    Např. při vložení primárního URL odkazující na Prahu funkce vrátí všechna URL pro výsledky voleb v pražských městských částech.
    """
    tagy = soup.find_all("td", {"class": "cislo"})
    hrefs = []
    for tag in tagy:
        href = tag.find('a')['href']
        href = "https://volby.cz/pls/ps2017nss/" + href
        hrefs.append(href)
    return hrefs


def ziskej_kody_a_nazvy_obci(soup) -> tuple[list, list]:
    """
    Funkce pracuje se vstupním bs4 objektem, na základě vloženého primárního URL při spuštění programu.
    Vrací tuple všech kódů a názvů obcí z primárního URL.
    """
    tagy1 = soup.find_all("td", {"class": "cislo"})
    kody_obci = [tag.text for tag in tagy1]

    tagy2 = soup.find_all("td", {"class": "overflow_name"})
    nazvy_obci = [tag.text for tag in tagy2]
    return kody_obci, nazvy_obci


def ziskej_nazev_obce(url_odkaz_na_volebni_vysledky) -> str:
    """
    Funkce má jako vstup URL odkaz na volební výsledky v rámci jednotlivých obcí / městských částí.
    Název obce je v hledaném listu tagů vždy na třetím místě od konce (index -3).
    Výstupem funkce je název obce / mětské části očištěný o prázdný string na konci.
    """
    soup = make_soup(url_odkaz_na_volebni_vysledky)
    tagy = soup.find_all("h3")
    print(tagy[-3].text, "- Načítám data...", end="")

    nazev_obce = tagy[-3].text.split(" ", maxsplit=1)[1].rstrip()
    return nazev_obce


def najdi_odpovidajici_kod_obce(hledam_obec, obce, kody) -> str:
    """
    Funkce páruje všechny kódy obcí s jejich názvy.
    Následně vypíše kód obce, který odpovídá obci, kterou dle názvu hledáme.
    Kódy obcí nejsou totiž dostupné v rámci URL výsledků pro jednotlivé obce.
    """
    slovnik = {}
    for obec, kod in zip(obce, kody):
        slovnik[obec] = kod
    return slovnik.get(hledam_obec)


def scraping_hlavickovych_dat_jednotlivych_obci(url_odkaz_na_volebni_vysledky) -> tuple[list, list, list]:
    """
    Funkce má jako vstup URL odkaz na volební výsledky v rámci jednotlivých obcí / městských částí.
    Na základě vstupního URL je pomocí funkce make_soup() vytvořen bs4 objekt, v němž hledáme odpovídající html tagy.
    Atribut 'headers' má hodnotu ve formě listu 3 prvků, vzhledem k tomu, že scrapujeme 3 různé údaje.
    Výstupem funkce jsou počty oprávněných voličů, vydaných obálek a platných hlasů v dané obci.
    """
    soup = make_soup(url_odkaz_na_volebni_vysledky)
    tagy = soup.find_all("td", {"class": "cislo", "headers": ("sa2", "sa3", "sa6")})
    tagy = preved_specialni_znaky_na_cislo([tag.text for tag in tagy])

    pocty_opravnenych_volicu, pocty_vydanych_obalek, pocty_platnych_hlasu = tagy
    return pocty_opravnenych_volicu, pocty_vydanych_obalek, pocty_platnych_hlasu


def scraping_nazvu_stran(url_odkaz_na_volebni_vysledky) -> list:
    """
    Funkce má jako vstup URL odkaz na volební výsledky v rámci jednotlivých obcí / městských částí.
    Výstupem je seznam kandidujících politických stran v dané obci.
    """
    soup = make_soup(url_odkaz_na_volebni_vysledky)
    tagy = soup.find_all("td", {"class": "overflow_name"})
    return [tag.text for tag in tagy]


def preved_specialni_znaky_na_cislo(sekvence_necitelnych_udaju) -> list:
    """
    Funkce převádí seznam nečitelných dat na seznam čísel.
    """
    return [int(udaj.replace("\xa0", "")) for udaj in sekvence_necitelnych_udaju]


def scraping_poctu_hlasu_stran(url_odkaz_na_volebni_vysledky) -> list:
    """
    Funkce má opět jako vstup URL odkaz na volební výsledky v rámci jednotlivých obcí / městských částí.
    Ve vytvořeném bs4 objektu hledáme počty hlasů jednotlivých stran v dané obci. Atribut 'heades' má dva parametry,
    vzhledem k tomu, že počty hlasů stran jsou rozděleny do dvou tabulek.
    Výstupem funkce je seznam počtu hlasů jednotlivých stran v dané obci.
    """
    soup = make_soup(url_odkaz_na_volebni_vysledky)
    tagy = soup.find_all("td", {"class": "cislo", "headers": ("t1sa2 t1sb3", "t2sa2 t2sb3")})
    return preved_specialni_znaky_na_cislo([tag.text for tag in tagy])


def vytvor_slovnik(kod, nazev, opravneni_volici, pocet_obalek, platne_hlasy, strana, pocet_hlasu) -> dict:
    """
    Funkce spojuje veškerá vyscrapovaná data do výsledného slovníku za účelem pozdějšího snadného zapsání do csv.
    """
    slovnik = {
        "Kód obce": kod,
        "Název obce": nazev,
        "Voliči v seznamu": opravneni_volici,
        "Vydané obálky": pocet_obalek,
        "Platné hlasy": platne_hlasy
        }
    for strana, pocet_hlasu in zip(strana, pocet_hlasu):
        slovnik[strana] = pocet_hlasu
    return slovnik


def uloz_data_csv(seznam_volebnich_vysledku, jmeno_souboru):
    """
    Funkce bere jako vstup seznam všech slovníků, který vzniká procházením jednotlivých územních URL.
    Druhým parametrem je jméno souboru, jež odpovídá druhému zadanému argumentu při spouštění celého programu v rámci příkazové řádky.
    Soubor je následně uložen do csv, přičemž je neprve zapsána hlavička, poté jednotlivé řádky.
    """
    zahlavi = seznam_volebnich_vysledku[0].keys()
    with open(jmeno_souboru, mode="w", encoding="utf-8", newline="") as soubor:
        zapisovac = csv.DictWriter(soubor, delimiter=";", fieldnames=zahlavi)
        zapisovac.writeheader()
        zapisovac.writerows(seznam_volebnich_vysledku)
    print()
    print("Data byla úspěšně exportována do souboru", jmeno_souboru)


if __name__ == "__main__":
    main()
