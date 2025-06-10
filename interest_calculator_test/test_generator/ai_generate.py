import google.generativeai as genai
import PIL.Image
import os
import re

# 推薦方式：請在執行此腳本前，於您的終端機設定環境變數。
#   - macOS / Linux: export GOOGLE_API_KEY="貼上您的金鑰"
#   - Windows (CMD):   set GOOGLE_API_KEY="貼上您的金鑰"
#   - Windows (PowerShell): $env:GOOGLE_API_KEY="貼上您的金鑰"

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except (KeyError, AttributeError):
    print("錯誤：無法讀取 API 金鑰。請確認您已設定 'GOOGLE_API_KEY' 環境變數。")
    exit()

model_instance = genai.GenerativeModel(
       model_name="gemini-2.5-pro-preview-06-05", 
   )

def analyze_ui_and_generate_tests(image_path: str):
    """
    使用 Gemini 分析 UI 截圖並生成 Behave 測試檔案。
    """
    # --- 智慧路徑設定 ---
    # 獲取此腳本所在的目錄 (例如 .../test_generator)
    script_dir = os.path.dirname(__file__)
    # 獲取專案的根目錄 (上一層)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))

    print(f"正在讀取圖片: {image_path}...")
    try:
        img = PIL.Image.open(image_path)
    except FileNotFoundError:
        print(f"錯誤：找不到圖片檔案 '{image_path}'")
        return

    # --- 提示工程 (Prompt Engineering) ---
    prompt = """
    你是一位資深的自動化測試專家，專精於 Python、Behave 和 Selenium。
    你的任務是分析使用者提供的 UI 截圖，並自動生成 BDD (行為驅動開發) 測試檔案。

    請嚴格依照以下步驟執行：

    1.  **分析截圖**:
        * 辨識截圖中的所有 UI 元素，包含：標籤 (label)、輸入框 (input)、按鈕 (button) 和結果顯示區。
        * 從截圖中提取每個輸入框的標籤文字 (例如「本金 (Principal):」) 和其中已填寫的數值 (例如 "10000")。
        * 辨識觸發計算的按鈕文字 (例如 "計算")。
        * 辨識結果的標籤 (例如「總利息:」) 和其顯示的數值 (例如 "$900.00")。

    2.  **生成 .feature 檔案**:
        * 根據分析結果，撰寫一個 Gherkin 場景 (`Scenario`)。
        * 這個場景應該描述使用者的操作流程：Given (在某個頁面)、When (輸入數值並點擊按鈕)、Then (驗證結果是否正確)。
        * 在一個標記為 `FEATURE_FILE` 的標題後，提供一個 `gherkin` 格式的 Markdown 程式碼區塊。
        * 此為範例請依照此格式生成：
        Feature: 簡易利率計算機功能
          Scenario: 計算單利
          Given 我在簡易利率計算機頁面
          When 我輸入本金為 "10000"
          And 我輸入年利率為 "3"
          And 我輸入期間為 "3" 年
          And 我點擊計算按鈕
          Then 計算出的總利息應該是 "$900.00"*

    3.  **生成 step 的 .py 檔案**:
        * 為上述 Gherkin 場景中的每一個步驟 (`Given`, `When`, `Then`) 編寫對應的 Python 實作函式。
        * 使用 `behave` 和 `selenium` 函式庫。
        * 在 @given 步驟的實作中，產生的程式碼必須能找到並打開位於測試執行根目錄下的 'interest_calculator.html' 檔案。請使用 'os.path.abspath' 和 'file://' 協議來建構一個絕對路徑，確保無論從哪個子目錄執行都能正確找到檔案。 
        * 我們需要將每個裝飾器修改為 behave 的參數化語法，使用大括號 {} 將您想傳遞的參數包起來。像下面的：
        * @then('計算出的總利息應該是 "expected_interest"') 的範例
        * **智慧推斷定位器 (Locator)**: 根據元素的標籤文字，推斷出合理的 Selenium 定位器策略。
        * 在一個標記為 `PYTHON_FILE` 的標題後，提供一個 `python` 格式的 Markdown 程式碼區塊。
        * 此py檔的開頭請依照下列生成
        from behave import given, when, then
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import os

        # --- 定位器 (Locators) ---
        H3_HEADER = (By.TAG_NAME, "h3")
        PRINCIPAL_INPUT = (By.NAME, "principal")
        INTEREST_RATE_INPUT = (By.NAME, "interest")
        PERIOD_INPUT = (By.NAME, "period")
        CALCULATE_BUTTON = (By.CSS_SELECTOR, "input[type='submit']")
        TOTAL_INTEREST_RESULT = (By.ID, "total-interest-result")

        # --- 修正: 定義等待時間 (秒) ---
        TIMEOUT = 10
        *

    請開始分析提供的圖片並生成檔案。
    """

    print("正在呼叫 Gemini API 進行分析與生成...")
    model_instance = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model_instance.generate_content([prompt, img])

    if not response.parts:
        print("\n錯誤：API 回應為空。這通常是因為內容觸發了安全設定而被阻擋。")
        if response.prompt_feedback:
            print(f"阻擋原因: {response.prompt_feedback}")
        return

    # --- 處理與儲存檔案 ---
    try:
        full_response_text = response.text
        
        # 修正 #1：使用新的正規表示式來正確解析 Gemini 的回應格式
        # 這個模式會先找到 'FEATURE_FILE' 或 'PYTHON_FILE' 標籤，然後擷取它後方的第一個程式碼區塊
        feature_match = re.search(r"FEATURE_FILE\s*```(?:gherkin)?\s*([\s\S]+?)\s*```", full_response_text, re.IGNORECASE)
        python_match = re.search(r"PYTHON_FILE\s*```(?:python)?\s*([\s\S]+?)\s*```", full_response_text, re.IGNORECASE)

        if not feature_match or not python_match:
            print("\n錯誤：無法從 Gemini 的回應中解析出必要的程式碼區塊。")
            print("--- Gemini 回應原文 ---")
            print(full_response_text)
            return

        feature_content = feature_match.group(1).strip()
        python_content = python_match.group(1).strip()
        
        # 建立 features 資料夾和檔案
        features_dir = "features"
        os.makedirs(features_dir, exist_ok=True)
        feature_filename = os.path.join(features_dir, "generated_test.feature")
        with open(feature_filename, "w", encoding="utf-8") as f:
            f.write(feature_content)
        print(f"成功生成檔案: {feature_filename}")

        # 建立 steps 資料夾和檔案
        steps_dir = "steps"
        os.makedirs(steps_dir, exist_ok=True)
        python_filename = os.path.join(steps_dir, "generated_steps.py")
        with open(python_filename, "w", encoding="utf-8") as f:
            f.write(python_content)
        print(f"成功生成檔案: {python_filename}")

    except Exception as e:
        print(f"\n處理 API 回應時發生錯誤: {e}")
        if 'full_response_text' in locals():
            print("--- Gemini 回應原文 ---")
            print(full_response_text)

if __name__ == "__main__":
    screenshot_path = "ui_screenshot.png"
    analyze_ui_and_generate_tests(screenshot_path)