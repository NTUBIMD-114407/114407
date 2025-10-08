// static/js/food_mission/detail.js
"use strict";

let selectedStars = 0;
let allRestaurants = [];
let latestSelectedRestaurant = null;

let map, geocoder, placesService;
let restaurantAddress = null;
let fallbackName = null;
let lastPlaceId = null;

// ★ 目前登入者資料（沒登入就全為 null）
const currentUser = {
  loggedIn: false,
  name: null,     // display_name > username > email
  email: null,
  avatar: null,   // avatar_url
};

/* ---------- Google Map ---------- */
function initMap() {
  geocoder = new google.maps.Geocoder();
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 16,
    center: { lat: 25.0330, lng: 121.5654 }
  });
  // 仍用 PlacesService（官方建議改 Place，但這版可相容）
  placesService = new google.maps.places.PlacesService(map);

  if (restaurantAddress) {
    geocodeAddress(restaurantAddress);
  } else if (fallbackName) {
    geocodeByName(fallbackName);
  }
}
window.initMap = initMap;

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
      lastPlaceId = results[0].place_id || null;
      placesService.getDetails(
        {
          placeId: lastPlaceId,
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

/* ---------- 套資料到頁面（避免重複） ---------- */
function updatePlaceUI(place) {
  const info = document.querySelector(".store-text");

  // 店名（保底）
  const nameEl = document.querySelector(".store-name");
  if (!nameEl.textContent || nameEl.textContent === "店家") {
    nameEl.textContent = place.name || nameEl.textContent;
  }

  // ⭐ 評分＋評論數
  let starTagEl = document.querySelector(".star-tag");
  let reviewCntEl = document.querySelector(".review-count");
  if (!starTagEl) {
    const ratingLine = document.querySelector(".rating-line") || info;
    starTagEl = document.createElement("span");
    starTagEl.className = "star-tag";
    ratingLine.appendChild(starTagEl);
  }
  if (!reviewCntEl) {
    const ratingLine = document.querySelector(".rating-line") || info;
    reviewCntEl = document.createElement("span");
    reviewCntEl.className = "review-count";
    ratingLine.appendChild(reviewCntEl);
  }
  if (place.rating != null && place.user_ratings_total != null) {
    starTagEl.textContent   = `⭐ ${Number(place.rating).toFixed(1)}`;
    reviewCntEl.textContent = `（${place.user_ratings_total} 則 Google 評論）`;
  }

  // 🕒 今日營業時間（僅一行）
  if (place.opening_hours?.weekday_text) {
    const days = place.opening_hours.weekday_text;
    const today = new Date().getDay();          // Sun=0
    const idx = today === 0 ? 6 : today - 1;    // Mon=0

    let hoursEl = document.querySelector(".hours-line");
    if (!hoursEl) {
      hoursEl = document.createElement("p");
      hoursEl.className = "hours-line";
      hoursEl.style.fontSize = "14px";
      hoursEl.style.margin = "4px 0";
      const ratingLine = document.querySelector(".rating-line");
      (ratingLine || info).insertAdjacentElement("afterend", hoursEl);
    }
    hoursEl.textContent = `🕒 ${days[idx]}`;
  }

  // 圖片
  if (place.photos?.length) {
    const imageUrl = place.photos[0].getUrl();
    const imageDiv = document.querySelector(".store-image");
    imageDiv.style.backgroundImage = `url(${imageUrl})`;
    imageDiv.style.backgroundSize = "cover";
    imageDiv.style.backgroundPosition = "center";
  }

  // 地址（若尚未填）
  if (!restaurantAddress && place.formatted_address) {
    restaurantAddress = place.formatted_address;
    const addrEl = document.querySelector(".address");
    addrEl.textContent = `店家地址｜${restaurantAddress}`;
  }

  // 「Google評論」按鈕
  const btn = document.querySelector(".google-btn");
  if (btn) {
    const openUrl = place.url
      ? place.url
      : (lastPlaceId
          ? `https://www.google.com/maps/search/?api=1&query=Google&query_place_id=${lastPlaceId}`
          : `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(nameEl.textContent)}`);
    btn.onclick = () => window.open(openUrl, "_blank");
  }
}

/* ---------- 會員中心：名稱 & 頭像 ---------- */
async function getProfile() {
  try {
    const res = await fetch("http://140.131.115.112:8000/api/accounts/profile/", {
      credentials: "include",
      headers: { Accept: "application/json" }
    });
    if (!res.ok) return null;
    const data = await res.json();
    // 後端若欄位不同，這裡按實際鍵名取值
    return {
      loggedIn: true,
      name: data.display_name || data.username || data.email || null,
      email: data.email || null,
      avatar: data.avatar_url || null
    };
  } catch {
    return null;
  }
}

/** 只把「屬於自己」的評論卡換成大頭貼（其他人維持 👤） */
function applySelfAvatarToReviews() {
  if (!currentUser.loggedIn || !currentUser.avatar) return;

  document.querySelectorAll("section.review").forEach(sec => {
    const nameEl = sec.querySelector(".review-meta p");
    if (!nameEl) return;
    const who = (nameEl.textContent || "").trim();
    if (who && (who === currentUser.name || who === currentUser.email)) {
      const pic = sec.querySelector(".user-pic");
      if (pic) {
        pic.style.background = `center/cover no-repeat url("${currentUser.avatar}")`;
        pic.textContent = "";
        pic.style.borderRadius = "50%";
      }
    }
  });
}

/* ---------- 主流程 ---------- */
document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const restaurantName = params.get("name");

  if (!restaurantName) {
    alert("❌ 餐廳名稱未指定！");
    return;
  }

  // 先把店名寫上
  document.querySelector(".store-name").textContent = restaurantName;

  // 預設評分
  document.querySelector(".star-tag").textContent = "⭐ 平均星數：—";
  document.querySelector(".review-count").textContent = "(0 則評論)";

  fallbackName = restaurantName;

  // 先查登入者資訊（之後渲染評論時可用）
  const profile = await getProfile();
  if (profile) Object.assign(currentUser, profile);

  try {
    const res = await fetch(
      `http://140.131.115.112:8000/api/api/checkin-reviews/list/?restaurant_name=${encodeURIComponent(restaurantName)}`
    );
    const json = await res.json();
    const reviews = json.reviews || [];

    if (reviews.length > 0) {
      document.querySelector(".star-tag").textContent = `⭐ 平均星數：${reviews[0].rating}`;
      document.querySelector(".review-count").textContent = `(${reviews.length} 則評論)`;
    } else {
      document.querySelector(".review-title").insertAdjacentHTML("beforeend", "<p>⚠️ 尚無評論</p>");
    }

    // 地址：評論有就用，否則排行榜補
    restaurantAddress =
      (reviews[0] && reviews[0].address) || (await fetchRestaurantAddress(restaurantName));
    document.querySelector(".address").textContent =
      `店家地址｜${restaurantAddress || "未提供"}`;

    // 先清掉舊評論，再渲染
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
        // ★ 若後端沒給 reviewer_name，就用登入者名稱；未登入就「訪客」
        const displayName = r.reviewer_name || (currentUser.loggedIn ? currentUser.name : "訪客");

        const section = document.createElement("section");
        section.className = "review";
        section.innerHTML = `
          <div class="user-pic">👤</div>
          <div class="review-meta">
            <p>${displayName || "訪客"}</p>
            <p>${r.created_at ? new Date(r.created_at).toLocaleDateString() : ""}</p>
          </div>
          <div class="review-box">${r.comment || ""}</div>
        `;
        container.appendChild(section);
      }

      // 僅把屬於「自己」的評論卡換成頭像；其他維持 👤
      applySelfAvatarToReviews();
    }

    // 等地圖 API 來後才 init（避免 initMap 未定義）
    const wait = setInterval(() => {
      if (window.google?.maps?.Map) {
        clearInterval(wait);
        initMap();
      }
    }, 200);
  } catch (err) {
    console.error("🚨 載入評論失敗：", err);
    alert("❌ 無法載入評論資料");
    const wait = setInterval(() => {
      if (window.google?.maps?.Map) {
        clearInterval(wait);
        initMap();
      }
    }, 200);
  }

  // 其他按鈕
  const bookBtn = document.querySelector(".book-btn");
  if (bookBtn) {
    bookBtn.addEventListener("click", () => {
      const q = encodeURIComponent(fallbackName || "餐廳");
      window.open(`https://www.google.com/search?q=${q}+線上訂位`, "_blank");
    });
  }
  const shareBtn = document.querySelector(".share-btn");
  if (shareBtn) {
    shareBtn.addEventListener("click", async () => {
      const title = document.querySelector(".store-name").textContent || fallbackName || "餐廳";
      const url = window.location.href;
      const text = `推薦這家餐廳給你：${title}`;
      if (navigator.share) {
        try { await navigator.share({ title, text, url }); }
        catch (e) { console.error("❌ 分享失敗：", e); }
      } else {
        alert("此裝置不支援分享，請手動複製網址");
      }
    });
  }
});

/* ---------- 幫你抓排行榜地址（備援） ---------- */
async function fetchRestaurantAddress(name) {
  const res = await fetch("http://140.131.115.112:8000/api/api/top-checkin-restaurants/");
  const json = await res.json();
  const match = (json.restaurants || []).find(r => r.restaurant_name === name);
  return match?.address || null;
}

/* ---------- 中文極簡關鍵字 ---------- */
function extractKeywords(text) {
  const common = ['的','了','和','是','在','我','有','也','很','吃','好','覺得','超'];
  const words = (text || "").replace(/[^一-龥]/g, '').split("");
  const count = {};
  for (const w of words) {
    if (w && !common.includes(w)) count[w] = (count[w] || 0) + 1;
  }
  return Object.entries(count)
    .sort((a,b)=>b[1]-a[1])
    .map(w=>w[0])
    .slice(0,3);
}

