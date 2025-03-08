document.addEventListener('DOMContentLoaded', function() {
    // DOM要素
    const usersTableBody = document.getElementById('users-body');
    const itemsTableBody = document.getElementById('items-body');
    const addUserAdminBtn = document.getElementById('add-user-admin-btn');
    const addItemAdminBtn = document.getElementById('add-item-admin-btn');
    const deleteAllReservationsBtn = document.getElementById('delete-all-reservations-btn');
    
    // モーダル関連
    const addUserModal = document.getElementById('add-user-modal');
    const addItemModal = document.getElementById('add-item-modal');
    const confirmDeleteAllModal = document.getElementById('confirm-delete-all-modal');
    const addUserForm = document.getElementById('add-user-form');
    const addItemForm = document.getElementById('add-item-form');
    const confirmDeleteAllBtn = document.getElementById('confirm-delete-all-btn');
    const cancelDeleteAllBtn = document.getElementById('cancel-delete-all-btn');
    const closeButtons = document.querySelectorAll('.close');
    
    // サイドバーナビゲーション
    const sidebarLinks = document.querySelectorAll('.sidebar-list a');
    
    // 初期データの取得
    fetchUsers();
    fetchItems();
    
    // イベントリスナーの設定
    addUserAdminBtn.addEventListener('click', function() {
        addUserModal.style.display = 'block';
    });
    
    addItemAdminBtn.addEventListener('click', function() {
        addItemModal.style.display = 'block';
    });
    
    deleteAllReservationsBtn.addEventListener('click', function() {
        confirmDeleteAllModal.style.display = 'block';
    });
    
    addUserForm.addEventListener('submit', function(e) {
        e.preventDefault();
        addUser();
    });
    
    addItemForm.addEventListener('submit', function(e) {
        e.preventDefault();
        addItem();
    });
    
    confirmDeleteAllBtn.addEventListener('click', function() {
        deleteAllReservations();
    });
    
    cancelDeleteAllBtn.addEventListener('click', function() {
        confirmDeleteAllModal.style.display = 'none';
    });
    
    closeButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            addUserModal.style.display = 'none';
            addItemModal.style.display = 'none';
            confirmDeleteAllModal.style.display = 'none';
        });
    });
    
    // サイドバーナビゲーションのイベントリスナー
    sidebarLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // アクティブクラスを更新
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // 対応するセクションにスクロール
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // 利用者リストを取得する関数
    function fetchUsers() {
        fetch('/api/users')
        .then(response => response.json())
        .then(data => {
            let html = '';
            data.forEach(user => {
                html += `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                </tr>
                `;
            });
            usersTableBody.innerHTML = html;
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
            let html = '';
            data.forEach(item => {
                html += `
                <tr>
                    <td>${item.id}</td>
                    <td>${item.name}</td>
                </tr>
                `;
            });
            itemsTableBody.innerHTML = html;
        })
        .catch(error => {
            console.error('備品リストの取得に失敗しました。', error);
        });
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
    
    // 全予約を削除する関数
    function deleteAllReservations() {
        // APIリクエスト
        fetch('/api/reservations/all', {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            // モーダルを閉じる
            confirmDeleteAllModal.style.display = 'none';
            
            alert(data.message);
        })
        .catch(error => {
            alert('予約の削除に失敗しました。');
            console.error(error);
        });
    }
}); 