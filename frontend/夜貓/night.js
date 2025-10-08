const stationData = {
    "R 淡水信義線": [
      { name: "象山", value: "R02" },
      { name: "台北101/世貿", value: "R03" },
      { name: "信義安和", value: "R04" },
      { name: "大安", value: "R05" },
      { name: "大安森林公園", value: "R06" },
      { name: "東門", value: "R07" },
      { name: "中正紀念堂", value: "R08" },
      { name: "台大醫院", value: "R09" },
      { name: "台北車站", value: "R10" },
      { name: "中山", value: "R11" },
      { name: "雙連", value: "R12" },
      { name: "民權西路", value: "R13" },
      { name: "圓山", value: "R14" },
      { name: "劍潭", value: "R15" },
      { name: "士林", value: "R16" },
      { name: "芝山", value: "R17" },
      { name: "明德", value: "R18" },
      { name: "石牌", value: "R19" },
      { name: "唭哩岸", value: "R20" },
      { name: "奇岩", value: "R21" },
      { name: "北投", value: "R22" },
      { name: "新北投", value: "R22A" },
      { name: "復興崗", value: "R23" },
      { name: "忠義", value: "R24" },
      { name: "關渡", value: "R25" },
      { name: "竹圍", value: "R26" },
      { name: "紅樹林", value: "R27" },
      { name: "淡水", value: "R28" }
    ],
    "G 松山新店線": [
      { name: "新店", value: "G01" },
      { name: "新店區公所", value: "G02" },
      { name: "七張", value: "G03" },
      { name: "小碧潭", value: "G03A" },
      { name: "大坪林", value: "G04" },
      { name: "景美", value: "G05" },
      { name: "萬隆", value: "G06" },
      { name: "公館", value: "G07" },
      { name: "台電大樓", value: "G08" },
      { name: "古亭", value: "G09" },
      { name: "中正紀念堂", value: "G10" },
      { name: "小南門", value: "G11" },
      { name: "西門", value: "G12" },
      { name: "北門", value: "G13" },
      { name: "中山", value: "G14" },
      { name: "松江南京", value: "G15" },
      { name: "南京復興", value: "G16" },
      { name: "台北小巨蛋", value: "G17" },
      { name: "南京三民", value: "G18" },
      { name: "松山", value: "G19" }
    ],
    "O 中和新蘆線": [
      { name: "南勢角", value: "O01" },
      { name: "景安", value: "O02" },
      { name: "永安市場", value: "O03" },
      { name: "頂溪", value: "O04" },
      { name: "古亭", value: "O05" },
      { name: "東門", value: "O06" },
      { name: "忠孝新生", value: "O07" },
      { name: "松江南京", value: "O08" },
      { name: "行天宮", value: "O09" },
      { name: "中山國小", value: "O10" },
      { name: "民權西路", value: "O11" },
      { name: "大橋頭", value: "O12" },
      { name: "台北橋", value: "O13" },
      { name: "菜寮", value: "O14" },
      { name: "三重", value: "O15" },
      { name: "先嗇宮", value: "O16" },
      { name: "頭前庄", value: "O17" },
      { name: "新莊", value: "O18" },
      { name: "輔大", value: "O19" },
      { name: "丹鳳", value: "O20" },
      { name: "迴龍", value: "O21" },
      { name: "三重國小", value: "O50" },
      { name: "三和國中", value: "O51" },
      { name: "徐匯中學", value: "O52" },
      { name: "三民高中", value: "O53" },
      { name: "蘆洲", value: "O54" }
    ],
    "BL 板南線": [
      { name: "頂埔", value: "BL01" },
      { name: "永寧", value: "BL02" },
      { name: "土城", value: "BL03" },
      { name: "海山", value: "BL04" },
      { name: "亞東醫院", value: "BL05" },
      { name: "府中", value: "BL06" },
      { name: "板橋", value: "BL07" },
      { name: "新埔", value: "BL08" },
      { name: "江子翠", value: "BL09" },
      { name: "龍山寺", value: "BL10" },
      { name: "西門", value: "BL11" },
      { name: "台北車站", value: "BL12" },
      { name: "善導寺", value: "BL13" },
      { name: "忠孝新生", value: "BL14" },
      { name: "忠孝復興", value: "BL15" },
      { name: "忠孝敦化", value: "BL16" },
      { name: "國父紀念館", value: "BL17" },
      { name: "市政府", value: "BL18" },
      { name: "永春", value: "BL19" },
      { name: "後山埤", value: "BL20" },
      { name: "昆陽", value: "BL21" },
      { name: "南港", value: "BL22" },
      { name: "南港展覽館", value: "BL23" }
    ]
  };
