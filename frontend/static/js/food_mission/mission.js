// static/js/food_mission/mission.js
"use strict";

/* ========== 通知共用（收藏用） ========== */
const NOTIFY_KEY = "notifications_v1";
function loadNoti(){ try { return JSON.parse(localStorage.getItem(NOTIFY_KEY)) || []; } catch { return []; } }
function saveNoti(list){ localStorage.setItem(NOTIFY_KEY, JSON.stringify(list)); }
function makeId(){ return (crypto.randomUUID && crypto.randomUUID()) || (Date.now() + Math.random().toString(36).slice(2)); }
function safeName(o){
  return (o && (o.name || o.restaurant_name || o.restaurantName || o.store_name || o.title)) || "未命名餐廳";
}
function pushFavoriteNotify(item, action="add"){
  const name = safeName(item);
  const noti = {
    id: makeId(),
    type: "favorite",
    title: action === "add" ? "已收藏美食" : "取消收藏",
    message: action === "add" ? `將「${name}」加入收藏` : `已取消「${name}」收藏`,
    time: new Date().toISOString(),
    read: false,
    item: {
      name,
      address: item.address || "",
      place_id: item.place_id || null
    }
  };
  const list = loadNoti();
  list.unshift(noti);
  saveNoti(list);
}
/* ======================================= */

/* ========== 收藏共用 ========== */
const FAV_KEY  = "fav_restaurants_v1";
const FAV_PAGE = "favorites_food.html"; // 目前不跳轉，保留常數以後用

