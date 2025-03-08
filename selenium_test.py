from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from datetime import datetime, timedelta

# テスト結果を保存するリスト
test_results = {
    "errors": [],
    "warnings": [],
    "suggestions": []
}

def add_error(message, details=None):
    test_results["errors"].append({"message": message, "details": details})

def add_warning(message, details=None):
    test_results["warnings"].append({"message": message, "details": details})

def add_suggestion(message, details=None):
    test_results["suggestions"].append({"message": message, "details": details})

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # ヘッドレスモードを有効化
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_element(driver, by, value, timeout=15):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        add_error(f"要素が見つかりません: {value}", f"タイムアウト {timeout}秒")
        return None

def find_calendar_element(driver):
    """カレンダー要素を複数の方法で探す"""
    try:
        # 複数の方法でカレンダー要素を探す
        selectors = [
            (By.ID, "calendar-grid"),
            (By.CLASS_NAME, "calendar-grid"),
            (By.CSS_SELECTOR, ".calendar"),
            (By.ID, "calendar"),
            (By.CLASS_NAME, "main-content")
        ]
        
        for by, value in selectors:
            try:
                element = driver.find_element(by, value)
                print(f"カレンダー要素が見つかりました: {by}={value}")
                return element
            except NoSuchElementException:
                continue
                
        # DOMの状態をデバッグ
        print("ページの主要要素をデバッグします...")
        body = driver.find_element(By.TAG_NAME, "body")
        print(f"Body要素が存在します: {body is not None}")
        
        try:
            header = driver.find_element(By.TAG_NAME, "header")
            print(f"Header要素が存在します: {header.text[:50] if header else 'なし'}")
        except:
            print("Header要素が見つかりません")
            
        try:
            main_elements = driver.find_elements(By.TAG_NAME, "div")
            print(f"{len(main_elements)}個のdiv要素が見つかりました")
        except:
            print("Div要素が見つかりません")
            
        # HTML全体を取得してデバッグ
        page_source = driver.page_source[:500]  # 最初の500文字だけ表示
        print(f"ページソース (先頭部分):\n{page_source}...")
        
        add_error("カレンダー要素が見つかりません", "複数の方法で検索しましたが見つかりませんでした")
        return None
    except Exception as e:
        add_error("カレンダー要素検索中にエラーが発生しました", str(e))
        return None

def test_calendar_navigation(driver):
    print("カレンダーナビゲーションのテスト中...")
    
    try:
        # 現在の月を取得
        current_month_el = driver.find_element(By.ID, "current-month")
        current_month_text = current_month_el.text
        print(f"現在の月: {current_month_text}")
        
        # 次の月ボタンをクリック
        next_month_btn = driver.find_element(By.ID, "next-month")
        next_month_btn.click()
        time.sleep(2)
        
        # 月が変わったことを確認
        new_month_text = current_month_el.text
        if current_month_text == new_month_text:
            add_error("次の月ボタンが機能していません", f"月表示が変わりませんでした: {current_month_text}")
        else:
            print(f"次の月に移動: {new_month_text}")
            
        # 前の月ボタンをクリック
        prev_month_btn = driver.find_element(By.ID, "prev-month")
        prev_month_btn.click()
        time.sleep(2)
        
        # 元の月に戻ったことを確認
        restored_month_text = current_month_el.text
        if restored_month_text != current_month_text:
            add_error("前の月ボタンが機能していません", f"元の月に戻りませんでした: 元の月={current_month_text}, 現在の月={restored_month_text}")
        else:
            print("前の月に戻りました")
            
        # 今日ボタンをテスト
        try:
            today_btn = driver.find_element(By.ID, "today-btn")
            today_btn.click()
            time.sleep(2)
            print("今日ボタンをクリックしました")
            
            # 今日の日付が選択されているか確認
            try:
                today_cell = driver.find_element(By.CLASS_NAME, "today")
                if today_cell:
                    print("今日の日付が選択されています")
                else:
                    add_warning("今日ボタンが正しく機能していない可能性があります", "今日の日付が選択されていません")
            except NoSuchElementException:
                add_warning("今日の日付セルが見つかりません")
        except NoSuchElementException:
            add_warning("今日ボタンが見つかりません")
    
    except Exception as e:
        add_error("カレンダーナビゲーションテスト中にエラーが発生しました", str(e))

