let map;
let markers = [];
let placesService;
let allRestaurantsData = [];

const mrtStations = {
    "台北車站": { lat: 25.046255, lng: 121.517532 },
    "忠孝敦化": { lat: 25.041478, lng: 121.551098 },
    "西門": { lat: 25.04209, lng: 121.508303 }
};

function initMap() {
    const defaultStation = "台北車站";

    map = new google.maps.Map(document.getElementById("map"), {
        center: mrtStations[defaultStation],
        zoom: 15
    });

    placesService = new google.maps.places.PlacesService(map);

    updateStationData(defaultStation);
}

async function updateStationData(stationName) {
    if (!(stationName in mrtStations)) return;

    map.setCenter(mrtStations[stationName]);

    markers.forEach(marker => marker.setMap(null));
    markers = [];

    const request = {
        location: mrtStations[stationName],
        radius: 1000,
        type: "restaurant"
    };

    placesService.nearbySearch(request, (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            const uniqueRestaurants = results.slice(0, 9).map(place => ({
                restaurant_name: place.name,
                rating: place.rating || "無評分",
                place_id: place.place_id
            }));

            updateRestaurantList(uniqueRestaurants);
        } else {
            console.error("Google Places API 查詢失敗", status);
        }
    });
}

function updateRestaurantList(restaurants) {
    const foodContainer = document.querySelector(".food-container");
    foodContainer.innerHTML = "";

    // 清除舊的地圖標記
    markers.forEach(marker => marker.setMap(null));
    markers = [];

    restaurants.forEach(restaurant => {
        const card = document.createElement("div");
        card.className = "food-card";
        card.innerHTML = `<h3>${restaurant.restaurant_name}</h3><p>⭐ ${restaurant.rating}</p>`;

        foodContainer.appendChild(card);

        // **在地圖上標記餐廳**
        const request = {
            placeId: restaurant.place_id,
            fields: ["geometry", "name"]
        };

        placesService.getDetails(request, (place, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && place.geometry) {
                const marker = new google.maps.Marker({
                    position: place.geometry.location,
                    map: map,
                    title: restaurant.restaurant_name
                });

                markers.push(marker);

                // 創建資訊視窗
                const infoWindow = new google.maps.InfoWindow({
                    content: `<h3>${restaurant.restaurant_name}</h3><p>⭐ ${restaurant.rating}</p>`
                });

                // **點擊標記時顯示資訊**
                marker.addListener("click", () => {
                    infoWindow.open(map, marker);
                    fetchReviews(restaurant.place_id, restaurant.restaurant_name); // 可選：點擊標記時開啟評論
                });

                // **點擊餐廳卡片時，地圖移動到該餐廳**
                card.addEventListener("click", () => {
                    map.setCenter(place.geometry.location); // 移動畫面
                    map.setZoom(17); // 可選：放大查看細節
                    infoWindow.open(map, marker); // 打開資訊視窗
                    fetchReviews(restaurant.place_id, restaurant.restaurant_name); // 可選：載入評論
                });
            }
        });
    });
}


function fetchReviews(placeId, restaurantName) {
    placesService.getDetails({ placeId: placeId, fields: ["reviews"] }, (place, status) => {
        const reviewsContainer = document.querySelector(".reviews-container");
        reviewsContainer.innerHTML = `<h3>${restaurantName} 的評論</h3>`;

        if (status === google.maps.places.PlacesServiceStatus.OK && place.reviews) {
            const reviews = place.reviews;
            console.log("評論數量:", reviews.length); // 檢查評論數量
            const maxVisibleReviews = 3; // 改成 3 來確保按鈕出現
            let showingAllReviews = false;

            // 創建評論區
            const reviewList = document.createElement("div");
            reviewList.className = "review-list";
            reviewsContainer.appendChild(reviewList);

            function renderReviews() {
                reviewList.innerHTML = ""; 
                const reviewsToShow = showingAllReviews ? reviews : reviews.slice(0, maxVisibleReviews);

                reviewsToShow.forEach(review => {
                    const reviewElement = document.createElement("div");
                    reviewElement.className = "review-item";
                    reviewElement.innerHTML = `<p><strong>${review.author_name}</strong>: ${review.text}</p>`;
                    reviewList.appendChild(reviewElement);
                });

                // 檢查按鈕區塊是否存在
                let buttonContainer = document.getElementById("show-more-container");
                if (!buttonContainer) {
                    buttonContainer = document.createElement("div");
                    buttonContainer.id = "show-more-container";
                    reviewsContainer.appendChild(buttonContainer);
                }

                // **清空舊的按鈕，避免重複**
                buttonContainer.innerHTML = "";

                // **即使評論數量小於 10，也顯示按鈕**
                if (reviews.length > maxVisibleReviews || reviews.length <= maxVisibleReviews) {
                    const showMoreButton = document.createElement("button");
                    showMoreButton.textContent = showingAllReviews ? "顯示較少" : "顯示更多留言";
                    showMoreButton.addEventListener("click", () => {
                        showingAllReviews = !showingAllReviews;
                        renderReviews();
                    });

                    buttonContainer.appendChild(showMoreButton);
                    console.log("按鈕已加入:", buttonContainer.innerHTML); // 檢查按鈕是否出現
                }
            }

            renderReviews();
        } else {
            reviewsContainer.innerHTML += "<p>目前沒有評論</p>";
        }
    });
}


document.addEventListener("DOMContentLoaded", function () {
    const stationSelect = document.getElementById("station-select");

    stationSelect.addEventListener("change", () => {
        const selectedStation = stationSelect.value;
        document.getElementById('station-name').textContent = selectedStation;
        updateStationData(selectedStation);
    });
});

window.initMap = initMap;
