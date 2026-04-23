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
        context = browser.new_context(user_agent="Mozilla/5.0 ...")
        page = context.new_page()

        for index, row in df_links.iterrows():
            name, url = row.iloc[0], row.iloc[1]
            if pd.isna(url) or "booking.com" not in str(url): continue
            
            print(f"Detailní scraping: {name}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(5)
                
                # Celkové hodnocení
                score = page.locator('[data-testid="review-score-component"]').first.inner_text().split('\n')[0]
                
                # Pokus o získání kategorií (úklid, personál...)
                # Booking má tyto hodnoty v malých kartách
                categories = {"Cistota": 0, "Personal": 0, "Lokalita": 0}
                
                rows = page.locator('[data-testid="v2_review_category_score_inner"]').all()
                for r in rows:
                    text = r.inner_text()
                    if "Čistota" in text: categories["Cistota"] = text.split('\n')[-1]
                    if "Personál" in text: categories["Personal"] = text.split('\n')[-1]
                    if "Lokalita" in text: categories["Lokalita"] = text.split('\n')[-1]

                results.append({
                    "Datum": time.strftime("%Y-%m-%d"),
                    "Apartman": name,
                    "Celkove": score.replace(',', '.'),
                    "Uklid": str(categories["Cistota"]).replace(',', '.'),
                    "Personal": str(categories["Personal"]).replace(',', '.'),
                    "Lokalita": str(categories["Lokalita"]).replace(',', '.'),
                    "Platforma": "Booking"
                })
            except Exception as e:
                print(f"Chyba u {name}: {e}")

        browser.close()
    
    if results:
        new_data = pd.DataFrame(results)
        output_file = 'vysledne_recenze.csv'
        header = not os.path.exists(output_file)
        new_data.to_csv(output_file, mode='a', header=header, index=False)

if __name__ == "__main__":
    scrape_booking()
