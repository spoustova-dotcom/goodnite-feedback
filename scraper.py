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
        context = browser.new_context(viewport={'width': 1280, 'height': 800}, user_agent="Mozilla/5.0...")
        page = context.new_page()

        for index, row in df_links.iterrows():
            name, url = row.iloc[0], row.iloc[1]
            if "booking.com" not in str(url): continue
            
            print(f"Scrapuji: {name}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)
                
                # Skóre
                score = "0"
                score_el = page.locator('[data-testid="review-score-component"]').first
                if score_el.is_visible():
                    score = score_el.inner_text().split('\n')[0].replace(',', '.')
                
                # Čistota
                clean_score = "0"
                cat_elements = page.locator('[data-testid="v2_review_category_score_inner"]').all()
                for el in cat_elements:
                    txt = el.inner_text()
                    if "Čistota" in txt or "Cleanliness" in txt:
                        clean_score = txt.split('\n')[-1].replace(',', '.')

                # Recenze (Opraveno!)
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
            except Exception as e:
                print(f"Chyba u {name}: {e}")

        browser.close()
    
    if results:
        new_df = pd.DataFrame(results)
        output = 'vysledne_recenze.csv'
        new_df.to_csv(output, mode='a', header=not os.path.exists(output), index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    scrape_booking()
