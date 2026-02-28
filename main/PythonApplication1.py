# ♥♥♥♥♥♥♥   ♥♥♥♥♥♥♥♥
# ♥         ♥
# ♥         ♥   ♥♥♥♥♥
# ♥         ♥        ♥
# ♥♥♥♥♥♥♥   ♥♥♥♥♥♥♥♥

import re
import time as t
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exc
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException

# Preferences
base_url = "https://stopgame.ru/user/"
print("Hello, user!")
profile_name = input("Enter your username: ")

status_translation = {
    'beaten': 'Beaten',
    'sleep': 'Dropped',
    'playing': 'Playing',
    'wishlist': 'Wishlist',
}

# 1. Launching browser
print("Launching browser...")
options = Options()
options.add_argument("--log-level=3") #Turning off all browser logs (stupid Edge)
options.add_experimental_option('excludeSwitches', ['enable-logging']) #Turning off all browser logs 2
options.page_load_strategy = 'eager' # Doesn't wait for loading
driver = webdriver.Edge(options=options)
try:
    # 2. Opening site
    driver.get("https://stopgame.ru/")

    t.sleep(2)
    try:
        button = WebDriverWait(driver, 3).until(
            exc.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Войти'], button[class*='profile-btn'], button[class*='auth-btn']"))
        )
        driver.execute_script("arguments[0].click();", button)
    except TimeoutException:
        pass
    except StaleElementReferenceException:
        pass
    
    # 3. Messages and input
    print("\n" + "*"*60)
    print("!!! WARNING !!!")
    print("In browser which appeared, log in your StopGame account.")
    input("Press ENTER when you ready, to begin collecting data...")
    print("*"*60 + "\n")

    games_list = []
    base_url = base_url+profile_name+"/games" # Making profile url
    driver.get(base_url)

    try:
        WebDriverWait(driver, 3).until(
            exc.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="_description-row"]'))
        )
    except ElementNotInteractableException:
        pass
    except TimeoutException:
        pass

    total_pages_s = driver.find_element(By.CSS_SELECTOR, 'div[class*="_description-row"]')
    text = total_pages_s.get_attribute('textContent')
    match = re.search(r'\d+', text)
    total_pages = int(match.group())
    print(f"Founded pages: {total_pages}")

    # 4. Начинаем сбор
    try:
        with tqdm(total=total_pages, desc="Processing pages", colour="blue") as pbar:
            for page in range(1, total_pages + 1):
                url = f"{base_url}/p{page}"
                pbar.update(1) # Updating pbar

                driver.get(url)
                # Taking some time
                try:
                    WebDriverWait(driver, 3).until(
                        exc.visibility_of_element_located((By.CSS_SELECTOR, '[data-game-card]'))
                    )
                except ElementNotInteractableException:
                    pass
                except TimeoutException:
                    pass

                # Finding all cards
                cards = driver.find_elements(By.CSS_SELECTOR, '[data-game-card]')

                if not cards:
                    print("Page are empty!.")
                    continue

                for card in cards:
                    try:
                        # --- Name ---
                        title = card.get_attribute("title")
                        if not title: title = "Unnamed"

                        # --- Grade (counting stars) ---
                        my_rating = "-"
                        try:
                            # Ищем блок с заливкой звезд
                            stars_fill = card.find_element(By.CSS_SELECTOR, 'div[class*="_user-rating__stars__fill_"]')
                            inner_html = stars_fill.get_attribute('innerHTML')

                            full_stars = inner_html.count('href="#fa/star"')     # Full
                            half_stars = inner_html.count('href="#fa/star-half"') # Half

                            score = full_stars + (half_stars * 0.5)
                            if score > 0:
                                my_rating = str(score).replace('.0', '')
                        except NoSuchElementException:
                            pass

                        mark = "-"
                        try:
                            mark_fill = card.find_element(By.CSS_SELECTOR, 'button[class*="_stars-button"]')
                            mark_inner_html = mark_fill.get_attribute('innerHTML')
                            if "_heart--active" in mark_inner_html:
                                mark = "❤"
                        except NoSuchElementException:
                            pass

                        status = "Not assigned"
                        try:
                            # 1. Trying to find by attribute data-game-watch-icon-status
                            status_icon = card.find_element(By.CSS_SELECTOR, '[data-game-watch-icon-status]')
                            raw_status = status_icon.get_attribute('data-game-watch-icon-status')
                            status = status_translation.get(raw_status, raw_status)
                        except NoSuchElementException:
                            pass

                        # Forming string
                        games_list.append(f"{title:<70} | {my_rating:<6} | {status:<9} | {mark:<1}")

                    except Exception:
                        pass

    except KeyboardInterrupt:
        print("\n\n[!] Parsing was interrupted manually!")
    except Exception as e:
        print(f"\n\n[!] Error: {e}")

finally:
    driver.quit()

# Saving
with open('SG_List.txt', 'w', encoding='utf-8') as f:
    header = f"{'Game name':<70} | {'Grade':<6} | {'Status':<9} | {'Favourite':<1}"
    f.write(header + "\n")
    f.write("-" * 102 + "\n")
    for game in games_list:
        f.write(game + "\n")

print(f"\nDone! Collected {len(games_list)} games!\nCheck 'SG_List.txt' file!\nMade by CoinGH :)")