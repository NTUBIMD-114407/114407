"use strict";

let placesService;
let allRestaurants = [];

/* =============== 通知共用（收藏用） =============== */
const NOTIFY_KEY = "notifications_v1";
function loadNoti(){ try{return JSON.parse(localStorage.getItem(NOTIFY_KEY))||[];}catch{return[];} }
function saveNoti(list){ localStorage.setItem(NOTIFY_KEY, JSON.stringify(list)); }
function makeId(){ return (crypto.randomUUID && crypto.randomUUID()) || (Date.now()+Math.random().toString(36).slice(2)); }
// 名稱保底
function safeName(o){
  return (o && (o.name || o.restaurant_name || o.restaurantName || o.store_name || o.title)) || "未命名餐廳";
}
function pushFavoriteNotify(item, action="add"){
  const name = safeName(item);
  const noti = {
    id: makeId(),
    type: "favorite",
    title: action==="add" ? "已收藏美食" : "取消收藏",
    message: action==="add" ? `將「${name}」加入收藏` : `已取消「${name}」收藏`,
    time: new Date().toISOString(),
    read: false,
    item: { name, address: item.address || "", place_id: item.place_id || null }
  };
  const list = loadNoti();
  list.unshift(noti);
  saveNoti(list);
}
/* ================================================== */

/* ================= 收藏共用 ================= */
const FAV_KEY = "fav_restaurants_v1";
function loadFavs(){ try { return JSON.parse(localStorage.getItem(FAV_KEY)) || []; } catch { return []; } }
function saveFavs(list){ localStorage.setItem(FAV_KEY, JSON.stringify(list)); }
// 以 place_id 為優先；沒有就用 name@address
const favKey = d => (d.place_id ? `pid:${d.place_id}` : `${(d.name||"")}@${(d.address||"")}`);
function isFav(item){
  const k = favKey(item);
  return loadFavs().some(x => favKey(x) === k);
}
function toggleFav(item){
  const list = loadFavs();
  const k = favKey(item);
  const i = list.findIndex(x => favKey(x) === k);
  if (i === -1) { list.push(item); saveFavs(list); return true; }  // 加入 → 已收藏
  list.splice(i,1); saveFavs(list); return false;                  // 移除 → 未收藏
}
function setFavState(btn, saved){
  btn.textContent = saved ? "已收藏" : "收藏";
  btn.classList.toggle("active", saved);
}
/* ========================================= */

/* ===== 站點對照／距離工具 ===== */
const codeToIdMap = {};
const codeToNameMap = {};
const codeToCoordMap = {}; // 新增：站碼 → {lat,lng}
const WALK_M_PER_MIN = 80;
const haversine = (aLat,aLng,bLat,bLng) => {
  const R=6371000, rad=d=>d*Math.PI/180;
  const dLat=rad(bLat-aLat), dLng=rad(bLng-aLng);
  const s=Math.sin(dLat/2)**2 + Math.cos(rad(aLat))*Math.cos(rad(bLat))*Math.sin(dLng/2)**2;
  return 2*R*Math.asin(Math.sqrt(s));
};
const gmapsDir = (lat,lng)=>`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(lat+','+lng)}`;

