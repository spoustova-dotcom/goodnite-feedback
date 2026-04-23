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
        browser = p.chromium.launch(headless=True)
        iphone = p.devices['iPhone 13']
        context = browser.new_context(**iphone)
        page = context.new_page()

        for index, row in df_links.iterrows():
            name, url = row.iloc[0], row.iloc[1]
            if "booking.com" not in str(url): continue
            
            print(f"Scrapuji: {name}")
            try:
                page.goto(url, wait_until="commit", timeout=60000)
                time.sleep(6) # Čas na základní načtení
                
                # 1. Celkové skóre
                score = "0"
                score_el = page.locator('[data-testid="review-score-component"]').first
                if score_el.is_visible():
                    match = re.search(r"(\d+\.\d+|\d+)", score_el.inner_text().replace(',', '.'))
                    if match: score = match.group(1)
                    score_el.click() # Otevřeme detaily
                    time.sleep(5) # ZDE JE KLÍČOVÉ ČEKÁNÍ NA OKNO

                # 2. Sběr kategorií z okna
                details = {"Clean": "0", "Staff": "0"}
                
                # Hledáme Čistotu
                clean_row = page.locator('div:has-text("Čistota"), div:has-text("Cleanliness")').last
                if clean_row.is_visible():
                    m = re.search(r"(\d+\.\d+|\d+)", clean_row.inner_text().replace(',', '.'))
                    if m: details["Clean"] = m.group(1)
                
                # Hledáme Personál
                staff_row = page.locator('div:has-text("Personál"), div:has-text("Staff")').last
                if staff_row.is_visible():
                    m = re.search(r"(\d+\.\d+|\d+)", staff_row.inner_text().replace(',', '.'))
                    if m: details["Staff"] = m.group(1)

                # 3. Psané recenze
                review_elements = page.locator('[data-testid="review-card-description"]').all()
                all_texts = [r.inner_text().replace('\n', ' ').strip() for r in review_elements if len(r.inner_text()) > 10]
                combined_text = " | ".join(all_texts[:3])

                results.append({
                    "Datum": time.strftime("%Y-%m-%d"),
                    "Apartman": name,
                    "Celkove": score,
                    "Cistota": details["Clean"],
                    "Personal": details["Staff"],
                    "Text_Recenze": combined_text if combined_text else "Bez textu",
                    "Kategorie_Problemu": categorize_review(combined_text)
                })
                print(f"Uloženo: {name} ({score} / C:{details['Clean']} / P:{details['Staff']})")
                
            except Exception as e:
                print(f"Chyba u {name}: {e}")
            
            page.close()
            page = context.new_page()

        browser.close()
    
    if results:
        new_df = pd.DataFrame(results)
        output = 'vysledne_recenze.csv'
        new_df.to_csv(output, mode='a', header=not os.path.exists(output), index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    scrape_booking()
