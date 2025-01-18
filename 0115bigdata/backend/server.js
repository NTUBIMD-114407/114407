// 確保先安裝必要的套件：npm install express body-parser

const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;

// 使用 body-parser 來解析請求中的 JSON 數據
app.use(bodyParser.json());

// 模擬一個數據庫，這裡用一個數組來存儲用戶
let users = [];

// 註冊 API
app.post('/register', (req, res) => {
    const { username, password } = req.body;

    // 驗證必填欄位
    if (!username || !password) {
        return res.status(400).json({ message: 'Username and password are required.' });
    }

    // 檢查用戶名是否已存在
    const userExists = users.find(user => user.username === username);
    if (userExists) {
        return res.status(409).json({ message: 'Username already exists.' });
    }

    // 新增用戶到 "數據庫"
    users.push({ username, password });

    // 返回成功消息
    res.status(201).json({ message: 'User registered successfully.' });
});

// 啟動服務器
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
