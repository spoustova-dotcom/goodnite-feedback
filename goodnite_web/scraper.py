import pandas as pd
import time
import os
from playwright.sync_api import sync_playwright

def scrape_booking():
    file_path = 'apartments_links_clean.csv'
    if not os.path.exists(file_path):
        print(f"Chyba: Soubor {file_path} nenalezen!")
        return

    df_links = pd.read_csv(file_path)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for index, row in df_links.iterrows():
            name = row['Apartmán']
            url = row['Booking URL']
            
            if pd.isna(url) or "booking.com" not in str(url):
                continue
                
            print(f"Zkouším: {name}")
            try:
                page.goto(url, timeout=60000)
                # Jednoduchý sběr skóre
                score = page.locator('[data-testid="review-score-component"]').first.inner_text().split('\n')[0]
                results.append({"Datum": time.strftime("%d.%m.%Y"), "apartmán": name, "hodnoceni": score, "Platforma": "Booking"})
                print(f"OK: {name} ({score})")
            except Exception as e:
                print(f"Přeskočeno {name}: {e}")

        browser.close()
    
    if results:
        pd.DataFrame(results).to_csv('Recenze ⭐ - Text_recenze.csv', mode='a', header=False, index=False)
        print("Data uložena.")

if __name__ == "__main__":
    scrape_booking()
