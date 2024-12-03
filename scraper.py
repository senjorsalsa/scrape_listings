from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import pandas as pd
import openpyxl


def scrape_main(v1, v2, v3, v4):
    if v1.get() == 1:
        b_address, b_rooms, b_prices, b_links = scrape_blocket()
    else:
        b_address, b_rooms, b_prices, b_links = None, None, None, None
    if v2.get() == 1:
        r_address, r_rooms, r_prices, r_links = scrape_riksbyggen()
    else:
        r_address, r_rooms, r_prices, r_links = None, None, None, None
    if v3.get() == 1:
        h_address, h_rooms, h_prices, h_links = scrape_heimstaden()
    else:
        h_address, h_rooms, h_prices, h_links = None, None, None, None
    if v4.get() == 1:
        bs_address, bs_rooms, bs_prices, bs_links = scrape_boplatssyd()
    else:
        bs_address, bs_rooms, bs_prices, bs_links = None, None, None, None

    all_addresses = combine_lists(b_address, r_address, h_address, bs_address)
    all_rooms = combine_lists(b_rooms, r_rooms, h_rooms, bs_rooms)
    all_prices = combine_lists(b_prices, r_prices, h_prices, bs_prices)
    all_links = combine_lists(b_links, r_links, h_links, bs_links)

    df = pd.DataFrame({
        "Adress": all_addresses,
        "Rum": all_rooms,
        "Pris": all_prices,
        "Link": all_links
    })
    curr_time = datetime.now()
    filename = f"result {curr_time.strftime('%Y-%m-%dT%H%M%S')}.xlsx"
    df.to_excel(f"Results\\{filename}", index=False)
    print(f"File saved as {filename}")


# lists can be empty, hence this function, combines lists unless they are None
def combine_lists(list1=None, list2=None, list3=None, list4=None, ):
    lists_to_combine = [lst for lst in [list1, list2, list3, list4] if lst]
    combined_list = [item for sublist in lists_to_combine for item in sublist]

    return combined_list


def scrape_riksbyggen():
    scrape_url = "https://www.riksbyggen.se/hyresratter/skane-lan/trelleborg-kommun/trelleborg/innerstaden/"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(chrome_options)
    driver.get(scrape_url)
    driver.implicitly_wait(4)

    try:
        fact_spans = driver.find_elements(By.CSS_SELECTOR, ".search-result-fact")

        all_rooms = []
        all_prices = []
        current_rok = None

        for fact in fact_spans:
            inner_span = fact.find_element(By.TAG_NAME, 'span')
            if inner_span:
                value = inner_span.text.strip()
                unit = fact.text.replace(value, '').strip()

                if 'rok' in unit:
                    current_rok = f"{value} {unit}"
                elif 'kvm' in unit and current_rok:
                    all_rooms.append(f"{current_rok} | {value} {unit}")
                    current_rok = None
                elif 'kr/mån' in unit:
                    all_prices.append(f"{value} kr")

        all_addresses = []
        all_links = []
        address_divs = driver.find_elements(By.CSS_SELECTOR, ".heading-with-label")
    except NoSuchElementException as e:
        print("No apartments available at Riksbyggen:", e)
        driver.quit()
        return None, None, None, None

    for address_h3 in address_divs:
        h3_tag = address_h3.find_element(By.TAG_NAME, "h3")
        h3_anchor = h3_tag.find_element(By.TAG_NAME, "a")
        all_addresses.append(h3_tag.text.strip())
        all_links.append(h3_anchor.get_attribute("href"))
    driver.quit()
    return all_addresses, all_rooms, all_prices, all_links


