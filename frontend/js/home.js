// 等待 DOM 完全加載
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logoutBtn');
    
    // 檢查登入狀態
    checkLoginStatus();
    
    // 登出按鈕點擊事件
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

// 檢查登入狀態
async function checkLoginStatus() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/accounts/check-auth/', {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.is_authenticated) {
            // 清除會話存儲
            sessionStorage.clear();
            // 重定向到登入頁面
            window.location.replace('index.html');
        }
    } catch (error) {
        console.error('Error checking login status:', error);
        // 發生錯誤時也重定向到登入頁面
        sessionStorage.clear();
        window.location.replace('index.html');
    }
}

// 處理登出
async function handleLogout() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/accounts/logout/', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            // 清除會話存儲
            sessionStorage.clear();
            // 重定向到登入頁面
            window.location.replace('index.html');
        } else {
            throw new Error('登出失敗');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('登出過程發生錯誤，請稍後再試');
    }
} 