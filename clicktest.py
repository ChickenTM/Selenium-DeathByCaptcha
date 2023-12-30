from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as UC
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from tempfile import TemporaryDirectory
import time
import deathbycaptcha
import json
import re


# normal chrome driver
driver = webdriver.Chrome(r"chromedriver\\chromedriver.exe")

# ------------undetected chromedriver---------------

# options = webdriver.ChromeOptions()
# options.headless = True
# options.add_argument("--headless")
# options.add_argument("start-maximized")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# Path_to_executable = r"chromedriver\chromedriver.exe"
# serv = Service(Path_to_executable)
# driver = UC.Chrome(r"chromedriver\\chromedriver.exe")
# driver = UC.Chrome(options=options, executable_path="chromedriver\\chromedriver.exe")


# ------------chrome driver stealth--------------
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# path_to_executable = "chromedriver\\chromedriver.exe"
# serv = Service(path_to_executable)
# driver = webdriver.Chrome(options=options, service=serv)
# stealth(driver,
#        languages=["en-US", "en"],
#        vendor="Google Inc.",
#       platform="Win32",
#        webgl_vendor="Intel Inc.",
#        renderer="Intel Iris OpenGL Engine",
#        fix_hairline=True,
#        )


"""-------------urls-----------------
cloudflare - https://www.gasbuddy.com/
image captcha test - https://rod.chippewacountymi.gov/landweb.dll/$/
recaptcha v3 - https://2captcha.com/demo/recaptcha-v3
v3 - https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php
"""
url = "https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php"
step = {
    # "key_xpath" : "/html/body/main/form/fieldset/div[@class='g-recaptcha form-field']",
    # "checkbox_xpath" : '/html/body/table/tbody/tr/td/div/div[1]/table/tbody/tr/td[1]/div[6]/label/input',
    # "checkbox_css" : "#cf-stage > div.ctp-checkbox-container > label > input[type=checkbox]",
    # "iframe_xpath" : '/html/body/div[1]/div/main/div/section/form/div/div/iframe',
    # image test
    "image_xpath": "/html/body/div[2]/form/img",
    "text_xpath": "/html/body/div[2]/form/input[1]",
    "validate_xpath": "/html/body/div[2]/form/input[2]",
    "radio_xpath": "/html/body/div[3]/form/span[1]/input",
    "guest_xpath": "/html/body/div[3]/div[1]/form/input[5]",
    # recaptchav3
    "key_xpath": "/html/head/captcha-widgets/captcha-widget",
    "submit_xpath": "/html/body/div[1]/div/main/div/section/form/button",
    "iframe_xpath": "/html/body/div[3]/div/div[1]/iframe",
}


# element1 = driver.find_element_by_xpath(step["key_xpath"])
# googlekey = element1.get_attribute('data-sitekey')
# print(googlekey)

# element = WebDriverWait(driver,15).until(
#                EC.element_to_be_clickable((By.CSS_SELECTOR, step["checkbox_css"]))
# )
# time.sleep(10)
# iframe= driver.find_element(By.XPATH, step["iframe_xpath"])
# driver.switch_to.frame(iframe)

# element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, step["checkbox_xpath"])))

# element1 = driver.find_element(By.XPATH, step["checkbox_xpath"])
# element1.click()

# DBC Creds
DBC_USERNAME = ""
DBC_PASSWORD = ""

driver.get(url)
# time.sleep(10)

type = "recaptchav3"


client = deathbycaptcha.HttpClient(DBC_USERNAME, DBC_PASSWORD)


if type == "website":
    radio_element = driver.find_element(By.XPATH, step["radio_xpath"])
    radio_element.click()

    guest_element = driver.find_element(By.XPATH, step["guest_xpath"])
    guest_element.click()

    with TemporaryDirectory() as tempdir:
        with open(f"{tempdir}\captcha.png", "wb") as file:
            img = driver.find_element(By.XPATH, step["image_xpath"])
            file.write(img.screenshot_as_png)
        print("Solving captcha...")
        # Calling API
        result = client.decode(f"{tempdir}\captcha.png")

        # Enter solution in text box
        driver.find_element(By.XPATH, step["text_xpath"]).send_keys(result["text"])

        # Click Submit
        validate_button = driver.find_element(By.XPATH, step["validate_xpath"])
        validate_button.click()

elif type == "recaptchav3":
    recaptcha_iframe = driver.find_element(By.XPATH, step["iframe_xpath"])
    # driver.switch_to_frame(recaptcha_iframe)

    src = recaptcha_iframe.get_attribute("src")
    key_match = re.search(r"k=([\w]+)", src)
    if key_match:
        data_sitekey = key_match.group(1)

    # data_sitekey = driver.find_element(By.CSS_SELECTOR, 'div.recaptcha[data-sitekey]').get_attribute('data-sitekey')

    payload = {
        "proxy": "",
        "proxytype": "HTTP",
        "googlekey": data_sitekey,
        "pageurl": driver.current_url,
        "action": "captcha/v3scores",
        "min_score": 0.3,
    }

    json_payload = json.dumps(payload)
    print("Solving captcha...")
    client.is_verbose = True
    # Calling API
    result = client.decode(type=5, token_params=json_payload)
    solution = result.get("text")

    # Click on Check button
    # check_button = driver.find_element(By.XPATH, step["checkbox_xpath"])
    # check_button.click()

    # replace value text with solution in webpage
    # driver.execute_script(
    #         "document.getElementById('g-recaptcha-response').value='%s'" % solution
    #     )

    # Click Submit
    submit_button = driver.find_element(By.XPATH, step["submit_xpath"])
    submit_button.click()
