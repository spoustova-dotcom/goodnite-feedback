import pandas as pd
import time
import os
from playwright.sync_api import sync_playwright

def scrape_booking():
    file_path = 'apartments_links_clean.csv'
    if not os.path.exists(file_path): return

    df_links = pd.read_csv(file_path)
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()

        for index, row in df_links.iterrows():
            name = row.iloc[0]
            url = str(row.iloc[1])
            
            if "booking.com" not in url: continue
            
            print(f"Scrapuji: {name}...")
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(4)
                
                # --- SBĚR HODNOCENÍ ---
                score = "0"
                score_el = page.locator('[data-testid="review-score-component"]').first
                if score_el.is_visible():
                    score = score_el.inner_text().split('\n')[0].replace(',', '.')

                # --- SBĚR TEXTOVÝCH RECENZÍ ---
                # Pokusíme se najít texty posledních recenzí
                reviews_list = []
                review_elements = page.locator('[data-testid="review-card-text-positive"], [data-testid="review-card-description"]').all()
                for el in review_elements[:3]: # Vezmeme první 3 recenze
                    text = el.inner_text().strip()
                    if text: reviews_list.append(text)
                
                review_text = " | ".join(reviews_list) if reviews_list else "Žádné nové textové recenze."

                results.append({
                    "Datum": time.strftime("%Y-%m-%d"),
                    "Apartman": name,
                    "Celkove": score,
                    "Uklid": 9.0, # Booking tyto detaily často dynamicky mění, pro demo tam dáme fixní nebo zkusíme najít
                    "Personal": 9.0,
                    "Text_Recenze": review_text,
                    "Platforma": "Booking"
                })
                print(f"Úspěch: {name}")

            except Exception as e:
                print(f"Chyba u {name}: {e}")

        browser.close()
    
    if results:
        new_data = pd.DataFrame(results)
        output_file = 'vysledne_recenze.csv'
        header = not os.path.exists(output_file)
        new_data.to_csv(output_file, mode='a', header=header, index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    scrape_booking()
