import time
import json
import base64
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import deathbycaptcha
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy
from tempfile import TemporaryDirectory

PROXY = "proxy url"
opts = Options()
webdriver.DesiredCapabilities.CHROME["proxy"] = {
    "httpProxy": PROXY,
    "httpsProxy": PROXY,
    "proxyType": "MANUAL",
}

driver = webdriver.Chrome(r"chromedriver\chromedriver.exe", options=opts)

"""-----------captcha test URL's-------------
recaptcha v2 - https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php
recpatcha v3 - https://2captcha.com/demo/recaptcha-v3
image captcha(normal) - https://captcha.com/demos/features/captcha-demo.aspx 
hCaptcha - https://accounts.hcaptcha.com/demo
hcaptcha - https://democaptcha.com/demo-form-eng/hcaptcha.html
geetest - https://2captcha.com/demo/geetest
          https://www.geetest.com/en/demo
geetest V4 - 
funcaptcha - https://nopecha.com/demo/funcaptcha
funcaptcha - https://api.funcaptcha.com/tile-game-lite-mode/fc/api/nojs/?pkey=69A21A01-CC7B-B9C6-0F9A-E7FA06677FFC&lang=en


"""


url = "https://democaptcha.com/demo-form-eng/hcaptcha.html"

# type = "reCaptcha"
step = {
    # recaptcha v2
    "key_xpath": "/html/body/main/form/fieldset/div[@class='g-recaptcha form-field']",
    "checkbox_xpath": "/html/body/main/form/fieldset/div[@class='g-recaptcha form-field']/div/div/iframe",
    "submit_xpath": "/html/body/main/form/fieldset/button",
    # normal captcha
    "image_xpath": "/html/body/div[1]/div[1]/div[1]/form/fieldset[1]/div[1]/div/div[1]/img",
    "validate_xpath": "/html/body/div[1]/div[1]/div[1]/form/fieldset[1]/div[2]/input[2]",
    "text_xpath": "/html/body/div[1]/div[1]/div[1]/form/fieldset[1]/div[2]/input[1]",
    # hCaptcha
    "sitekey_xpath": "/html/body/main/article/div/form/div",
    "hsubmit_xpath": "/html/body/main/article/div/form/input[2]",
    # geetest
    "link_xpath": "/html/head/script[28]",
    # funcaptcha
    "fun_iframe_xpath": "/html/body/div[4]/div/div[2]/iframe",
    "verify_button_xpath": "/html/body/div/form/div/button",
    "api_link_xpath": "/html/body/div/div/div[2]/a",
}

driver.get(url)

# DBC Creds
DBC_USERNAME = ""
DBC_PASSWORD = ""

# DBC Proxy
proxy_host = ""
proxy_port = ""
proxy_user = ""
proxy_pwd = ""

# Check the class of the captcha element to determine the type of captcha
# captcha_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class*='captcha']")))
# captcha_class = captcha_element.get_attribute("class")
# if "g-recaptcha" in captcha_class:
#     type = "reCaptcha"
# elif "h-captcha" in captcha_class:
#     type = "hCaptcha"
# else:
#     type = "normal"

# print("captcha type:", type)

type = "hCaptcha"


