import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

# Настройки
base_url = "https://stopgame.ru/user/CoinGH228/games"

status_translation = {
    'beaten': 'Пройдено',
    'sleep': 'Заброшено',
    'playing': 'Играю',
    'wishlist': 'В планах',
    'stopped': 'Дропнул',
}

# 1. Запускаем браузер
print("Запускаю браузер...")
options = Options()
options.add_argument("--log-level=3")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.page_load_strategy = 'eager'
driver = webdriver.Edge(options=options)

try:
    # 2. Открываем страницу входа
    driver.get("https://stopgame.ru/")
    
    # 3. ПАУЗА ДЛЯ РУЧНОГО ВХОДА
    print("\n" + "="*60)
    print("!!! ВНИМАНИЕ !!!")
    print("В открывшемся браузере войди в свой аккаунт StopGame.")
    print("Когда успешно войдешь - вернись сюда.")
    input("Нажми ENTER в этой консоли, чтобы начать сбор данных...")
    print("="*60 + "\n")

    games_list = []
    
    driver.get(base_url)
    time.sleep(2)
    total_pages_s = driver.find_element(By.CSS_SELECTOR, 'div[class*="_description-row"]')
    text = total_pages_s.get_attribute('textContent')
    match = re.search(r'\d+', text)
    total_pages = int(match.group())
    print(f"Найдено страниц: {total_pages}")

    # 4. Начинаем сбор
    for page in range(1, total_pages + 1):
        url = f"{base_url}/p{page}"
        print(f"Обрабатываю страницу {page} из {total_pages}...")
        
        driver.get(url)
        time.sleep(1) # Даем время прогрузиться скриптам

        # Находим все карточки игр
        cards = driver.find_elements(By.CSS_SELECTOR, '[data-game-card]')
        
        if not cards:
            print("Карточки не найдены на этой странице.")
            continue

        for card in cards:
            try:
                # --- Название ---
                title = card.get_attribute("title")
                if not title: title = "Без названия"

                # --- Оценка (считаем звезды) ---
                my_rating = "-"
                try:
                    # Ищем блок с заливкой звезд
                    stars_fill = card.find_element(By.CSS_SELECTOR, 'div[class*="_user-rating__stars__fill_"]')
                    inner_html = stars_fill.get_attribute('innerHTML')
                    
                    full_stars = inner_html.count('href="#fa/star"')     # Целые
                    half_stars = inner_html.count('href="#fa/star-half"') # Половинки
                    
                    score = full_stars + (half_stars * 0.5)
                    if score > 0:
                        my_rating = str(score).replace('.0', '')
                except:
                    pass 

                mark = "-"
                try:
                    mark_fill = card.find_element(By.CSS_SELECTOR, 'button[class*="_stars-button"]')
                    mark_inner_html = mark_fill.get_attribute('innerHTML')
                    if "_heart--active" in mark_inner_html:
                        mark = "❤"
                except:
                    pass

                status = "Не указан"
                try:
                    # 1. Пробуем найти по атрибуту data-game-watch-icon-status
                    status_icon = card.find_element(By.CSS_SELECTOR, '[data-game-watch-icon-status]')
                    raw_status = status_icon.get_attribute('data-game-watch-icon-status')
                    status = status_translation.get(raw_status, raw_status)
                except:
                    pass

                # Формируем строку
                games_list.append(f"{title:<70} | {my_rating:<6} | {status:<9} | {mark:<1}")

            except Exception as e:
                pass

finally:
    driver.quit()

# Сохранение
with open('SG_List.txt', 'w', encoding='utf-8') as f:
    header = f"{'Название игры':<70} | {'Оценка':<6} | {'Статус':<9} | {'Любимая':<1}"
    f.write(header + "\n")
    f.write("-" * 102 + "\n")
    for game in games_list:
        f.write(game + "\n")

print(f"\nГотово! Собрано игр: {len(games_list)}")
print("Проверь файл 'SG_List.txt'")