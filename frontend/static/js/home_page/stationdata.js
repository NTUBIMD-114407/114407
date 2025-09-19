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
    const fromInput = document.getElementById('station-from');
    const toInput = document.getElementById('station-to');
    const swapBtn = document.getElementById('swap-btn');
    const searchBtn = document.getElementById('search-btn');
    const featureBtns = document.querySelectorAll('.feature-btn');
    const stationImageDiv = document.querySelector('.station-image');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
  
    let map, placesService;
  
    function initMapForTop10() {
      map = new google.maps.Map(document.createElement("div"));
      placesService = new google.maps.places.PlacesService(map);
    }
  
    function searchRestaurantPhotoAndRender(shop, container) {
      const request = {
        location: new google.maps.LatLng(parseFloat(shop.latitude), parseFloat(shop.longitude)),
        radius: 1000,
        query: shop.name
      };
  
      placesService.textSearch(request, (results, status) => {
        if (status === google.maps.places.PlacesServiceStatus.OK && results.length > 0) {
          const place = results[0];
          const photoUrl = place.photos?.[0]?.getUrl({ maxWidth: 300 }) || "預設圖片.png";
          container.innerHTML = `
          <img src="${photoUrl}" alt="${shop.name}" 
               style="width:100%; height:auto; aspect-ratio: 4 / 3; object-fit: cover; border-radius:10px;">
          <p><strong>${shop.name}</strong></p>
          <p>⭐ 評分：${shop.rating}</p>
          
        `;
        
        } else {
          container.innerHTML = `
            <img src="預設圖片.png" alt="無圖片" style="width:100%; border-radius:10px;">
            <p><strong>${shop.name}</strong></p>
            <p>⭐ 評分：${shop.rating}</p>
            <p>📍 ${shop.address}</p>
          `;
        }
      });
    }
  
    function loadTop10Restaurants() {
      fetch('http://140.131.115.112:8000/api/api/restaurants/')
        .then(response => response.json())
        .then(data => {
          const restaurantList = Array.isArray(data) ? data : data.data;
          if (!Array.isArray(restaurantList)) {
            console.error("Top10 餐廳資料錯誤格式：", data);
            return;
          }
  
          const top10 = restaurantList
            .filter(r => !isNaN(parseFloat(r.rating)))
            .sort((a, b) => parseFloat(b.rating) - parseFloat(a.rating))
            .slice(0, 10);
  
          const shopList = document.querySelector('.shop-list');
          shopList.innerHTML = '';
  
          top10.forEach(shop => {
            const div = document.createElement('div');
            div.className = 'shop-item';
            shopList.appendChild(div);
            searchRestaurantPhotoAndRender(shop, div);
          });
        })
        .catch(err => {
          console.error("Top10 餐廳載入失敗：", err);
          const shopList = document.querySelector('.shop-list');
          shopList.innerHTML = '<p style="color:white">載入失敗，請稍後再試。</p>';
        });
    }
  
    const allStations = [];
    for (let line in stationData) {
      stationData[line].forEach(station => {
        allStations.push({
          label: `${station.name} (${station.value})`,
          value: station.name,
          code: station.value
        });
      });
    }
  
    const lineColors = {
      BR: "#a05a2c",
      R: "#be1e2d",
      G: "#009944",
      O: "#fbb040",
      BL: "#0072bc"
    };
  
    const createAwesomplete = (inputEl) => {
      const list = allStations.map(s => s.label);
      const awesomplete = new Awesomplete(inputEl, {
        list,
        minChars: 0,
        maxItems: 100,
        autoFirst: true,
        sort: false
      });
  
      inputEl.addEventListener("focus", () => {
        awesomplete.evaluate();
      });
  
      inputEl.addEventListener("input", updateBackgroundAndSearch);
      inputEl.addEventListener("awesomplete-selectcomplete", updateBackgroundAndSearch);
  
      function updateBackgroundAndSearch() {
        const matched = allStations.find(
          (s) => inputEl.value.includes(s.value) || inputEl.value.includes(s.name)
        );
        if (matched) {
          const codePrefix = matched.code.match(/^[A-Z]+/)[0];
          const color = lineColors[codePrefix] || "#ccc";
          inputEl.style.backgroundColor = color;
          inputEl.style.color = "#fff";
        } else {
          inputEl.style.backgroundColor = "white";
          inputEl.style.color = "black";
        }
      }
  
      awesomplete.item = function (text, input) {
        const item = document.createElement("li");
        item.innerHTML = text;
        const match = text.match(/\(([A-Z]+)/);
        const lineCode = match ? match[1].match(/^[A-Z]+/)[0] : null;
        if (lineCode) item.setAttribute("data-line", lineCode);
        return item;
      };
    };
  
    createAwesomplete(fromInput);
    createAwesomplete(toInput);
  
    swapBtn.addEventListener('click', () => {
      const temp = fromInput.value;
      fromInput.value = toInput.value;
      toInput.value = temp;
      fromInput.dispatchEvent(new Event('input'));
      toInput.dispatchEvent(new Event('input'));
    });
  
    if (featureBtns.length > 0) {
      featureBtns[0].addEventListener('click', function () {
        window.location.href = "night.html";
      });
    }
    if (featureBtns.length > 1) {
      featureBtns[1].addEventListener('click', function () {
        window.location.href = "food_checkin.html";
      });
    }
    if (featureBtns.length > 2) {
      featureBtns[2].addEventListener('click', function () {
        window.location.href = "timetable.html";
      });
    }
  
    function getDirection(destination) {
      if (destination.includes("南港")) return "東向";
      if (destination.includes("淡水")) return "北向";
      if (destination.includes("新店")) return "南向";
      if (destination.includes("迴龍") || destination.includes("蘆洲")) return "西向";
      return "未知";
    }
  
    function displayTrains(trains, title) {
      let html = `<h3 class="train-title">${title}</h3>`;
      trains.forEach(train => {
        const direction = getDirection(train.destinationName);
        html += `
          <div class="train-card">
            <div class="train-line"></div>
            <div class="train-content">
              <p>🚉 <strong>出發站：</strong>${train.stationName}</p>
              <p>📍 <strong>目的地：</strong>${train.destinationName}</p>
              <p>🧭 <strong>方向：</strong>${direction}</p>
              <p>⏱️ <strong>到站倒數：</strong>${train.countDown}</p>
              <p>📅 <strong>更新時間：</strong>${train.nowDateTime}</p>
            </div>
          </div>
        `;
      });
      const resultDiv = document.createElement('div');
      resultDiv.classList.add('result-section');
      resultDiv.innerHTML = html;
      stationImageDiv.innerHTML = '';
      stationImageDiv.appendChild(resultDiv);
    }


  
    function loadDefaultStationInfo() {
      const defaultStation = "台北車站";
      stationImageDiv.innerHTML = `<p>載入中...</p>`;
      fetch('http://140.131.115.112:8000/api/track-info/')
        .then(response => response.json())
        .then(result => {
          if (result.status !== "success") {
            stationImageDiv.innerHTML = `<p>預設站查詢失敗</p>`;
            return;
          }
          const allLines = result.data;
          let matchedTrains = [];
          for (const lineName in allLines) {
            const trains = allLines[lineName];
            trains.forEach(train => {
              if (train.stationName.includes(defaultStation)) {
                matchedTrains.push(train);
              }
            });
          }
          if (matchedTrains.length === 0) {
            stationImageDiv.innerHTML = `<p>目前 ${defaultStation} 無列車即時資訊</p>`;
          } else {
            displayTrains(matchedTrains, `熱門站「${defaultStation}」即時資訊`);
          }
        });
    }
  
    initMapForTop10();
    loadDefaultStationInfo();
    loadTop10Restaurants();
  


  async function searchRoute() {
    const startStation = fromInput.value.trim();
    const endStation = toInput.value.trim();

    const cleanName = name => name === '台北車站' ? name : name.replace(/\s*\(.*\)/, '').replace('站', '');
    const processedStartStation = cleanName(startStation);
    const processedEndStation = cleanName(endStation);

    if (!startStation || !endStation) {
      alert('請選擇起點站和終點站！');
      return;
    }
    if (startStation === endStation) {
      alert('起點站和終點站不能相同！');
      return;
    }

    try {
      loadingDiv.style.display = 'block';
      resultDiv.style.display = 'none';

      const requestData = { start: processedStartStation, end: processedEndStation };
      console.log('📤 發送查詢資料:', requestData);

      const response = await fetch('http://140.131.115.112:8000/api/api/metro-route/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      loadingDiv.style.display = 'none';

      if (!response.ok) {
        const errorText = await response.text();
        console.error('伺服器錯誤響應:', errorText);
        throw new Error(`伺服器錯誤 (${response.status}): ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ API 響應:', result);

      resultDiv.style.display = 'block';
      resultDiv.innerHTML = `
  <div class="result-container">
    <h3>查詢結果</h3>
    <div class="station-info">
      <div>起點站：<span class="value">${processedStartStation}</span> (${result.EntryStationID || '無資料'})</div>
      <div>終點站：<span class="value">${processedEndStation}</span> (${result.ExitStationID || '無資料'})</div>
    </div>

    <div class="route-section">
      <h4>建議路線</h4>
      <div class="route-path">
        ${
          result.Path ? result.Path.split('-').filter(s => s).map((station, index, array) => {
            const isTransfer = result.TransferStations?.includes(station);
            const isLast = index === array.length - 1;
            const dotColor = isTransfer ? '#28a745' : '#007bff';
            return `
              <div class="station-node">
                <div class="station-dot" style="background:${dotColor}"></div>
                <div class="station-name">${station}</div>
                ${!isLast ? '<div class="station-line"></div>' : ''}
              </div>
            `;
          }).join('') : '無資料'
        }
      </div>
    </div>

    <div class="route-section">
      <h4>轉乘站</h4>
      <div class="transfer-path">
        ${result.TransferStations ? result.TransferStations.replace(/[-→\s]+$/, '').split('-').filter(Boolean).join(' → ')
                                  : '無需轉乘'}

      </div>
    </div>


    <div class="route-section">
      <h4>預估時間</h4>
      <div class="time">
        ${result.Time ? result.Time + ' 分鐘' : '無資料'}
      </div>
    </div>
  </div>
`;

    } catch (error) {
      loadingDiv.style.display = 'none';
      console.error('API 請求錯誤:', error);
      alert(`查詢時發生錯誤：${error.message}`);
    }
  }

  // 防止相同站點選取
  fromInput.addEventListener('change', () => {
    if (fromInput.value === toInput.value) toInput.value = '';
  });
  toInput.addEventListener('change', () => {
    if (toInput.value === fromInput.value) fromInput.value = '';
  });

  // 綁定查詢事件
  searchBtn.addEventListener('click', searchRoute);
});





  
  