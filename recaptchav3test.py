import time
import json
import base64
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import deathbycaptcha
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

driver = webdriver.Chrome(r"chromedriver\\chromedriver.exe")

url = "https://2captcha.com/demo/recaptcha-v3"
step = {
    # recaptchav3
    "submit_xpath": "/html/body/div[1]/div/main/div/section/form/button",
    "iframe_xpath": "/html/body/div[3]/div/div[1]/iframe",
}

DBC_USERNAME = ""
DBC_PASSWORD = ""

driver.get(url)
client = deathbycaptcha.HttpClient(DBC_USERNAME, DBC_PASSWORD)

# submit_button = driver.find_element(By.XPATH, "/html/body/main/ol/li[2]/button[2]")
# submit_button.click()

recaptcha_iframe = driver.find_element(By.XPATH, step["iframe_xpath"])
# driver.switch_to_frame(recaptcha_iframe)

src = recaptcha_iframe.get_attribute("src")
key_match = re.search(r"k=([\w]+)", src)
if key_match:
    data_sitekey = key_match.group(1)

# action = driver.execute_script("return arguments[0].action;", driver.find_element(By.TAG_NAME, "script"))

scripts = driver.find_elements(By.TAG_NAME, "script")

for script in scripts:
    script_text = script.get_attribute("text")
    match = re.search(r"\b" + "action" + r"\b\s*:\s*\'?([^,\']+)\'?", script_text)
    if match:
        action = match.group(1)
        break


payload = {
    "proxy": "",
    "proxytype": "HTTP",
    "googlekey": data_sitekey,
    "pageurl": driver.current_url,
    "action": action,
    "min_score": 0.3,
}

json_payload = json.dumps(payload)
print("Solving captcha...")
client.is_verbose = True
# Calling API
result = client.decode(type=5, token_params=json_payload)
solution = result.get("text")


# replace value text with solution in webpage
driver.execute_script(
    "document.getElementsByName('g-recaptcha-response')[0].value='%s'" % solution
)

# Click Submit
submit_button = driver.find_element(By.XPATH, step["submit_xpath"])
submit_button.click()