function loadFavs(){ try{ return JSON.parse(localStorage.getItem(FAV_KEY)) || []; }catch{ return []; } }
function saveFavs(list){ localStorage.setItem(FAV_KEY, JSON.stringify(list)); }
const favKey = d => ((d.name||d.restaurant_name||"") + "@" + (d.address||""));
function addToFav(item){ const list = loadFavs(); const k = favKey(item); if (!list.some(x => favKey(x) === k)) list.push(item); saveFavs(list); }
function isFav(item){ const k = favKey(item); return loadFavs().some(x => favKey(x) === k); }
function toggleFav(item){
  const list = loadFavs(); const k = favKey(item);
  const i = list.findIndex(x => favKey(x) === k);
  if (i === -1) { list.push(item); saveFavs(list); return true; }  // 加入 → 已收藏
  list.splice(i,1); saveFavs(list); return false;                  // 移除 → 未收藏
}
function setFavState(btn, saved){
  btn.textContent = saved ? "已收藏" : "收藏";
  btn.classList.toggle("pill--primary", saved);
  btn.classList.toggle("pill--muted", !saved);
}
function extractBgUrl(el){
  const s = getComputedStyle(el).backgroundImage;
  const m = s && s.match(/url\(["']?(.*?)["']?\)/);
  return m ? m[1] : "";
}

/* ========== 初始化 ========== */
document.addEventListener("DOMContentLoaded", init);

async function init() {
  const container = document.querySelector(".cards");
  if (!container) return;
  container.innerHTML = "";

  try {
    const res = await fetch("http://140.131.115.112:8000/api/api/top-checkin-restaurants/");
    const { restaurants = [] } = await res.json();

    const data = restaurants.filter(notTest).map(normalize);

    if (!data.length) {
      container.innerHTML = '<p class="empty">⚠️ 目前沒有可顯示的餐廳</p>';
      return;
    }

    for (const r of data) {
      const card = await buildCard(r);
      container.appendChild(card);
    }
  } catch (err) {
    console.error("🚨 無法取得打卡餐廳列表：", err);
    container.innerHTML = '<p class="empty">🚨 無法取得打卡餐廳列表</p>';
  }
}

/* ---------- Utils ---------- */
function notTest(r) {
  if (r?.is_test === true) return false;
  const name = (r?.restaurant_name || r?.name || "").toLowerCase();
  return !/(測試|test|demo|樣板|範例|dummy)/i.test(name);
}
function first(obj, keys) {
  for (const k of keys) {
    const v = obj?.[k];
    if (v !== undefined && v !== null && String(v).trim() !== "") return v;
  }
  return null;
}

// 把 Google price_level 轉成「均消區間」近似
function priceLevelToRange(level) {
  if (!Number.isFinite(level) || level <= 0) return null;
  switch (Number(level)) {
    case 1: return "$100–200";
    case 2: return "$200–400";
    case 3: return "$400–600";
    case 4: return "$600–1000+";
    default: return null;
  }
}

function normalize(r) {
  const priceLevel = Number(first(r, ["price_level","priceLevel","pricelevel"]));
  const avgPriceNum = Number(first(r, ["avg_price","average_price","avgPrice","averagePrice"]));
  const lat = Number(first(r, ["lat","latitude"]));
  const lng = Number(first(r, ["lng","longitude"]));
  const opening = first(r, ["opening_hours","opening_hours_text","open_hours","hours","business_hours","businessHours"]);

  const priceText =
    (Number.isFinite(avgPriceNum) && avgPriceNum > 0) ? `$${avgPriceNum}` :
    priceLevelToRange(priceLevel);

  return {
    name: first(r, ["restaurant_name","name"]) || "未命名",
    rating: first(r, ["rating"]) ?? "-",
    review_count: first(r, ["review_count","user_ratings_total"]) ?? 0,
    address: first(r, ["address","formatted_address"]) || "",
    website: first(r, ["website","url"]) || "",
    phone: first(r, ["phone","formatted_phone_number","tel"]) || "",
    opening_text: opening || "",
    price_text: priceText,
    lat: Number.isFinite(lat) ? lat : null,
    lng: Number.isFinite(lng) ? lng : null
  };
}

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}

/* ---------- Card ---------- */
async function buildCard(d) {
  const card = el("article", "card");
  const imgBox = el("div", "img-box", "📷 圖片未提供");
  const info = el("div", "info");

  const title = el("h2", "shop-name", d.name);
  const ratingDiv = el("div", "rating");
  ratingDiv.innerHTML =
    `<span class="star-label">⭐ ${d.rating}</span><span class="count">（${d.review_count} 則評論）</span>`;

  // 營業時間（可被 Places 更新）
  const timeRow = el("div", "meta-row");
  timeRow.innerHTML = `<span class="meta-label">營業時間</span><span class="divider">｜</span>`;
  const timeVal = document.createElement("span");
  timeVal.textContent = d.opening_text || "—";
  timeRow.appendChild(timeVal);

  // 地址（可被 Places 更新）
  const addrRow = el("div", "meta-row");
  addrRow.innerHTML = `<span class="meta-label">店家地址</span><span class="divider">｜</span>`;
  const addrVal = document.createElement("span");
  addrVal.textContent = d.address || "—";
  addrRow.appendChild(addrVal);

  // 動作：導航 + 收藏（距離已移除）
  const actions = el("div", "actions");

  const navBtn = el("button", "pill pill--primary");
  navBtn.innerHTML = `<span class="pill-ic">▶</span> 導航`;
  navBtn.addEventListener("click", () => {
    if (d.lat && d.lng) {
      const q = encodeURIComponent(d.name);
      window.open(`https://www.google.com/maps/search/?api=1&query=${d.lat},${d.lng}(${q})`, "_blank");
    } else if (addrVal.textContent && addrVal.textContent !== "—") {
      window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(addrVal.textContent)}`, "_blank");
    }
  });

  // ✅ 收藏按鈕（不跳頁、可切換 + 發通知）
  const favBtn = el("button", "pill pill--muted");
  const buildPayload = () => ({
    name: d.name,
    address: d.address || addrVal.textContent || "",
    rating: d.rating ?? null,
    review_count: d.review_count ?? null,
    opening_text: d.opening_text || (timeVal.textContent || ""),
    price_text: d.price_text || "",
    lat: d.lat ?? null,
    lng: d.lng ?? null,
    website: d.website || "",
    image: extractBgUrl(imgBox),
    place_id: null   // 此頁目前沒有 place_id，可留空
  });
  setFavState(favBtn, isFav(buildPayload()));  // 依現況初始化
  favBtn.addEventListener("click", () => {
    const payload = buildPayload();
    const saved = toggleFav(payload);           // 切換收藏
    setFavState(favBtn, saved);                 // 更新樣式/文字
    pushFavoriteNotify(payload, saved ? "add" : "remove"); // 🔔 發通知
  });

  actions.append(navBtn, favBtn);

  // 標籤：詳情 / 均消 / 官網
  const tags = el("div", "tags");
  const detail = document.createElement("a");
  detail.href = `store_details.html?name=${encodeURIComponent(d.name)}`;
  detail.innerHTML = `<button>🔍 查看詳情</button>`;
  const priceBtn = el("button", null, d.price_text ? `均消 ${d.price_text}` : "均消 —");
  const site = document.createElement("a");
  site.target = "_blank";
  site.href = d.website || `https://www.google.com/search?q=${encodeURIComponent(d.name + " " + (d.address||""))}`;
  site.innerHTML = `<button>🌐 官方網站</button>`;
  tags.append(detail, priceBtn, site);

  info.append(title, ratingDiv, timeRow, addrRow, actions, tags);
  card.append(imgBox, info);

  // 用 Google Places 補：照片 / 地址 / 營業時間 / 價位等級→均消
  if (window.google?.maps?.places) {
    try {
      await enrichFromPlaces(d.name, {
        onPhoto: url => {
          imgBox.style.backgroundImage = `url('${url}')`;
          imgBox.style.backgroundSize = "cover";
          imgBox.style.backgroundPosition = "center";
          imgBox.textContent = "";
        },
        onDetails: det => {
          // 地址
          if (!d.address && det?.formatted_address) {
            d.address = det.formatted_address;
            addrVal.textContent = d.address;
          }
          // 營業時間
          const weekday = det?.opening_hours?.weekday_text;
          if ((!d.opening_text || d.opening_text === "—") && Array.isArray(weekday) && weekday.length) {
            const idx = new Date().getDay(); // 0(日)~6(六)
            const line = weekday[idx] || weekday[0];
            timeVal.textContent = line.replace(/^[^:]+:\s?/, "");
            d.opening_text = timeVal.textContent; // 寫回 d，收藏時帶到
          } else if (det?.opening_hours?.isOpen && typeof det.opening_hours.isOpen === "function") {
            timeVal.textContent = det.opening_hours.isOpen() ? "營業中" : "休息中";
            d.opening_text = timeVal.textContent;
          }
          // 價位等級 → 均消
          if (!d.price_text && Number.isFinite(det?.price_level)) {
            d.price_text = priceLevelToRange(det.price_level);
            if (d.price_text) priceBtn.textContent = `均消 ${d.price_text}`;
          }
          // 可能地址/時間改了 → 依新資料更新收藏按鈕狀態
          setFavState(favBtn, isFav(buildPayload()));
        }
      });
    } catch {}
  }

  return card;
}

/* 透過 Places：textSearch 取 place_id，再 getDetails */
function enrichFromPlaces(query, handlers) {
  const service = new google.maps.places.PlacesService(document.createElement("div"));
  return new Promise((resolve, reject) => {
    service.textSearch({ query: `${query} 台灣` }, (results, status) => {
      if (status !== google.maps.places.PlacesServiceStatus.OK || !results?.length) {
        return reject(new Error("找不到店家"));
      }
      const top = results[0];

      if (top?.photos?.length) {
        const url = top.photos[0].getUrl({ maxWidth: 640 });
        handlers?.onPhoto?.(url);
      }

      if (!top.place_id) return resolve();
      service.getDetails({
        placeId: top.place_id,
        fields: ["price_level","formatted_address","geometry","opening_hours","website","formatted_phone_number","photos","rating","user_ratings_total"]
      }, (det, st) => {
        if (st === google.maps.places.PlacesServiceStatus.OK) {
          handlers?.onDetails?.(det);
        }
        resolve();
      });
    });
  });
}
