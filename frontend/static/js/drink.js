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