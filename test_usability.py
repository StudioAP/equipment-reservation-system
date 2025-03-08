from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import random

# テスト結果保存用
test_results = {
    "tests": [],
    "issues": []
}

def log_issue(description, severity="中", component="UI"):
    """問題点を記録する"""
    test_results["issues"].append({
        "description": description,
        "severity": severity,
        "component": component
    })

def log_test(name, result, details=""):
    """テスト結果を記録する"""
    test_results["tests"].append({
        "name": name,
        "result": result,
        "details": details
    })

def run_usability_tests():
    """ユーザビリティテストの実行"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # アプリケーションにアクセス
        driver.get("http://localhost:5003")
        time.sleep(2)
        
        # テスト1: 「新規予約」ボタンのテスト
        test_create_reservation_button(driver)
        
        # テスト2: カレンダー日付選択テスト
        test_calendar_date_selection(driver)
        
        # テスト3: 予約フォーム操作テスト
        test_reservation_form(driver)
        
        # テスト4: サイドバーナビゲーションテスト
        test_sidebar_navigation(driver)
        
        # テスト5: 備品カテゴリフィルタリングテスト
        test_item_category_filtering(driver)
        
        # テスト6: レスポンシブデザインテスト（ウィンドウサイズ変更）
        test_responsive_design(driver)
        
        # テスト7: 予約の作成から削除までの一連の流れテスト
        test_reservation_workflow(driver)
        
    finally:
        # テスト結果の保存
        with open('usability_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=4)
            
        print("ユーザビリティテストが完了しました。結果はusability_test_results.jsonに保存されました。")
        driver.quit()

def test_create_reservation_button(driver):
    """「新規予約」ボタンのテスト"""
    try:
        # サイドバーの「新規予約」ボタンをクリック
        create_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "create-reservation-btn"))
        )
        create_btn.click()
        time.sleep(1)
        
        # 予約フォームが表示されることを確認
        reservation_form = driver.find_element(By.ID, "reservation-form")
        if reservation_form.is_displayed():
            log_test("新規予約ボタンテスト", "成功", "ボタンクリックで予約フォームが正しく表示されました")
        else:
            log_test("新規予約ボタンテスト", "失敗", "ボタンクリックしても予約フォームが表示されません")
            log_issue("「新規予約」ボタンクリック時に予約フォームが表示されない", "高", "予約フォーム")
        
        # キャンセルボタンをクリック
        cancel_btn = driver.find_element(By.ID, "cancel-btn")
        cancel_btn.click()
        time.sleep(1)
        
        # フォームが非表示になることを確認
        if not reservation_form.is_displayed():
            log_test("予約フォームキャンセルテスト", "成功", "キャンセルボタンで予約フォームが閉じました")
        else:
            log_test("予約フォームキャンセルテスト", "失敗", "キャンセルボタンをクリックしても予約フォームが閉じません")
            log_issue("キャンセルボタンクリック時に予約フォームが閉じない", "中", "予約フォーム")
            
    except Exception as e:
        log_test("新規予約ボタンテスト", "エラー", str(e))
        log_issue(f"新規予約ボタンテスト中にエラー: {str(e)}", "高", "予約フォーム")

def test_calendar_date_selection(driver):
    """カレンダー日付選択テスト"""
    try:
        # カレンダーの日付をランダムに選択
        calendar_days = driver.find_elements(By.CSS_SELECTOR, ".calendar-day:not(.other-month)")
        if not calendar_days:
            log_test("カレンダー日付選択テスト", "失敗", "カレンダー日付要素が見つかりません")
            log_issue("カレンダー日付要素が表示されない", "高", "カレンダー")
            return
            
        random_day = random.choice(calendar_days)
        day_number = random_day.find_element(By.CLASS_NAME, "day-number").text
        random_day.click()
        time.sleep(1)
        
        # 日付が選択されたかチェック（選択された日付のクラスが追加されるはず）
        if "selected" in random_day.get_attribute("class"):
            log_test("カレンダー日付選択テスト", "成功", f"{day_number}日をクリックして選択状態になりました")
        else:
            log_test("カレンダー日付選択テスト", "失敗", f"{day_number}日をクリックしましたが選択状態になりません")
            log_issue("カレンダーで日付クリック時に選択状態が視覚的に表示されない", "中", "カレンダー")
        
        # 選択した日付の予約スケジュールが表示されるかチェック
        schedule_container = driver.find_element(By.ID, "schedule-container")
        if schedule_container.is_displayed():
            log_test("予約スケジュール表示テスト", "成功", "日付選択時に予約スケジュールが表示されました")
        else:
            log_test("予約スケジュール表示テスト", "失敗", "日付選択時に予約スケジュールが表示されません")
            log_issue("日付選択時に予約スケジュールが表示されない", "高", "予約スケジュール")
            
    except Exception as e:
        log_test("カレンダー日付選択テスト", "エラー", str(e))
        log_issue(f"カレンダー操作中にエラー: {str(e)}", "高", "カレンダー")

def test_reservation_form(driver):
    """予約フォーム操作テスト"""
    try:
        # 「新規予約」ボタンをクリック
        create_btn = driver.find_element(By.ID, "create-reservation-btn")
        create_btn.click()
        time.sleep(1)
        
        # 各フォーム要素が操作可能か確認
        # 利用者選択
        user_select = driver.find_element(By.ID, "user-select")
        options = user_select.find_elements(By.TAG_NAME, "option")
        if len(options) > 1:  # 「選択してください」以外にオプションがあるか
            options[1].click()  # 最初の実際のオプションを選択
            log_test("利用者選択テスト", "成功", "利用者を選択できました")
        else:
            log_test("利用者選択テスト", "失敗", "選択可能な利用者がありません")
            log_issue("予約フォームに選択可能な利用者がない", "中", "予約フォーム")
        
        # 備品選択
        item_select = driver.find_element(By.ID, "item-select")
        options = item_select.find_elements(By.TAG_NAME, "option")
        if len(options) > 1:
            options[1].click()
            log_test("備品選択テスト", "成功", "備品を選択できました")
        else:
            log_test("備品選択テスト", "失敗", "選択可能な備品がありません")
            log_issue("予約フォームに選択可能な備品がない", "中", "予約フォーム")
        
        # 時間枠選択（連続した時間枠のみ選択）
        time_slots = driver.find_elements(By.CLASS_NAME, "time-slot-checkbox")
        if time_slots:
            time_slots[0].click()  # 最初の時間枠を選択
            time_slots[1].click()  # 2番目の時間枠を選択（連続している）
            
            # 選択状態を確認
            if time_slots[0].is_selected() and time_slots[1].is_selected():
                log_test("時間枠選択テスト", "成功", "時間枠を選択できました")
            else:
                log_test("時間枠選択テスト", "失敗", "時間枠を選択できません")
                log_issue("予約フォームで時間枠が選択できない", "高", "予約フォーム")
        else:
            log_test("時間枠選択テスト", "失敗", "時間枠要素が見つかりません")
            log_issue("予約フォームに時間枠選択欄がない", "高", "予約フォーム")
        
        # フォームをキャンセル
        cancel_btn = driver.find_element(By.ID, "cancel-btn")
        cancel_btn.click()
        time.sleep(1)
        
    except Exception as e:
        log_test("予約フォーム操作テスト", "エラー", str(e))
        log_issue(f"予約フォーム操作中にエラー: {str(e)}", "高", "予約フォーム")

def test_sidebar_navigation(driver):
    """サイドバーナビゲーションテスト"""
    try:
        # 予約カレンダーリンクをクリック
        calendar_link = driver.find_element(By.CSS_SELECTOR, ".sidebar-list li:nth-child(1) a")
        calendar_link.click()
        time.sleep(1)
        
        # カレンダーが表示されていることを確認
        calendar_section = driver.find_element(By.CLASS_NAME, "calendar-section")
        if calendar_section.is_displayed():
            log_test("予約カレンダーリンクテスト", "成功", "予約カレンダーが表示されました")
        else:
            log_test("予約カレンダーリンクテスト", "失敗", "予約カレンダーが表示されません")
            log_issue("予約カレンダーリンクをクリックしてもカレンダーが表示されない", "高", "サイドバー")
        
        # 予約リストリンクをクリック
        reservation_list_link = driver.find_element(By.CSS_SELECTOR, ".sidebar-list li:nth-child(2) a")
        reservation_list_link.click()
        time.sleep(1)
        
        # 予約リストが表示されていることを確認
        reservation_list_view = driver.find_element(By.CLASS_NAME, "reservation-list-view")
        if reservation_list_view.is_displayed():
            log_test("予約リストリンクテスト", "成功", "予約リストが表示されました")
        else:
            log_test("予約リストリンクテスト", "失敗", "予約リストが表示されません")
            log_issue("予約リストリンクをクリックしても予約リストが表示されない", "高", "サイドバー")
        
        # 戻る
        calendar_link.click()
        time.sleep(1)
        
    except Exception as e:
        log_test("サイドバーナビゲーションテスト", "エラー", str(e))
        log_issue(f"サイドバー操作中にエラー: {str(e)}", "高", "サイドバー")

def test_item_category_filtering(driver):
    """備品カテゴリフィルタリングテスト"""
    try:
        # 備品カテゴリリンクがあるか確認
        item_categories = driver.find_elements(By.CSS_SELECTOR, "#item-categories li a")
        
        if not item_categories:
            log_test("備品カテゴリフィルタリングテスト", "失敗", "備品カテゴリが表示されていません")
            log_issue("サイドバーに備品カテゴリが表示されない", "中", "サイドバー")
            return
            
        # 最初のカテゴリをクリック
        item_categories[0].click()
        time.sleep(1)
        
        # フィルター状態が表示されるか確認
        filter_status = driver.find_elements(By.ID, "filter-status")
        if filter_status and filter_status[0].is_displayed():
            log_test("備品カテゴリフィルタリングテスト", "成功", "フィルター状態が表示されました")
        else:
            log_test("備品カテゴリフィルタリングテスト", "失敗", "フィルター状態が表示されません")
            log_issue("備品カテゴリでフィルタリングしてもフィルター状態が表示されない", "中", "フィルタリング")
        
        # フィルターリセットボタンがあれば押下
        reset_buttons = driver.find_elements(By.ID, "reset-filter")
        if reset_buttons:
            reset_buttons[0].click()
            time.sleep(1)
            log_test("フィルターリセットテスト", "成功", "フィルターリセットボタンがクリックできました")
        else:
            log_test("フィルターリセットテスト", "失敗", "フィルターリセットボタンが見つかりません")
            log_issue("フィルターリセットボタンが表示されない", "中", "フィルタリング")
        
    except Exception as e:
        log_test("備品カテゴリフィルタリングテスト", "エラー", str(e))
        log_issue(f"備品カテゴリフィルタリング中にエラー: {str(e)}", "中", "フィルタリング")

def test_responsive_design(driver):
    """レスポンシブデザインテスト"""
    original_size = driver.get_window_size()
    
    try:
        # 小さいウィンドウサイズに変更（モバイル表示）
        driver.set_window_size(375, 667)  # iPhoneサイズ
        time.sleep(1)
        
        # サイドバートグルボタンが表示されるか確認
        sidebar_toggle = driver.find_elements(By.ID, "sidebar-toggle")
        if sidebar_toggle and sidebar_toggle[0].is_displayed():
            log_test("モバイル表示テスト", "成功", "サイドバートグルボタンが表示されました")
            
            # トグルボタンをクリック
            sidebar_toggle[0].click()
            time.sleep(1)
            
            # サイドバーが表示されるか確認
            sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
            if "active" in sidebar.get_attribute("class"):
                log_test("サイドバートグルテスト", "成功", "サイドバートグルでサイドバーが表示されました")
            else:
                log_test("サイドバートグルテスト", "失敗", "サイドバートグルでサイドバーが表示されません")
                log_issue("モバイル表示でサイドバートグルボタンが機能しない", "中", "レスポンシブ")
        else:
            log_test("モバイル表示テスト", "失敗", "サイドバートグルボタンが表示されません")
            log_issue("モバイルサイズでサイドバートグルボタンが表示されない", "中", "レスポンシブ")
        
        # レイアウトが縦に変わるか確認（flex-containerがcolumn方向になる）
        flex_container = driver.find_element(By.CLASS_NAME, "flex-container")
        container_style = driver.execute_script("return window.getComputedStyle(arguments[0]).flexDirection", flex_container)
        
        if container_style == "column":
            log_test("レスポンシブレイアウトテスト", "成功", "モバイル表示で縦並びレイアウトになりました")
        else:
            log_test("レスポンシブレイアウトテスト", "失敗", "モバイル表示で縦並びレイアウトになりません")
            log_issue("モバイルサイズでレイアウトが縦並びに変わらない", "中", "レスポンシブ")
        
    except Exception as e:
        log_test("レスポンシブデザインテスト", "エラー", str(e))
        log_issue(f"レスポンシブデザインテスト中にエラー: {str(e)}", "中", "レスポンシブ")
    finally:
        # 元のウィンドウサイズに戻す
        driver.set_window_size(original_size['width'], original_size['height'])
        time.sleep(1)

def test_reservation_workflow(driver):
    """予約の作成から削除までの一連の流れテスト"""
    try:
        # カレンダーの日付を選択
        calendar_days = driver.find_elements(By.CSS_SELECTOR, ".calendar-day:not(.other-month)")
        if not calendar_days:
            log_test("予約ワークフローテスト", "失敗", "カレンダー日付要素が見つかりません")
            return
            
        random_day = random.choice(calendar_days)
        random_day.click()
        time.sleep(1)
        
        # 「新規予約」ボタンをクリック（詳細セクションの方）
        add_reservation_btn = driver.find_element(By.ID, "add-reservation-btn")
        add_reservation_btn.click()
        time.sleep(1)
        
        # 予約フォームに入力
        # 利用者選択
        user_select = driver.find_element(By.ID, "user-select")
        options = user_select.find_elements(By.TAG_NAME, "option")
        if len(options) > 1:
            options[1].click()
        else:
            log_test("予約ワークフローテスト", "失敗", "選択可能な利用者がありません")
            return
        
        # 備品選択
        item_select = driver.find_element(By.ID, "item-select")
        options = item_select.find_elements(By.TAG_NAME, "option")
        if len(options) > 1:
            options[1].click()
        else:
            log_test("予約ワークフローテスト", "失敗", "選択可能な備品がありません")
            return
        
        # 時間枠選択（連続した時間枠を選択）
        time_slots = driver.find_elements(By.CLASS_NAME, "time-slot-checkbox")
        if time_slots and len(time_slots) >= 2:
            time_slots[0].click()
            time_slots[1].click()
        else:
            log_test("予約ワークフローテスト", "失敗", "時間枠を選択できません")
            return
        
        # フォームを送信 - カスタムメッセージ表示のため直接submitではなくクリックで処理
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)  # 送信処理の完了を待つ
        
        # 予約が作成されたかチェック（スケジュールテーブルに行が追加されるはず）
        schedule_rows = driver.find_elements(By.CSS_SELECTOR, "#schedule-body tr")
        if schedule_rows:
            log_test("予約作成テスト", "成功", "予約が正常に作成されました")
            
            # 作成した予約の削除テスト
            delete_btn = driver.find_elements(By.CSS_SELECTOR, ".delete-btn")
            if delete_btn:
                delete_btn[0].click()
                time.sleep(1)
                
                # 削除確認モーダル
                confirm_delete_btn = driver.find_element(By.ID, "confirm-delete-btn")
                confirm_delete_btn.click()
                time.sleep(2)
                
                # 削除後のスケジュール確認
                new_schedule_rows = driver.find_elements(By.CSS_SELECTOR, "#schedule-body tr")
                if len(new_schedule_rows) < len(schedule_rows):
                    log_test("予約削除テスト", "成功", "予約が正常に削除されました")
                else:
                    log_test("予約削除テスト", "失敗", "予約が削除されていません")
                    log_issue("予約削除後にカレンダー表示が更新されない", "高", "予約管理")
            else:
                log_test("予約削除テスト", "失敗", "削除ボタンが見つかりません")
                log_issue("スケジュール表に削除ボタンがない", "高", "予約管理")
        else:
            log_test("予約作成テスト", "失敗", "予約が作成されていないか、表示されていません")
            log_issue("予約フォーム送信後に予約が作成されない", "高", "予約管理")
        
    except Exception as e:
        log_test("予約ワークフローテスト", "エラー", str(e))
        log_issue(f"予約ワークフロー中にエラー: {str(e)}", "高", "予約管理")

if __name__ == "__main__":
    run_usability_tests() 