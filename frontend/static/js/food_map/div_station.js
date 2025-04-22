const stations = [
    { name: "台北車站", code: "R10", x: 45, y: 62 },
    { name: "西門", code: "BL11", x: 32, y: 66 },
    { name: "忠孝敦化", code: "BL13", x: 61, y: 65 },
    { name: "龍山寺", code: "BL10", x: 28, y: 67.5 },
    { name: "國父紀念館", code: "BL17", x: 67, y: 61.5 },
    { name: "昆陽", code: "BL21", x: 81, y: 61 },
    { name: "南港", code: "BL22", x: 85, y: 61 },
    { name: "南港展覽館", code: "BL23", x: 94, y: 59 },
    { name: "府中", code: "BL06", x: 16, y: 81 },
    { name: "板橋", code: "BL07", x: 16, y: 77 },
    { name: "新埔", code: "BL08", x: 20, y: 74 },
    { name: "江子翠", code: "BL09", x: 25, y: 72 },
    { name: "善導寺", code: "BL13", x: 45, y: 65 },
    { name: "忠孝新生", code: "BL14", x: 52, y: 62 },
    { name: "忠孝復興", code: "BL15", x: 60, y: 62 },
    { name: "永春", code: "BL19", x: 74, y: 65 },
    { name: "後山埤", code: "BL20", x: 79, y: 64 },
    { name: "亞東醫院", code: "BL05", x: 14.5, y: 84 },
    { name: "海山", code: "BL04", x: 16, y: 87 },
    { name: "土城", code: "BL03", x: 16, y: 90.5 },
    { name: "永寧", code: "BL02", x: 13, y: 93 },
    { name: "頂埔", code: "BL01", x: 11, y: 95.5 },
    { name: "市政府", code: "BL18", x: 69, y: 65 },
    { name: "中山", code: "R11", x: 43, y: 57 },
    { name: "象山", code: "R02", x: 72, y: 67 },
    { name: "淡水", code: "R28", x: 11, y: 15 },
    { name: "紅樹林", code: "R27", x: 14, y: 18 },
    { name: "竹圍", code: "R26", x: 14, y: 22 },
    { name: "關渡", code: "R25", x: 14, y: 25 },
    { name: "忠義", code: "R24", x: 20, y: 28 },
    { name: "復興崗", code: "R23", x: 25, y: 28 },
    { name: "北投", code: "R22", x: 30, y: 28 },
    { name: "新北投", code: "R22A", x: 36, y: 24 },
    { name: "奇岩", code: "R21", x: 35.5, y: 28 },
    { name: "芝山", code: "R17", x: 43, y: 38.5 },
    { name: "明德", code: "R18", x: 43, y: 35 },
    { name: "石牌", code: "R19", x: 41, y: 32 },
    { name: "唭哩岸", code: "R20", x: 38, y: 30 },
    { name: "士林", code: "R16", x: 43, y: 42 },
    { name: "劍潭", code: "R15", x: 43, y: 45 },
    { name: "圓山", code: "R14", x: 43, y: 48.5 },
    { name: "民權西路", code: "R13", x: 43.5, y: 50.5 },
    { name: "雙連", code: "R12", x: 43, y: 55 },
    { name: "臺大醫院", code: "R09", x: 39, y: 66 },
    { name: "紀念堂", code: "R08", x: 40, y: 71 },
    { name: "東門", code: "R07", x: 46.5, y: 67.5 },
    { name: "森林公園", code: "R06", x: 52.5, y: 67.5 },
    { name: "大安", code: "R05", x: 58, y: 67.5 },
    { name: "信義安和", code: "R04", x: 64, y: 67.5 },
    { name: "台北101/世貿", code: "R03", x: 67, y: 70.5 },
    { name: "頂溪", code: "O04", x: 36, y: 77.5 },
    { name: "新店", code: "G01", x: 56, y: 95 },
    { name: "景美", code: "G05", x: 56, y: 82.5 }
  ];
  
  
  // 假資料：對應站點的美食推薦
  const foodTop3 = {
    "R10": ["滷肉飯王", "牛肉麵之家", "珍珠奶茶店"],
    "BL11": ["阿宗麵線", "紅豆餅", "西門炸雞"],
    "BL15": ["義大利麵館", "拉麵店", "便當鋪"],
    "BL18": ["燒肉專門店", "日式便當", "甜點咖啡屋"],
    "G01": ["早午餐店", "燒餅油條", "川味牛肉麵"],
    "BL01": ["便當店", "陽春麵", "涼麵小吃"],
    "R02": ["火鍋店", "壽司店", "韓式炸雞"],
    "R07": ["東門餃子館", "湯包專賣", "炸醬麵館"],
    "R22": ["溫泉拉麵", "北投便當", "古早味早餐"]
  };
  
  document.addEventListener("DOMContentLoaded", () => {
    const mapContainer = document.querySelector(".map-container");
    const foodTitle = document.querySelector(".top3-food h3");
    const foodItems = document.querySelectorAll(".food-item");
  
    stations.forEach(station => {
      const div = document.createElement("div");
      div.className = "station";
      div.textContent = station.name;
      div.setAttribute("data-station", station.code);
      div.style.position = "absolute";
      div.style.left = `${station.x}%`;
      div.style.top = `${station.y}%`;
      div.style.transform = "translate(-50%, -50%)";
  
      // 點擊事件：顯示美食 Top3
      div.addEventListener("click", () => {
        const foods = foodTop3[station.code] || ["尚無資料"];
        foodTitle.textContent = `${station.name} 美食 TOP3`;
        foodItems.forEach((item, i) => item.textContent = foods[i] || "");
  
        // 滑動到美食區塊
        document.querySelector(".top3-food").scrollIntoView({ behavior: "smooth" });
      });
  
      mapContainer.appendChild(div);
    });
  });