def scrape_heimstaden():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    scrape_url = "https://heimstaden.com/se/sok-lagenhet/?text=Trelleborg%2C%20Sverige&display_mode=picture" \
                 "&search_version=1.5&order=&tracking_object_type=Apartment&google_place_id" \
                 "=ChIJf5zvoBtlUUYR5E91QW3RWUU&google_place_type=locality&google_place_name=Trelleborg" \
                 "&number_of_rooms_min=1&number_of_rooms_max=10&rent_min=0&rent_max=26000&size_min=0&size_max=300" \
                 "&properties_true_false%5B%5D=not_student&offset=15"
    driver.get(scrape_url)
    # Heimstaden webpage can be slow at times, implicitly waiting 10 seconds seems to work okay
    driver.implicitly_wait(10)

    try:
        all_links = [anchor.get_attribute("href") for anchor in driver.find_elements(By.CSS_SELECTOR, ".main-img")]

        all_addresses = [adress.text for adress in
                         driver.find_elements(By.CSS_SELECTOR, ".object-teaser-picture-card__content-heading")]
        all_prices = [cost.text.split("/")[0] for cost in
                      driver.find_elements(By.CSS_SELECTOR, ".object-teaser-picture-card__content-pricing")]
        all_rooms = []
        content_listing = driver.find_elements(By.CSS_SELECTOR, ".object-teaser-picture-card__content-list")
    except NoSuchElementException as e:
        print("No apartments available at Heimstaden", e)
        driver.quit()
        return None, None, None, None

    for listing in content_listing:
        li_tag = listing.find_element(By.TAG_NAME, "li")
        all_rooms.append(li_tag.text.split(":")[1].strip())
    driver.quit()
    return all_addresses, all_rooms, all_prices, all_links


def scrape_boplatssyd():
    scrape_url = "https://www.boplatssyd.se/mypages/app/?region=Trelleborg"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(chrome_options)
    driver.get(scrape_url)
    driver.implicitly_wait(4)

    try:
        all_links = [anchor.get_attribute("href") for anchor in
                     driver.find_elements(By.CSS_SELECTOR, ".rental-object__item-title-link")]
        all_addresses = [address.text for address in
                         driver.find_elements(By.CSS_SELECTOR, ".rental-object__item-title-link")]
        all_prices = []
        rooms_temp = []
        all_rooms = []
        properties = driver.find_elements(By.CSS_SELECTOR, ".rental-object__item-properties")
    except NoSuchElementException as e:
        print("No apartments available at Boplats Syd:", e)
        driver.quit()
        return None, None, None, None

    for listing_data in properties:
        all_prices.append(listing_data.text.replace("\n", "").split("•")[-1])
        rooms_temp.append(listing_data.text.replace("\n", "").split("•")[:2])
    for room_data in rooms_temp:
        all_rooms.append(room_data[0] + " | " + room_data[1])

    driver.quit()
    return all_addresses, all_rooms, all_prices, all_links


def scrape_blocket():
    URL = "https://bostad.blocket.se/sv/find-home?searchAreas=Trelleborg~~se"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(chrome_options)

    driver.get(URL)

    driver.implicitly_wait(2)

    try:
        cookie_accept = driver.find_element(By.CSS_SELECTOR, ".qds-13bz2bp")
        cookie_accept.click()
    except NoSuchElementException as e:
        print("No cookies to accept at Blocket:", e)

    try:
        all_cards = driver.find_elements(By.CSS_SELECTOR, ".e1kwthy90.qds-v6u3t0")
        all_address = [card.find_element(By.CSS_SELECTOR, "h2.qds-1k8lqgx").text.title() for card in all_cards]
        all_prices = [card.find_element(By.CSS_SELECTOR, ".qds-y8cht8").text for card in all_cards]
        anchors = driver.find_elements(By.CSS_SELECTOR, "div.qds-atu8yt.e1v66ncn1 a")
        all_links = [anchor.get_attribute("href") for anchor in anchors]

        all_room_sizes_divided = []
        for card in all_cards:
            p_tags = card.find_elements(By.CSS_SELECTOR, ".qds-173zymv p")
            p_texts = [p.text for p in p_tags]
            all_room_sizes_divided.append(p_texts)
    except NoSuchElementException as e:
        print("No apartments available at Blocket:", e)
        driver.quit()
        return None, None, None, None

    all_rooms = [' '.join(sublist) for sublist in all_room_sizes_divided]

    driver.quit()
    return all_address, all_rooms, all_prices, all_links