def test_reservation_creation(driver):
    print("予約作成のテスト中...")
    
    try:
        # 今日の日付をクリック
        try:
            today_cell = driver.find_element(By.CLASS_NAME, "today")
            today_cell.click()
            time.sleep(2)
            print("今日の日付をクリックしました")
        except NoSuchElementException:
            add_warning("今日の日付のセルが見つかりません")
            # 任意の日付をクリックする
            cells = driver.find_elements(By.CLASS_NAME, "calendar-day")
            if cells:
                cells[15].click()  # 適当な日付をクリック
                time.sleep(2)
                print("任意の日付をクリックしました")
            else:
                add_error("カレンダーのセルが見つかりません")
                return
        
        # 新規予約ボタンをクリック
        try:
            add_reservation_btn = driver.find_element(By.ID, "add-reservation-btn")
            add_reservation_btn.click()
            time.sleep(2)
            print("新規予約ボタンをクリックしました")
        except NoSuchElementException:
            try:
                create_reservation_btn = driver.find_element(By.ID, "create-reservation-btn")
                create_reservation_btn.click()
                time.sleep(2)
                print("新規予約ボタン(サイドバー)をクリックしました")
            except NoSuchElementException:
                add_error("新規予約ボタンが見つかりません")
                return
        
        # 予約フォームが表示されたことを確認
        form_container = wait_for_element(driver, By.ID, "reservation-form")
        if not form_container or not form_container.is_displayed():
            add_error("予約フォームが表示されていません")
            return
        
        # 利用者を選択
        try:
            user_select = driver.find_element(By.ID, "user-select")
            options = user_select.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:
                options[1].click()  # 最初の実際の選択肢を選ぶ
                print("利用者を選択しました")
            else:
                add_warning("利用者の選択肢がありません")
                
                # 新規利用者を追加
                add_user_btn = driver.find_element(By.ID, "add-user-btn")
                add_user_btn.click()
                time.sleep(2)
                
                # 新規利用者モーダルが表示されたことを確認
                user_modal = wait_for_element(driver, By.ID, "add-user-modal")
                if user_modal and user_modal.is_displayed():
                    new_user_name = driver.find_element(By.ID, "new-user-name")
                    new_user_name.send_keys("テストユーザー")
                    
                    add_user_form = driver.find_element(By.ID, "add-user-form")
                    add_user_form.submit()
                    time.sleep(2)
                    print("新規利用者を追加しました")
                    
                    # アラートを処理
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        time.sleep(2)
                    except:
                        pass
                    
                    # 再度利用者を選択
                    user_select = driver.find_element(By.ID, "user-select")
                    options = user_select.find_elements(By.TAG_NAME, "option")
                    if len(options) > 1:
                        options[1].click()
                    else:
                        add_error("利用者が追加されませんでした")
                        return
                else:
                    add_error("利用者追加モーダルが表示されていません")
                    return
        except Exception as e:
            add_error("利用者選択中にエラーが発生しました", str(e))
            return
        
        # 備品を選択
        try:
            item_select = driver.find_element(By.ID, "item-select")
            options = item_select.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:
                options[1].click()  # 最初の実際の選択肢を選ぶ
                print("備品を選択しました")
            else:
                add_warning("備品の選択肢がありません")
                
                # 新規備品を追加
                add_item_btn = driver.find_element(By.ID, "add-item-btn")
                add_item_btn.click()
                time.sleep(2)
                
                # 新規備品モーダルが表示されたことを確認
                item_modal = wait_for_element(driver, By.ID, "add-item-modal")
                if item_modal and item_modal.is_displayed():
                    new_item_name = driver.find_element(By.ID, "new-item-name")
                    new_item_name.send_keys("テスト備品")
                    
                    add_item_form = driver.find_element(By.ID, "add-item-form")
                    add_item_form.submit()
                    time.sleep(2)
                    print("新規備品を追加しました")
                    
                    # アラートを処理
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        time.sleep(2)
                    except:
                        pass
                    
                    # 再度備品を選択
                    item_select = driver.find_element(By.ID, "item-select")
                    options = item_select.find_elements(By.TAG_NAME, "option")
                    if len(options) > 1:
                        options[1].click()
                    else:
                        add_error("備品が追加されませんでした")
                        return
                else:
                    add_error("備品追加モーダルが表示されていません")
                    return
        except Exception as e:
            add_error("備品選択中にエラーが発生しました", str(e))
            return
        
        # 時間枠を選択
        try:
            time_slot_1 = driver.find_element(By.ID, "time-slot-1")
            time_slot_2 = driver.find_element(By.ID, "time-slot-2")
            
            if not time_slot_1.is_selected():
                time_slot_1.click()
                print("1講時を選択しました")
            
            if not time_slot_2.is_selected():
                time_slot_2.click()
                print("2講時を選択しました")
                
            # 連続していない時間枠を選択して、バリデーションをテスト
            time_slot_4 = driver.find_element(By.ID, "time-slot-4")
            time_slot_4.click()
            print("連続しない3講時を選択しました（バリデーションテスト）")
            
            # アラートを処理
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                if "連続していない時間枠は選択できません" in alert_text:
                    print("連続時間枠バリデーションが正しく機能しています")
                else:
                    add_warning("連続時間枠バリデーションのメッセージが期待通りではありません", f"アラートメッセージ: {alert_text}")
                alert.accept()
                time.sleep(2)
            except:
                add_warning("連続時間枠バリデーションでアラートが表示されませんでした")
                
            # 再度正しい時間枠を選択
            time_slot_1 = driver.find_element(By.ID, "time-slot-1")
            time_slot_2 = driver.find_element(By.ID, "time-slot-2")
            
            if not time_slot_1.is_selected():
                time_slot_1.click()
            
            if not time_slot_2.is_selected():
                time_slot_2.click()
                
        except Exception as e:
            add_error("時間枠選択中にエラーが発生しました", str(e))
            return
        
        # 予約を作成
        try:
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button.primary-btn[type='submit']")
            submit_btn.click()
            time.sleep(2)
            print("予約を作成しました")
            
            # アラートを処理
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                if "予約が完了しました" in alert_text:
                    print("予約が正常に作成されました")
                else:
                    add_warning("予約作成後のメッセージが期待通りではありません", f"アラートメッセージ: {alert_text}")
                alert.accept()
                time.sleep(2)
            except:
                add_warning("予約作成後にアラートが表示されませんでした")
                
        except Exception as e:
            add_error("予約作成中にエラーが発生しました", str(e))
            return
        
        # スケジュール表示が更新されたか確認
        try:
            schedule_table = driver.find_element(By.ID, "schedule-table")
            rows = schedule_table.find_elements(By.TAG_NAME, "tr")
            if len(rows) <= 1:  # ヘッダー行のみ
                add_warning("予約が作成されましたが、スケジュール表に表示されていません")
            else:
                print("スケジュール表に予約が表示されています")
                
            # カレンダー上に予約表示があるか確認
            try:
                reservation_items = driver.find_elements(By.CLASS_NAME, "reservation-item")
                if not reservation_items:
                    add_warning("カレンダー上に予約が表示されていません")
                else:
                    print("カレンダー上に予約が表示されています")
            except NoSuchElementException:
                add_warning("カレンダー上に予約表示が見つかりません")
                
        except Exception as e:
            add_warning("スケジュール表の確認中にエラーが発生しました", str(e))
    
    except Exception as e:
        add_error("予約作成テスト中に予期しないエラーが発生しました", str(e))

