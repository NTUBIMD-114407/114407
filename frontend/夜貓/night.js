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
let map;
let marker;
let isMapReady = false;

document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.search-bar input');
  const recommendContainer = document.querySelector('.recommend-container');
  const mapDiv = document.querySelector('.map');

  const dataList = document.createElement('datalist');
  dataList.id = 'station-options';
  document.body.appendChild(dataList);

  searchInput.setAttribute('list', 'station-options');

  let allRestaurants = [];

  fetch('http://140.131.115.112:8000/api/api/restaurants/night/')
    .then(response => response.json())
    .then(data => {
      allRestaurants = data.results;
      const stationsSet = new Set();

      data.results.forEach(item => {
        if (item.stations && item.stations.length > 0) {
          item.stations.forEach(station => {
            stationsSet.add(station);
          });
        }
      });

      stationsSet.forEach(station => {
        const option = document.createElement('option');
        option.value = station;
        dataList.appendChild(option);
      });
    })
    .catch(error => {
      console.error('載入站點失敗:', error);
    });

  searchInput.addEventListener('change', function() {
    if (!isMapReady) {
      alert('地圖還在載入中，請稍後再試喔！');
      return;
    }

    const selectedStation = searchInput.value.trim();
    if (!selectedStation) return;

    const filteredRestaurants = allRestaurants.filter(restaurant =>
      restaurant.stations && restaurant.stations.includes(selectedStation)
    );

    updateRecommendSection(filteredRestaurants);

    if (filteredRestaurants.length > 0) {
      moveMapToAddress(filteredRestaurants[0].address, selectedStation);
    }
  });

  function updateRecommendSection(restaurants) {
    recommendContainer.innerHTML = '';

    if (restaurants.length === 0) {
      recommendContainer.innerHTML = '<p>找不到符合的店家。</p>';
      return;
    }

    restaurants.forEach(item => {
      const foodCard = document.createElement('div');
      foodCard.className = 'food-card';

      const imageBox = document.createElement('div');
      imageBox.className = 'image-box';

      const img = document.createElement('img');
      img.style.width = '100%';
      img.style.height = '100%';
      img.style.borderRadius = '5px';
      img.src = '圖片/store1.png'; // 預設圖片

      imageBox.appendChild(img);

      const nameP = document.createElement('p');
      nameP.textContent = item.name;
      nameP.style.cursor = 'pointer';
      nameP.style.fontWeight = 'bold';
      nameP.addEventListener('click', function() {
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
      moreBtn.addEventListener('click', function() {
        showMorePopup(item);
      });

      foodCard.appendChild(imageBox);
      foodCard.appendChild(nameP);
      foodCard.appendChild(descP);
      foodCard.appendChild(starsDiv);
      foodCard.appendChild(moreBtn);

      recommendContainer.appendChild(foodCard);

      getPhotoUrlByPlaceName(item.name, function(photoUrl) {
        if (photoUrl) {
          img.src = photoUrl;
        }
      });
    });
  }

  function getPhotoUrlByPlaceName(placeName, callback) {
    const service = new google.maps.places.PlacesService(document.createElement('div'));

    const request = {
      query: placeName,
      fields: ['photos'],
    };

    service.findPlaceFromQuery(request, (results, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && results[0]) {
        if (results[0].photos && results[0].photos.length > 0) {
          const photoUrl = results[0].photos[0].getUrl({ maxWidth: 400 });
          callback(photoUrl);
        } else {
          callback(null);
        }
      } else {
        callback(null);
      }
    });
  }

  function generateStars(rating) {
    if (!rating) rating = 0;

    const fullStar = '⭐';
    const halfStar = '✩';
    const emptyStar = '☆';
    let starsHTML = '';

    const rounded = Math.round(rating * 2) / 2;

    for (let i = 1; i <= 5; i++) {
      if (rounded >= i) {
        starsHTML += fullStar;
      } else if (rounded + 0.5 === i) {
        starsHTML += halfStar;
      } else {
        starsHTML += emptyStar;
      }
    }

    return starsHTML;
  }

  function moveMapToAddress(address, title) {
    if (!isMapReady) {
      console.error('地圖尚未初始化');
      return;
    }
    const geocoder = new google.maps.Geocoder();

    geocoder.geocode({ address: address }, function(results, status) {
      if (status === 'OK') {
        const location = results[0].geometry.location;
        map.setCenter(location);
        map.setZoom(17);

        if (marker) {
          marker.setMap(null);
        }

        marker = new google.maps.Marker({
          map: map,
          position: location,
          title: title
        });
      } else {
        console.error('地址轉換失敗:', status);
      }
    });
  }

  function showMorePopup(item) {
    const overlay = document.createElement('div');
    overlay.className = 'popup-overlay';
  
    const popup = document.createElement('div');
    popup.className = 'popup-card';
  
    // ⭐ 新增處理 business_hours 的字串
    let businessHoursText = '';
    if (Array.isArray(item.business_hours)) {
      businessHoursText = item.business_hours.map(obj => `${obj.day} ${obj.hours}`).join('<br>');
    } else {
      businessHoursText = '無資料';
    }
  
    popup.innerHTML = `
      <h3>推薦美食</h3>
      <div class="popup-content">
        <p><strong>${item.name}</strong></p>
        <p>${item.stations ? item.stations.join('、') : '捷運站未知'}</p>
        <p><strong>營業時間：</strong><br>${businessHoursText}</p>
        <div class="stars">${generateStars(item.rating)}</div>
        <div class="icons">
          <img src="圖片/map.png" alt="地圖" class="icon">
          <img src="圖片/ubike.png" alt="Ubike" class="icon">
          <img src="圖片/walk.png" alt="步行" class="icon">
        </div>
        <button class="back-btn">BACK</button>
      </div>
    `;
  
    overlay.appendChild(popup);
    document.body.appendChild(overlay);
  
    const backBtn = popup.querySelector('.back-btn');
    backBtn.addEventListener('click', function() {
      document.body.removeChild(overlay);
    });
  }
  
});

