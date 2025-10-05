window.addEventListener('DOMContentLoaded', async () => {
    const data = JSON.parse(localStorage.getItem('selectedRestaurant'));
    if (!data) {
      alert('❌ 找不到商家資料');
      return;
    }
  
    // 把捷運站名稱顯示在 header
    document.getElementById('restaurant-name').textContent = `${data.station} 美食`;
  
    const lat = parseFloat(data.latitude);
    const lng = parseFloat(data.longitude);
    const isValidLatLng = !isNaN(lat) && !isNaN(lng);
  
    const mapDiv = document.getElementById('map');
    const map = new google.maps.Map(mapDiv, {
      center: isValidLatLng ? { lat, lng } : { lat: 25.0330, lng: 121.5654 },
      zoom: 16
    });
  
    new google.maps.Marker({
      position: isValidLatLng ? { lat, lng } : { lat: 25.0330, lng: 121.5654 },
      map: map,
      title: data.name
    });
  
    const reviewList = document.getElementById('review-list');
  
    try {
    const response = await fetch(`http://140.131.115.112:8000/api/restaurants/${data.id}/reviews/`);
      if (!response.ok) throw new Error(`HTTP 錯誤 ${response.status}`);
      const reviews = await response.json();
  
      if (reviews.length === 0) {
        for (let i = 0; i < 5; i++) {
          const placeholder = document.createElement('div');
          placeholder.className = 'review-card';
          placeholder.textContent = '尚無評論';
          reviewList.appendChild(placeholder);
        }
      } else {
        reviews.slice(0, 5).forEach(review => {
          const div = document.createElement('div');
          div.className = 'review-card';
          div.textContent = review.text || review.content || '（無內容）';
          reviewList.appendChild(div);
        });
      }
    } catch (error) {
      console.error('🚨 無法取得評論：', error);
      for (let i = 0; i < 5; i++) {
        const placeholder = document.createElement('div');
        placeholder.className = 'review-card';
        placeholder.textContent = '評論載入失敗';
        reviewList.appendChild(placeholder);
      }
    }
  });