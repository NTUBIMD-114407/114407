document.addEventListener("DOMContentLoaded", function () {
    const map = document.getElementById("metro-map");
    const stations = document.querySelectorAll(".station");

    function updateStationPositions() {
        const mapRect = map.getBoundingClientRect();
        stations.forEach(station => {
            const coords = station.getAttribute("data-coords").split(",");
            const xPercent = parseFloat(coords[0]);
            const yPercent = parseFloat(coords[1]);

            // 動態計算位置，根據圖片的尺寸
            const left = (mapRect.width * xPercent) / 100;
            const top = (mapRect.height * yPercent) / 100;

            station.style.left = `${left}px`;
            station.style.top = `${top}px`;
        });
    }

    window.addEventListener("resize", updateStationPositions);
    updateStationPositions();

    stations.forEach(station => {
        station.addEventListener("click", function () {
            const targetUrl = this.getAttribute("data-target");
            if (targetUrl) {
                window.location.href = targetUrl;
            }
        });
    });
});