window.addEventListener('load', async () => {
  const stationSelect = document.getElementById('station-select');
  const foodTitle = document.querySelector('.top3-food h3');
  const foodList = document.querySelector('.food-list');
  const confirmBtn = document.querySelector('.confirm-btn');
  const loadMoreBtn = document.querySelector('.load-more-btn');

  const dummyMap = new google.maps.Map(document.createElement('div'));
  placesService = new google.maps.places.PlacesService(dummyMap);

  try {
    const linesRes = await fetch('http://140.131.115.112:8000/api/lines/');
    const lines = await linesRes.json();

    for (const line of lines) {
      const stationsRes = await fetch(`http://140.131.115.112:8000/api/lines/${line.id}/stations/`);
      const stations = await stationsRes.json();

      stations.forEach(station => {
        codeToIdMap[station.station_code] = station.id;
        codeToNameMap[station.station_code] = station.name;
        // 盡量抓經緯度常見欄位
        const lat = parseFloat(station.latitude ?? station.lat);
        const lng = parseFloat(station.longitude ?? station.lng ?? station.lon);
        if (Number.isFinite(lat) && Number.isFinite(lng)) {
          codeToCoordMap[station.station_code] = { lat, lng };
        }

        const option = document.createElement('option');
        option.value = station.station_code;
        option.textContent = `${station.station_code} ${station.name}`;
        stationSelect.appendChild(option);
      });
    }

    if (stationSelect.options.length > 0) {
      stationSelect.selectedIndex = 0;
    }

    const userRes = await fetch('http://140.131.115.112:8000/api/accounts/user/', {
      credentials: 'include',
      headers: { 'Accept': 'application/json','Content-Type': 'application/json' }
    });
    if (!userRes.ok) throw new Error(`HTTP error! status: ${userRes.status}`);
    const user = await userRes.json();
    if (user.isAuthenticated && user.user) {
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('userEmail', user.user.email);
      localStorage.setItem('username', user.user.username);
    } else {
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('username');
    }
  } catch (err) {
    console.error('獲取使用者資訊失敗：', err);
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('username');
  }

  confirmBtn.addEventListener('click', async () => {
    const selectedCode = stationSelect.value;
    const stationId = codeToIdMap[selectedCode];
    const stationName = codeToNameMap[selectedCode];

    if (!stationId) {
      console.warn('⚠️ 找不到對應站點 ID', selectedCode);
      return;
    }

    foodTitle.textContent = `${stationName} 美食TOP3`;
    foodList.innerHTML = '<p>載入中...</p>';
    loadMoreBtn.style.display = 'none';
    allRestaurants = [];

    try {
      const res = await fetch(`http://140.131.115.112:8000/api/stations/${stationId}/restaurants/`);
      const data = await res.json();

      foodList.innerHTML = '';
      allRestaurants = data;

      if (data.length === 0) {
        foodList.innerHTML = '<p>目前尚無推薦美食</p>';
        return;
      }

      const preview = data.slice(0, 3);
      const results = await enrichWithPhotos(preview);
      renderRestaurantCards(results);   // ✅ 下面已內建「導航 + 距離」

      if (data.length > 3) loadMoreBtn.style.display = 'block';
    } catch (err) {
      foodList.innerHTML = '<p>⚠️ 餐廳資料載入失敗</p>';
      console.error('🚨 取得餐廳資料失敗：', err);
    }
  });

  loadMoreBtn.addEventListener('click', async () => {
    const more = allRestaurants.slice(3);
    const results = await enrichWithPhotos(more);
    renderRestaurantCards(results);     // ✅ 依然會帶導航 + 距離
    loadMoreBtn.style.display = 'none';
  });
});

async function enrichWithPhotos(list) {
  return await Promise.all(list.map(async item => {
    let photoUrl = await getPhotoFromGoogle(item.place_id);
    if (!photoUrl && item.name && item.address) {
      photoUrl = await getPhotoByQuery(`${item.name}, ${item.address}`);
    }
    return { ...item, photoUrl: photoUrl || 'https://via.placeholder.com/400x200?text=No+Image' };
  }));
}

