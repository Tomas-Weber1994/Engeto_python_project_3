## Web Scraping - CZ Elections in 2017

Výsledky voleb do Poslanecké sněmovny Parlamentu České republiky.

### Zadání 
Úkolem bylo vytvořit scraper výsledků voleb z roku 2017, který vytáhne data přímo z webu: https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ

Skript má za úkol scrapovat výsledky voleb pro jakýkoliv územní celek, který si užovatel zvolí. Volbu územního celku provede uživatel v rámci výše uvedeného webu  pomocí "X" ve sloupci výběr obce. Program následně pracuje s daným URL.  Např. "X" u územního celku Benešov odkazuje na web: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101

Výstupem je csv ve tvaru "soubor.csv", přičemž každý řádek obsahuje informace pro konkrétní obec. Tedy podobu:

- kód obce
- název obce
- voliči v seznamu
- vydané obálky
- platné hlasy
- kandidující strany a jejich počty hlasů

Výskedný soubor se spouští pomocí  příkazové řádky a 2 argumentů. První argument obsahuje odkaz, který územní celek chcete scrapovat (např. při zvolené obci Benešov je argument: "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101"). Druhým argumentem je jméno výstupního souboru (např. "volby_Benesov.csv"). 

### Instalace knihoven 
Pro funkčnost kódu je nutné si nainstalovat použité knihovny. Ty jsou dostupné v rámci souboru "requirements.txt", který je dostupný v repozitáři. Knihovny doporučuji instalovat do virtuálního prostředí. 

### Spouštění kódu 
Je třeba si otevřít příkazovou řádku v dané složce, ve které je skript dostupný. Do příkazové řádky (na uvedeném příkladě Benešova) zadáme: 
python Election_Scraper.py "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" "volby_Benesov.csv"

Pokud uživatel nezadá argumenty nebo zadá jejich nesprávný počet, je upozorněn a program končí. Pokud není vložené URL validní, zobrazí se taktéž upozornění. 



