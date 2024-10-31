from re import search, sub
from typing import Optional
from itertools import zip_longest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as ChromeOptions


def format_examples(input_str: str, header: Optional[str], body: Optional[str]) -> tuple[str]:
    '''Функция для выделения жирным шрифтом введенной фразы в выдаваемых результатах'''
    if header:
        header = sub(input_str, f"<b>{input_str}</b>", header.text)
    if body:
        body = sub(input_str, f"<b>{input_str}</b>", body.text)

    return (header, body)


def baidu_phrase_parser(input_string: str, chr_options) -> Optional[list[tuple]]:
    '''Функция для поиска точных совпадений с заданной фразой в Baidu'''
    HOME_URL = "https://www.baidu.com/"
    result = []
    
    browser = webdriver.Remote(
    command_executor='http://selenium:4444/wd/hub',
    options=chr_options)
    
    browser.get(HOME_URL)
    search_bar = WebDriverWait(browser, 7).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.s_ipt")))

    search_bar.send_keys(input_string.strip())
    browser.find_element(By.CSS_SELECTOR, "input#su").click()

    WebDriverWait(browser, 7).until(EC.presence_of_element_located((By.XPATH, "//a[em]")))
    
    headers = (header if search(input_string, header.text) else None for header in browser.find_elements(By.XPATH, "//a[em]"))
    bodies = (body if search(input_string, body.text) else None for body in browser.find_elements(By.XPATH, "//span[starts-with(@class, 'content-right')]"))
    
    
    for header, body in zip_longest(headers, bodies):
        try:
            link = header.get_attribute("href")
        except AttributeError:
            continue
        
        examples = format_examples(input_string, header, body)
        
        if any(examples):
            result.append((link, examples))
    
    browser.quit()
    return result if result else None


def run_parser(input_string: str) -> Optional[list[tuple]]:
    '''Функция-интерфейс для запуска парсера'''
    browser_options = ChromeOptions()

# Настройка дополнительных опций для Chrome
    browser_options.add_argument('--headless')
    browser_options.add_argument('--disable-gpu')
    browser_options.add_argument('--no-sandbox')
    browser_options.add_argument('--disable-dev-shm-usage')
    browser_options.add_argument('--disable-background-timer-throttling')
    browser_options.add_argument('--disable-backgrounding-occluded-windows')
    browser_options.add_argument('--disable-breakpad')
    browser_options.add_argument('--disable-client-side-phishing-detection')
    browser_options.add_argument('--disable-default-apps')
    browser_options.add_argument('--disable-extensions')
    browser_options.add_argument('--disable-hang-monitor')
    browser_options.add_argument('--disable-ipc-flooding-protection')
    browser_options.add_argument('--disable-popup-blocking')
    browser_options.add_argument('--disable-prompt-on-repost')
    browser_options.add_argument('--disable-sync')
    browser_options.add_argument('--metrics-recording-only')
    browser_options.add_argument('--no-first-run')
    
    return baidu_phrase_parser(input_string, browser_options)