function renderRestaurantCards(list) {
  const foodList = document.querySelector('.food-list');
  const stationSelect = document.getElementById('station-select');
  const selectedCode = stationSelect?.value || null;
  const selectedStationName = (selectedCode && codeToNameMap[selectedCode]) || "";
  const selectedCoord = (selectedCode && codeToCoordMap[selectedCode]) || null;

  list.forEach(item => {
    const card = document.createElement('div');
    card.className = 'food-item';

    // 收藏要存的 payload
    const payload = {
      name: item.name || item.restaurant_name || "未命名餐廳",
      address: item.address || "",
      rating: item.rating ?? null,
      review_count: item.user_ratings_total ?? null,
      opening_text: "",
      price_text: item.price_text || "",
      lat: item.latitude ?? null,
      lng: item.longitude ?? null,
      website: item.website || "",
      image: item.photoUrl || "",
      place_id: item.place_id || null
    };

    // 計算距離（若站點或餐廳缺座標就不顯示）
    let distanceLine = "";
    const rlat = parseFloat(item.latitude), rlng = parseFloat(item.longitude);
    if (selectedCoord && Number.isFinite(rlat) && Number.isFinite(rlng)) {
      const d = Math.round(haversine(selectedCoord.lat, selectedCoord.lng, rlat, rlng)); // 公尺
      const m = Math.max(1, Math.round(d / WALK_M_PER_MIN)); // 步行分鐘（80m/分）
      distanceLine = `
        <p class="distance-line" style="margin:6px 0 0; color:#475569;">
          🚶 距離${selectedStationName}站約 <b>${d}</b> 公尺（步行約 <b>${m}</b> 分鐘）
        </p>`;
    }

    // 導航連結（開啟 Google Maps 導航）
    const navHref = (Number.isFinite(rlat) && Number.isFinite(rlng)) ? gmapsDir(rlat, rlng) : "#";

    card.innerHTML = `
      <h4 class="section-title">🏢 商家資訊</h4>
      <img src="${item.photoUrl}" alt="${safeName(item)}" class="restaurant-img" loading="lazy">
      <h4 class="restaurant-name" style="font-size: 18px; color: #2c3e50; font-weight: bold; margin-top: 8px;">
        <a href="#" onclick='goToStationPage(${JSON.stringify(item).replace(/'/g, "\\'")})' style="text-decoration: none; color: #2c3e50;">
          ${safeName(item)}
        </a>
      </h4>
      <p class="rating">⭐ 評分：${item.rating || '無評分'}</p>
      <p class="address">${item.address || '地址未知'}</p>

      <div class="btn-group">
        <button class="review-btn" onclick="fetchReviews('${item.id}', '${safeName(item)}')">查看評論</button>
        <button class="fav-btn">收藏</button>
        <a class="nav-btn" href="${navHref}" target="_blank" rel="noopener">導航</a>
        <button class="close-btn" onclick="this.closest('.food-item').remove()">關閉</button>
      </div>

      ${distanceLine}
    `;

    // 收藏鈕
    const favBtn = card.querySelector('.fav-btn');
    setFavState(favBtn, isFav(payload));
    favBtn.addEventListener('click', () => {
      const saved = toggleFav(payload);
      setFavState(favBtn, saved);
      pushFavoriteNotify(payload, saved ? "add" : "remove");
    });

    foodList.appendChild(card);
  });
}

async function getPhotoFromGoogle(placeId) {
  return new Promise((resolve) => {
    if (!placesService || !placeId) return resolve(null);
    const request = { placeId, fields: ['photos'] };
    placesService.getDetails(request, (place, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && place.photos?.length) {
        resolve(place.photos[0].getUrl({ maxWidth: 400 }));
      } else {
        resolve(null);
      }
    });
  });
}

async function getPhotoByQuery(query) {
  return new Promise((resolve) => {
    if (!placesService || !query) return resolve(null);
    const request = { query, fields: ['place_id'] };
    placesService.findPlaceFromQuery(request, (results, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && results.length > 0) {
        getPhotoFromGoogle(results[0].place_id).then(resolve);
      } else {
        resolve(null);
      }
    });
  });
}

function fetchReviews(restaurantId, name) {
  fetch(`http://140.131.115.112:8000/api/restaurants/${restaurantId}/`)
    .then(res => res.json())
    .then(data => {
      const placeId = data.place_id;
      if (placeId) {
        const url = `https://www.google.com/maps/search/?api=1&query=Google&query_place_id=${placeId}`;
        window.open(url, '_blank');
      } else {
        const query = encodeURIComponent(`${data.name} ${data.address}`);
        const fallbackUrl = `https://www.google.com/maps/search/?api=1&query=${query}`;
        window.open(fallbackUrl, '_blank');
      }
    })
    .catch(err => {
      console.error('❌ 錯誤', err);
      alert('無法載入評論頁面');
    });
}

function goToStationPage(item) {
  const stationSelect = document.getElementById('station-select');
  const selectedOption = stationSelect.options[stationSelect.selectedIndex];
  const stationName = selectedOption.textContent.split(' ').slice(1).join(' ');

  localStorage.setItem('selectedRestaurant', JSON.stringify({
    ...item,
    station: stationName,
    latitude: item.latitude,
    longitude: item.longitude
  }));

  window.location.href = 'review.html';
}