def test_reservation_deletion(driver):
    print("予約削除のテスト中...")
    
    try:
        # スケジュール表から削除ボタンを探す
        try:
            delete_btns = driver.find_elements(By.CLASS_NAME, "delete-reservation-btn")
            if not delete_btns:
                add_warning("削除できる予約が見つかりません")
                return
                
            # 最初の削除ボタンをクリック
            delete_btns[0].click()
            time.sleep(1)
            print("削除ボタンをクリックしました")
            
            # 確認モーダルが表示されたか確認
            modal = wait_for_element(driver, By.ID, "confirm-delete-modal")
            if not modal or not modal.is_displayed():
                add_error("削除確認モーダルが表示されていません")
                return
                
            # 削除を確認
            confirm_btn = driver.find_element(By.ID, "confirm-delete-btn")
            confirm_btn.click()
            time.sleep(1)
            print("削除を確認しました")
            
            # アラートを処理
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                if "削除しました" in alert_text:
                    print("予約が正常に削除されました")
                else:
                    add_warning("予約削除後のメッセージが期待通りではありません", f"アラートメッセージ: {alert_text}")
                alert.accept()
                time.sleep(1)
            except:
                add_warning("予約削除後にアラートが表示されませんでした")
                
            # スケジュール表から予約が削除されたか確認
            try:
                no_reservations = driver.find_element(By.ID, "no-reservations")
                if no_reservations.is_displayed():
                    print("予約が正常にスケジュール表から削除されました")
                else:
                    add_warning("予約が削除されましたが、スケジュール表の「予約はありません」メッセージが表示されていません")
            except NoSuchElementException:
                schedule_table = driver.find_element(By.ID, "schedule-table")
                rows = schedule_table.find_elements(By.TAG_NAME, "tr")
                if len(rows) > 1:  # ヘッダー行以外もある
                    add_warning("予約が削除されましたが、スケジュール表から削除されていません")
            
            # カレンダー上から予約表示が削除されたか確認
            try:
                reservation_items = driver.find_elements(By.CLASS_NAME, "reservation-item")
                if reservation_items:
                    add_warning("予約が削除されましたが、カレンダー上の表示が更新されていません")
                else:
                    print("カレンダー上の予約表示も削除されました")
            except:
                pass
                
        except NoSuchElementException:
            add_warning("削除ボタンが見つかりません")
    
    except Exception as e:
        add_error("予約削除テスト中にエラーが発生しました", str(e))

