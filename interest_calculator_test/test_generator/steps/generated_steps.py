from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium import webdriver

# --- 定位器 (Locators) ---
H3_HEADER = (By.TAG_NAME, "h3")
PRINCIPAL_INPUT = (By.NAME, "principal")
INTEREST_RATE_INPUT = (By.NAME, "interest")
PERIOD_INPUT = (By.NAME, "period")
CALCULATE_BUTTON = (By.CSS_SELECTOR, "input[type='submit']")
TOTAL_INTEREST_RESULT = (By.ID, "total-interest-result")

# --- 修正: 定義等待時間 (秒) ---
TIMEOUT = 10

@given('我在簡易利率計算機頁面')
def step_impl(context):
    # 使用 os.path.abspath 建構絕對路徑
    file_path = os.path.abspath('interest_calculator.html')
    url = 'file://' + file_path
    context.driver = webdriver.Chrome()  # 或者其他瀏覽器
    context.driver.get(url)
    WebDriverWait(context.driver, TIMEOUT).until(
        EC.presence_of_element_located(H3_HEADER)
    )

@when('我輸入本金為 "{principal}"')
def step_impl(context, principal):
    principal_input = WebDriverWait(context.driver, TIMEOUT).until(
        EC.presence_of_element_located(PRINCIPAL_INPUT)
    )
    principal_input.send_keys(principal)


@when('我輸入年利率為 "{interest_rate}"')
def step_impl(context, interest_rate):
    interest_rate_input = WebDriverWait(context.driver, TIMEOUT).until(
        EC.presence_of_element_located(INTEREST_RATE_INPUT)
    )
    interest_rate_input.send_keys(interest_rate)

@when('我輸入期間為 "{period}" 年')
def step_impl(context, period):
    period_input = WebDriverWait(context.driver, TIMEOUT).until(
        EC.presence_of_element_located(PERIOD_INPUT)
    )
    period_input.send_keys(period)

@when('我點擊計算按鈕')
def step_impl(context):
    calculate_button = WebDriverWait(context.driver, TIMEOUT).until(
        EC.element_to_be_clickable(CALCULATE_BUTTON)
    )
    calculate_button.click()

@then('計算出的總利息應該是 "{expected_interest}"')
def step_impl(context, expected_interest):
    total_interest_result = WebDriverWait(context.driver, TIMEOUT).until(
        EC.presence_of_element_located(TOTAL_INTEREST_RESULT)
    )
    actual_interest = total_interest_result.text
    assert actual_interest == expected_interest, f"Expected {expected_interest}, but got {actual_interest}"
    context.driver.quit()  # 關閉瀏覽器