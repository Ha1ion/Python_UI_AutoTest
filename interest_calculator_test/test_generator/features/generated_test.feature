Feature: 簡易利率計算機功能
  Scenario: 計算單利
    Given 我在簡易利率計算機頁面
    When 我輸入本金為 "10000"
    And 我輸入年利率為 "3"
    And 我輸入期間為 "3" 年
    And 我點擊計算按鈕
    Then 計算出的總利息應該是 "$900.00"