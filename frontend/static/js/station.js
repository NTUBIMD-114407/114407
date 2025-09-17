let map;
let markers = [];
let placesService;

const mrtStations = {
    red: {
        "象山": { lat: 25.03283, lng: 121.569576 },
    "台北101/世貿": { lat: 25.033102, lng: 121.563292 },
    "信義安和": { lat: 25.033326, lng: 121.553526 },
    "大安": { lat: 25.032943, lng: 121.543551 },
    "大安森林公園": { lat: 25.033396, lng: 121.534882 },
    "東門": { lat: 25.033847, lng: 121.528739 },
    "中正紀念堂": { lat: 25.032729, lng: 121.51827 },
    "台大醫院": { lat: 25.041256, lng: 121.51604 },
    "台北車站": { lat: 25.046255, lng: 121.517532 },
    "中山": { lat: 25.052685, lng: 121.520392 },
    "雙連": { lat: 25.057805, lng: 121.520627 },
    "民權西路": { lat: 25.062905, lng: 121.51932 },
    "圓山": { lat: 25.071353, lng: 121.520118 },
    "劍潭": { lat: 25.084873, lng: 121.525078 },
    "士林": { lat: 25.093535, lng: 121.52623 },
    "芝山": { lat: 25.10306, lng: 121.522514 },
    "明德": { lat: 25.109721, lng: 121.518848 },
    "石牌": { lat: 25.114523, lng: 121.515559 },
    "唭哩岸": { lat: 25.120872, lng: 121.506252 },
    "奇岩": { lat: 25.125491, lng: 121.501132 },
    "北投": { lat: 25.131841, lng: 121.498633 },
    "新北投": { lat: 25.136933, lng: 121.50253 },
    "復興崗": { lat: 25.137474, lng: 121.485444 },
    "忠義": { lat: 25.130969, lng: 121.47341 },
    "關渡": { lat: 25.125633, lng: 121.467102 },
    "竹圍": { lat: 25.13694, lng: 121.459479 },
    "紅樹林": { lat: 25.154042, lng: 121.458872 },
    "淡水": { lat: 25.167818, lng: 121.445561 }
    },
    blue: {
    "頂埔": { lat: 24.96012, lng: 121.4205 },
    "永寧": { lat: 24.966726, lng: 121.436072 },
    "土城": { lat: 24.973094, lng: 121.444362 },
    "海山": { lat: 24.985339, lng: 121.448786 },
    "亞東醫院": { lat: 24.998037, lng: 121.452514 },
    "府中": { lat: 25.008619, lng: 121.459409 },
    "板橋": { lat: 25.013618, lng: 121.462302 },
    "新埔": { lat: 25.023738, lng: 121.468361 },
    "江子翠": { lat: 25.03001, lng: 121.47239 },
    "龍山寺": { lat: 25.03528, lng: 121.499826 },
    "西門": { lat: 25.04209, lng: 121.508303 },
    "善導寺": { lat: 25.044823, lng: 121.523208 },
    "忠孝新生": { lat: 25.042356, lng: 121.532905 },
    "忠孝復興": { lat: 25.041629, lng: 121.543767 },
    "忠孝敦化": { lat: 25.041478, lng: 121.551098 },
    "國父紀念館": { lat: 25.041349, lng: 121.557802 },
    "市政府": { lat: 25.041171, lng: 121.565228 },
    "永春": { lat: 25.040859, lng: 121.576293 },
    "後山埤": { lat: 25.045055, lng: 121.582522 },
    "昆陽": { lat: 25.050461, lng: 121.593268 },
    "南港": { lat: 25.052116, lng: 121.606686 }
    }
};

// 初始化地圖
function initMap() {
    const defaultStation = "台北車站";

    map = new google.maps.Map(document.getElementById("map"), {
        center: mrtStations.red[defaultStation] || mrtStations.blue[defaultStation],
        zoom: 15
    });

    placesService = new google.maps.places.PlacesService(map);

    updateStationOptions(); // 初始化捷運站選單
    updateStationData(defaultStation);
}

