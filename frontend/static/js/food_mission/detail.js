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
    if (status === "OK" && results[0]) {
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
    if (status === "OK" && results[0]) {
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
  const request = { location, radius: 200, keyword: fallbackName };

  placesService.nearbySearch(request, (results, status) => {
    if (status === google.maps.places.PlacesServiceStatus.OK && results[0]) {
      const placeId = results[0].place_id;
      placesService.getDetails(
        {
          placeId,
          fields: [
            "name",
            "rating",
            "user_ratings_total",
            "opening_hours",
            "photos",
            "url",
            "formatted_address"
          ]
        },
        (place, st) => {
          if (st === google.maps.places.PlacesServiceStatus.OK) {
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

  // 名稱補上（如果還是預設值或空）
  const nameEl = document.querySelector(".store-name");
  if (!nameEl.textContent || nameEl.textContent === "店家") {
    nameEl.textContent = place.name || nameEl.textContent;
  }

  // 評分
  if (place.rating && place.user_ratings_total) {
    const ratingText = `⭐ ${place.rating.toFixed(1)}（${place.user_ratings_total} 則 Google 評論）`;
    const star = document.createElement("p");
    star.style.margin = "4px 0";
    star.style.fontSize = "14px";
    star.textContent = ratingText;
    info.appendChild(star);
  }

  // 🕒 今日營業時間
  if (place.opening_hours?.weekday_text) {
    const days = place.opening_hours.weekday_text;
    const today = new Date().getDay();         // Sun=0
    const index = today === 0 ? 6 : today - 1; // Mon=0
    const hoursText = document.createElement("p");
    hoursText.textContent = `🕒 ${days[index]}`;
    hoursText.style.fontSize = "14px";
    info.appendChild(hoursText);
  }

  // 照片
  if (place.photos?.length) {
    const imageUrl = place.photos[0].getUrl();
    const imageDiv = document.querySelector(".store-image");
    imageDiv.style.backgroundImage = `url(${imageUrl})`;
    imageDiv.style.backgroundSize = "cover";
    imageDiv.style.backgroundPosition = "center";
  }

  // 地址（如果之前沒有）
  if (!restaurantAddress && place.formatted_address) {
    restaurantAddress = place.formatted_address;
    const addrEl = document.querySelector(".address");
    addrEl.textContent = `店家地址｜${restaurantAddress}`;
  }

  // Google 按鈕
  const btn = document.querySelector(".google-btn");
  if (btn && place.url) {
    btn.onclick = () => window.open(place.url, "_blank");
  }
}

async function fetchRestaurantAddress(name) {
  const res = await fetch("http://140.131.115.112:8000/api/api/top-checkin-restaurants/");
  const json = await res.json();
  const match = (json.restaurants || []).find(r => r.restaurant_name === name);
  return match?.address || null;
}

document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const restaurantName = params.get("name");

  if (!restaurantName) {
    alert("❌ 餐廳名稱未指定！");
    return;
  }

  // ✅ 先把店名寫上（無論後續是否有評論）
  document.querySelector(".store-name").textContent = restaurantName;

  // 評分區先給預設
  document.querySelector(".star-tag").textContent = "⭐ 平均星數：—";
  document.querySelector(".review-count").textContent = "(0 則評論)";

  fallbackName = restaurantName;

  try {
    const res = await fetch(
      `http://140.131.115.112:8000/api/api/checkin-reviews/list/?restaurant_name=${encodeURIComponent(restaurantName)}`
    );
    const json = await res.json();
    const reviews = json.reviews || [];

    // 有評論再更新平均星數與數量
    if (reviews.length > 0) {
      document.querySelector(".star-tag").textContent = `⭐ 平均星數：${reviews[0].rating}`;
      document.querySelector(".review-count").textContent = `(${reviews.length} 則評論)`;
    } else {
      document.querySelector(".review-title").innerHTML += "<p>⚠️ 尚無評論</p>";
    }

    // 地址：評論內有就用，否則打排行榜 API 補
    restaurantAddress =
      (reviews[0] && reviews[0].address) || (await fetchRestaurantAddress(restaurantName));
    document.querySelector(".address").textContent =
      `店家地址｜${restaurantAddress || "未提供"}`;

    // 關鍵字（只在有評論時跑）
    const container = document.querySelector("main.store-container");
    document.querySelectorAll("section.review").forEach(e => e.remove());

    if (reviews.length > 0) {
      const allComments = reviews.map(r => r.comment || "").join(" ");
      const keywords = extractKeywords(allComments);
      const tagButtons = document.querySelector(".tags").querySelectorAll("button");
      tagButtons.forEach((btn, i) => {
        if (i === 0) return; // 第一顆保留均消
        btn.textContent = keywords[i - 1] || `關鍵字${i}`;
      });

      for (const r of reviews) {
        const section = document.createElement("section");
        section.className = "review";
        section.innerHTML = `
          <div class="user-pic">👤</div>
          <div class="review-meta">
            <p>${r.reviewer_name || "匿名"}</p>
            <p>${r.created_at ? new Date(r.created_at).toLocaleDateString() : ""}</p>
          </div>
          <div class="review-box">${r.comment || ""}</div>
        `;
        container.appendChild(section);
      }
    }

    // 等地圖 API 來後就初始化（無論有沒有評論/地址都會跑）
    const wait = setInterval(() => {
      if (window.google?.maps?.Map) {
        clearInterval(wait);
        initMap();
      }
    }, 200);
  } catch (err) {
    console.error("🚨 載入評論失敗：", err);
    alert("❌ 無法載入評論資料");

    // 即使失敗也嘗試只用名稱開地圖
    const wait = setInterval(() => {
      if (window.google?.maps?.Map) {
        clearInterval(wait);
        initMap();
      }
    }, 200);
  }

  // 放到 DOMContentLoaded 裡，確保 fallbackName 已設定
  const bookBtn = document.querySelector('.book-btn');
  if (bookBtn) {
    bookBtn.addEventListener('click', () => {
      const q = encodeURIComponent(fallbackName || "餐廳");
      window.open(`https://www.google.com/search?q=${q}+線上訂位`, '_blank');
    });
  }

  const shareBtn = document.querySelector('.share-btn');
  if (shareBtn) {
    shareBtn.addEventListener('click', async () => {
      const title = document.querySelector('.store-name').textContent || fallbackName || "餐廳";
      const url = window.location.href;
      const text = `推薦這家餐廳給你：${title}`;
      if (navigator.share) {
        try { await navigator.share({ title, text, url }); } 
        catch (err) { console.error('❌ 分享失敗：', err); }
      } else {
        alert('❗ 此裝置不支援分享功能，請手動複製網址');
      }
    });
  }
});

function extractKeywords(text) {
  const common = ['的','了','和','是','在','我','有','也','很','吃','好','覺得','超'];
  const words = (text || "").replace(/[^一-龥]/g, '').split("");
  const count = {};
  for (const w of words) {
    if (w && !common.includes(w)) count[w] = (count[w] || 0) + 1;
  }
  return Object.entries(count).sort((a,b)=>b[1]-a[1]).map(w=>w[0]).slice(0,3);
}
