document.addEventListener('DOMContentLoaded', function() {
    const baseURL = window.location.origin;
    
    // DOM要素
    const usersList = document.getElementById('users-list');
    const itemsList = document.getElementById('items-list');
    const userForm = document.getElementById('add-user-form');
    const itemForm = document.getElementById('add-item-form');
    const deleteAllBtn = document.getElementById('delete-all-btn');
    
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
        fetch(`${baseURL}/api/users`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('利用者の取得に失敗しました');
                }
                return response.json();
            })
            .then(users => {
                let html = `
                    <tr>
                        <th>ID</th>
                        <th>利用者名</th>
                    </tr>
                `;
                
                if (users.length === 0) {
                    html += `
                        <tr>
                            <td colspan="2" style="text-align: center;">利用者がいません</td>
                        </tr>
                    `;
                } else {
                    users.forEach(user => {
                        html += `
                            <tr>
                                <td>${user.id}</td>
                                <td>${user.name}</td>
                            </tr>
                        `;
                    });
                }
                
                usersList.innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                usersList.innerHTML = `
                    <tr>
                        <td colspan="2" style="text-align: center; color: red;">
                            利用者データの取得に失敗しました
                        </td>
                    </tr>
                `;
            });
    }
    
    // 備品リストを取得する関数
    function fetchItems() {
        fetch(`${baseURL}/api/items`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('備品の取得に失敗しました');
                }
                return response.json();
            })
            .then(items => {
                let html = `
                    <tr>
                        <th>ID</th>
                        <th>備品名</th>
                    </tr>
                `;
                
                if (items.length === 0) {
                    html += `
                        <tr>
                            <td colspan="2" style="text-align: center;">備品がありません</td>
                        </tr>
                    `;
                } else {
                    items.forEach(item => {
                        html += `
                            <tr>
                                <td>${item.id}</td>
                                <td>${item.name}</td>
                            </tr>
                        `;
                    });
                }
                
                itemsList.innerHTML = html;
            })
            .catch(error => {
                console.error('Error:', error);
                itemsList.innerHTML = `
                    <tr>
                        <td colspan="2" style="text-align: center; color: red;">
                            備品データの取得に失敗しました
                        </td>
                    </tr>
                `;
            });
    }
    
    // 利用者を追加する関数
    function addUser() {
        const userName = document.getElementById('user-name').value;
        
        if (!userName) {
            alert('利用者名を入力してください');
            return;
        }
        
        fetch(`${baseURL}/api/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: userName })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                document.getElementById('user-name').value = '';
                fetchUsers();
                alert('利用者を追加しました');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('利用者の追加に失敗しました');
            });
    }
    
    // 備品を追加する関数
    function addItem() {
        const itemName = document.getElementById('item-name').value;
        
        if (!itemName) {
            alert('備品名を入力してください');
            return;
        }
        
        fetch(`${baseURL}/api/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: itemName })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                document.getElementById('item-name').value = '';
                fetchItems();
                alert('備品を追加しました');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('備品の追加に失敗しました');
            });
    }
    
    // 全予約を削除する関数
    function deleteAllReservations() {
        if (!confirm('全ての予約を削除してもよろしいですか？この操作は取り消せません。')) {
            return;
        }
        
        fetch(`${baseURL}/api/reservations/all`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message || '全ての予約を削除しました');
                } else {
                    alert(data.error || '予約の削除に失敗しました');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('予約の削除に失敗しました');
            });
    }
}); 