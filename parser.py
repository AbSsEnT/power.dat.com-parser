import time
from googleSheets import add_load
from webDrivers import chromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException

driver = chromeDriver
wait = WebDriverWait(driver, 30)


def conv_to_num(string):
    """Convert number, containing string, to float type"""
    symbols = ['(', '$', ',', ')']

    for _ in symbols:
        string = string.replace(_, '')

    return float(string)


def set_focus_by_css_selector(css_selector):
    """Set focus on specific area by css selector"""
    driver.find_element_by_css_selector(css_selector).click()
    time.sleep(1)
    driver.find_element_by_css_selector(css_selector).click()


def set_focus_on_certain_object(certain_object):
    """Set focus on specific object"""
    certain_object.click()
    time.sleep(1)
    certain_object.click()


def sign_in(username, password):
    """Sign in"""
    driver.get("https://power.dat.com/login")
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("login").click()


def get_loads_list(pos):
    """Get loads from specific search position"""
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "#filterPanel")))
    search_loads = driver.find_elements_by_css_selector(".searchListTable > .isView")

    if len(search_loads) == 0 or pos > len(search_loads):
        return

    search_loads[pos - 1].click()
    wait.until(ec.invisibility_of_element_located((By.CSS_SELECTOR, "#exactMatchGetNextPageSpinner")))
    time.sleep(2)
    set_focus_by_css_selector(".searchResultsTable")

    loads_num = driver.find_element_by_css_selector('#searchResults > .fixed-table-container-inner > table > thead > '
                                                    '.exactMatchHeader > td').text
    space_pos = loads_num.find(' ')
    loads_num = conv_to_num(loads_num[:space_pos])

    loads_open = 50

    while True:
        loads_open += 50
        driver.find_element_by_tag_name("body").send_keys(Keys.END)
        driver.find_element_by_tag_name("body").send_keys(Keys.ARROW_UP)
        wait.until(ec.invisibility_of_element_located((By.CSS_SELECTOR, "#exactMatchGetNextPageSpinner")))

        if loads_open == 1000 or loads_open > loads_num:
            result_loads = driver.find_elements_by_css_selector(".searchResultsTable > .exactMatch")
            break

    for result_load in result_loads:
        load_data = result_load.find_elements_by_css_selector(".resultSummary > *")

        if load_data[9].text == '—' or load_data[16].text == '—' \
                or "blocked" in result_load.get_attribute("class") \
                or "iscanceledmatch" in result_load.get_attribute("class"):
            continue

        driver.execute_script("arguments[0].scrollIntoView();", result_load)
        result_load.click()

        price_range_css_selector = ".qa-scrollLock > .resultDetails > td > div > div > div > " \
                                   ".widget-numbers > .widget-numbers-range"

        try:
            wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, price_range_css_selector)))
            price_range = result_load.find_element_by_css_selector(price_range_css_selector).text
        except (NoSuchElementException, TimeoutException):
            set_focus_on_certain_object(result_load)
            try:
                wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, price_range_css_selector)))
                price_range = result_load.find_element_by_css_selector(price_range_css_selector).text
            except (NoSuchElementException, TimeoutException):
                continue

        comment1 = driver.find_element_by_css_selector(".qa-scrollLock > .resultDetails > td > dl > .comments1").text
        comment2 = driver.find_element_by_css_selector(".qa-scrollLock > .resultDetails > td > dl > .comments2").text

        van = load_data[5].text
        origin = load_data[8].text
        length = load_data[14].text
        number = load_data[13].text
        weight = load_data[15].text
        company = load_data[12].text
        date_pick = load_data[4].text
        destination = load_data[10].text

        rate = conv_to_num(load_data[16].text)
        trip = conv_to_num(load_data[9].text)

        if '.' in price_range:
            min_price = conv_to_num(price_range[2:6])
            max_price = conv_to_num(price_range[10:14])
        else:
            trip = 1
            space_pos = price_range.find(' ')
            min_price = conv_to_num(price_range[:space_pos])
            max_price = conv_to_num(price_range[space_pos + 3:])

        min_rate = min_price * trip
        max_rate = max_price * trip
        my_rate = rate - max_rate

        add_load([comment1, comment2, " ", number, company, " ", " ", " ", rate, min_rate, max_rate, my_rate, van,
                  length, origin, date_pick, " ", " ", destination, " ", " ", " ", weight, " "])


if __name__ == "__main__":
    driver.maximize_window()

    sign_in("LOGIN", "PASSWORD")
    driver.get("https://power.dat.com/search/loads")

    get_loads_list(int(input("Set the number of the search position you want to parse: ")))

    driver.close()