// 更新捷運站選單
function updateStationOptions() {
    const lineSelect = document.getElementById("line-select");
    const stationSelect = document.getElementById("station-select");
    const selectedLine = lineSelect.value;

    stationSelect.innerHTML = ""; // 清空選單

    if (selectedLine === "all") {
        Object.keys(mrtStations).forEach(line => {
            Object.keys(mrtStations[line]).forEach(station => {
                let option = document.createElement("option");
                option.value = station;
                option.textContent = station;
                stationSelect.appendChild(option);
            });
        });
    } else {
        Object.keys(mrtStations[selectedLine]).forEach(station => {
            let option = document.createElement("option");
            option.value = station;
            option.textContent = station;
            stationSelect.appendChild(option);
        });
    }

    updateStationData(stationSelect.value);
}

// 取得捷運站附近的美食推薦
async function updateStationData(stationName) {
    const lineSelect = document.getElementById("line-select").value;
    const stationData = mrtStations[lineSelect]?.[stationName] || mrtStations.red[stationName] || mrtStations.blue[stationName];

    if (!stationData) return;

    map.setCenter(stationData);
    map.setZoom(15);

    markers.forEach(marker => marker.setMap(null));
    markers = [];

    const request = {
        location: stationData,
        radius: 1000,
        type: "restaurant"
    };

    placesService.nearbySearch(request, (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            const uniqueRestaurants = results.slice(0, 9).map(place => ({
                restaurant_name: place.name || "無名稱",
                rating: place.rating || "無評分",
                place_id: place.place_id
            }));

            updateRestaurantList(uniqueRestaurants);
        } else {
            console.error("Google Places API 查詢失敗", status);
        }
    });
}

// 更新餐廳列表並標記在地圖上
function updateRestaurantList(restaurants) {
    const foodContainer = document.querySelector(".food-container");
    foodContainer.innerHTML = "";

    markers.forEach(marker => marker.setMap(null));
    markers = [];

    restaurants.forEach(restaurant => {
        const card = document.createElement("div");
        card.className = "food-card";
        card.innerHTML = `<h3>${restaurant.restaurant_name}</h3>
                          <p>⭐ ${restaurant.rating}</p>`;

        foodContainer.appendChild(card);

        // 查詢商家詳細資訊
        const request = {
            placeId: restaurant.place_id,  // 確保這裡有 place_id
            fields: ["place_id", "geometry", "name", "formatted_address", "rating", "photos"]
        };

        placesService.getDetails(request, (place, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && place.geometry) {
                const marker = new google.maps.Marker({
                    position: place.geometry.location,
                    map: map,
                    title: place.name
                });

                markers.push(marker);

                // **⚠️ 確保 `place_id` 不為 `undefined`**
                if (!place.place_id) {
                    console.error("❌ Google Places API 沒有返回 place_id:", place);
                    return;
                }

                // **點擊標記時，在右側顯示商家資訊並更新評論**
                marker.addListener("click", () => {
                    displayBusinessInfo(place);
                    fetchReviews(place.place_id, place.name); // 🚀 **點擊地圖標記時，同步評論**
                });

                // **點擊推薦餐廳卡片時，在右側顯示商家資訊並更新評論**
                card.addEventListener("click", () => {
                    map.setCenter(place.geometry.location);
                    map.setZoom(17);
                    displayBusinessInfo(place);
                    fetchReviews(place.place_id, place.name); // 🚀 **點擊餐廳卡片時，同步評論**
                });
            } else {
                console.error("❌ 無法獲取商家資訊:", request.placeId, status);
            }
        });
    });
}

function scrollToReviews() {
    const reviewsSection = document.getElementById("reviews");

    if (reviewsSection) {
        reviewsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    } else {
        console.error("❌ 找不到 reviews 區域！");
    }
}

// 在右側顯示商家資訊
function displayBusinessInfo(place) {
    if (!place || !place.name) {
        console.error("❌ 無法獲取商家資訊！");
        return;
    }

    const mapContainer = document.getElementById("map-container");
    const businessInfo = document.getElementById("business-info");
    const businessDetails = document.getElementById("business-details");

    // **顯示商家資訊並縮小地圖**
    mapContainer.classList.add("business-active");

    // **清除舊內容**
    businessDetails.innerHTML = "";

    // **處理圖片**
    const photoUrl = place.photos ? place.photos[0].getUrl() : "https://via.placeholder.com/300";

    // **插入新的商家資訊**
    businessDetails.innerHTML = `
        
        <img src="${photoUrl}" alt="${place.name}" style="width:100%; border-radius:10px;">
        <h3>${place.name}</h3>
        <p>⭐ ${place.rating || "無評分"}</p>
        <p>${place.formatted_address || "地址未知"}</p>
        <button onclick="fetchReviews('${place.place_id}', '${place.name}'); scrollToReviews();">查看評論</button>
        <button onclick="hideBusinessInfo()">關閉</button>
    `;

    businessInfo.style.display = "block";
}

