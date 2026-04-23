import pandas as pd
import time
import os
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
        # Nastavení jako reálný uživatel
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()

        for index, row in df_links.iterrows():
            name, url = row.iloc[0], row.iloc[1]
            if "booking.com" not in str(url): continue
            
            print(f"Scrapuji: {name}")
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                time.sleep(7) # Musíme dát Bookingu čas na vykreslení bublin s čísly
                
                # Agresivnější hledání celkového skóre
                score = "0"
                # Zkusíme několik možných cest, kde Booking schovává skóre
                score_selectors = ['[data-testid="review-score-component"]', 'div.a3332d346a', 'div._9c5f70443']
                for selector in score_selectors:
                    el = page.locator(selector).first
                    if el.is_visible():
                        score_text = el.inner_text().replace(',', '.')
                        # Vytáhneme jen první číslo (např. 8.7)
                        import re
                        match = re.search(r"(\d+\.\d+|\d+)", score_text)
                        if match:
                            score = match.group(1)
                            break
                
                # Hledání čistoty v tabulce detailů
                clean_score = "0"
                page.mouse.wheel(0, 1500) # Sjedeme dolů, kde bývají kategorie
                time.sleep(2)
                cat_elements = page.locator('div.d6d4671780, [data-testid="v2_review_category_score_inner"]').all()
                for el in cat_elements:
                    txt = el.inner_text()
                    if "Čistota" in txt or "Cleanliness" in txt:
                        match = re.search(r"(\d+\.\d+|\d+)", txt)
                        if match: clean_score = match.group(1)

                # Psané recenze
                review_elements = page.locator('[data-testid="review-card-description"]').all()
                all_texts = [r.inner_text().replace('\n', ' ') for r in review_elements[:3]]
                combined_text = " | ".join(all_texts)
                problem_cat = categorize_review(combined_text)

                results.append({
                    "Datum": time.strftime("%Y-%m-%d"),
                    "Apartman": name,
                    "Celkove": score,
                    "Cistota": clean_score,
                    "Text_Recenze": combined_text if combined_text else "Bez textu",
                    "Kategorie_Problemu": problem_cat
                })
                print(f"Úspěch: {name} ({score})")
            except Exception as e:
                print(f"Chyba u {name}: {e}")

        browser.close()
    
    if results:
        new_df = pd.DataFrame(results)
        output = 'vysledne_recenze.csv'
        new_df.to_csv(output, mode='a', header=not os.path.exists(output), index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    scrape_booking()