// ====== 夜貓美食頁 JS（含：地圖、搜尋、卡片、評論彈窗＋距離與導航、末五班車）======
/* ===== 夜貓美食頁 JS（地圖／搜尋／卡片／評論彈窗＋距離與導航＋末五班車）=====
 * Google Maps 請用：
 * <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_KEY&libraries=places&callback=initMap" async defer></script>
 */

//// 你的 stationData 保留在檔案上方 ////

let map;
let marker;
let isMapReady = false;

// 目前選到的捷運站（文字）
let currentSelectedStation = null;

// 座標快取（站名、地址都可當 key）
const stationCoordCache = Object.create(null);
const addressCoordCache = Object.create(null);

document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.querySelector('.search-bar input');
  const recommendContainer = document.querySelector('.recommend-container');

  // datalist：站名自動完成
  const dataList = document.createElement('datalist');
  dataList.id = 'station-options';
  document.body.appendChild(dataList);
  if (searchInput) searchInput.setAttribute('list', 'station-options');

  let allRestaurants = [];

  // 取夜貓餐廳資料
  fetch('http://140.131.115.112:8000/api/api/restaurants/night/')
    .then((response) => response.json())
    .then((data) => {
      allRestaurants = data.results || [];
      const stationsSet = new Set();

      allRestaurants.forEach((item) => {
        (item.stations || []).forEach((s) => stationsSet.add(s));
      });

      // 填 datalist
      stationsSet.forEach((station) => {
        const option = document.createElement('option');
        option.value = station;
        dataList.appendChild(option);
      });
    })
    .catch((error) => {
      console.error('載入站點失敗:', error);
    });

  // 切換站名 → 篩餐廳 + 移動地圖
  if (searchInput) {
    searchInput.addEventListener('change', function () {
      if (!isMapReady) {
        alert('地圖還在載入中，請稍後再試喔！');
        return;
      }
      const selectedStation = searchInput.value.trim();
      if (!selectedStation) return;

      // 記住目前站名
      currentSelectedStation = selectedStation;

      const filteredRestaurants = allRestaurants.filter(
        (r) => Array.isArray(r.stations) && r.stations.includes(selectedStation)
      );

      updateRecommendSection(filteredRestaurants);

      if (filteredRestaurants.length > 0) {
        moveMapToAddress(filteredRestaurants[0].address, filteredRestaurants[0].name);
      }
    });
  }

  // 生成餐廳卡片
  function updateRecommendSection(restaurants) {
    if (!recommendContainer) return;
    recommendContainer.innerHTML = '';

    if (!restaurants.length) {
      recommendContainer.innerHTML = '<p>找不到符合的店家。</p>';
      return;
    }

    restaurants.forEach((item) => {
      const foodCard = document.createElement('div');
      foodCard.className = 'food-card';

      const imageBox = document.createElement('div');
      imageBox.className = 'image-box';

      const img = document.createElement('img');
      img.style.width = '100%';
      img.style.height = '100%';
      img.style.borderRadius = '5px';
      img.src = '圖片/store1.png'; // 預設
      imageBox.appendChild(img);

      const nameP = document.createElement('p');
      nameP.textContent = item.name;
      nameP.style.cursor = 'pointer';
      nameP.style.fontWeight = 'bold';
      nameP.addEventListener('click', function () {
        moveMapToAddress(item.address, item.name);
      });

      const descP = document.createElement('p');
      descP.textContent = item.description || '商圈介紹';

      const starsDiv = document.createElement('div');
      starsDiv.className = 'stars';
      starsDiv.innerHTML = generateStars(item.rating);

      const moreBtn = document.createElement('button');
      moreBtn.className = 'more-btn';
      moreBtn.textContent = 'MORE';
      moreBtn.addEventListener('click', function () {
        showMorePopup(item);
      });

      foodCard.appendChild(imageBox);
      foodCard.appendChild(nameP);
      foodCard.appendChild(descP);
      foodCard.appendChild(starsDiv);
      foodCard.appendChild(moreBtn);
      recommendContainer.appendChild(foodCard);

      // 取 Google 照片（PlacesService；新專案會看到建議改用 Place）
      getPhotoUrlByPlaceName(item.name, function (photoUrl) {
        if (photoUrl) img.src = photoUrl;
      });
    });
  }

  // 以名稱找 Google 照片
  function getPhotoUrlByPlaceName(placeName, callback) {
    if (!window.google?.maps?.places) return callback(null);
    const service = new google.maps.places.PlacesService(document.createElement('div'));
    const request = { query: placeName, fields: ['photos'] };

    service.findPlaceFromQuery(request, (results, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && results?.[0]?.photos?.length) {
        const photoUrl = results[0].photos[0].getUrl({ maxWidth: 400 });
        callback(photoUrl);
      } else {
        callback(null);
      }
    });
  }

  // 生成星星
  function generateStars(rating) {
    if (!rating) rating = 0;
    const fullStar = '⭐';
    const halfStar = '✩';
    const emptyStar = '☆';
    let starsHTML = '';
    const rounded = Math.round(rating * 2) / 2;

    for (let i = 1; i <= 5; i++) {
      if (rounded >= i) starsHTML += fullStar;
      else if (rounded + 0.5 === i) starsHTML += halfStar;
      else starsHTML += emptyStar;
    }
    return starsHTML;
  }

  // 地圖移動到指定地址
  function moveMapToAddress(address, title) {
    if (!isMapReady) return console.error('地圖尚未初始化');
    if (!address) return;

    // 快取地址座標
    if (addressCoordCache[address]) {
      centerMap(addressCoordCache[address], title);
      return;
    }

    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address }, (results, status) => {
      if (status === 'OK' && results[0]) {
        const loc = results[0].geometry.location;
        const pos = { lat: loc.lat(), lng: loc.lng() };
        addressCoordCache[address] = pos;
        centerMap(pos, title);
      } else {
        console.error('地址轉換失敗:', status);
      }
    });
  }

  function centerMap(position, title) {
    map.setCenter(position);
    map.setZoom(17);
    if (marker) marker.setMap(null);
    marker = new google.maps.Marker({ map, position, title });
  }

  // ====== 工具：站名→座標、直線距離 ======

  // 依站名拿站點座標（先找 stationData，有就用；否則用 Geocoder 查「站名 + 捷運站」）
  async function getStationLatLngByName(name) {
    if (!name) return null;

    // 先看快取
    if (stationCoordCache[name]) return stationCoordCache[name];

    // 1) 試著從 stationData 取（如果未來你補上 lat/lng 就會走這裡）
    if (typeof stationData === 'object' && stationData) {
      for (const line in stationData) {
        const hit = stationData[line].find((s) => s.name === name && s.lat && s.lng);
        if (hit) {
          const found = { lat: hit.lat, lng: hit.lng, name: hit.name };
          stationCoordCache[name] = found;
          return found;
        }
      }
    }

    // 2) 沒有 lat/lng，改用 Geocoder 解析「站名 + 捷運站」
    const geocoder = new google.maps.Geocoder();
    const query = `${name} 捷運站`;
    const result = await new Promise((resolve) => {
      geocoder.geocode({ address: query }, (results, status) => {
        if (status === 'OK' && results && results.length) {
          const loc = results[0].geometry.location;
          resolve({ lat: loc.lat(), lng: loc.lng(), name });
        } else {
          resolve(null);
        }
      });
    });

    if (result) stationCoordCache[name] = result;
    return result;
  }

  // Haversine：兩點直線距離（公尺）
  function haversineMeters(a, b) {
    const R = 6371000;
    const dLat = ((b.lat - a.lat) * Math.PI) / 180;
    const dLng = ((b.lng - a.lng) * Math.PI) / 180;
    const lat1 = (a.lat * Math.PI) / 180;
    const lat2 = (b.lat * Math.PI) / 180;
    const x =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2;
    const d = 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
    return Math.round(R * d);
  }

  // ====== 彈窗（含：距離 + 導航） ======
  async function showMorePopup(item) {
    const overlay = document.createElement('div');
    overlay.className = 'popup-overlay';

    const popup = document.createElement('div');
    popup.className = 'popup-card';

    // 營業時間
    let businessHoursText = '無資料';
    if (Array.isArray(item.business_hours)) {
      businessHoursText = item.business_hours.map((obj) => `${obj.day} ${obj.hours}`).join('<br>');
    }

    const distanceHTML =
      '<div class="distance-line" style="margin:8px 0 10px;font-size:14px;color:#333;">計算距離中…</div>';

    popup.innerHTML = `
      <h3>推薦美食</h3>
      <div class="popup-content">
        <p><strong>${item.name}</strong></p>
        <p>${item.stations ? item.stations.join('、') : '捷運站未知'}</p>
        <p><strong>營業時間：</strong><br>${businessHoursText}</p>
        <div class="stars">${generateStars(item.rating)}</div>

        ${distanceHTML}

        <div class="btn-row" style="display:flex;gap:8px;justify-content:center;margin-top:6px;">
          <button class="nav-btn">導航</button>
          <button class="back-btn">BACK</button>
        </div>
      </div>
    `;

    overlay.appendChild(popup);
    document.body.appendChild(overlay);

    const backBtn = popup.querySelector('.back-btn');
    const navBtn = popup.querySelector('.nav-btn');
    const distanceLine = popup.querySelector('.distance-line');

    backBtn.addEventListener('click', () => document.body.removeChild(overlay));

    // 起點：優先用目前選到的站；沒有就用此店第一個站
    const stationName =
      currentSelectedStation ||
      (Array.isArray(item.stations) && item.stations.length ? item.stations[0] : null);

    // 起點座標（stationData 或 Geocoder）
    const origin = await getStationLatLngByName(stationName || '');

    // 目的地座標（快取地址 → Geocoder）
    let dest = null;
    if (item.address && addressCoordCache[item.address]) {
      dest = addressCoordCache[item.address];
    } else if (item.address) {
      const geocoder = new google.maps.Geocoder();
      dest = await new Promise((resolve) => {
        geocoder.geocode({ address: item.address }, (results, status) => {
          if (status === 'OK' && results?.length) {
            const loc = results[0].geometry.location;
            resolve({ lat: loc.lat(), lng: loc.lng() });
          } else {
            resolve(null);
          }
        });
      });
      if (dest) addressCoordCache[item.address] = dest;
    }

    // 顯示距離 & 綁定導航
    if (!dest) {
      distanceLine.textContent = '無法取得餐廳位置';
      navBtn.onclick = () => {
        const url = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(
          stationName || '捷運站'
        )}&destination=${encodeURIComponent(item.name)}&travelmode=walking`;
        window.open(url, '_blank');
      };
      return;
    }

    if (origin) {
      const meters = haversineMeters(origin, dest);
      const mins = Math.max(1, Math.round(meters / 80)); // 80m/分
      distanceLine.textContent = `距離「${origin.name}」約 ${meters.toLocaleString()} 公尺（步行約 ${mins} 分鐘）`;

      navBtn.onclick = () => {
        const url = `https://www.google.com/maps/dir/?api=1&origin=${origin.lat},${origin.lng}&destination=${dest.lat},${dest.lng}&travelmode=walking`;
        window.open(url, '_blank');
      };
    } else {
      distanceLine.textContent = '找不到對應的捷運站座標';
      navBtn.onclick = () => {
        const url = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(
          stationName || '捷運站'
        )}&destination=${dest.lat},${dest.lng}&travelmode=walking`;
        window.open(url, '_blank');
      };
    }
  }
});

// ====== Google Map 初始化（需在全域，供 callback 呼叫）======
window.initMap = function () {
  map = new google.maps.Map(document.querySelector('.map'), {
    center: { lat: 25.033, lng: 121.5654 },
    zoom: 14,
  });
  isMapReady = true;
};

// ====== 末五班車（保留你的功能；若 stationData 未含座標也不影響）======

// 1) 動態生成站名下拉
const stationSelect = document.getElementById('station-select');
if (stationSelect && typeof stationData === 'object' && stationData) {
  stationSelect.innerHTML = '';
  for (const lineName in stationData) {
    const optgroup = document.createElement('optgroup');
    optgroup.label = lineName;
    stationData[lineName].forEach((station) => {
      const option = document.createElement('option');
      option.value = station.name;
      option.textContent = station.name;
      optgroup.appendChild(option);
    });
    stationSelect.appendChild(optgroup);
  }

  // 2) 綁定查詢按鈕
  const queryBtn = document.getElementById('query-last-train');
  if (queryBtn) {
    queryBtn.addEventListener('click', async () => {
      const stationName = stationSelect.value;
      if (!stationName) {
        alert('請選擇車站');
        return;
      }

      const apiUrl = `http://140.131.115.112:8000/api/api/station-last-five-trains/?station_name=${encodeURIComponent(
        stationName
      )}`;

      try {
        const response = await fetch(apiUrl);
        if (!response.ok) throw new Error('回傳失敗');
        const result = await response.json();

        const target = document.getElementById('last-train-result');
        if (!Array.isArray(result) || result.length === 0) {
          target.innerHTML = '<p>查無資料</p>';
          return;
        }

        let displayHTML = '';
        result.forEach((direction) => {
          displayHTML += `
            <div class="train-block">
              <h4>${direction.station_name} → ${direction.destination}</h4>
              <p>行駛方向：${direction.direction}</p>
              <ul>
                ${direction.trains
                  .map((t) => `<li>第${t.train_sequence}班：${t.train_time}</li>`)
                  .join('')}
              </ul>
            </div>
            <hr/>
          `;
        });

        target.innerHTML = displayHTML;
      } catch (err) {
        console.error('錯誤：', err);
        document.getElementById('last-train-result').innerHTML =
          '<p>查詢失敗，請稍後再試。</p>';
      }
    });
  }
}





