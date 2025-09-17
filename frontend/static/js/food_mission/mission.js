document.addEventListener("DOMContentLoaded", async () => {
  const container = document.body;

  try {
    const res = await fetch('http://140.131.115.112:8000/api/api/top-checkin-restaurants/');
    const data = await res.json();
    const restaurants = data.restaurants;

    if (!Array.isArray(restaurants) || restaurants.length === 0) {
      container.innerHTML += "<p>⚠️ 尚無打卡餐廳資料</p>";
      return;
    }

    for (const r of restaurants) {
      const card = await createRestaurantCard(r);
      container.appendChild(card);
    }
  } catch (err) {
    console.error("🚨 無法取得打卡餐廳列表：", err);
  }
});

async function createRestaurantCard(data) {
  const card = document.createElement("section");
  card.className = "card";

  const imgBox = document.createElement("div");
  imgBox.className = "img-box";
  imgBox.textContent = "📷 圖片未提供"; // 預設文字

  const info = document.createElement("div");
  info.className = "info";

  const title = document.createElement("h2");
  title.textContent = data.restaurant_name;

  const ratingDiv = document.createElement("div");
  ratingDiv.className = "rating";
  ratingDiv.innerHTML = `
    <span class="star-label">⭐ ${data.rating}</span>
    <span class="count">(${data.review_count} 則評論)</span>
  `;

  const addressP = document.createElement("p");
  addressP.textContent = `地址：${data.address}`;

  const phoneP = document.createElement("p");
  phoneP.textContent = `電話：${data.phone}`;

  const tagDiv = document.createElement("div");
  tagDiv.className = "tags";
  tagDiv.innerHTML = `
    <a href="store_details.html?name=${encodeURIComponent(data.restaurant_name)}">
      <button>🔍 查看詳情</button>
    </a>
    <button>均消 $${data.price_level * 100}</button>
    <a href="${data.website}" target="_blank"><button>🌐 官方網站</button></a>
  `;

  info.appendChild(title);
  info.appendChild(ratingDiv);
  info.appendChild(addressP);
  info.appendChild(phoneP);
  info.appendChild(tagDiv);

  card.appendChild(imgBox);
  card.appendChild(info);

  // 🔥 嘗試去 Google Places API 抓圖片
  try {
    await fetchPlacePhoto(data.restaurant_name, imgBox);
  } catch (err) {
    console.warn(`⚠️ 無法載入圖片：${data.restaurant_name}`, err);
  }

  return card;
}

async function fetchPlacePhoto(name, imgBox) {
  const service = new google.maps.places.PlacesService(document.createElement('div'));

  return new Promise((resolve, reject) => {
    service.textSearch({ query: name + " 台灣" }, (results, status) => {
      if (status === google.maps.places.PlacesServiceStatus.OK && results[0]?.photos?.length > 0) {
        const photoUrl = results[0].photos[0].getUrl({ maxWidth: 400 });
        imgBox.style.backgroundImage = `url('${photoUrl}')`;
        imgBox.style.backgroundSize = "cover";
        imgBox.style.backgroundPosition = "center";
        imgBox.textContent = ""; // 清除原本的📷文字
        resolve();
      } else {
        reject(new Error("找不到照片"));
      }
    });
  });
}
