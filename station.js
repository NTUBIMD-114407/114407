document.addEventListener("DOMContentLoaded", function () {
    console.log("🚆 station.js 已載入");

    // 取得 URL 參數
    const params = new URLSearchParams(window.location.search);
    const station = params.get("station"); // 取得捷運站名稱

    // 確保站名不是 null
    if (station) {
        console.log("🔹 目前站名:", station);

        // 將捷運站名稱更新到標題
        document.getElementById("station-name").textContent = station;
        document.getElementById("page-title").textContent = station + " - 捷運站";
    } else {
        console.warn("⚠️ 未獲取到 station 參數，顯示預設名稱");
    }
});


    // 取得評論
    loadReviews(station);

// 假設這是一個模擬的 document.addEventListener("DOMContentLoaded", function () {
    console.log("🚆 station.js 已載入");

    // 取得 URL 參數
    const params = new URLSearchParams(window.location.search);
    const station = params.get("station") || "捷運站"; // 預設顯示「捷運站」

    // 更新標題名稱
    document.getElementById("station-name").textContent = station;
    document.getElementById("page-title").textContent = station + " - 捷運站";
    
    // Google Map 設置 (這邊你可以填上不同捷運站的經緯度)
    const mapSrc = {
        "善導寺": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3621.933385467191!2d121.523!3d25.0442",
        "西門": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3621.00000!2d121.508!3d25.0420"
    };

    document.getElementById("google-map").src = mapSrc[station] || mapSrc["善導寺"];

    // 取得評論
    loadReviews(station);

// 假設這是一個模擬的 API，等後端有資料後可以換成 fetch
function loadReviews(station) {
    const fakeReviews = {
        "善導寺": [
            { user: "小明", comment: "這裡的美食很多，推薦排骨飯！", date: "2024-03-10" },
            { user: "小美", comment: "環境乾淨，出站後附近有很多咖啡店。", date: "2024-03-09" }
        ],
        "西門": [
            { user: "小杰", comment: "西門町超熱鬧，很多年輕人！", date: "2024-03-11" },
            { user: "阿豪", comment: "有很多服飾店，還有手搖飲很棒。", date: "2024-03-10" }
        ]
    };

    const reviews = fakeReviews[station] || [];
    const reviewList = document.getElementById("review-list");
    reviewList.innerHTML = "";

    if (reviews.length === 0) {
        reviewList.innerHTML = "<p>暫無評論</p>";
    } else {
        reviews.forEach(review => {
            const reviewBox = document.createElement("div");
            reviewBox.classList.add("review-box");
            reviewBox.innerHTML = `
                <h3>${review.user}</h3>
                <p>${review.comment}</p>
                <span>${review.date}</span>
            `;
            reviewList.appendChild(reviewBox);
        });
    }
}
 fetch
function loadReviews(station) {
    const fakeReviews = {
        善導寺: [
            { user: "小明", comment: "這裡的美食很多，推薦排骨飯！", date: "2024-03-10" },
            { user: "小美", comment: "環境乾淨，出站後附近有很多咖啡店。", date: "2024-03-09" }
        ],
        西門: [
            { user: "小杰", comment: "西門町超熱鬧，很多年輕人！", date: "2024-03-11" },
            { user: "阿豪", comment: "有很多服飾店，還有手搖飲很棒。", date: "2024-03-10" }
        ]
    };

    const reviews = fakeReviews[station] || [];
    const reviewList = document.getElementById("review-list");
    reviewList.innerHTML = "";

    if (reviews.length === 0) {
        reviewList.innerHTML = "<p>暫無評論</p>";
    } else {
        reviews.forEach(review => {
            const reviewBox = document.createElement("div");
            reviewBox.classList.add("review-box");
            reviewBox.innerHTML = `
                <h3>${review.user}</h3>
                <p>${review.comment}</p>
                <span>${review.date}</span>
            `;
            reviewList.appendChild(reviewBox);
        });
    }
}
