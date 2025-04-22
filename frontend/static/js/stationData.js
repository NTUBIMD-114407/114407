const stationData = {
    "BR": {
        name: "文湖線",
        stations: [
            { id: "BR01", name: "動物園" },
            { id: "BR02", name: "木柵" },
            { id: "BR03", name: "萬芳社區" },
            { id: "BR04", name: "萬芳醫院" },
            { id: "BR05", name: "辛亥" },
            { id: "BR06", name: "麟光" },
            { id: "BR07", name: "六張犁" },
            { id: "BR08", name: "科技大樓" },
            { id: "BR09", name: "大安" },
            { id: "BR10", name: "忠孝復興" },
            { id: "BR11", name: "南京復興" },
            { id: "BR12", name: "中山國中" },
            { id: "BR13", name: "松山機場" },
            { id: "BR14", name: "大直" },
            { id: "BR15", name: "劍南路" },
            { id: "BR16", name: "西湖" },
            { id: "BR17", name: "港墘" },
            { id: "BR18", name: "文德" },
            { id: "BR19", name: "內湖" },
            { id: "BR20", name: "大湖公園" },
            { id: "BR21", name: "葫洲" },
            { id: "BR22", name: "東湖" },
            { id: "BR23", name: "南港軟體園區" },
            { id: "BR24", name: "南港展覽館" }
        ]
    },
    // 可以繼續添加其他路線...
};

// 導出資料
if (typeof module !== 'undefined' && module.exports) {
    module.exports = stationData;
} 