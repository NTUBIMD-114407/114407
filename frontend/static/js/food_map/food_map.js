let placesService;
let allRestaurants = [];

window.addEventListener('load', async () => {
  const stationSelect = document.getElementById('station-select');
  const foodTitle = document.querySelector('.top3-food h3');
  const foodList = document.querySelector('.food-list');
  const confirmBtn = document.querySelector('.confirm-btn');
  const loadMoreBtn = document.querySelector('.load-more-btn');

  const codeToIdMap = {};
  const codeToNameMap = {};

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
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    });
   
    if (!userRes.ok) {
      throw new Error(`HTTP error! status: ${userRes.status}`);
    }
   
    const user = await userRes.json();
    console.log('當前使用者資訊：', user);
   
    if (user.isAuthenticated && user.user) {
      console.log('已登入，使用者名稱：', user.user.username);
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('userEmail', user.user.email);
      localStorage.setItem('username', user.user.username);
    } else {
      console.log('未登入或認證失敗');
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
      renderRestaurantCards(results);

      if (data.length > 3) {
        loadMoreBtn.style.display = 'block';
      }
    } catch (err) {
      foodList.innerHTML = '<p>⚠️ 餐廳資料載入失敗</p>';
      console.error('🚨 取得餐廳資料失敗：', err);
    }
  });

  loadMoreBtn.addEventListener('click', async () => {
    const more = allRestaurants.slice(3);
    const results = await enrichWithPhotos(more);
    renderRestaurantCards(results);
    loadMoreBtn.style.display = 'none';
  });
});

async function enrichWithPhotos(list) {
  return await Promise.all(list.map(async item => {
    let photoUrl = await getPhotoFromGoogle(item.place_id);
    if (!photoUrl && item.name && item.address) {
      photoUrl = await getPhotoByQuery(`${item.name}, ${item.address}`);
    }
    return {
      ...item,
      photoUrl: photoUrl || 'https://via.placeholder.com/400x200?text=No+Image'
    };
  }));
}

function renderRestaurantCards(list) {
  const foodList = document.querySelector('.food-list');

  list.forEach(item => {
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
        <button class="review-btn" onclick="fetchReviews('${item.id}', '${item.name}')">查看評論</button>
        <button class="close-btn" onclick="this.closest('.food-item').remove()">關閉</button>
      </div>
    `;
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
