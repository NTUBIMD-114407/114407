// /static/js/reviews.js
// 判斷是不是合法的 Google Place ID（JS Places 老版格式）
const isValidPlaceId = (pid) =>
  typeof pid === "string" &&
  pid.length >= 15 &&
  /^[A-Za-z0-9_-]+$/.test(pid) &&
  pid.startsWith("ChI"); // 多數 Place ID 以 ChI 開頭

(function () {
  // ---------- utils ----------
  const $ = (sel) => document.querySelector(sel);
  const getParam = (k) => {
    const v = new URLSearchParams(location.search).get(k);
    return v == null ? "" : v.trim();
  };
  const toNum = (v) => {
    const n = typeof v === "string" ? parseFloat(v) : Number(v);
    return Number.isFinite(n) ? n : NaN;
  };
  const setTitle = (t) => { if (t) $("#restaurant-name").textContent = t; };

  // Haversine 計距（公尺）
  function distM(aLat, aLng, bLat, bLng) {
    const R=6371000, rad=d=>d*Math.PI/180;
    const dLat=rad(bLat-aLat), dLng=rad(bLng-aLng);
    const s=Math.sin(dLat/2)**2 + Math.cos(rad(aLat))*Math.cos(rad(bLat))*Math.sin(dLng/2)**2;
    return 2*R*Math.asin(Math.sqrt(s));
  }

  function showMsg(html, color = "#6b7280") {
    $("#review-list").innerHTML =
      `<p style="color:${color};font-weight:600;margin:8px 0">${html}</p>`;
  }

  // 正規化名稱做相似度比對（去掉空白、括號和全半形差異）
  function normalizeName(s="") {
    return s.toLowerCase()
      .replace(/\s+/g, "")
      .replace(/[（）()【】\[\]／/・・•・]/g, "")
      .replace(/＆/g,"&")
      .replace(/－/g,"-");
  }

  // 回傳 0~1 的簡單相似度（越大越像）
  function nameSimilarity(a="", b="") {
    a = normalizeName(a); b = normalizeName(b);
    if (!a || !b) return 0;
    if (a === b) return 1;
    if (a.includes(b) || b.includes(a)) return 0.9;
    // Jaccard of trigrams（簡化）
    const tri = s => new Set(s.match(/.{1,3}/g) || []);
    const A = tri(a), B = tri(b);
    let inter = 0;
    A.forEach(x => { if (B.has(x)) inter++; });
    const union = A.size + B.size - inter;
    return union ? inter / union : 0;
  }

  // 從多個 TextSearch 結果挑最佳（名稱相似度 + 距離分數）
  function chooseBestPlace(results, targetName, latNum, lngNum) {
    let best = null, bestScore = -Infinity;
    results.forEach(r => {
      let score = 0;
      score += nameSimilarity(targetName, r.name || "") * 100;
      if (Number.isFinite(latNum) && Number.isFinite(lngNum) && r.geometry?.location) {
        const d = distM(latNum, lngNum, r.geometry.location.lat(), r.geometry.location.lng());
        // 0~100 距離分數（<=100m 給滿分，>1500m 越遠越低）
        const distScore = Math.max(0, 100 - Math.min(100, (d - 100) / 14));
        score += distScore;
      }
      // 評分與評論數輕微加權
      if (typeof r.rating === "number") score += r.rating * 2;
      if (typeof r.user_ratings_total === "number") score += Math.min(20, r.user_ratings_total / 50);
      if (score > bestScore) { bestScore = score; best = r; }
    });
    return best || results[0];
  }

  // 來源優先：URL → sessionStorage.reviewTarget → localStorage.selectedRestaurant
  function getTargetFromUrlOrStorage() {
    // 1) URL
    let place_id = getParam("place_id");
    let name     = getParam("name");
    let lat      = getParam("lat");
    let lng      = getParam("lng");

    // 2) sessionStorage
    if (!place_id && !name) {
      try {
        const raw = sessionStorage.getItem("reviewTarget");
        if (raw) {
          const o = JSON.parse(raw);
          place_id = o.place_id || "";
          name     = o.name || "";
          lat      = o.lat  || o.latitude  || "";
          lng      = o.lng  || o.longitude || "";
        }
      } catch {}
    }

    // 3) localStorage（food_map 的 goToStationPage() 寫入）
    if (!place_id && !name) {
      try {
        const raw = localStorage.getItem("selectedRestaurant");
        if (raw) {
          const o = JSON.parse(raw);
          place_id = o.place_id || "";
          name     = o.name || o.restaurant_name || o.store_name || "";
          lat      = (o.latitude ?? "").toString();
          lng      = (o.longitude ?? "").toString();
        }
      } catch {}
    }

    if (name) { try { name = decodeURIComponent(name); } catch {} }
    return { place_id, name, lat, lng };
  }

  // ---------- render ----------
  function renderReviews(place) {
    const list = $("#review-list");
    const reviews = (place.reviews || []).slice(0, 10);
    if (!reviews.length) {
      list.innerHTML = `<p style="opacity:.75">這家店暫無公開評論。</p>`;
      return;
    }
    list.innerHTML = reviews.map((r) => {
      const d = r.time ? new Date(r.time * 1000) : null;
      const dateStr = d ? d.toLocaleDateString("zh-TW") : "";
      const stars   = "★".repeat(Math.round(r.rating || 0)).padEnd(5, "☆");
      const text    = (r.text || "").replace(/\n/g, "<br>");
      const avatar  = r.profile_photo_url || "";
      const author  = r.author_name || "訪客";
      return `
        <div class="review-item" style="padding:12px 0;border-bottom:1px solid #eee">
          <div style="display:flex;gap:8px;align-items:center">
            <img src="${avatar}" alt="" style="width:28px;height:28px;border-radius:50%;object-fit:cover">
            <div style="font-weight:700">${author}</div>
          </div>
          <div style="font-size:12px;opacity:.65;margin-top:2px">${dateStr}　${stars}</div>
          <p style="margin-top:6px;line-height:1.7">${text}</p>
        </div>`;
    }).join("");
  }

  function paintPlace(map, place) {
    setTitle(place.name || $("#restaurant-name").textContent);

    if (place.formatted_address) {
      const addr = document.createElement("div");
      addr.className = "addr-row";
      addr.style.cssText = "font-size:13px;opacity:.8;margin-top:2px";
      addr.textContent = place.formatted_address;
      $("#restaurant-name").after(addr);
    }

    if (place.geometry?.location) {
      map.setCenter(place.geometry.location);
      new google.maps.Marker({
        position: place.geometry.location,
        map,
        title: place.name || ""
      });
    }
    renderReviews(place);
  }

  // ---------- Google Maps entry ----------
  window.initMap = function () {
    const { place_id, name, lat, lng } = getTargetFromUrlOrStorage();
    const latNum = toNum(lat), lngNum = toNum(lng);
    const hasLL  = Number.isFinite(latNum) && Number.isFinite(lngNum);

    // 先把店名（若已知）放上標題
    if (name) setTitle(name);

    // 地圖初始化（預設台北市）
    const map = new google.maps.Map($("#map"), {
      center: hasLL ? { lat: latNum, lng: lngNum } : { lat: 25.0418, lng: 121.536 },
      zoom: 15,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: true
    });

    // 地圖容器高度保護（避免 CSS 沒設高度看起來像沒載入）
    if (parseInt(getComputedStyle($("#map")).height) < 50) {
      $("#map").style.height = "320px";
    }

    const svc = new google.maps.places.PlacesService(map);

    // 1) 有合法 place_id：最穩
    if (isValidPlaceId(place_id)) {
      showMsg("正在載入商家資訊與評論…", "#6b7280");
      svc.getDetails({
        placeId: place_id,
        fields: ["name","formatted_address","geometry","rating","user_ratings_total","reviews"]
      }, (place, status) => {
        if (status !== google.maps.places.PlacesServiceStatus.OK || !place) {
          showMsg("找不到這家店的詳細資料（place_id 可能無效）。", "#c0392b");
          return;
        }
        paintPlace(map, place);
      });
      return;
    } else if (place_id) {
      // 有帶東西但不是合法 Place ID，避免 INVALID 'placeid'，直接走名稱搜尋
      console.warn("非合法的 place_id，改用文字搜尋：", place_id);
    }

    // 2) 無 place_id：用店名搜尋（可帶經緯度偏好）
    if (!name) {
      showMsg("缺少店名參數（?name=）或 place_id（?place_id=）。", "#c0392b");
      return;
    }

    showMsg("正在搜尋商家…", "#6b7280");

    const req = {
      query: name,
      // TextSearch 使用 location+radius 當作 bias
      location: hasLL ? new google.maps.LatLng(latNum, lngNum) : undefined,
      radius: hasLL ? 1500 : undefined
    };

    svc.textSearch(req, (results, status) => {
      if (status !== google.maps.places.PlacesServiceStatus.OK || !results?.length) {
        showMsg("找不到相符的商家，請確認店名是否正確。", "#c0392b");
        return;
      }

      // 智能挑選最佳結果
      const best = chooseBestPlace(results, name, latNum, lngNum);
      const pid  = best.place_id;

      svc.getDetails({
        placeId: pid,
        fields: ["name","formatted_address","geometry","rating","user_ratings_total","reviews"]
      }, (place, status2) => {
        if (status2 !== google.maps.places.PlacesServiceStatus.OK || !place) {
          showMsg("已找到商家，但讀取詳細資料失敗。", "#c0392b");
          return;
        }
        paintPlace(map, place);
      });
    });
  };
})();