def test_admin_page(driver):
    print("管理者ページのテスト中...")
    
    try:
        # 管理者ページへ移動
        admin_link = driver.find_element(By.XPATH, "//a[contains(text(), '管理者ページ')]")
        admin_link.click()
        time.sleep(2)
        print("管理者ページに移動しました")
        
        # 管理者ページが正しく表示されているか確認
        try:
            admin_heading = driver.find_element(By.XPATH, "//h2[contains(text(), '管理者機能')]")
            print("管理者ページが正しく表示されています")
        except NoSuchElementException:
            add_error("管理者ページが正しく表示されていません")
            return
            
        # サイドバーナビゲーションをテスト
        try:
            sidebar_links = driver.find_elements(By.CSS_SELECTOR, ".sidebar-list a")
            if len(sidebar_links) < 3:
                add_warning("サイドバーに十分なナビゲーションリンクがありません")
            else:
                # 備品管理リンクをクリック
                items_link = driver.find_element(By.XPATH, "//a[contains(text(), '備品管理')]")
                items_link.click()
                time.sleep(1)
                print("備品管理セクションに移動しました")
                
                # データ管理リンクをクリック
                danger_link = driver.find_element(By.XPATH, "//a[contains(text(), 'データ管理')]")
                danger_link.click()
                time.sleep(1)
                print("データ管理セクションに移動しました")
                
                # 利用者管理リンクをクリック
                users_link = driver.find_element(By.XPATH, "//a[contains(text(), '利用者管理')]")
                users_link.click()
                time.sleep(1)
                print("利用者管理セクションに移動しました")
        except NoSuchElementException:
            add_warning("サイドバーナビゲーションが機能していません")
        
        # 利用者テーブルを確認
        try:
            users_table = driver.find_element(By.ID, "users-table")
            users_rows = users_table.find_elements(By.TAG_NAME, "tr")
            if len(users_rows) <= 1:  # ヘッダー行のみ
                add_warning("利用者テーブルにデータがありません")
            else:
                print(f"利用者テーブルに {len(users_rows) - 1} 人の利用者が表示されています")
        except NoSuchElementException:
            add_error("利用者テーブルが見つかりません")
            
        # 備品テーブルを確認
        try:
            items_table = driver.find_element(By.ID, "items-table")
            items_rows = items_table.find_elements(By.TAG_NAME, "tr")
            if len(items_rows) <= 1:  # ヘッダー行のみ
                add_warning("備品テーブルにデータがありません")
            else:
                print(f"備品テーブルに {len(items_rows) - 1} 個の備品が表示されています")
        except NoSuchElementException:
            add_error("備品テーブルが見つかりません")
        
        # トップページに戻る
        try:
            home_link = driver.find_element(By.XPATH, "//a[contains(text(), '予約カレンダー')]")
            home_link.click()
            time.sleep(2)
            print("トップページに戻りました")
            
            # 正しく戻ったか確認
            try:
                calendar_el = driver.find_element(By.ID, "calendar-grid")
                print("カレンダーページが正しく表示されています")
            except NoSuchElementException:
                add_error("トップページに正しく戻っていません")
        except NoSuchElementException:
            add_error("トップページへのリンクが見つかりません")
    
    except Exception as e:
        add_error("管理者ページテスト中にエラーが発生しました", str(e))

