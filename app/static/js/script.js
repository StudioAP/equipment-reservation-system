document.addEventListener('DOMContentLoaded', function() {
    // 現在の日付を取得
    const today = new Date();
    let currentMonth = today.getMonth();
    let currentYear = today.getFullYear();
    
    // 選択された日付
    let selectedDate = null;
    
    // 予約データのキャッシュ
    let reservationsCache = {};
    
    // 削除対象の予約ID
    let reservationToDelete = null;
    
    // 現在のフィルター状態
    let currentFilter = {
        type: null,
        id: null
    };
    
    // DOM要素
    const calendarGridEl = document.getElementById('calendar-grid');
    const currentMonthEl = document.getElementById('current-month');
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const todayBtn = document.getElementById('today-btn');
    const reservationFormEl = document.getElementById('reservation-form');
    const scheduleContainerEl = document.getElementById('schedule-container');
    const scheduleDateEl = document.getElementById('schedule-date');
    const scheduleBodyEl = document.getElementById('schedule-body');
    const noReservationsEl = document.getElementById('no-reservations');
    const selectedDateInput = document.getElementById('selected-date');
    const userSelectEl = document.getElementById('user-select');
    const itemSelectEl = document.getElementById('item-select');
    const addReservationBtn = document.getElementById('add-reservation-btn');
    const createReservationBtn = document.getElementById('create-reservation-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const createReservationForm = document.getElementById('create-reservation-form');
    const timeSlotCheckboxes = document.querySelectorAll('.time-slot-checkbox');
    const itemCategoriesEl = document.getElementById('item-categories');
    
    // モーダル関連
    const addUserBtn = document.getElementById('add-user-btn');
    const addItemBtn = document.getElementById('add-item-btn');
    const addUserModal = document.getElementById('add-user-modal');
    const addItemModal = document.getElementById('add-item-modal');
    const confirmDeleteModal = document.getElementById('confirm-delete-modal');
    const addUserForm = document.getElementById('add-user-form');
    const addItemForm = document.getElementById('add-item-form');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const closeButtons = document.querySelectorAll('.close');
    
    // サイドバートグル機能
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    // サイドバーオーバーレイを作成
    const sidebarOverlay = document.createElement('div');
    sidebarOverlay.className = 'sidebar-overlay';
    document.body.appendChild(sidebarOverlay);
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation(); // イベント伝播を停止
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
        });
        
        // オーバーレイクリックでサイドバーを閉じる
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        });
        
        // サイドバー内のリンククリック時にモバイル表示ではサイドバーを閉じる
        const sidebarLinks = sidebar.querySelectorAll('a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    sidebar.classList.remove('active');
                    sidebarOverlay.classList.remove('active');
                }
            });
        });
    }
    
    // ウィンドウリサイズ時にサイドバーの状態を調整
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            // デスクトップ表示時はサイドバーを表示
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        }
    });
    
    // ガイダンスモーダル関連
    const guidanceModal = document.getElementById('guidance-modal');
    const guidanceCloseBtn = document.getElementById('guidance-close-btn');
    const dontShowAgainCheckbox = document.getElementById('dont-show-again');
    
    // サイドバーナビゲーション要素
    const calendarLink = document.querySelector('.sidebar-list li:nth-child(1) a');
    const reservationListLink = document.querySelector('.sidebar-list li:nth-child(2) a');
    
    // サイドバーのコンテンツ表示領域
    const calendarView = document.querySelector('.calendar-header').parentElement;
    const reservationListView = document.createElement('div');
    reservationListView.className = 'reservation-list-view';
    reservationListView.style.display = 'none';
    // 予約リストビューを親要素に追加
    if (calendarView.parentElement) {
        calendarView.parentElement.appendChild(reservationListView);
    }
    
    // ガイダンスモーダルの表示判定
    // 開発中は常に表示しないように設定
    localStorage.setItem('guidanceShown', 'true');
    
    if (!localStorage.getItem('guidanceShown')) {
        showGuidance();
    } else {
        // ガイダンスモーダルを非表示にする
        if (guidanceModal) {
            guidanceModal.style.display = 'none';
        }
    }
    
    // ガイダンスモーダルのイベントリスナー
    if (guidanceCloseBtn) {
        guidanceCloseBtn.addEventListener('click', function() {
            if (dontShowAgainCheckbox.checked) {
                localStorage.setItem('guidanceShown', 'true');
            }
            guidanceModal.style.display = 'none';
        });
    }
    
    // カレンダーの初期化
    renderCalendar(currentMonth, currentYear);
    
    // 初期データ取得
    fetchUsers();
    fetchItems();
    
    // 備品カテゴリのイベントハンドラを初期化
    setupItemCategoryHandlers();
    
    // イベントリスナーの設定
    prevMonthBtn.addEventListener('click', function() {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar(currentMonth, currentYear);
    });
    
    nextMonthBtn.addEventListener('click', function() {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar(currentMonth, currentYear);
    });
    
    todayBtn.addEventListener('click', function() {
        currentMonth = today.getMonth();
        currentYear = today.getFullYear();
        renderCalendar(currentMonth, currentYear);
        
        // 今日の日付を選択
        const todayStr = formatDate(today);
        selectDate(todayStr);
    });
    
    addReservationBtn.addEventListener('click', function() {
        showReservationForm();
    });
    
    createReservationBtn.addEventListener('click', function() {
        if (selectedDate) {
            showReservationForm();
        } else {
            // 今日の日付を選択
            const todayStr = formatDate(today);
            selectDate(todayStr);
            showReservationForm();
        }
    });
    
    cancelBtn.addEventListener('click', function() {
        hideReservationForm();
        // スケジュール表示を表示
        scheduleContainerEl.style.display = 'block';
    });
    
    createReservationForm.addEventListener('submit', function(e) {
        e.preventDefault();
        createReservation();
    });
    
    // モーダル関連のイベントリスナー
    addUserBtn.addEventListener('click', function() {
        addUserModal.style.display = 'block';
    });
    
    addItemBtn.addEventListener('click', function() {
        addItemModal.style.display = 'block';
    });
    
    addUserForm.addEventListener('submit', function(e) {
        e.preventDefault();
        addUser();
    });
    
    addItemForm.addEventListener('submit', function(e) {
        e.preventDefault();
        addItem();
    });
    
    confirmDeleteBtn.addEventListener('click', function() {
        if (reservationToDelete) {
            deleteReservation(reservationToDelete);
        }
    });
    
    cancelDeleteBtn.addEventListener('click', function() {
        confirmDeleteModal.style.display = 'none';
    });
    
    closeButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            addUserModal.style.display = 'none';
            addItemModal.style.display = 'none';
            confirmDeleteModal.style.display = 'none';
        });
    });
    
    // 時間枠チェックボックスのイベントリスナー
    timeSlotCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const selectedSlots = Array.from(timeSlotCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => parseInt(cb.value));
            
            if (selectedSlots.length > 1) {
                // 選択された時間枠をソート
                selectedSlots.sort((a, b) => a - b);
                
                // 連続しているかチェック
                for (let i = 0; i < selectedSlots.length - 1; i++) {
                    if (selectedSlots[i + 1] - selectedSlots[i] !== 1) {
                        showMessage('連続していない時間枠は選択できません。', 'error');
                        
                        // このチェックボックスの選択を解除
                        this.checked = false;
                        return;
                    }
                }
            }
        });
    });
    
    // サイドバーナビゲーションのイベントリスナー
    if (calendarLink) {
        calendarLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // アクティブクラスの切り替え
            document.querySelectorAll('.sidebar-list a').forEach(item => {
                item.classList.remove('active');
            });
            this.classList.add('active');
            
            // ビューの切り替え
            calendarView.style.display = 'block';
            reservationListView.style.display = 'none';
            
            // フィルターをリセット
            resetFilter();
        });
    }
    
    if (reservationListLink) {
        reservationListLink.addEventListener('click', function(e) {
            e.preventDefault();
            
            // アクティブクラスの切り替え
            document.querySelectorAll('.sidebar-list a').forEach(item => {
                item.classList.remove('active');
            });
            this.classList.add('active');
            
            // ビューの切り替え
            calendarView.style.display = 'none';
            reservationListView.style.display = 'block';
            
            // 予約リストを表示
            showReservationList();
        });
    }
    
    // 備品カテゴリのイベントハンドラを設定する関数
    function setupItemCategoryHandlers() {
        setTimeout(() => {
            document.querySelectorAll('.item-category').forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    const itemId = this.getAttribute('data-id');
                    console.log('備品カテゴリがクリックされました: ' + itemId);
                    
                    // アクティブクラスの切り替え
                    document.querySelectorAll('.item-category').forEach(el => {
                        el.classList.remove('active');
                    });
                    this.classList.add('active');
                    
                    // 備品IDでフィルタリング
                    filterByItemId(itemId);
                });
            });
        }, 500); // DOMの更新が確実に完了するまで少し待つ
    }
    
    // 備品IDでフィルタリングする関数
    function filterByItemId(itemId) {
        currentFilter.type = 'item';
        currentFilter.id = itemId;
        
        // フィルター状態を表示
        updateFilterStatus();
        
        // 現在の表示に応じて適切な処理を行う
        if (calendarView.style.display !== 'none') {
            // カレンダー表示の場合
            updateCalendarWithFilter();
        } else {
            // 予約リスト表示の場合
            showReservationList();
        }
    }
    
    // フィルターをリセットする関数
    function resetFilter() {
        currentFilter.type = null;
        currentFilter.id = null;
        
        // 備品カテゴリのアクティブ状態をリセット
        document.querySelectorAll('.item-category').forEach(el => {
            el.classList.remove('active');
        });
        
        // フィルター状態を更新
        updateFilterStatus();
        
        // 現在のビューを更新
        if (calendarView.style.display !== 'none') {
            updateCalendarWithFilter();
        } else {
            showReservationList();
        }
    }
    
    // フィルター状態を表示する関数
    function updateFilterStatus() {
        // フィルター状態表示要素
        let filterStatusEl = document.getElementById('filter-status');
        
        // 存在しない場合は作成
        if (!filterStatusEl) {
            filterStatusEl = document.createElement('div');
            filterStatusEl.id = 'filter-status';
            filterStatusEl.className = 'filter-status';
            
            // カレンダーヘッダーの下に追加
            const calendarHeader = document.querySelector('.calendar-header');
            if (calendarHeader && calendarHeader.parentNode) {
                calendarHeader.parentNode.insertBefore(filterStatusEl, calendarHeader.nextSibling);
            }
        }
        
        // フィルターがない場合
        if (!currentFilter.type) {
            filterStatusEl.style.display = 'none';
            return;
        }
        
        // フィルター状態を表示
        filterStatusEl.style.display = 'block';
        
        if (currentFilter.type === 'item') {
            // 備品名を取得
            const itemEl = document.querySelector(`.item-category[data-id="${currentFilter.id}"]`);
            const itemName = itemEl ? itemEl.textContent.trim() : '選択された備品';
            
            filterStatusEl.innerHTML = `
                <div class="filter-info">
                    <span>フィルター: ${itemName}</span>
                    <button id="reset-filter" title="フィルターをリセット">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            
            // リセットボタンにイベントリスナーを設定
            document.getElementById('reset-filter').addEventListener('click', resetFilter);
        }
    }
    
    // フィルターを適用したカレンダー表示を更新する関数
    function updateCalendarWithFilter() {
        // フィルターがない場合は通常のカレンダー表示
        if (!currentFilter.type) {
            renderCalendar(currentMonth, currentYear);
            return;
        }
        
        // フィルターがある場合、カレンダーの各日付の予約を更新
        const calendarDays = document.querySelectorAll('.calendar-day:not(.other-month)');
        
        calendarDays.forEach(day => {
            const dayContent = day.querySelector('.day-content');
            if (!dayContent) return;
            
            const dateStr = dayContent.getAttribute('data-date');
            if (!dateStr) return;
            
            // この日付の予約を取得
            fetch(`/api/reservations?date=${dateStr}`)
                .then(response => response.json())
                .then(data => {
                    // フィルターを適用
                    const filteredReservations = data.reservations.filter(res => {
                        if (currentFilter.type === 'item') {
                            return res.item_id == currentFilter.id;
                        }
                        return true;
                    });
                    
                    // フィルターされた予約で表示を更新
                    updateCalendarReservations(dateStr, filteredReservations);
                })
                .catch(error => console.error('Error updating calendar with filter:', error));
        });
    }
    
    // 予約リストビューを表示する関数
    function showReservationList() {
        // カレンダーとスケジュール表示を非表示
        calendarView.style.display = 'none';
        
        // 予約フォームも非表示
        reservationFormEl.style.display = 'none';
        
        // 予約リストビューを表示
        reservationListView.style.display = 'block';
        reservationListView.innerHTML = '<h2>予約リスト</h2><div class="loading-spinner">読み込み中...</div>';
        
        // すべての予約を取得
        fetch('/api/reservations/all')
            .then(response => response.json())
            .then(data => {
                let html = '<h2>予約リスト</h2>';
                
                if (!data.reservations || data.reservations.length === 0) {
                    html += '<div class="no-data">予約はありません</div>';
                    reservationListView.innerHTML = html;
                    return;
                }
                
                // フィルターを適用
                let filteredReservations = data.reservations;
                if (currentFilter.type === 'item') {
                    filteredReservations = data.reservations.filter(res => res.item_id == currentFilter.id);
                }
                
                if (filteredReservations.length === 0) {
                    html += '<div class="no-data">条件に一致する予約はありません</div>';
                    reservationListView.innerHTML = html;
                    return;
                }
                
                // 予約リストを表示
                html += '<div class="reservation-list-container">';
                html += '<table class="reservation-table">';
                html += '<thead><tr><th>日付</th><th>時間帯</th><th>備品</th><th>利用者</th><th>操作</th></tr></thead>';
                html += '<tbody>';
                
                filteredReservations.forEach(reservation => {
                    const date = new Date(reservation.date);
                    const formattedDate = formatDateJP(date);
                    
                    // 時間枠の名前
                    const timeSlotNames = {
                        '1': '1講時 (8:50-10:20)',
                        '2': '2講時 (10:30-12:00)',
                        '3': '昼休み (12:00-13:00)',
                        '4': '3講時 (13:00-14:30)',
                        '5': '4講時 (14:40-16:10)',
                        '6': '5講時 (16:20-17:50)',
                        '7': '6講時 (18:00-19:30)'
                    };
                    
                    const timeSlots = reservation.time_slots.split(',');
                    let timeText = '';
                    
                    if (timeSlots.length > 1) {
                        timeText = `${timeSlotNames[timeSlots[0].trim()].split(' ')[0]} 〜 ${timeSlotNames[timeSlots[timeSlots.length - 1].trim()].split(' ')[0]}`;
                    } else {
                        timeText = timeSlotNames[timeSlots[0].trim()].split(' ')[0];
                    }
                    
                    html += `<tr>`;
                    html += `<td>${formattedDate}</td>`;
                    html += `<td>${timeText}</td>`;
                    html += `<td>${reservation.item_name}</td>`;
                    html += `<td>${reservation.user_name}</td>`;
                    html += `<td><button class="delete-btn" data-id="${reservation.id}">削除</button></td>`;
                    html += `</tr>`;
                });
                
                html += '</tbody></table></div>';
                reservationListView.innerHTML = html;
                
                // 削除ボタンのイベントリスナーを設定
                reservationListView.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const id = this.getAttribute('data-id');
                        showDeleteConfirmation(id);
                    });
                });
            })
            .catch(error => {
                console.error('Error fetching reservations:', error);
                reservationListView.innerHTML = '<h2>予約リスト</h2><div class="error">予約の取得に失敗しました</div>';
            });
    }
    
    // カレンダーをレンダリングする関数
    function renderCalendar(month, year) {
        // 月の最初の日を取得
        const firstDay = new Date(year, month, 1);
        // 月の最後の日を取得
        const lastDay = new Date(year, month + 1, 0);
        
        // 月の名前を設定
        const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
        currentMonthEl.textContent = `${year}年${monthNames[month]}`;
        
        // カレンダーグリッドをクリア
        calendarGridEl.innerHTML = '';
        
        // 最初の行の空白を埋める
        let date = 1;
        let dayOfWeek = firstDay.getDay();
        
        // 前月の日付を取得
        const prevMonthLastDay = new Date(year, month, 0).getDate();
        
        // 前月の日付を表示
        for (let i = 0; i < dayOfWeek; i++) {
            const prevDate = prevMonthLastDay - (dayOfWeek - i - 1);
            const prevMonth = month === 0 ? 11 : month - 1;
            const prevYear = month === 0 ? year - 1 : year;
            const dateStr = formatDate(new Date(prevYear, prevMonth, prevDate));
            
            const dayEl = document.createElement('div');
            dayEl.className = 'calendar-day other-month';
            dayEl.innerHTML = `
                <div class="day-number">${prevDate}</div>
                <div class="day-content" data-date="${dateStr}"></div>
            `;
            calendarGridEl.appendChild(dayEl);
        }
        
        // 当月の日付を表示
        while (date <= lastDay.getDate()) {
            const currentDate = new Date(year, month, date);
            const dateStr = formatDate(currentDate);
            
            const dayEl = document.createElement('div');
            dayEl.className = 'calendar-day';
            
            // 今日の日付かどうか
            if (currentDate.toDateString() === today.toDateString()) {
                dayEl.classList.add('today');
            }
            
            // 日付がクリックされた時のイベントリスナー
            dayEl.addEventListener('click', (e) => handleDayClick(e, currentDate));
            
            dayEl.innerHTML = `
                <div class="day-number">${date}</div>
                <div class="day-content" data-date="${dateStr}"></div>
                <div class="day-reservations"></div>
            `;
            
            calendarGridEl.appendChild(dayEl);
            
            // 日付の予約を取得
            fetchReservationsForCalendar(dateStr, dayEl);
            
            date++;
        }
        
        // 次月の日付を表示（6週間分になるように）
        const totalCells = 42; // 6週間 × 7日
        const remainingCells = totalCells - (dayOfWeek + lastDay.getDate());
        
        for (let i = 1; i <= remainingCells; i++) {
            const nextMonth = month === 11 ? 0 : month + 1;
            const nextYear = month === 11 ? year + 1 : year;
            const dateStr = formatDate(new Date(nextYear, nextMonth, i));
            
            const dayEl = document.createElement('div');
            dayEl.className = 'calendar-day other-month';
            dayEl.innerHTML = `
                <div class="day-number">${i}</div>
                <div class="day-content" data-date="${dateStr}"></div>
            `;
            calendarGridEl.appendChild(dayEl);
        }
        
        // 月が変わったら予約データを取得
        fetchReservationsForMonth(year, month);
    }
    
    // 日付を選択する関数
    function selectDate(dateStr) {
        const date = new Date(dateStr);
        selectedDate = date;
        
        // 既存の選択を解除
        const selectedDays = document.querySelectorAll('.calendar-day.selected');
        selectedDays.forEach(day => day.classList.remove('selected'));
        
        // 新しい日付を選択
        const dayElements = document.querySelectorAll('.calendar-day:not(.other-month)');
        const selectedDayNumber = date.getDate();
        
        dayElements.forEach(dayEl => {
            const dayNumber = parseInt(dayEl.querySelector('.day-number').textContent);
            if (dayNumber === selectedDayNumber) {
                dayEl.classList.add('selected');
            }
        });
        
        // 日付選択後に予約フォームを直接表示
        // 選択した日付をフォームにセット
        selectedDateInput.value = formatDateJP(date);
        
        // カレンダー表示の横にフォームを表示
        scheduleContainerEl.style.display = 'none';
        reservationFormEl.style.display = 'block';
        
        // すでに予約がある場合は表示して参照できるようにする
        fetchReservationsForDate(dateStr);
    }
    
    // カレンダーの日をクリックした時のイベントハンドラ
    function handleDayClick(e, date) {
        e.stopPropagation();
        
        // 以前に選択された日付のハイライトを削除
        const previouslySelected = document.querySelectorAll('.calendar-day.selected');
        previouslySelected.forEach(day => day.classList.remove('selected'));
        
        // クリックされた日付をハイライト
        const dayElement = e.currentTarget;
        dayElement.classList.add('selected');
        
        // 選択された日付を更新
        selectedDate = date;
        
        // 選択された日付を表示
        document.getElementById('selected-date').value = formatDateJP(new Date(date));
        
        // 予約の詳細を表示
        updateSchedule(date);
        
        // 予約フォームを表示 - 直感的なフロー改善のため、クリック時にすぐフォームを表示
        showReservationForm();
        
        // スケジュールコンテナを非表示
        document.getElementById('schedule-container').style.display = 'none';
    }
    
    // スケジュール表示を更新する関数
    function updateSchedule(dateStr) {
        scheduleDateEl.textContent = formatDateJP(new Date(dateStr));
        
        // 予約データを取得
        const reservations = reservationsCache[dateStr] || [];
        
        if (reservations.length === 0) {
            scheduleBodyEl.innerHTML = '';
            noReservationsEl.style.display = 'block';
            return;
        }
        
        noReservationsEl.style.display = 'none';
        
        // 時間枠の名前
        const timeSlotNames = {
            '1': '1講時 (8:50-10:20)',
            '2': '2講時 (10:30-12:00)',
            '3': '昼休み (12:00-13:00)',
            '4': '3講時 (13:00-14:30)',
            '5': '4講時 (14:40-16:10)',
            '6': '5講時 (16:20-17:50)',
            '7': '6講時 (18:00-19:30)'
        };
        
        // スケジュールテーブルを生成
        let scheduleHTML = '';
        
        reservations.forEach(function(reservation) {
            const timeSlots = reservation.time_slots.split(',');
            const timeSlotTexts = timeSlots.map(slot => timeSlotNames[slot]).join(', ');
            
            scheduleHTML += `
            <tr>
                <td>${timeSlotTexts}</td>
                <td>${reservation.item_name}</td>
                <td>${reservation.user_name}</td>
                <td>
                    <button class="btn danger-btn delete-reservation-btn" data-id="${reservation.id}">削除</button>
                </td>
            </tr>
            `;
        });
        
        scheduleBodyEl.innerHTML = scheduleHTML;
        
        // 削除ボタンのイベントリスナーを設定
        const deleteButtons = scheduleBodyEl.querySelectorAll('.delete-reservation-btn');
        deleteButtons.forEach(function(btn) {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                showDeleteConfirmation(id);
            });
        });
    }
    
    // 予約フォームを表示する関数
    function showReservationForm() {
        const formContainer = document.getElementById('reservation-form');
        const scheduleContainer = document.getElementById('schedule-container');
        
        // フォームを表示
        formContainer.style.display = 'block';
        scheduleContainer.style.display = 'none';
        
        // 選択された日付がない場合は今日の日付を使用
        if (!selectedDate) {
            const today = new Date();
            selectedDate = formatDate(today);
            document.getElementById('selected-date').value = formatDateJP(today);
            
            // カレンダーで今日の日付をハイライト
            const todayElement = document.querySelector('.calendar-day.today');
            if (todayElement) {
                todayElement.classList.add('selected');
            }
        }
        
        // 時間枠のチェックボックスをリセット
        document.querySelectorAll('.time-slot-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // フォームにフォーカス
        if (document.getElementById('user-select')) {
            document.getElementById('user-select').focus();
        }
    }
    
    // 予約フォームを非表示にする関数
    function hideReservationForm() {
        reservationFormEl.style.display = 'none';
        scheduleContainerEl.style.display = 'block';
    }
    
    // 予約を作成する関数
    function createReservation() {
        // フォームから値を取得
        const userId = userSelectEl.value;
        const itemId = itemSelectEl.value;
        const dateStr = selectedDate ? formatDate(selectedDate) : '';
        
        // バリデーション
        if (!userId) {
            showMessage('利用者を選択してください', 'error');
            return;
        }
        
        if (!itemId) {
            showMessage('備品を選択してください', 'error');
            return;
        }
        
        if (!dateStr) {
            showMessage('日付を選択してください', 'error');
            return;
        }
        
        // 選択された時間枠を取得
        const selectedTimeSlots = [];
        timeSlotCheckboxes.forEach(function(checkbox) {
            if (checkbox.checked) {
                selectedTimeSlots.push(checkbox.value);
            }
        });
        
        if (selectedTimeSlots.length === 0) {
            showMessage('予約講時を選択してください', 'error');
            return;
        }
        
        // フォームボタンを無効化
        const submitButton = createReservationForm.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = '送信中...';
        }
        
        // APIリクエスト
        fetch('/api/reservations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                item_id: itemId,
                date: dateStr,
                time_slots: selectedTimeSlots.join(',')
            })
        })
        .then(response => {
            // フォームボタンを再有効化
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = '予約する';
            }
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || '予約の作成に失敗しました。');
                });
            }
            return response.json();
        })
        .then(data => {
            showMessage(data.message || '予約が完了しました', 'success');
            
            // 予約データを更新
            fetchReservationsForDate(dateStr);
            
            // カレンダーの表示も更新
            updateCalendarDisplay(dateStr);
            
            // 予約フォームをリセット
            createReservationForm.reset();
            
            // 予約フォームを非表示にし、スケジュール表示を表示
            hideReservationForm();
        })
        .catch(error => {
            console.error('Reservation creation error:', error);
            showMessage(error.message || '予約の作成中にエラーが発生しました', 'error');
        });
    }
    
    // 予約削除の確認を表示する関数
    function showDeleteConfirmation(id) {
        reservationToDelete = id;
        confirmDeleteModal.style.display = 'block';
    }
    
    // 利用者を追加する関数
    function addUser() {
        const name = document.getElementById('new-user-name').value;
        
        if (!name) {
            alert('利用者名を入力してください。');
            return;
        }
        
        // APIリクエスト
        fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: name })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || '利用者の追加に失敗しました。');
                });
            }
            return response.json();
        })
        .then(data => {
            // モーダルを閉じる
            addUserModal.style.display = 'none';
            
            // フォームをリセット
            document.getElementById('new-user-name').value = '';
            
            // 利用者リストを更新
            fetchUsers();
            
            alert('利用者を追加しました。');
        })
        .catch(error => {
            alert(error.message);
        });
    }
    
    // 備品を追加する関数
    function addItem() {
        const name = document.getElementById('new-item-name').value;
        
        if (!name) {
            alert('備品名を入力してください。');
            return;
        }
        
        // APIリクエスト
        fetch('/api/items', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: name })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || '備品の追加に失敗しました。');
                });
            }
            return response.json();
        })
        .then(data => {
            // モーダルを閉じる
            addItemModal.style.display = 'none';
            
            // フォームをリセット
            document.getElementById('new-item-name').value = '';
            
            // 備品リストを更新
            fetchItems();
            
            alert('備品を追加しました。');
        })
        .catch(error => {
            alert(error.message);
        });
    }
    
    // 利用者リストを取得する関数
    function fetchUsers() {
        fetch('/api/users')
        .then(response => response.json())
        .then(data => {
            let options = '<option value="">選択してください</option>';
            data.forEach(user => {
                options += `<option value="${user.id}">${user.name}</option>`;
            });
            userSelectEl.innerHTML = options;
        })
        .catch(error => {
            console.error('利用者リストの取得に失敗しました。', error);
        });
    }
    
    // 備品リストを取得する関数
    function fetchItems() {
        fetch('/api/items')
        .then(response => response.json())
        .then(data => {
            let options = '<option value="">選択してください</option>';
            data.forEach(item => {
                options += `<option value="${item.id}">${item.name}</option>`;
            });
            itemSelectEl.innerHTML = options;
            
            // 備品カテゴリを更新
            updateItemCategories(data);
        })
        .catch(error => {
            console.error('備品リストの取得に失敗しました。', error);
        });
    }
    
    // 備品カテゴリを更新する関数
    function updateItemCategories(items) {
        let html = '';
        const colors = ['type-1', 'type-2', 'type-3', 'type-4', 'type-5'];
        
        items.forEach((item, index) => {
            const colorClass = colors[index % colors.length];
            html += `
            <li>
                <a href="#" class="item-category" data-id="${item.id}">
                    <i class="fas fa-circle" style="color: var(--${colorClass}-color);"></i>
                    ${item.name}
                </a>
            </li>
            `;
        });
        
        itemCategoriesEl.innerHTML = html;
        
        // 備品カテゴリのイベントハンドラを設定
        setupItemCategoryHandlers();
    }
    
    // 月の予約データを取得する関数
    function fetchReservationsForMonth(year, month) {
        // 月の最初の日と最後の日を取得
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        // 日付範囲を文字列に変換
        const startDate = formatDate(firstDay);
        const endDate = formatDate(lastDay);
        
        // 各日付の予約データを取得
        for (let d = new Date(firstDay); d <= lastDay; d.setDate(d.getDate() + 1)) {
            const dateStr = formatDate(d);
            fetchReservationsForDate(dateStr);
        }
    }
    
    // 特定の日の予約データを取得する関数
    function fetchReservationsForDate(dateStr) {
        fetch(`/api/reservations?date=${dateStr}`)
        .then(response => response.json())
        .then(data => {
            // 予約データをキャッシュに保存
            reservationsCache[dateStr] = data;
            
            // カレンダーの表示を更新
            updateCalendarReservations(dateStr, data.reservations);
            
            // 選択された日付と一致する場合はスケジュール表示も更新
            if (selectedDate && formatDate(selectedDate) === dateStr) {
                updateSchedule(dateStr);
            }
        })
        .catch(error => {
            console.error('予約データの取得に失敗しました。', error);
        });
    }
    
    // カレンダー用に日付の予約を取得する関数
    function fetchReservationsForCalendar(dateStr, dayElement) {
        fetch(`/api/reservations?date=${dateStr}`)
        .then(response => response.json())
        .then(data => {
            if (data.reservations && data.reservations.length > 0) {
                // 予約があることを示すクラスを追加
                dayElement.classList.add('has-reservations');
                
                // 予約データを更新
                updateCalendarReservations(dateStr, data.reservations);
            }
        })
        .catch(error => console.error('Error fetching reservations:', error));
    }
    
    // カレンダーの予約表示を更新する関数
    function updateCalendarReservations(dateStr, reservations) {
        const dayContent = document.querySelector(`.day-content[data-date="${dateStr}"]`);
        if (!dayContent) return;
        
        // 既存の予約表示をクリア
        dayContent.innerHTML = '';
        
        if (reservations.length === 0) return;
        
        // 予約を表示（最大3件まで）
        const maxDisplay = 3;
        const displayCount = Math.min(reservations.length, maxDisplay);
        const colors = ['type-1', 'type-2', 'type-3', 'type-4', 'type-5'];
        
        for (let i = 0; i < displayCount; i++) {
            const reservation = reservations[i];
            const timeSlots = reservation.time_slots.split(',');
            const firstSlot = timeSlots[0];
            const lastSlot = timeSlots[timeSlots.length - 1];
            
            // 時間枠の名前
            const timeSlotNames = {
                '1': '1講時',
                '2': '2講時',
                '3': '昼休み',
                '4': '3講時',
                '5': '4講時',
                '6': '5講時',
                '7': '6講時'
            };
            
            const timeText = timeSlots.length > 1 
                ? `${timeSlotNames[firstSlot]}〜${timeSlotNames[lastSlot]}`
                : timeSlotNames[firstSlot];
            
            const colorClass = colors[i % colors.length];
            
            const reservationEl = document.createElement('div');
            reservationEl.className = `day-reservation ${colorClass}`;
            
            // 備品名と利用者名を表示（短く）
            const shortItemName = reservation.item_name.length > 10 
                ? reservation.item_name.substring(0, 10) + '...' 
                : reservation.item_name;
                
            reservationEl.textContent = `${timeText} ${shortItemName}`;
            reservationEl.setAttribute('data-id', reservation.id);
            reservationEl.setAttribute('title', `${reservation.item_name} (${reservation.user_name})`);
            
            reservationEl.addEventListener('click', function(e) {
                e.stopPropagation();
                const id = this.getAttribute('data-id');
                showDeleteConfirmation(id);
            });
            
            dayContent.appendChild(reservationEl);
        }
        
        // 表示しきれない予約がある場合
        if (reservations.length > maxDisplay) {
            const moreEl = document.createElement('div');
            moreEl.className = 'more-reservations';
            moreEl.textContent = `他 ${reservations.length - maxDisplay} 件`;
            dayContent.appendChild(moreEl);
        }
    }
    
    // 連続する時間枠のみ選択できるようにする関数
    function validateTimeSlots() {
        const selectedSlots = [];
        timeSlotCheckboxes.forEach(function(checkbox) {
            if (checkbox.checked) {
                selectedSlots.push(parseInt(checkbox.value));
            }
        });
        
        if (selectedSlots.length <= 1) return true;
        
        // 選択された時間枠をソート
        selectedSlots.sort((a, b) => a - b);
        
        // 連続しているかチェック
        for (let i = 0; i < selectedSlots.length - 1; i++) {
            if (selectedSlots[i + 1] - selectedSlots[i] !== 1) {
                showMessage('連続していない時間枠は選択できません。', 'error');
                
                // チェックボックスをリセット
                timeSlotCheckboxes.forEach(function(checkbox) {
                    checkbox.checked = false;
                });
                
                return false;
            }
        }
        
        return true;
    }
    
    // 日付をYYYY-MM-DD形式に変換する関数
    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }
    
    // 日付を日本語形式（YYYY年MM月DD日）に変換する関数
    function formatDateJP(date) {
        const year = date.getFullYear();
        const month = date.getMonth() + 1;
        const day = date.getDate();
        return `${year}年${month}月${day}日`;
    }
    
    // カレンダー上の予約表示を更新する関数
    function updateCalendarDisplay(dateStr) {
        // 現在表示中の月のすべての日付の予約を再取得
        const currentMonth = parseInt(currentMonthEl.textContent.match(/(\d+)月/)[1]) - 1;
        const currentYear = parseInt(currentMonthEl.textContent.match(/(\d+)年/)[1]);
        
        // カレンダー上のすべての日付要素
        const dayElements = document.querySelectorAll('.calendar-day:not(.other-month)');
        
        dayElements.forEach(dayEl => {
            const dayNumber = dayEl.querySelector('.day-number').textContent;
            const date = new Date(currentYear, currentMonth, parseInt(dayNumber));
            const dateString = formatDate(date);
            
            // この日付の予約を再取得
            fetchReservationsForCalendar(dateString, dayEl);
        });
    }
    
    // ガイダンスモーダルを表示する関数
    function showGuidance() {
        if (guidanceModal) {
            guidanceModal.style.display = 'block';
            
            // モーダル内のCloseボタンのイベントリスナー
            const closeBtn = guidanceModal.querySelector('.close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    if (dontShowAgainCheckbox.checked) {
                        localStorage.setItem('guidanceShown', 'true');
                    }
                    guidanceModal.style.display = 'none';
                });
            }
        }
    }
    
    // カスタムメッセージを表示する関数
    function showMessage(message, type = 'info') {
        // 既存のメッセージがあれば削除
        const existingMessage = document.querySelector('.message-container');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // メッセージコンテナを作成
        const messageContainer = document.createElement('div');
        messageContainer.className = `message-container ${type}`;
        
        // メッセージテキスト
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = message;
        
        // 閉じるボタン
        const closeBtn = document.createElement('button');
        closeBtn.className = 'message-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.addEventListener('click', () => {
            messageContainer.classList.add('closing');
            setTimeout(() => messageContainer.remove(), 300);
        });
        
        // 要素を組み立てる
        messageContainer.appendChild(messageText);
        messageContainer.appendChild(closeBtn);
        
        // ドキュメントに追加
        document.body.appendChild(messageContainer);
        
        // 一定時間後に自動的に閉じる
        setTimeout(() => {
            if (document.body.contains(messageContainer)) {
                messageContainer.classList.add('closing');
                setTimeout(() => {
                    if (document.body.contains(messageContainer)) {
                        messageContainer.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
    
    // 初期表示時は予約フォームを非表示にする
    reservationFormEl.style.display = 'none';
    scheduleContainerEl.style.display = 'block';
    
    // モバイル対応のナビゲーション設定
    setupMobileNavigation();
    
    // 予約削除イベントのハンドラを更新
    document.getElementById('confirm-delete-btn').addEventListener('click', function() {
        if (reservationToDelete) {
            deleteReservation(reservationToDelete);
        }
    });
});

// 予約削除後の更新問題の修正
function deleteReservation(id) {
    fetch(`/api/reservations/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) throw new Error('削除に失敗しました');
        return response.json();
    })
    .then(data => {
        // 成功メッセージを表示
        showMessage('予約を削除しました', 'success');
        
        // 予約スケジュールを更新
        if (selectedDate) {
            fetchReservationsForDate(selectedDate);
        }
        
        // カレンダーを更新 - ここが足りていなかった
        fetchReservationsForMonth(currentYear, currentMonth + 1);
        
        // モーダルを閉じる
        const modal = document.getElementById('confirm-delete-modal');
        modal.style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('削除に失敗しました: ' + error.message, 'error');
    });
}

// モバイル対応のサイドバー制御
function setupMobileNavigation() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            
            // オーバーレイの作成
            let overlay = document.querySelector('.sidebar-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = 'sidebar-overlay';
                document.body.appendChild(overlay);
                
                // オーバーレイをクリックしたらサイドバーを閉じる
                overlay.addEventListener('click', function() {
                    sidebar.classList.remove('active');
                    overlay.classList.remove('active');
                });
            }
            
            if (sidebar.classList.contains('active')) {
                overlay.classList.add('active');
            } else {
                overlay.classList.remove('active');
            }
        });
    }
    
    // 画面サイズの変更を監視
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
            const overlay = document.querySelector('.sidebar-overlay');
            if (overlay) {
                overlay.classList.remove('active');
            }
        }
    });
} 