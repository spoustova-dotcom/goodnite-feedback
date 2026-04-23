import pandas as pd
import time
import os
from playwright.sync_api import sync_playwright

def scrape_booking():
    # Zkusíme najít soubor pod oběma možnými názvy
    file_path = 'apartments_links_clean.csv'
    if not os.path.exists(file_path):
        print(f"Chyba: Soubor {file_path} nenalezen!")
        return

    # Načteme CSV
    df_links = pd.read_csv(file_path)
    
    # Automaticky detekujeme sloupce podle pozice (0 = první, 1 = druhý)
    # Tím vymažeme chybu KeyError: 'Apartmán'
    results = []

    with sync_playwright() as p:
        print("Spouštím prohlížeč...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()

        for index, row in df_links.iterrows():
            # Vezmeme data podle pozice, ne podle jména
            name = row.iloc[0] 
            url = row.iloc[1]
            
            if pd.isna(url) or "booking.com" not in str(url):
                continue
                
            print(f"Scrapuji: {name}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5) 
                
                rating_element = page.locator('[data-testid="review-score-component"]').first
                if rating_element.is_visible():
                    rating = rating_element.inner_text().split('\n')[0]
                    results.append({
                        "Datum": time.strftime("%d.%m.%Y"),
                        "apartmán": name,
                        "hodnoceni": rating.replace(',', '.'),
                        "Platforma": "Booking"
                    })
                    print(f"Úspěch: {name} -> {rating}")
                else:
                    print(f"U {name} nebylo nalezeno hodnocení.")
                    
            except Exception as e:
                print(f"Chyba u {name}: {e}")

        browser.close()
    
    if results:
        new_data = pd.DataFrame(results)
        output_file = 'Recenze ⭐ - Seznam.csv' # Ukládáme do souboru, který používá app.py
        header = not os.path.exists(output_file)
        new_data.to_csv(output_file, mode='a', header=header, index=False)
        print(f"Hotovo! Zapsáno {len(results)} záznamů.")
    else:
        print("Žádná data nebyla získána.")

if __name__ == "__main__":
    scrape_booking()
