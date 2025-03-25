// 等待 DOM 完全加載
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    
    if (!form) {
        console.error('找不到註冊表單');
        return;
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const emailInput = document.getElementById('registerEmail');
        const passwordInput = document.getElementById('registerPassword');
        const confirmPasswordInput = document.getElementById('confirmPassword');

        if (!emailInput || !passwordInput || !confirmPasswordInput) {
            alert('找不到輸入欄位');
            return;
        }

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        if (!email || !password || !confirmPassword) {
            alert('請填寫所有欄位');
            return;
        }

        if (password !== confirmPassword) {
            alert('密碼不一致，請重新輸入');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/api/accounts/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                alert('註冊成功！請登入');
                window.location.href = 'index.html';
            } else {
                alert(data.error || '註冊失敗，請稍後再試');
            }
        } catch (error) {
            console.error('註冊錯誤:', error);
            alert('註冊失敗，請稍後再試');
        }
    });
}); 