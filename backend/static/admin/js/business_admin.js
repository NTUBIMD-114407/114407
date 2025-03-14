document.addEventListener('DOMContentLoaded', function() {
    const placeIdInput = document.getElementById('id_google_place_id');
    if (!placeIdInput) return;

    // 創建自動填充按鈕
    const autoFillButton = document.createElement('button');
    autoFillButton.type = 'button';
    autoFillButton.textContent = '自動填充商家資訊';
    autoFillButton.style.marginLeft = '10px';
    placeIdInput.parentNode.appendChild(autoFillButton);

    autoFillButton.addEventListener('click', async function(e) {
        e.preventDefault();
        const placeId = placeIdInput.value;
        if (!placeId) {
            alert('請先輸入 Google Place ID');
            return;
        }

        try {
            const response = await fetch(`/admin/users/business/fetch-place-details/?place_id=${placeId}`);
            const data = await response.json();

            if (response.ok) {
                // 填充基本資訊
                document.getElementById('id_name').value = data.name;
                document.getElementById('id_address').value = data.address;
                document.getElementById('id_latitude').value = data.latitude;
                document.getElementById('id_longitude').value = data.longitude;
                document.getElementById('id_phone').value = data.phone || '';
                document.getElementById('id_website').value = data.website || '';
                document.getElementById('id_rating').value = data.rating || '';
                document.getElementById('id_rating_count').value = data.rating_count || 0;
                document.getElementById('id_business_status').value = data.business_status;
                
                // 填充商家類型和營業時間（JSON 格式）
                document.getElementById('id_types').value = JSON.stringify(data.types);
                document.getElementById('id_opening_hours').value = JSON.stringify(data.opening_hours);
            } else {
                alert(data.error || '無法獲取商家資訊');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('發生錯誤，請查看控制台');
        }
    });
}); 