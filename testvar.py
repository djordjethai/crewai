import re

def extract_cena_eur(text):
    # Updated regex patterns to include optional decimal part and more flexibility
    patterns = [
        re.compile(r"odnosno\s+(\d+,\d+|\d+)\s*eur", re.IGNORECASE),
        re.compile(r"nivou iznosi\s+(\d+,\d+|\d+)\s*eur", re.IGNORECASE)
    ]
    
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            # Replace comma with period for float conversion and return
            return match.group(1).replace(',', '.')
    
    # If no pattern matches, raise a ValueError with a clear message
    raise ValueError("No valid price (number before 'eur') found in the text.")

# Example usage
try:
    text = "Cena usluge na mesečnom nivou iznosi 13,5 eur + PDV po korisniku. Ugovor se sklapa na period od 12 meseci."
    cena_eur = float(extract_cena_eur(text))
    print(cena_eur)
except ValueError as e:
    print(e)
