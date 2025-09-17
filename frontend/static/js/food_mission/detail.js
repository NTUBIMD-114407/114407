let selectedStars = 0;
let allRestaurants = [];
let latestSelectedRestaurant = null;

let map, geocoder, placesService;
let restaurantAddress = null;
let fallbackName = null;

function initMap() {
  geocoder = new google.maps.Geocoder();
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 16,
    center: { lat: 25.0330, lng: 121.5654 }
  });
  placesService = new google.maps.places.PlacesService(map);

  if (restaurantAddress) {
    geocodeAddress(restaurantAddress);
  } else if (fallbackName) {
    geocodeByName(fallbackName);
  }
}

function geocodeAddress(address) {
  geocoder.geocode({ address }, (results, status) => {
    if (status === "OK") {
      const location = results[0].geometry.location;
      map.setCenter(location);
      new google.maps.Marker({ map, position: location });
      searchPlaceDetails(location);
    } else {
      console.error("📍 地址轉換失敗：", status);
    }
  });
}

function geocodeByName(name) {
  const query = `${name} 台灣`;
  geocoder.geocode({ address: query }, (results, status) => {
    if (status === "OK") {
      const location = results[0].geometry.location;
      map.setCenter(location);
      new google.maps.Marker({ map, position: location });
      searchPlaceDetails(location);
    } else {
      console.error("📍 餐廳名稱轉換失敗：", status);
    }
  });
}

function searchPlaceDetails(location) {
  const request = {
    location,
    radius: 200,
    keyword: fallbackName
  };

  placesService.nearbySearch(request, (results, status) => {
    if (status === google.maps.places.PlacesServiceStatus.OK && results[0]) {
      const placeId = results[0].place_id;
      placesService.getDetails(
        {
          placeId,
          fields: ["name", "rating", "user_ratings_total", "opening_hours", "photos", "url", "formatted_address"]
        },
        (place, status) => {
          if (status === google.maps.places.PlacesServiceStatus.OK) {
            updatePlaceUI(place);
          }
        }
      );
    } else {
      console.warn("❌ 未找到符合的 Google 商家");
    }
  });
}

function updatePlaceUI(place) {
  const info = document.querySelector(".store-text");

  if (place.rating && place.user_ratings_total) {
    const ratingText = `⭐ ${place.rating.toFixed(1)}（${place.user_ratings_total} 則 Google 評論）`;
    const star = document.createElement("p");
    star.style.margin = "4px 0";
    star.style.fontSize = "14px";
    star.textContent = ratingText;
    info.appendChild(star);
  }

  // 🕒 顯示今日營業時間
  if (place.opening_hours?.weekday_text) {
    const days = place.opening_hours.weekday_text;
    const today = new Date().getDay(); // Sunday = 0
    const index = today === 0 ? 6 : today - 1; // 轉換成 Monday = 0
    const todayText = days[index];
    const hoursText = document.createElement("p");
    hoursText.textContent = `🕒 ${todayText}`;
    hoursText.style.fontSize = "14px";
    info.appendChild(hoursText);
  }

  if (place.photos && place.photos.length > 0) {
    const imageUrl = place.photos[0].getUrl();
    const imageDiv = document.querySelector(".store-image");
    imageDiv.style.backgroundImage = `url(${imageUrl})`;
    imageDiv.style.backgroundSize = "cover";
    imageDiv.style.backgroundPosition = "center";
  }

  if (place.url) {
    const btn = document.querySelector(".google-btn");
    btn.addEventListener("click", () => {
      window.open(place.url, "_blank");
    });
  }
}

async function fetchRestaurantAddress(name) {
  const res = await fetch("http://140.131.115.112:8000/api/api/top-checkin-restaurants/");
  const json = await res.json();
  const match = json.restaurants.find(r => r.restaurant_name === name);
  return match?.address || null;
}

document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const restaurantName = params.get("name");

  if (!restaurantName) {
    alert("❌ 餐廳名稱未指定！");
    return;
  }

  fallbackName = restaurantName;

  try {
    const res = await fetch(`http://140.131.115.112:8000/api/api/checkin-reviews/list/?restaurant_name=${encodeURIComponent(restaurantName)}`);
    const json = await res.json();
    const reviews = json.reviews;

    if (!Array.isArray(reviews) || reviews.length === 0) {
      document.querySelector(".review-title").innerHTML += "<p>⚠️ 尚無評論</p>";
      return;
    }

    document.querySelector(".store-name").textContent = restaurantName;
    document.querySelector(".star-tag").textContent = `⭐ 平均星數：${reviews[0].rating}`;
    document.querySelector(".review-count").textContent = `(${reviews.length} 則評論)`;

    restaurantAddress = reviews[0].address || await fetchRestaurantAddress(restaurantName);
    document.querySelector(".address").textContent = `店家地址｜${restaurantAddress || "未提供"}`;

    const container = document.querySelector("main.store-container");
    document.querySelectorAll("section.review").forEach(e => e.remove());

    const allComments = reviews.map(r => r.comment).join(" ");
    const keywords = extractKeywords(allComments);
    const tagButtons = document.querySelector(".tags").querySelectorAll("button");
    tagButtons.forEach((btn, i) => {
      if (i === 0) return; // 第一顆保留均消價格
      btn.textContent = keywords[i - 1] || `關鍵字${i}`;
    });

    for (const r of reviews) {
      const section = document.createElement("section");
      section.className = "review";
      section.innerHTML = `
        <div class="user-pic">👤</div>
        <div class="review-meta">
          <p>${r.reviewer_name}</p>
          <p>${new Date(r.created_at).toLocaleDateString()}</p>
        </div>
        <div class="review-box">${r.comment}</div>
      `;
      container.appendChild(section);
    }

    const wait = setInterval(() => {
      if (typeof google !== 'undefined' && google.maps && google.maps.Map) {
        clearInterval(wait);
        initMap();
      }
    }, 200);
  } catch (err) {
    console.error("🚨 載入評論失敗：", err);
    alert("❌ 無法載入評論資料");
  }
});

function extractKeywords(text) {
  const common = ['的', '了', '和', '是', '在', '我', '有', '也', '很', '吃', '好', '覺得', '超'];
  const words = text.replace(/[^一-龥]/g, '').split("");
  const count = {};
  for (const word of words) {
    if (word.length > 0 && !common.includes(word)) {
      count[word] = (count[word] || 0) + 1;
    }
  }
  return Object.entries(count).sort((a, b) => b[1] - a[1]).map(w => w[0]).slice(0, 3);
}
document.querySelector('.book-btn').addEventListener('click', function () {
  const query = encodeURIComponent(fallbackName || "餐廳");
  window.open(`https://www.google.com/search?q=${query}+線上訂位`, '_blank');
});
document.querySelector('.share-btn').addEventListener('click', async () => {
  const title = document.querySelector('.store-name').textContent;
  const url = window.location.href;
  const text = `推薦這家餐廳給你：${title}`;

  if (navigator.share) {
    try {
      await navigator.share({ title, text, url });
    } catch (err) {
      console.error('❌ 分享失敗：', err);
    }
  } else {
    alert('❗ 此裝置不支援分享功能，請手動複製網址');
  }
});
