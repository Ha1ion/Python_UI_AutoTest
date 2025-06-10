# environment.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from behave import fixture, use_fixture

@fixture
def selenium_browser_chrome(context):
    """
    初始化並設定 Chrome WebDriver。
    """
    # 設定 Chrome 選項，--headless=new 代表在背景執行，不會跳出 UI 視窗
    options = Options()
    #options.add_argument("--headless=new")
    
    # 初始化 WebDriver
    context.driver = webdriver.Chrome(options=options)
    yield context.driver
    
    # 測試結束後的清理動作
    context.driver.quit()
    print("\n===============> Browser is quit")


def before_scenario(context, scenario):
    """
    在每個 Scenario 開始前執行。
    """
    # 呼叫並使用上面定義好的 fixture
    use_fixture(selenium_browser_chrome, context)

    