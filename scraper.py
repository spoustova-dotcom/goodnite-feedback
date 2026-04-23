import pandas as pd
import time
import os
import re
from playwright.sync_api import sync_playwright

def categorize_review(text):
    text = str(text).lower()
    categories = []
    keywords = {
        "Úklid": ["špína", "prach", "koupelna", "vlasy", "špinav", "uklid", "čistota", "dirty", "clean", "bathroom"],
        "Hluk": ["hluk", "ulice", "okna", "spát", "hlučné", "noise", "loud", "street", "party"],
        "Vybavení": ["postel", "matrace", "kuchyň", "tv", "wifi", "internet", "sprcha", "equipment", "bed", "shower"],
        "Komunikace": ["personál", "recepce", "zpráva", "instrukce", "majitel", "staff", "reception", "message", "host"]
    }
    for cat, kws in keywords.items():
        if any(kw in text for kw in kws):
            categories.append(cat)
    return ", ".join(categories) if categories else "Bez specifických problémů"

def scrape_booking():
    file_path = 'apartments_links_clean.csv'
    if not os.path.exists(file_path): return
    df_links = pd.read_csv(file_path)
    results = []

    with sync_playwright() as p:
        # Spouštíme s emulací iPhonu - mobilní verze je k robotům přívětivější
        browser = p.chromium.launch(headless=True)
        iphone_13 = p.devices['iPhone 13']
        context = browser.new_context(**iphone_13)
        page = context.new_page()

        for index, row in df_links.iterrows():
            name, url = row.iloc[0], row.iloc[1]
            if "booking.com" not in str(url): continue
            
            print(f"Scrapuji: {name}")
            try:
                page.goto(url, wait_until="commit", timeout=60000)
                time.sleep(5)
                
                # 1. Celkové skóre
                score = "0"
                score_el = page.locator('[data-testid="review-score-component"]').first
                if score_el.is_visible():
                    match = re.search(r"(\d+\.\d+|\d+)", score_el.inner_text().replace(',', '.'))
                    if match: score = match.group(1)

                # 2. KLIKNUTÍ PRO DETAILY (Čistota + Texty)
                # Klikneme na skóre, aby se otevřelo okno s recenzemi
                if score_el.is_visible():
                    score_el.click()
                    time.sleep(4)

                # 3. Čistota v detailu
                clean_score = "0"
                # Hledáme text Čistota v nově otevřeném okně
                clean_row = page.locator('div:has-text("Čistota"), div:has-text("Cleanliness")').last
                if clean_row.is_visible():
                    row_text = clean_row.inner_text().replace(',', '.')
                    match = re.search(r"(\d+\.\d+|\d+)", row_text)
                    if match: clean_score = match.group(1)

                # 4. Psané recenze v detailu
                review_elements = page.locator('[data-testid="review-card-description"]').all()
                all_texts = [r.inner_text().replace('\n', ' ').strip() for r in review_elements if len(r.inner_text()) > 10]
                combined_text = " | ".join(all_texts[:3])
                problem_cat = categorize_review(combined_text)

                results.append({
                    "Datum": time.strftime("%Y-%m-%d"),
                    "Apartman": name,
                    "Celkove": score,
                    "Cistota": clean_score,
                    "Text_Recenze": combined_text if combined_text else "Bez textu",
                    "Kategorie_Problemu": problem_cat
                })
                print(f"Úspěch: {name} ({score} / Čistota: {clean_score})")
                
            except Exception as e:
                print(f"Chyba u {name}: {e}")
            
            # Zavřeme stránku a otevřeme novou pro další apartmán, abychom vyčistili paměť
            page.close()
            page = context.new_page()

        browser.close()
    
    if results:
        new_df = pd.DataFrame(results)
        output = 'vysledne_recenze.csv'
        new_df.to_csv(output, mode='a', header=not os.path.exists(output), index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    scrape_booking()
