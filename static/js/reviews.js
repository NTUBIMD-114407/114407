document.addEventListener("DOMContentLoaded", function () {
    console.log("reviews.js 已載入");

    const params = new URLSearchParams(window.location.search);
    const station = params.get("station") || "shandao";

    // 模擬的評論資料
    const fakeReviews = {
        shandao: [
            { user: "小明", comment: "這裡的美食很多，推薦排骨飯！", date: "2024-03-10" },
            { user: "小美", comment: "環境乾淨，出站後附近有很多咖啡店。", date: "2024-03-09" },
            { user: "阿偉", comment: "交通方便，離台北車站很近。", date: "2024-03-08" }
        ],
        ximen: [
            { user: "小杰", comment: "西門町超熱鬧，很多年輕人！", date: "2024-03-11" },
            { user: "阿豪", comment: "有很多服飾店，還有手搖飲很棒。", date: "2024-03-10" }
        ]
    };

    const reviews = fakeReviews[station] || [];

    // 更新評論區塊
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
});
