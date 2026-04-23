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
        # Maskujeme se jako běžný prohlížeč
        context = browser.new_context(viewport={'width': 1920, 'height': 1080}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()

        for index, row in df_links.iterrows():
            name, url = row.iloc[0], row.iloc[1]
            if "booking.com" not in str(url): continue
            
            print(f"Pracuji na: {name}...")
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.mouse.wheel(0, 1000) # Simulace čtení
                time.sleep(5)
                
                # Celkové skóre
                score = page.locator('[data-testid="review-score-component"]').first.inner_text().split('\n')[0].replace(',', '.')

                # Kategorie (Čistota, Personál, Cena/Kvalita)
                cats = {"Cleanliness": 0, "Staff": 0, "Value": 0}
                cat_elements = page.locator('[data-testid="v2_review_category_score_inner"]').all()
                for el in cat_elements:
                    text = el.inner_text()
                    val = text.split('\n')[-1].replace(',', '.')
                    if "Čistota" in text or "Cleanliness" in text: cats["Cleanliness"] = val
                    if "Personál" in text or "Staff" in text: cats["Staff"] = val
                    if "Poměr" in text or "Value" in text: cats["Value"] = val

                # Textové recenze (pozitivní i negativní)
                review_texts = page.locator('[data-testid="review-card-description"]').all()
                combined_reviews = " | ".join([r.inner_text().replace('\n', ' ') for r in review_texts[:3]])

                results.append({
                    "Datum": time.strftime("%Y-%m-%d"),
                    "Apartman": name,
                    "Celkove": score,
                    "Cistota": cats["Cleanliness"],
                    "Personal": cats["Staff"],
                    "Cena_Kvalita": cats["Value"],
                    "Text_Recenze": combined_reviews if combined_reviews else "Bez textového komentáře"
                })
                print(f"Uloženo: {name} ({score})")
            except Exception as e:
                print(f"Chyba u {name}: {e}")

        browser.close()
    
    if results:
        new_df = pd.DataFrame(results)
        output = 'vysledne_recenze.csv'
        new_df.to_csv(output, mode='a', header=not os.path.exists(output), index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    scrape_booking()
