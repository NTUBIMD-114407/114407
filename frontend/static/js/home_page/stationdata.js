// 放在檔案最上面與 let map... 同一層
const stationCoordCache = {}; // { '板橋': {lat:25.xxx, lng:121.xxx, name:'板橋'} }

const stationData = {
    "BR 文湖線": [
      { name: "動物園", value: "BR01" },
      { name: "木柵", value: "BR02" },
      { name: "萬芳社區", value: "BR03" },
      { name: "萬芳醫院", value: "BR04" },
      { name: "辛亥", value: "BR05" },
      { name: "麟光", value: "BR06" },
      { name: "六張犁", value: "BR07" },
      { name: "科技大樓", value: "BR08" },
      { name: "大安", value: "BR09" },
      { name: "忠孝復興", value: "BR10" },
      { name: "南京復興", value: "BR11" },
      { name: "中山國中", value: "BR12" },
      { name: "松山機場", value: "BR13" },
      { name: "大直", value: "BR14" },
      { name: "劍南路", value: "BR15" },
      { name: "西湖", value: "BR16" },
      { name: "港墘", value: "BR17" },
      { name: "文德", value: "BR18" },
      { name: "內湖", value: "BR19" },
      { name: "大湖公園", value: "BR20" },
      { name: "葫洲", value: "BR21" },
      { name: "東湖", value: "BR22" },
      { name: "南港軟體園區", value: "BR23" },
      { name: "南港展覽館", value: "BR24" }
    ],
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

document.addEventListener('DOMContentLoaded', function () {
  "use strict";

  const fromInput = document.getElementById('station-from');
  const toInput = document.getElementById('station-to');
  const swapBtn = document.getElementById('swap-btn');
  const searchBtn = document.getElementById('search-btn');
  const featureBtns = document.querySelectorAll('.feature-btn');
  const stationImageDiv = document.querySelector('.station-image');
  const loadingDiv = document.getElementById('loading');
  const resultDiv = document.getElementById('result');

  // ===== 底部導覽 active =====
  (() => {
    const navLinks = document.querySelectorAll('.nav-btn');
    const currentPath = window.location.pathname.split('/').pop();
    navLinks.forEach(link => {
      const linkPath = link.getAttribute('href');
      if (linkPath === currentPath) link.classList.add('active');
      else link.classList.remove('active');
    });
  })();

  // ===== 功能按鈕導頁 =====
  featureBtns.forEach((btn, i) => {
    const inLink = btn.getAttribute('data-link');
    const outLink = btn.getAttribute('data-external');
    btn.addEventListener('click', (e) => {
      if (inLink) { window.location.href = inLink; return; }
      if (outLink) { e.preventDefault(); e.stopPropagation(); window.open(outLink, "_blank", "noopener"); return; }
      if (i === 0) window.location.href = "night.html";
      if (i === 1) window.location.href = "food_checkin.html";
      if (i === 2) { e.preventDefault(); e.stopPropagation(); window.open("https://ericyu.org/TaipeiMetroTime/", "_blank", "noopener"); }
    });
  });

  // ===== Google Places（Top10）=====
  let map, placesService;
  function initMapForTop10() {
    if (!(window.google && google.maps && google.maps.places)) {
      console.warn("Google Maps Places 尚未載入，Top10 照片將使用預設圖。");
      return;
    }
    map = new google.maps.Map(document.createElement("div"));
    placesService = new google.maps.places.PlacesService(map);
  }

  /* ====== Top10：距離 & 導航（輔助） ====== */
  const WALK_M_PER_MIN = 80;
  let MRT_STATIONS = []; // [{name, lat, lng}]

  const haversine = (aLat,aLng,bLat,bLng)=>{
    const R=6371000, rad=d=>d*Math.PI/180;
    const dLat=rad(bLat-aLat), dLng=rad(bLng-aLng);
    const s=Math.sin(dLat/2)**2 + Math.cos(rad(aLat))*Math.cos(rad(bLat))*Math.sin(dLng/2)**2;
    return 2*R*Math.asin(Math.sqrt(s));
  };
  const gmapsDir = (lat,lng)=>`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(lat+','+lng)}`;

  async function loadStationsOnce(){
    if (MRT_STATIONS.length) return MRT_STATIONS;
    try{
      const lines = await (await fetch('http://140.131.115.112:8000/api/lines/')).json();
      const all = [];
      for (const line of lines){
        const stations = await (await fetch(`http://140.131.115.112:8000/api/lines/${line.id}/stations/`)).json();
        stations.forEach(s=>{
          const lat = parseFloat(s.latitude ?? s.lat);
          const lng = parseFloat(s.longitude ?? s.lng ?? s.lon);
          if (Number.isFinite(lat) && Number.isFinite(lng)) all.push({ name:s.name, lat, lng });
        });
      }
      MRT_STATIONS = all;
    }catch(e){ console.warn('讀取捷運站失敗', e); }
    return MRT_STATIONS;
  }
  function nearestStation(lat,lng){
    if (!Number.isFinite(lat) || !Number.isFinite(lng) || MRT_STATIONS.length===0) return null;
    let best=null, bestD=Infinity;
    for (const s of MRT_STATIONS){
      const d = haversine(lat,lng,s.lat,s.lng);
      if (d < bestD){ bestD=d; best=s; }
    }
    return best ? { ...best, meters: bestD } : null;
  }

  // Top10 卡片專用 CSS（導航鈕/距離）
(function injectTop10CSS(){
  if (document.getElementById('top10-go-css')) return;
  const css = `
    .shop-item{ line-height:1; }                          /* 整體行高更緊 */
    .shop-item p{ margin:4px 0; }                            /* 段落上下間距更小 */
    .shop-img{ width:100%; aspect-ratio:4/3; object-fit:cover; border-radius:10px; display:block; margin-bottom:8px; }

    .shop-title{ font-size:16px; }
    .shop-rating{ color:#fff; opacity:.95; }

    .shop-item .distance{ margin-top:6px; font-size:14px; color:#fff; opacity:.95; }
    .shop-item .btn-row{ margin-top:5px; }                  /* 距離與按鈕之間留一點距離 */
    .shop-item .go-btn{
      background:#aaa; color:#fff; padding:6px 12px; border-radius:6px;
      text-decoration:none; display:inline-flex; align-items:center; justify-content:center;
    }
    .shop-item .go-btn:hover{ background:#ffd633; color:#222; }
  `;
  document.head.insertAdjacentHTML('beforeend', `<style id="top10-go-css">${css}</style>`);
})();


  // 先渲染整張卡（含導航/距離），照片之後再補
function renderTop10Card(shop, container, photoUrl){
  const lat = parseFloat(shop.latitude), lng = parseFloat(shop.longitude);

  // 距離最近捷運站
  const near = (Number.isFinite(lat) && Number.isFinite(lng)) ? nearestStation(lat,lng) : null;
  let distanceHTML = '';
  if (near) {
    const m = Math.round(near.meters);
    const mins = Math.max(1, Math.round(m / WALK_M_PER_MIN));
    distanceHTML = `<p class="distance">🚶 距離${near.name}站約 <b>${m}</b> 公尺（步行約 <b>${mins}</b> 分鐘）</p>`;
  }

  // 導航按鈕（放在最底）
  const navHTML =
    (Number.isFinite(lat) && Number.isFinite(lng))
      ? `<div class="btn-row"><a class="go-btn" href="${gmapsDir(lat,lng)}" target="_blank" rel="noopener">導航</a></div>`
      : '';

  container.innerHTML = `
    <img class="shop-img" src="${photoUrl || '預設圖片.png'}" alt="${shop.name}">
    <p class="shop-title"><strong>${shop.name}</strong></p>
    <p class="shop-rating">⭐ 評分：${shop.rating ?? ""}</p>
    ${distanceHTML}
    ${navHTML}
  `;
}


  // 只更新圖片，不覆蓋卡片（避免把導航/距離清掉）
  function searchRestaurantPhotoAndRender(shop, container) {
    if (!placesService) return; // 沒 Places 就維持預設圖

    const lat = parseFloat(shop.latitude), lng = parseFloat(shop.longitude);
    const request = { query: shop.name };
    if (Number.isFinite(lat) && Number.isFinite(lng)) {
      request.location = new google.maps.LatLng(lat, lng);
      request.radius = 1000;
    }

    placesService.textSearch(request, (results, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && results?.length) {
        const url = results[0].photos?.[0]?.getUrl({ maxWidth: 300 });
        if (url) {
          const img = container.querySelector('img.shop-img');
          if (img) img.src = url;
        }
      }
      // 找不到就保持預設圖
    });
  }

  // 載入 Top10（含導航/距離）
  async function loadTop10Restaurants() {
    await loadStationsOnce();  // 先載捷運站，確保距離能算
    fetch('http://140.131.115.112:8000/api/api/restaurants/top10/')
      .then(r => r.json())
      .then(data => {
        const restaurantList = Array.isArray(data) ? data : data.data;
        if (!Array.isArray(restaurantList)) { console.error("Top10 餐廳資料錯誤格式：", data); return; }
        const top10 = restaurantList
          .filter(r => !isNaN(parseFloat(r.rating)))
          .sort((a, b) => parseFloat(b.rating) - parseFloat(a.rating))
          .slice(0, 10);

        const shopList = document.querySelector('.shop-list');
        if (!shopList) return;
        shopList.innerHTML = '';

        top10.forEach(shop => {
          const div = document.createElement('div');
          div.className = 'shop-item';
          shopList.appendChild(div);

          // 先渲染卡片（含導航/距離）
          renderTop10Card(shop, div, null);

          // 再補照片（只改 img）
          searchRestaurantPhotoAndRender(shop, div);
        });
      })
      .catch(err => {
        console.error("Top10 餐廳載入失敗：", err);
        const shopList = document.querySelector('.shop-list');
        if (shopList) shopList.innerHTML = '<p style="color:white">載入失敗，請稍後再試。</p>';
      });
  }

  // ===== 由 stationData 產生搜尋建議 =====
  if (typeof stationData === "undefined") {
    console.error("找不到 stationData（請先載入 static/js/home_page/stationdata.js）");
  }
  const allStations = [];
  if (typeof stationData !== "undefined") {
    for (let line in stationData) {
      stationData[line].forEach(station => {
        allStations.push({ label: `${station.name} (${station.value})`, value: station.name, code: station.value });
      });
    }
  }

  const lineColors = { BR: "#a05a2c", R: "#be1e2d", G: "#009944", O: "#fbb040", BL: "#0072bc" };
  window.lineColors = lineColors; // 讓兩欄卡片可取用

  // ===== 輸入解析與最佳站點匹配 =====
  function parseInput(val) {
    const codeMatch = val.match(/\(([A-Z0-9]+)\)/);
    const code = codeMatch ? codeMatch[1] : null;
    const name = val.replace(/\s*\([A-Z0-9]+\)\s*$/, '');
    return { code, name };
  }
  function findBestStation(val) {
    if (!val) return null;
    const { code, name } = parseInput(val);
    if (code) {
      const byCode = allStations.find(s => s.code === code);
      if (byCode) return byCode;
    }
    let exact = allStations.find(s => s.value === name);
    if (!exact) {
      const name2 = name.replace(/站$/, '');
      exact = allStations.find(s => s.value === name2);
    }
    if (exact) return exact;
    const q = name.trim();
    if (!q) return null;
    const candidates = allStations.filter(s => s.value.includes(q));
    if (candidates.length) {
      candidates.sort((a, b) => b.value.length - a.value.length);
      return candidates[0];
    }
    return null;
  }

  // ===== Awesomplete =====
  function createAwesomplete(inputEl) {
    const list = allStations.map(s => s.label);
    const awesomplete = new Awesomplete(inputEl, {
      list, minChars: 0, maxItems: 9999, autoFirst: true, sort: false,
      filter: function (text, input) {
        if (!input) return true;
        const name = text.split(' (')[0].toLowerCase();
        const m = text.match(/\(([A-Z0-9]+)\)/);
        const code = m ? m[1].toLowerCase() : '';
        const q = input.trim().toLowerCase();
        return name.includes(q) || code.includes(q);
      }
    });
    inputEl.addEventListener("focus", () => awesomplete.evaluate());
    function updateBackground() {
      const st = findBestStation(inputEl.value);
      if (st) {
        const codePrefix = st.code.match(/^[A-Z]+/)[0];
        const color = lineColors[codePrefix] || "#ccc";
        inputEl.style.backgroundColor = color; inputEl.style.color = "#fff";
      } else { inputEl.style.backgroundColor = "#fff"; inputEl.style.color = "#000"; }
    }
    inputEl.addEventListener("input", updateBackground);
    inputEl.addEventListener("awesomplete-selectcomplete", updateBackground);
    awesomplete.item = function (text) {
      const li = document.createElement("li");
      li.innerHTML = text;
      const m = text.match(/\(([A-Z]+)/);
      const lineCode = m ? m[1].match(/^[A-Z]+/)[0] : null;
      if (lineCode) li.setAttribute("data-line", lineCode);
      return li;
    };
  }
  if (fromInput) createAwesomplete(fromInput);
  if (toInput) createAwesomplete(toInput);

  // ===== 交換起訖站 & 防重 =====
  if (swapBtn) {
    swapBtn.addEventListener('click', () => {
      if (!fromInput || !toInput) return;
      const temp = fromInput.value; fromInput.value = toInput.value; toInput.value = temp;
      fromInput.dispatchEvent(new Event('input')); toInput.dispatchEvent(new Event('input'));
    });
  }
  if (fromInput) fromInput.addEventListener('change', () => { if (toInput && fromInput.value === toInput.value) toInput.value = ''; });
  if (toInput) toInput.addEventListener('change', () => { if (fromInput && toInput.value === fromInput.value) fromInput.value = ''; });

  // ===== 方向推斷 =====
  function getDirection(destination) {
    if (destination.includes("南港")) return "東向";
    if (destination.includes("淡水")) return "北向";
    if (destination.includes("新店")) return "南向";
    if (destination.includes("迴龍") || destination.includes("蘆洲")) return "西向";
    return "未知";
  }

  // ===== 即時列車（維持原樣）=====
  function displayTrains(trains, title) {
    let html = `<h3 class="train-title">${title}</h3>`;
    trains.forEach(train => {
      const direction = getDirection(train.destinationName);
      html += `
        <div class="train-card">
          <div class="train-content">
            <p>🚉 <strong>出發站：</strong>${train.stationName}</p>
            <p>📍 <strong>目的地：</strong>${train.destinationName}</p>
            <p>🧭 <strong>方向：</strong>${direction}</p>
            <p>⏱️ <strong>到站倒數：</strong>${train.countDown}</p>
            <p>📅 <strong>更新時間：</strong>${train.nowDateTime}</p>
          </div>
        </div>`;
    });
    const wrap = document.createElement('div');
    wrap.classList.add('result-section');
    wrap.innerHTML = html;
    if (stationImageDiv) { stationImageDiv.innerHTML = ''; stationImageDiv.appendChild(wrap); }
  }

  function loadDefaultStationInfo() {
    const defaultStation = "台北車站";
    if (!stationImageDiv) return;
    stationImageDiv.innerHTML = `<p>載入中...</p>`;
    fetch('http://140.131.115.112:8000/api/track-info/')
      .then(r => r.json())
      .then(result => {
        if (result.status !== "success") { stationImageDiv.innerHTML = `<p>預設站查詢失敗</p>`; return; }
        const allLines = result.data || {};
        const matchedTrains = [];
        for (const lineName in allLines) {
          const trains = allLines[lineName] || [];
          trains.forEach(train => { if ((train.stationName || "").includes(defaultStation)) matchedTrains.push(train); });
        }
        if (matchedTrains.length === 0) stationImageDiv.innerHTML = `<p>目前 ${defaultStation} 無列車即時資訊</p>`;
        else displayTrains(matchedTrains, `熱門站「${defaultStation}」即時資訊`);
      })
      .catch(() => { stationImageDiv.innerHTML = `<p>即時資訊載入失敗</p>`; });
  }

  /* ========= 兩欄版：捷運路線卡片（自動注入 CSS） ========= */
  (function () {
    if (!document.getElementById("metro-line-style-2col")) {
      const style = document.createElement("style");
      style.id = "metro-line-style-2col";
      style.textContent = `
        .metro-card{background:#fff;border-radius:14px;box-shadow:0 8px 24px rgba(15,23,42,.08);padding:14px 16px;color:#0f172a}
        .metro-head{display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center;margin-bottom:10px}
        .pill{padding:6px 10px;border-radius:999px;background:#f1f5f9;font-size:13px}
        .pill.accent{background:#e6f4ff;color:#0b63ce;font-weight:700}
        .pill.id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.2px}
        .est{margin-left:auto;font-weight:700;color:#16a34a}
        .mline-columns{display:grid;grid-template-columns:1fr 1fr;gap:10px 24px;align-items:start}
        @media (max-width:420px){ .mline-columns{grid-template-columns:1fr;} }
        .metro-line{position:relative;margin:6px 0 2px 0;padding-left:34px;list-style:none}
        .metro-line::before{content:"";position:absolute;left:18px;top:0;bottom:0;width:2px;background:#e2e8f0;border-radius:2px}
        .stop{position:relative;padding:10px 12px 10px 0}
        .stop .dot{position:absolute;left:13px;top:16px;width:10px;height:10px;border-radius:50%;background:#1976d2;box-shadow:0 0 0 3px #fff}
        .stop .seg{position:absolute;left:18px;top:26px;width:4px;height:34px;background:var(--seg-color,#cbd5e1);border-radius:2px}
        .stop:last-child .seg{display:none}
        .stop .name{font-size:15px;font-weight:600}
        .stop .badge{display:inline-flex;align-items:center;gap:4px;margin-left:8px;padding:2px 8px;border-radius:999px;background:#e8f7ee;color:#1f7a36;font-size:12px;font-weight:700}
        .stop.start .name,.stop.end .name{color:#0b63ce}
        .legend{margin-top:10px;color:#475569;font-size:13px}`;
      document.head.appendChild(style);
    }

    const LINE_COLORS = (window.lineColors) || { BR:"#a05a2c", R:"#be1e2d", G:"#009944", O:"#fbb040", BL:"#0072bc" };

    function buildNameToCodes(stationData) {
      const map = new Map();
      if (!stationData) return map;
      for (const line in stationData) {
        stationData[line].forEach(s => {
          const arr = map.get(s.name) || [];
          arr.push(s.value);
          map.set(s.name, arr);
        });
      }
      return map;
    }
    function sharedLinePrefix(aCodes = [], bCodes = []) {
      for (const a of aCodes) {
        const ap = (a.match(/^[A-Z]+/)||[])[0]; if (!ap) continue;
        for (const b of bCodes) {
          const bp = (b.match(/^[A-Z]+/)||[])[0];
          if (ap === bp) return ap;
        }
      }
      return null;
    }
    function computeSegments(stations, nameToCodes) {
      const segColors = [];
      for (let i = 0; i < stations.length - 1; i++) {
        const a = stations[i], b = stations[i+1];
        const aC = nameToCodes.get(a) || [];
        const bC = nameToCodes.get(b) || [];
        const pref = sharedLinePrefix(aC, bC);
        segColors.push(LINE_COLORS[pref] || "#1976d2");
      }
      return segColors;
    }
    function parseTransferSet(str) {
      if (!str) return new Set();
      return new Set(
        str.replace(/[-→,]+/g," ").split(/\s+/).map(s=>s.trim()).filter(Boolean)
      );
    }

    function beautifulRouteCard(result, { startName, endName, dir }) {
      const pathStr = (result.Path || "").trim();
      const stations = pathStr ? pathStr.split("-").filter(Boolean) : [];
      const nameToCodes = buildNameToCodes(window.stationData);
      const segColors = computeSegments(stations, nameToCodes);
      const transferSet = parseTransferSet(result.TransferStations);
      if (!stations.length) return `<div class="metro-card"><div class="pill">沒有路線資料</div></div>`;
      const total = stations.length;
      const split = Math.ceil(total / 2);
      const est = result.Time ? `${result.Time} 分鐘` : "無資料";

      const stopLI = (name, i) => {
        const nameColor = (i === 0) ? (segColors[0] || "#1976d2")
                                    : (segColors[i-1] || "#1976d2");
        const seg = (i < total - 1) ? (segColors[i] || "#cbd5e1") : "#cbd5e1";
        const isStart = (i === 0);
        const isEnd   = (i === total - 1);
        const isTransfer = transferSet.has(name);
        const ring = isTransfer ? ', 0 0 0 6px #2e7d32' : '';

        return `
          <li class="stop ${isStart ? "start":""} ${isEnd ? "end":""}"
              style="--seg-color:${seg};--name-color:${nameColor};--dot-color:${nameColor};">
            <span class="dot" style="box-shadow:0 0 0 3px #fff${ring}"></span>
            <span class="seg"></span>
            <span class="name">${name}</span>
            ${isTransfer ? `<span class="badge">轉乘</span>` : ``}
          </li>
        `;
      };

      const leftHtml = stations.slice(0, split).map((n, idx) => stopLI(n, idx)).join("");
      const rightHtml = stations.slice(split).map((n, jdx) => stopLI(n, split + jdx)).join("");

      return `
        <div class="metro-card">
          <div class="metro-head">
            <span class="pill">起：<b>${startName}</b> <span class="pill id">${result.EntryStationID || "—"}</span></span>
            <span class="pill">迄：<b>${endName}</b> <span class="pill id">${result.ExitStationID || "—"}</span></span>
            <span class="pill accent">方向：${dir}</span>
            <span class="est">⏱ ${est}</span>
          </div>
          <div class="mline-columns">
            <ol class="metro-line">${leftHtml}</ol>
            <ol class="metro-line">${rightHtml}</ol>
          </div>
          <div class="legend">轉乘站以綠色節點標示。兩欄按順序由左至右排列。</div>
        </div>`;
    }

    window.beautifulRouteCard = beautifulRouteCard;
  })();
  /* ========= end 兩欄卡片 ========= */

  // ===== 查詢路線（改用兩欄卡片渲染）=====
  async function searchRoute() {
    if (!fromInput || !toInput || !loadingDiv || !resultDiv) return;

    const cleanName = name => name === '台北車站' ? name : name.replace(/\s*\(.*\)/, '').replace('站', '');
    const startStation = fromInput.value.trim();
    const endStation = toInput.value.trim();
    const processedStartStation = cleanName(startStation);
    const processedEndStation = cleanName(endStation);

    if (!startStation || !endStation) { alert('請選擇起點站和終點站！'); return; }
    if (startStation === endStation) { alert('起點站和終點站不能相同！'); return; }

    try {
      loadingDiv.style.display = 'block';
      resultDiv.style.display = 'none';

      const requestData = { start: processedStartStation, end: processedEndStation };
      const response = await fetch('http://140.131.115.112:8000/api/api/metro-route/', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestData)
      });

      loadingDiv.style.display = 'none';
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`伺服器錯誤 (${response.status}): ${errorText}`);
      }

      const result = await response.json();
      const dir = getDirection(processedEndStation);

      resultDiv.style.display = 'block';
      resultDiv.innerHTML = window.beautifulRouteCard(result, {
        startName: processedStartStation,
        endName: processedEndStation,
        dir
      });

    } catch (err) {
      loadingDiv.style.display = 'none';
      console.error('API 請求錯誤:', err);
      alert(`查詢時發生錯誤：${err.message}`);
    }
  }

  if (searchBtn) searchBtn.addEventListener('click', searchRoute);

  // ===== 初始載入 =====
  initMapForTop10();
  loadDefaultStationInfo();
  loadTop10Restaurants();
});

// 讓站名往右移一點（想更遠就調整數字）
document.head.insertAdjacentHTML('beforeend',
  '<style>.metro-card .stop .name{ margin-left:30px }</style>');








  
  