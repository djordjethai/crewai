import re
def extract_tip_podrske(text):
    pattern = r"Trenutna telefonska podrška – (\d{1,2}/\d{1,2})"
    match = re.search(pattern, text)

    if match:
        extracted_hours = match.group(1)  # Group 1 contains the matched digits pattern
        print(f"Extracted hours: {extracted_hours}")
    else:
        print("No match found.")

t = """
Usluga PC Radno Mesto uključuje:

Korišćenje računarske opreme;

Legalnost Korisnika po pitanju operativnog sistema, za koju garantuje Davalac usluga;

Besplatnu isporuku opreme i podešavanje softvera, koji su predmet usluge u okviru postojećeg informacionog sistema;

Zamensku opremu u slučaju otkaza nekog od računara koji su predmet usluge da bi se usluga obavljala kontinuirano u roku od 2 radna dana;

Brz odziv – reakcija na prijavu neispravnosti od strane Korisnika u roku od 4 sata od trenutka prijave a u okviru svog radnog vremena;

Mogućnost proširenja obima usluge, uz zaključivanje Aneksa ugovora i prihvaćenu novu Ponudu;

Sophos Central Intercept X Essentials – instalacija Cloud antivirus rešenja na opremi koja je obuhvaćena ugovorom;

Konfigurisanje Sophos cloud portala;

Support servisi – instalacija Teamviewer Quick Support aplikacije koja omogućava daljinski pristup računaru Korisnika, nadzor nad Sophos cloud portalima i kreiranje novih korisnika, intervencije po uočenim događajima kao i po pozivu za servise koji se mogu daljinski održavati;

Trenutna telefonska podrška – 8/5;

3 meseca gratis korišćenja usluge, ukoliko se nakon trogodišnjeg aranžmana Korisnik opredeli za nastavak korišćenja usluge. To podrazumeva vraćanje uređaja i preuzimanje drugog.

Opcija zadržavanja starog uređaja po isteku ugovora bez novčane nadoknade.

Cena usluge na mesečnom nivou iznosi 19 eur + PDV po radnom mestu, odnosno 76 eur + pdv mesečno za 4 radna mesta. Ugovor se sklapa na period od 36 meseci.
"""


x = extract_tip_podrske(t)
print(x)