// **點擊「關閉」按鈕，恢復地圖大小，隱藏商家資訊**
function hideBusinessInfo() {
    const mapContainer = document.getElementById("map-container");

    // **恢復地圖大小**
    mapContainer.classList.remove("business-active");

    // **等動畫結束後再隱藏商家資訊**
    setTimeout(() => {
        document.getElementById("business-info").style.display = "none";
    }, 300);
}

// 獲取評論
// 確保 `place_id` 不為 `undefined`，避免 `Invalid 'placeid' parameter` 錯誤
function fetchReviews(placeId, restaurantName) {
    console.log("📌 嘗試獲取評論，placeId:", placeId);

    // **若 placeId 無效，則直接返回，避免 API 無效請求**
    if (!placeId || placeId === "undefined" || placeId === "無效") {
        console.error("❌ 無效的 placeId，無法獲取評論:", placeId);
        return;
    }

    placesService.getDetails({ placeId: placeId, fields: ["reviews"] }, (place, status) => {
        let reviewsContainer = document.getElementById("reviews-container");

        // **若 `reviews-container` 不存在，則自動建立**
        if (!reviewsContainer) {
            console.warn("❌ 找不到 reviews-container，將自動建立");
            reviewsContainer = document.createElement("div");
            reviewsContainer.id = "reviews-container";
            document.getElementById("reviews").appendChild(reviewsContainer);
        }

        reviewsContainer.innerHTML = `<h3>${restaurantName} 的評論</h3>`;

        // **檢查 API 是否成功返回評論**
        if (status === google.maps.places.PlacesServiceStatus.OK && place.reviews) {
            console.log("✅ 成功獲取評論:", place.reviews);

            const reviews = place.reviews;
            const maxVisibleReviews = 3;
            let showingAllReviews = false;

            const reviewList = document.createElement("div");
            reviewList.className = "review-list";
            reviewsContainer.appendChild(reviewList);

            function renderReviews() {
                reviewList.innerHTML = "";
                const reviewsToShow = showingAllReviews ? reviews : reviews.slice(0, maxVisibleReviews);

                reviewsToShow.forEach(review => {
                    const reviewElement = document.createElement("div");
                    reviewElement.className = "review-item";
                    reviewElement.innerHTML = `<p><strong>${review.author_name}</strong>: ${review.text || "無內容"}</p>`;
                    reviewList.appendChild(reviewElement);
                });

                let buttonContainer = document.getElementById("show-more-container");
                if (!buttonContainer) {
                    buttonContainer = document.createElement("div");
                    buttonContainer.id = "show-more-container";
                    reviewsContainer.appendChild(buttonContainer);
                }

                buttonContainer.innerHTML = "";

                if (reviews.length > maxVisibleReviews) {
                    const showMoreButton = document.createElement("button");
                    showMoreButton.textContent = showingAllReviews ? "顯示較少" : "顯示更多留言";
                    showMoreButton.addEventListener("click", () => {
                        showingAllReviews = !showingAllReviews;
                        renderReviews();
                    });

                    buttonContainer.appendChild(showMoreButton);
                }
            }

            renderReviews();
        } else {
            console.warn("❌ API 沒有返回評論或 API 限制", status);
            reviewsContainer.innerHTML += "<p>目前沒有評論</p>";
        }
    });
}

// 監聽捷運線選擇變更
document.getElementById("line-select").addEventListener("change", updateStationOptions);

// 監聽捷運站選擇變更
document.getElementById("station-select").addEventListener("change", () => {
    updateStationData(document.getElementById("station-select").value);
});

// 初始化選單
document.addEventListener("DOMContentLoaded", initMap);