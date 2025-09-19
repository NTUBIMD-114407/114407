let placesService;

window.addEventListener('load', async () => {
  const stationSelect = document.getElementById('station-select');
  const foodTitle = document.querySelector('.top3-food h3');
  const foodList = document.querySelector('.food-list');
  const confirmBtn = document.querySelector('.confirm-btn');

  const codeToIdMap = {};
  const codeToNameMap = {};

  const dummyMap = new google.maps.Map(document.createElement('div'));
  placesService = new google.maps.places.PlacesService(dummyMap);

  try {
    const linesRes = await fetch('http://140.131.115.97:8000/api/lines/');
    const lines = await linesRes.json();

    for (const line of lines) {
      const stationsRes = await fetch(`http://140.131.115.97:8000/api/lines/${line.id}/stations/`);
      const stations = await stationsRes.json();

      stations.forEach(station => {
        codeToIdMap[station.station_code] = station.id;
        codeToNameMap[station.station_code] = station.name;

        const option = document.createElement('option');
        option.value = station.station_code;
        option.textContent = `${station.station_code} ${station.name}`;
        stationSelect.appendChild(option);
      });
    }

    if (stationSelect.options.length > 0) {
      stationSelect.selectedIndex = 0;
    }
  } catch (err) {
    console.error('🚨 無法載入站點資料：', err);
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

    try {
      const res = await fetch(`http://140.131.115.97:8000/api/stations/${stationId}/restaurants/`);
      const data = await res.json();

      foodList.innerHTML = '';

      if (data.length === 0) {
        foodList.innerHTML = '<p>目前尚無推薦美食</p>';
      } else {
        const top3 = data.slice(0, 3);

        const results = await Promise.all(top3.map(async item => {
          let photoUrl = await getPhotoFromGoogle(item.place_id);
          if (!photoUrl && item.name && item.address) {
            photoUrl = await getPhotoByQuery(`${item.name}, ${item.address}`);
          }
          return {
            ...item,
            photoUrl: photoUrl || 'https://via.placeholder.com/400x200?text=No+Image'
          };
        }));

        for (const item of results) {
          const card = document.createElement('div');
          card.className = 'food-item';

          card.innerHTML = `
          <h4 class="section-title">🏢 商家資訊</h4>
          <img src="${item.photoUrl}" alt="${item.name}" class="restaurant-img" loading="lazy">
          <h4 class="restaurant-name" style="font-size: 18px; color: #2c3e50; font-weight: bold; margin-top: 8px;">
            <a href="#" onclick='goToStationPage(${JSON.stringify(item).replace(/'/g, "\\'")})' style="text-decoration: none; color: #2c3e50;">
              ${item.name}
            </a>
          </h4>
          <p class="rating">⭐ 評分：${item.rating || '無評分'}</p>
          <p class="address">${item.address || '地址未知'}</p>
          <div class="btn-group">
            <button class="review-btn" onclick="fetchReviews('${item.place_id}', '${item.name}')">查看評論</button>
            <button class="close-btn" onclick="this.closest('.food-item').remove()">關閉</button>
          </div>
        `;

          foodList.appendChild(card);
        }
      }
    } catch (err) {
      foodList.innerHTML = '<p>⚠️ 餐廳資料載入失敗</p>';
      console.error('🚨 取得餐廳資料失敗：', err);
    }
  });
});

async function getPhotoFromGoogle(placeId) {
  return new Promise((resolve) => {
    if (!placesService || !placeId) return resolve(null);

    const request = {
      placeId,
      fields: ['photos']
    };

    placesService.getDetails(request, (place, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && place.photos?.length) {
        const photoUrl = place.photos[0].getUrl({ maxWidth: 400 });
        resolve(photoUrl);
      } else {
        resolve(null);
      }
    });
  });
}

async function getPhotoByQuery(query) {
  return new Promise((resolve) => {
    if (!placesService || !query) return resolve(null);

    const request = {
      query: query,
      fields: ['place_id']
    };

    placesService.findPlaceFromQuery(request, (results, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && results.length > 0) {
        const placeId = results[0].place_id;
        getPhotoFromGoogle(placeId).then(resolve);
      } else {
        resolve(null);
      }
    });
  });
}

function fetchReviews(placeId, name) {
  alert(`🚀 準備查看 ${name} 的評論\nPlace ID: ${placeId}`);
}

function goToStationPage(item) {
  const stationSelect = document.getElementById('station-select');
  const selectedOption = stationSelect.options[stationSelect.selectedIndex];
  const stationName = selectedOption.textContent.split(' ').slice(1).join(' '); // 去掉站代碼，只留站名

  localStorage.setItem('selectedRestaurant', JSON.stringify({
    ...item,
    station: stationName,
    latitude: item.latitude,
    longitude: item.longitude
  }));

  window.location.href = 'review.html';
}

