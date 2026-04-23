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
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()

        for index, row in df_links.iterrows():
            name, url = row.iloc[0], row.iloc[1]
            if "booking.com" not in str(url): continue
            
            print(f"Scrapuji: {name}")
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # --- KLÍČOVÝ KROK: SKROLOVÁNÍ ---
                # Booking načítá detaily (čistotu a texty) až při skrolu
                for _ in range(3):
                    page.mouse.wheel(0, 1000)
                    time.sleep(2)
                
                # Celkové skóre
                score = "0"
                score_el = page.locator('[data-testid="review-score-component"]').first
                if score_el.is_visible():
                    match = re.search(r"(\d+\.\d+|\d+)", score_el.inner_text().replace(',', '.'))
                    if match: score = match.group(1)
                
                # Čistota (Hledáme v tabulce, která se teď díky skrolu načetla)
                clean_score = "0"
                # Hledáme text "Čistota" a pak jeho sourozence s číslem
                clean_el = page.get_by_text("Čistota", exact=False).first
                if clean_el.is_visible():
                    # Zkusíme najít číslo v okolí textu Čistota
                    parent_text = clean_el.locator("xpath=..").inner_text()
                    match = re.search(r"(\d+\.\d+|\d+)", parent_text.replace(',', '.'))
                    if match: clean_score = match.group(1)

                # Textové recenze (pozitivní i negativní)
                # Používáme širší selektor pro různé verze designu Bookingu
                review_elements = page.locator('[data-testid="review-card-description"], .review_item_main_content, .c-review-block__full-text').all()
                all_texts = [r.inner_text().replace('\n', ' ').strip() for r in review_elements if len(r.inner_text()) > 5]
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

        browser.close()
    
    if results:
        new_df = pd.DataFrame(results)
        output = 'vysledne_recenze.csv'
        new_df.to_csv(output, mode='a', header=not os.path.exists(output), index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    scrape_booking()
