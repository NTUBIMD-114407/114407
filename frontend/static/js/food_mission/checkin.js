let selectedStars = 0;
let allRestaurants = [];
let latestSelectedRestaurant = null;

document.addEventListener('DOMContentLoaded', () => {
  renderStars(0);
  setupDynamicAutocomplete();

  document.getElementById('export-btn').addEventListener('click', async () => {
    const storeInput = document.getElementById('store');
    const storeName = storeInput.value.trim();
    const station = document.getElementById('station').textContent.trim();
    const comment = document.getElementById('comment').value.trim();

    if (!storeName || !station || !comment || selectedStars === 0) {
      alert("⚠️ 請填寫完整資料與星數");
      return;
    }

    if (!latestSelectedRestaurant) {
      alert('❌ 找不到餐廳對應資料，請重新選擇');
      return;
    }

const username = localStorage.getItem("username") || "訪客";

const jsonData = {
  restaurant_name: latestSelectedRestaurant.name,
  rating: selectedStars,
  comment: comment,
  reviewer_name: username,
  restaurant: latestSelectedRestaurant.id,
  station: latestSelectedRestaurant.station_id,
  metro_line: latestSelectedRestaurant.metro_line_id
};

    console.log("📦 準備送出：", jsonData);

    try {
      const response = await fetch(`http://140.131.115.112:8000/api/api/checkin-reviews/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
      });

      const result = await response.json();

      if (response.ok) {
        document.querySelector(".submit-wrapper").innerHTML =
          `<p style="color: green; font-weight: bold; background-color: #e6ffe6; padding: 10px; border-radius: 10px; text-align: center;">✅ 打卡成功！感謝你的參與！</p>`;
      } else {
        alert(`❌ 上傳失敗：${result.error || "請稍後再試"}`);
      }
    } catch (error) {
      console.error("🚨 發生錯誤：", error);
      alert("❌ 發生錯誤，請檢查網路或伺服器");
    }
  });

  document.querySelector('.tag')?.addEventListener('click', () => {
    window.location.href = 'food_mission.html';
  });

  document.querySelector('.back-icon')?.addEventListener('click', () => {
    window.location.href = 'homepage.html';
  });
});

function renderStars(count) {
  const container = document.getElementById('star-container');
  container.innerHTML = '';
  for (let i = 1; i <= 5; i++) {
    const star = document.createElement('span');
    star.textContent = i <= count ? '⭐' : '☆';
    star.style.fontSize = '24px';
    star.style.cursor = 'pointer';
    star.dataset.value = i;

    star.addEventListener('click', () => {
      selectedStars = i;
      renderStars(selectedStars);
    });

    container.appendChild(star);
  }
}

function setupDynamicAutocomplete() {
  const input = document.getElementById('store');
  const loadingIndicator = document.createElement('div');
  loadingIndicator.id = 'loading-indicator';
  loadingIndicator.textContent = '🔄 載入中...';
  loadingIndicator.style.color = 'gray';
  loadingIndicator.style.fontSize = '14px';
  loadingIndicator.style.marginTop = '4px';
  input.parentElement.appendChild(loadingIndicator);
  loadingIndicator.style.display = 'none';

  let awesomplete = new Awesomplete(input, {
    list: [],
    autoFirst: true,
    minChars: 1,
    maxItems: 10,
    filter: function (text, input) {
      return text.toLowerCase().includes(input.toLowerCase());
    },
    replace: function (text) {
      this.input.value = text;
      const selected = allRestaurants.find(r => r.name === text);
      const stationDisplay = document.getElementById('station');
      if (selected && selected.station_name) {
        stationDisplay.textContent = selected.station_name;
        stationDisplay.style.cssText = 'background-color: #fff; border: 1px solid #ccc; padding: 6px 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #333; display: inline-block; min-width: 120px;';
        latestSelectedRestaurant = selected;
      } else {
        stationDisplay.textContent = '⚠️ 無法取得站名';
        stationDisplay.style.backgroundColor = 'transparent';
      }
    }
  });

  let timeoutId;
  input.addEventListener('input', () => {
    clearTimeout(timeoutId);
    const query = input.value.trim();
    if (query.length < 1) return;

    loadingIndicator.style.display = 'block';

    timeoutId = setTimeout(async () => {
      try {
        const res = await fetch(`http://140.131.115.112:8000/api/restaurants/search/?name=${encodeURIComponent(query)}`);
        const result = await res.json();
        allRestaurants = result.data || [];

        awesomplete.list = allRestaurants.map(r => r.name);
      } catch (error) {
        console.error('🚨 餐廳查詢失敗：', error);
      } finally {
        loadingIndicator.style.display = 'none';
      }
    }, 200);
  });

  input.addEventListener('blur', () => {
    const typed = input.value.trim();
    const selected = allRestaurants.find(r => r.name === typed);
    const stationDisplay = document.getElementById('station');
    if (selected && selected.station_name) {
      stationDisplay.textContent = selected.station_name;
      stationDisplay.style.cssText = 'background-color: #fff; border: 1px solid #ccc; padding: 6px 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #333; display: inline-block; min-width: 120px;';
      latestSelectedRestaurant = selected;
    }
  });
}