def test_responsive_design(driver):
    print("レスポンシブデザインのテスト中...")
    
    # モバイルサイズに設定
    driver.set_window_size(375, 667)  # iPhoneサイズ
    time.sleep(2)
    print("モバイルサイズに変更しました")
    
    try:
        # カレンダーが表示されているか確認
        try:
            calendar_el = driver.find_element(By.ID, "calendar-grid")
            print("モバイルでもカレンダーが表示されています")
        except NoSuchElementException:
            add_error("モバイルでカレンダーが表示されていません")
            
        # サイドバーがどのように表示されるか確認
        try:
            sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
            if sidebar.is_displayed() and sidebar.size['width'] > 100:
                add_warning("モバイルでもサイドバーが大きく表示されており、画面を圧迫しています")
            else:
                print("モバイルでのサイドバー表示は適切です")
        except NoSuchElementException:
            add_warning("モバイルでサイドバーが見つかりません")
            
        # ヘッダーが適切に表示されているか確認
        try:
            header = driver.find_element(By.TAG_NAME, "header")
            header_height = header.size['height']
            if header_height > 100:
                add_warning("モバイルでヘッダーが大きすぎます", f"高さ: {header_height}px")
            else:
                print("モバイルでのヘッダー表示は適切です")
        except NoSuchElementException:
            add_warning("モバイルでヘッダーが見つかりません")
        
        # カレンダーセルの表示を確認
        try:
            calendar_days = driver.find_elements(By.CLASS_NAME, "calendar-day")
            if calendar_days:
                day_width = calendar_days[0].size['width']
                if day_width < 30:
                    add_warning("モバイルでカレンダーセルが小さすぎます", f"幅: {day_width}px")
                else:
                    print("モバイルでのカレンダーセル表示は適切です")
            else:
                add_warning("モバイルでカレンダーセルが見つかりません")
        except:
            add_warning("モバイルでカレンダーセルの確認中にエラーが発生しました")
            
    except Exception as e:
        add_error("レスポンシブデザインテスト中にエラーが発生しました", str(e))
    
    # 元のサイズに戻す
    driver.set_window_size(1920, 1080)
    time.sleep(1)

def additional_observations(driver):
    print("その他の観察事項をチェック中...")
    
    # ロード時間の確認
    try:
        start_time = time.time()
        driver.refresh()
        wait_for_element(driver, By.ID, "calendar-grid")
        end_time = time.time()
        load_time = end_time - start_time
        
        if load_time > 3:
            add_warning(f"ページの読み込みが遅いです ({load_time:.2f}秒)", "パフォーマンス最適化を検討してください")
        else:
            print(f"ページの読み込み時間は適切です ({load_time:.2f}秒)")
    except:
        add_warning("ページの読み込み時間を測定できませんでした")
    
    # 視覚的な一貫性の確認
    try:
        # 色のコントラスト
        calendar_days = driver.find_elements(By.CLASS_NAME, "calendar-day")
        if calendar_days:
            # 背景色と文字色のコントラストをチェック (実際にはできないので観察のみ)
            add_suggestion("色のコントラスト比をチェックして、アクセシビリティ基準を満たしているか確認してください")
            
        # フォントサイズの一貫性
        add_suggestion("さまざまな画面サイズでフォントサイズの一貫性を確認してください")
        
        # 空白のスペース
        add_suggestion("UI要素間の空白スペースの一貫性を確認してください")
    except:
        pass
    
    # ローカライゼーション対応
    add_suggestion("多言語対応が必要な場合は、翻訳ファイルの準備を検討してください")
    
    # モバイルジェスチャー対応
    add_suggestion("モバイルでのスワイプやピンチなどのジェスチャー操作への対応を検討してください")

def run_all_tests():
    driver = setup_driver()
    try:
        # アプリケーションを開く
        driver.get("http://localhost:5001")
        print("アプリケーションを開きました")
        time.sleep(5)  # ページの読み込みを待つ時間を増やす
        
        # カレンダーが表示されるかチェック
        calendar_element = find_calendar_element(driver)
        if not calendar_element:
            print("カレンダー要素が見つかりません。テストを続行できるか確認中...")
        
        # 各テストを実行
        test_calendar_navigation(driver)
        test_reservation_creation(driver)
        test_reservation_deletion(driver)
        test_admin_page(driver)
        test_responsive_design(driver)
        additional_observations(driver)
        
    except Exception as e:
        add_error("テスト実行中に予期しないエラーが発生しました", str(e))
    finally:
        # テスト結果をJSONファイルに保存
        with open("test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
            
        # テスト結果を表示
        print("\n===== テスト結果 =====")
        print(f"エラー: {len(test_results['errors'])}")
        print(f"警告: {len(test_results['warnings'])}")
        print(f"提案: {len(test_results['suggestions'])}")
        
        # ブラウザを閉じる
        driver.quit()
        print("テストが完了しました")

if __name__ == "__main__":
    run_all_tests() 