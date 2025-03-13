document.addEventListener("DOMContentLoaded", function () {
    const stationSelect = document.getElementById("station-select");
    const googleMap = document.getElementById("google-map");
    const reviewsContainer = document.querySelector(".reviews-container");

    // Google Maps API Key
    const API_KEY = "AIzaSyCSjgDp4YRLipBUWzKnY0-jPkQSsriAu1w"; 

    // 捷運站的座標資料
    const mrtStations = {
        "台北車站": { lat: 25.046255, lng: 121.517532, english: "Taipei Main Station" },
        "忠孝敦化": { lat: 25.041478, lng: 121.551098, english: "Zhongxiao Dunhua" },
        "西門": { lat: 25.04209, lng: 121.508303, english: "Ximen" }
        // 你可以加入更多捷運站
    };

    function updateStationData(stationName) {
        if (!(stationName in mrtStations)) {
            console.warn(`找不到 ${stationName} 的資料`);
            return;
        }

        const { lat, lng, english } = mrtStations[stationName];

        // 更新標題
        document.getElementById("station-name").textContent = stationName;
        document.getElementById("station-english").textContent = english;
        document.getElementById("page-title").textContent = stationName;

        // 更新 Google 地圖
        googleMap.src = `https://www.google.com/maps/embed/v1/place?key=${API_KEY}&q=${lat},${lng}`;

        // 獲取該捷運站的評論
        fetch(`https://api.example.com/reviews?station=${stationName}`)
            .then(response => response.json())
            .then(data => {
                reviewsContainer.innerHTML = ""; // 清空現有評論

                if (data.reviews && data.reviews.length > 0) {
                    data.reviews.forEach(review => {
                        const reviewElement = document.createElement("div");
                        reviewElement.classList.add("review-card");
                        reviewElement.textContent = review.text;
                        reviewsContainer.appendChild(reviewElement);
                    });
                } else {
                    reviewsContainer.innerHTML = "<p>目前沒有評論</p>";
                }
            })
            .catch(error => {
                console.error("無法加載評論：", error);
                reviewsContainer.innerHTML = "<p>評論載入失敗</p>";
            });
    }

    // 監聽下拉式選單的變化
    stationSelect.addEventListener("change", function () {
        const selectedStation = stationSelect.value;
        updateStationData(selectedStation);
    });

    // 頁面載入時，顯示預設站點（例如：台北車站）
    updateStationData(stationSelect.value);
});
