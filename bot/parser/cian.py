# bot/parser/cian.py
import httpx
from selectolax.parser import HTMLParser
from fake_useragent import UserAgent
from typing import List, Dict
import re
import json

ua = UserAgent(browsers=["chrome"], os="windows")

#Паспорт заголовков для имитации реального браузера
HEADERS = {
    "User-Agent": ua.random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Referer": "https://www.cian.ru/",
}

#Собираем правильную строку, так как сайт часто меняет верстку
async def search_cian(city: str, min_price: int, max_price: int, limit: int = 10) -> List[Dict]:
    city_map = {
        "москва": "1", "москвы": "1",
        "спб": "2", "питер": "2", "петербург": "2",
        "екатеринбург": "3", "екб": "3",
        "новосибирск": "4",
        "казань": "5",
    }
    city_id = city_map.get(city.lower(), "1")

    url = "https://www.cian.ru/cat.php"
    
    #Имитация параметров запроса
    params = {
        "deal_type": "rent",
        "engine_version": "2",
        "offer_type": "flat",
        "region": city_id,
        "minprice": min_price,
        "maxprice": max_price,
        "sort": "creation_date_desc",
        "p": "1",
    }

    #Асинхронный запрос и парсинг
    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            print(f"Загружено {len(response.text)} символов HTML")

            tree = HTMLParser(response.text)

            cards = (
                tree.css("div[data-testid='serp-item']") or
                tree.css("div[class*='offer-card']") or
                tree.css("div[class*='_offerCard']") or
                tree.css("article[class*='serp-item']") or
                tree.css("div a[href*='/rent/flat/']")[:limit * 5]
            )[:limit]

            print(f"Найдено {len(cards)} потенциальных карточек")

            results = []
            for card in cards:
                try:
                    title_node = card.css_first("h6 a, span[data-mark='OfferTitle'], a span") or card.css_first("a")
                    title = title_node.text(strip=True) if title_node else "Квартира в аренду"

                    # ИСПРАВЛЕННАЯ ЦЕНА
                    price_nodes = card.css("span[class*='price'], span[data-mark='MainPrice']")
                    price_text = ""
                    for node in price_nodes:
                        if "₽" in node.text():
                            price_text = node.text(strip=True)
                            break

                    if not price_text:
                        match = re.search(r'(\d{1,3}(?:\s\d{3})*)\s*₽', card.text())
                        if match:
                            price_text = match.group(1).replace(" ", "")
                        else:
                            price_text = "0"

                    price = int(price_text) if price_text.isdigit() else 0

                    link_node = card.css_first("a[href*='/rent/flat/']")
                    href = link_node.attributes.get("href") if link_node else None
                    link = f"https://www.cian.ru{href}" if href and not href.startswith("http") else href

                    img_node = card.css_first("img")
                    photo = img_node.attributes.get("src") or img_node.attributes.get("data-src") if img_node else None

                    if link:
                        results.append({
                            "title": title,
                            "price": price,
                            "link": link,
                            "photo": photo,
                            "source": "ЦИАН"
                        })

                except Exception as e:
                    print(f"Ошибка парсинга карточки: {e}")
                    continue

            # Fallback JSON (без изменений)
            if len(results) < 3:
                scripts = tree.css("script")
                for script in scripts:
                    if "serp-offers" in script.text():
                        try:
                            data_str = script.text().split("serp-offers = ")[1].split(";")[0]
                            data = json.loads(data_str)
                            for offer in data.get("offers", [])[:limit]:
                                results.append({
                                    "title": offer.get("title", "Квартира"),
                                    "price": offer.get("price", 0),
                                    "link": offer.get("url"),
                                    "photo": offer.get("images", [None])[0],
                                    "source": "ЦИАН"
                                })
                        except:
                            pass

            print(f"Парсинг завершён: {len(results)} результатов")
            return results

        except httpx.HTTPStatusError as e:
            print(f"HTTP ошибка: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"Общая ошибка: {e}")
            return []