// 地圖初始化一定要放外面
window.initMap = function() {
  map = new google.maps.Map(document.querySelector('.map'), {
    center: { lat: 25.0330, lng: 121.5654 },
    zoom: 14,
  });
  isMapReady = true;
};


// stationData 請確保你已經有了

// 1. 動態生成站名選單（寫死也可以）
const stationSelect = document.getElementById('station-select');

// 清空原本的選項
stationSelect.innerHTML = '';

for (const lineName in stationData) {
  const optgroup = document.createElement('optgroup');
  optgroup.label = lineName;

  stationData[lineName].forEach(station => {
    const option = document.createElement('option');
    option.value = station.name;
    option.textContent = station.name;
    optgroup.appendChild(option);
  });

  stationSelect.appendChild(optgroup);
}

// 2. 綁定按鈕事件查詢末五班車
document.getElementById('query-last-train').addEventListener('click', async () => {
  const stationName = stationSelect.value;
  if (!stationName) {
    alert('請選擇車站');
    return;
  }

  const apiUrl = `http://140.131.115.112:8000/api/api/station-last-five-trains/?station_name=${encodeURIComponent(stationName)}`;

  try {
    const response = await fetch(apiUrl);
    if (!response.ok) throw new Error('回傳失敗');
    const result = await response.json();

    if (!Array.isArray(result) || result.length === 0) {
      document.getElementById('last-train-result').innerHTML = '<p>查無資料</p>';
      return;
    }

    let displayHTML = '';
    result.forEach(direction => {
      displayHTML += `
        <div class="train-block">
          <h4>${direction.station_name} → ${direction.destination}</h4>
          <p>行駛方向：${direction.direction}</p>
          <ul>
            ${direction.trains.map(train => `<li>第${train.train_sequence}班：${train.train_time}</li>`).join('')}
          </ul>
        </div>
        <hr/>
      `;
    });

    document.getElementById('last-train-result').innerHTML = displayHTML;

  } catch (err) {
    console.error('錯誤：', err);
    document.getElementById('last-train-result').innerHTML = '<p>查詢失敗，請稍後再試。</p>';
  }
});