def solve_captcha(driver, type, step):
    # Client for API connection
    client = deathbycaptcha.HttpClient(DBC_USERNAME, DBC_PASSWORD)

    if type == "reCaptcha":
        # acquire sitekey from webpage
        element = driver.find_element(By.XPATH, step["key_xpath"])
        googlekey = element.get_attribute("data-sitekey")

        payload = {
            "proxy": "",
            "proxytype": "HTTP",
            "googlekey": googlekey,
            "pageurl": driver.current_url,
        }

        json_payload = json.dumps(payload)
        print("Solving captcha...")
        client.is_verbose = True
        # Calling API
        result = client.decode(type=4, token_params=json_payload)
        solution = result.get("text")

        # Click on Check button
        check_button = driver.find_element(By.XPATH, step["checkbox_xpath"])
        check_button.click()

        # replace value text with solution in webpage
        driver.execute_script(
            "document.getElementById('g-recaptcha-response').value='%s'" % solution
        )

        # Click Submit
        submit_button = driver.find_element(By.XPATH, step["submit_xpath"])
        submit_button.click()

    elif type == "geetest":
        # acquire sitekey from webpage
        # element = driver.find_element(By.LINK_TEXT, "api.geetest.com") #fix this issue, find element by css selector, or xpath with contains[src, "api.geetest.com"]

        time.sleep(5)
        elements = driver.find_elements(By.TAG_NAME, "script")
        for element in elements:
            api_link = element.get_attribute("src")
            if api_link and "api.geetest.com/get.php" in api_link:
                api_string = api_link
                break

        # api_string = element.get_attribute('src')
        gt_match = re.search(r"gt=([\w]+)", api_string)
        if gt_match:
            gt = gt_match.group(1)

        challenge_match = re.search(r"challenge=([\w]+)", api_string)
        if challenge_match:
            challenge = challenge_match.group(1)

        payload = {
            "proxy": "",
            "proxytype": "HTTP",
            "gt": gt,
            "challenge": challenge,
            "pageurl": driver.current_url,
        }

        json_payload = json.dumps(payload)
        print("Solving captcha...")
        client.is_verbose = True
        # Calling API
        result = client.decode(type=8, geetest_params=json_payload)
        # print("type", type(result))
        print(result)

        # solution = result.get('text')

        # Click on Check button
        check_button = driver.find_element(By.XPATH, step["checkbox_xpath"])
        check_button.click()

        # replace value text with solution in webpage
        driver.execute_script(
            "document.getElementById('g-recaptcha-response').value='%s'" % solution
        )

        # Click Submit
        submit_button = driver.find_element(By.XPATH, step["submit_xpath"])
        submit_button.click()

    elif type == "funcaptcha":
        # verify_button = driver.find_element(By.XPATH, step["verify_button_xpath"])
        # verify_button.click()

        # time.sleep(5)

        captcha_link = driver.find_element(By.XPATH, step["api_link_xpath"])
        api_link = captcha_link.get_attribute("href")
        if api_link and "api.funcaptcha.com" in api_link:
            pk_match = re.search(r"pkey=([\w-]+)", api_link)
            if pk_match:
                pk = pk_match.group(1)

        # old method
        """captcha_iframe = driver.find_element(By.XPATH, step["fun_iframe_xpath"])
        api_link = captcha_iframe.get_attribute("src")
        if api_link and "api.funcaptcha.com" in api_link:
            pk_match = re.search(r"pk=([\w-]+)", api_link)
            if pk_match:
                pk = pk_match.group(1)
        """
        payload = {
            "proxy": "",
            "proxytype": "HTTP",
            "publickey": pk,
            "pageurl": driver.current_url,
        }

        json_payload = json.dumps(payload)
        print("Solving captcha...")
        client.is_verbose = True
        # Calling API
        result = client.decode(type=6, funcaptcha_params=json_payload)
        # print("type", type(result))
        print(result)

        solution = result.get("text")

        # Click on Check button
        check_button = driver.find_element(By.XPATH, step["checkbox_xpath"])
        check_button.click()

        # replace value text with solution in webpage
        driver.execute_script(
            "document.getElementById('g-recaptcha-response').value='%s'" % solution
        )

        # Click Submit
        submit_button = driver.find_element(By.XPATH, step["submit_xpath"])
        submit_button.click()

    elif type == "Normal":
        # saving the captcha image
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

    elif type == "hCaptcha":
        element = driver.find_element(By.XPATH, step["sitekey_xpath"])
        sitekey = element.get_attribute("data-sitekey")

        payload = {
            "proxy": "",
            "proxytype": "HTTP",
            "sitekey": sitekey,
            "pageurl": driver.current_url,
        }

        jsonpayload = json.dumps(payload)
        client.is_verbose = True
        result = client.decode(type=7, hcaptcha_params=jsonpayload)

        captcha_response = result.get("text")
        # print(type(result))
        # print(result)

        time.sleep(7)

        # try:
        #     element = WebDriverWait(driver,15).until(
        #         EC.presence_of_element_located((By.XPATH, step["iframe_xpath"]))
        #     )
        #     driver.execute_script("document.querySelector('iframe').setAttribute('data-hcaptcha-response', '%s');" % captcha_response)

        # except:
        #     print("iframe not found")

        driver.execute_script(
            "document.getElementsByName('h-captcha-response')[0].value='%s'"
            % captcha_response
        )

        # Click Submit
        submit_button = driver.find_element(By.XPATH, step["hsubmit_xpath"])
        submit_button.click()

        """#replace value text with solution in webpage
        #captcha_input = driver.find_element(By.NAME, "data-hcaptcha-response")
        #captcha_input.send_keys(solution)
        #driver.execute_script("document.getElementByXpath('%s').data-hcaptcha-response='%s'" % (step["iframe_xpath"], solution))
        
        driver.execute_script()"""

        # Check if success
        # try:
        #     success_element = driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-checkmark").getAttribute("style")
        #     if success_element:
        #       return True
        # except Exception as e:
        #     print("Success message not found: %s" % str(e))
        # return False


solve_captcha(driver, type, step)
