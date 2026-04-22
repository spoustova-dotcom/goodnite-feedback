import pandas as pd
import time
import os
from playwright.sync_api import sync_playwright

def scrape_booking():
    file_path = 'apartments_links_clean.csv'
    
    # Kontrola, jestli soubor existuje
    if not os.path.exists(file_path):
        print(f"KRITICKÁ CHYBA: Soubor {file_path} nebyl v adresáři nalezen!")
        print(f"Obsah adresáře: {os.listdir('.')}")
        return

    # Načtení tvých odkazů
    df_links = pd.read_csv(file_path)
    results = []

    with sync_playwright() as p:
        print("Spouštím prohlížeč...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()

        for index, row in df_links.iterrows():
            name = row['Apartmán']
            url = row['Booking URL']
            
            if pd.isna(url) or "booking.com" not in str(url):
                continue
                
            print(f"Scrapuji: {name}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5) # Počkáme na načtení dynamických prvků
                
                # Zkusíme najít skóre - upravený selektor
                rating_element = page.locator('[data-testid="review-score-component"]').first
                if rating_element.is_visible():
                    rating = rating_element.inner_text().split('\n')[0]
                    results.append({
                        "Datum": time.strftime("%d.%m.%Y"),
                        "apartmán": name,
                        "hodnoceni": rating.replace(',', '.'),
                        "Platforma": "Booking"
                    })
                    print(f"Úspěch: {name} má hodnocení {rating}")
                else:
                    print(f"Varování: U {name} nebylo nalezeno hodnocení.")
                    
            except Exception as e:
                print(f"Chyba u {name}: {e}")

        browser.close()
    
    if results:
        new_data = pd.DataFrame(results)
        output_file = 'Recenze ⭐ - Text_recenze.csv'
        header = not os.path.exists(output_file)
        new_data.to_csv(output_file, mode='a', header=header, index=False)
        print(f"Hotovo! Zapsáno {len(results)} nových záznamů.")
    else:
        print("Nebyla nalezena žádná nová data k zápisu.")

if __name__ == "__main__":
    scrape_booking()
