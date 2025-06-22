import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
import math
import time
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
import urllib.parse

# --- データ定義 (ユーザー提供のデータに全面的に刷新・最大限追加) ---
SPOTS = [
    # 北海道
    {"name": "名寄市（北海道）- なよろ市立天文台", "lat": 44.3533, "lon": 142.4862, "sqm_level": 20.98},
    {"name": "伊達市（北海道）- 北湯沢温泉", "lat": 42.6698, "lon": 140.9233, "sqm_level": 21.02},
    {"name": "斜里町（北海道）- 知床国立公園", "lat": 44.0768, "lon": 144.8561, "sqm_level": 21.84},
    {"name": "陸別町（北海道）- 銀河の森天文台", "lat": 43.4682, "lon": 143.7630, "sqm_level": 21.72},
    {"name": "弟子屈町（北海道）- 摩周湖", "lat": 43.5850, "lon": 144.5222, "sqm_level": 21.90},

    # 東北
    {"name": "八戸市（青森県）- 種差海岸", "lat": 40.5233, "lon": 141.5658, "sqm_level": 19.64},
    {"name": "二戸市（岩手県）- 古橋児童公園", "lat": 40.2647, "lon": 141.3039, "sqm_level": 20.42},
    {"name": "仙台市青葉区（宮城県）- 大倉ダム", "lat": 38.3094, "lon": 140.7075, "sqm_level": 19.71},
    {"name": "朝日町（山形県）- Asahi自然観", "lat": 38.3752, "lon": 140.0911, "sqm_level": 21.05},
    {"name": "田村市（福島県）- 星の村天文台", "lat": 37.3621, "lon": 140.6756, "sqm_level": 20.87},
    {"name": "いわき市（福島県）- いわき市中央台鹿島", "lat": 37.0160, "lon": 140.8930, "sqm_level": 19.40},
    {"name": "白河市（福島県）- 白河関の森公園", "lat": 37.0664, "lon": 140.1983, "sqm_level": 20.46},
    {"name": "広野町（福島県）- SUZUKI天体観測所", "lat": 37.2223, "lon": 141.0097, "sqm_level": 20.71},

    # 関東
    {"name": "つくば市（茨城県）- 吾妻", "lat": 36.0833, "lon": 140.1118, "sqm_level": 18.36},
    {"name": "常陸大宮市（茨城県）- 花立自然公園", "lat": 36.6369, "lon": 140.4578, "sqm_level": 20.60},
    {"name": "佐野市（栃木県）- 作原自然環境保全地域", "lat": 36.4259, "lon": 139.5161, "sqm_level": 20.52},
    {"name": "高山村（群馬県）- ぐんま天文台", "lat": 36.6331, "lon": 138.9631, "sqm_level": 20.31},
    {"name": "玉村町（群馬県）- 道の駅玉村宿", "lat": 36.3108, "lon": 139.1175, "sqm_level": 15.93},
    {"name": "さいたま市緑区（埼玉県）- 浦和美園4丁目公園", "lat": 35.9126, "lon": 139.7226, "sqm_level": 17.27},
    {"name": "草加市（埼玉県）- 谷塚駅前", "lat": 35.8086, "lon": 139.8003, "sqm_level": 17.53},
    {"name": "松戸市（千葉県）", "lat": 35.7876, "lon": 139.9043, "sqm_level": 17.46},
    {"name": "佐倉市（千葉県）", "lat": 35.7208, "lon": 140.2311, "sqm_level": 18.67},
    {"name": "習志野市（千葉県）- 谷津奏の杜公園", "lat": 35.6723, "lon": 140.0150, "sqm_level": 15.14},
    {"name": "八千代市（千葉県）", "lat": 35.7256, "lon": 140.1008, "sqm_level": 18.22},
    {"name": "鴨川市（千葉県）", "lat": 35.1158, "lon": 139.9022, "sqm_level": 20.20},
    {"name": "君津市（千葉県）", "lat": 35.3308, "lon": 139.8944, "sqm_level": 17.43},
    {"name": "いすみ市（千葉県）", "lat": 35.2573, "lon": 140.3159, "sqm_level": 19.90},
    {"name": "奥多摩町（東京都）- 奥多摩湖", "lat": 35.7905, "lon": 139.0069, "sqm_level": 20.41},
    {"name": "神津島村（東京都）- 赤崎遊歩道", "lat": 34.2375, "lon": 139.1328, "sqm_level": 21.21},
    {"name": "小笠原村（東京都）- コペペ海岸", "lat": 27.0800, "lon": 142.1952, "sqm_level": 21.47},
    {"name": "三鷹市（東京都）- 三鷹市大沢", "lat": 35.6748, "lon": 139.5414, "sqm_level": 17.18},
    {"name": "小金井市（東京都）- 都立小金井公園", "lat": 35.7163, "lon": 139.5126, "sqm_level": 16.66},
    {"name": "羽村市（東京都）", "lat": 35.7621, "lon": 139.3103, "sqm_level": 17.89},
    {"name": "清川村（神奈川県）- 宮ヶ瀬湖畔", "lat": 35.5333, "lon": 139.2333, "sqm_level": 19.47},
    {"name": "相模原市中央区（神奈川県）- 下溝", "lat": 35.5284, "lon": 139.3872, "sqm_level": 17.72},
    {"name": "藤沢市（神奈川県）", "lat": 35.3396, "lon": 139.4893, "sqm_level": 16.86},

    # 中部
    {"name": "新潟市北区（新潟県）", "lat": 37.9157, "lon": 139.1171, "sqm_level": 19.52},
    {"name": "佐渡市（新潟県）- 大野亀", "lat": 38.2253, "lon": 138.4117, "sqm_level": 21.46},
    {"name": "胎内市（新潟県）- 胎内自然天文館", "lat": 38.0553, "lon": 139.5011, "sqm_level": 21.18},
    {"name": "富山市（富山県）- 古洞ダム", "lat": 36.6300, "lon": 137.1519, "sqm_level": 19.43},
    {"name": "金沢市（石川県）", "lat": 36.5611, "lon": 136.6566, "sqm_level": 17.99},
    {"name": "かほく市（石川県）", "lat": 36.7208, "lon": 136.7025, "sqm_level": 19.20},
    {"name": "能登町（石川県）- 満天星", "lat": 37.3197, "lon": 137.0707, "sqm_level": 20.78},
    {"name": "小浜市（福井県）", "lat": 35.4958, "lon": 135.7453, "sqm_level": 20.17},
    {"name": "大野市（福井県）- 福井県自然保護センター", "lat": 35.9189, "lon": 136.6203, "sqm_level": 20.86},
    {"name": "おおい町（福井県）- 名田庄", "lat": 35.4182, "lon": 135.6888, "sqm_level": 21.58},
    {"name": "富士吉田市（山梨県）- 富士北麓公園", "lat": 35.4678, "lon": 138.8028, "sqm_level": 19.18},
    {"name": "北杜市（山梨県）- 白州町", "lat": 35.8361, "lon": 138.3308, "sqm_level": 10.46},
    {"name": "富士河口湖町（山梨県）- 大石公園", "lat": 35.5186, "lon": 138.7569, "sqm_level": 20.26},
    {"name": "小菅村（山梨県）- ヘリポート", "lat": 35.8428, "lon": 139.0067, "sqm_level": 20.80},
    {"name": "丹波山村（山梨県）", "lat": 35.8564, "lon": 138.9508, "sqm_level": 20.90},
    {"name": "松本市（長野県）- 乗鞍高原いがや", "lat": 36.1264, "lon": 137.6652, "sqm_level": 21.30},
    {"name": "上田市（長野県）", "lat": 36.4019, "lon": 138.2531, "sqm_level": 20.26},
    {"name": "岡谷市（長野県）- 塩嶺王城パークライン", "lat": 36.0463, "lon": 138.0163, "sqm_level": 19.02},
    {"name": "飯田市（長野県）", "lat": 35.5161, "lon": 137.8228, "sqm_level": 21.11},
    {"name": "諏訪市（長野県）- 霧ヶ峰自然保護センター", "lat": 36.0963, "lon": 138.2001, "sqm_level": 20.68},
    {"name": "小諸市（長野県）", "lat": 36.3267, "lon": 138.4231, "sqm_level": 20.06},
    {"name": "伊那市（長野県）- 西春近北小学校", "lat": 35.8119, "lon": 137.9575, "sqm_level": 20.22},
    {"name": "駒ヶ根市（長野県）- アルプスの丘", "lat": 35.7289, "lon": 137.8932, "sqm_level": 21.78},
    {"name": "茅野市（長野県）", "lat": 35.9939, "lon": 138.1561, "sqm_level": 21.00},
    {"name": "塩尻市（長野県）- 奈良井ダム", "lat": 35.9869, "lon": 137.7819, "sqm_level": 20.77},
    {"name": "佐久市（長野県）", "lat": 36.2514, "lon": 138.4739, "sqm_level": 20.10},
    {"name": "千曲市（長野県）- 中央公園", "lat": 36.4678, "lon": 138.1206, "sqm_level": 20.65},
    {"name": "東御市（長野県）", "lat": 36.3572, "lon": 138.3314, "sqm_level": 19.62},
    {"name": "南牧村（長野県）- 野辺山", "lat": 35.9575, "lon": 138.4770, "sqm_level": 20.51},
    {"name": "北相木村（長野県）- 栃原", "lat": 36.0353, "lon": 138.5619, "sqm_level": 21.18},
    {"name": "下諏訪町（長野県）- 八島湿原", "lat": 36.1167, "lon": 138.1333, "sqm_level": 20.62},
    {"name": "原村（長野県）- 八ヶ岳自然文化園", "lat": 35.9594, "lon": 138.2522, "sqm_level": 20.77},
    {"name": "箕輪町（長野県）- 箕輪北小学校", "lat": 35.9328, "lon": 137.9869, "sqm_level": 20.25},
    {"name": "南箕輪村（長野県）", "lat": 35.8894, "lon": 137.9839, "sqm_level": 20.29},
    {"name": "阿智村（長野県）- 伍和栗矢観測所", "lat": 35.4594, "lon": 137.7885, "sqm_level": 20.67},
    {"name": "下條村（長野県）", "lat": 35.4182, "lon": 137.8427, "sqm_level": 20.63},
    {"name": "大鹿村（長野県）", "lat": 35.5398, "lon": 138.0805, "sqm_level": 21.63},
    {"name": "木祖村（長野県）- 東京大学木曽観測所", "lat": 35.9750, "lon": 137.6433, "sqm_level": 20.53},
    {"name": "王滝村（長野県）", "lat": 35.8617, "lon": 137.5583, "sqm_level": 20.74},
    {"name": "木曽町（長野県）- 木曽馬の里", "lat": 35.8821, "lon": 137.6256, "sqm_level": 21.71},
    {"name": "山形村（長野県）- ミラードーム", "lat": 36.1667, "lon": 137.8833, "sqm_level": 19.88},
    {"name": "朝日村（長野県）- 朝日小学校", "lat": 36.1436, "lon": 137.8467, "sqm_level": 20.50},
    {"name": "坂城町（長野県）", "lat": 36.4528, "lon": 138.1883, "sqm_level": 19.80},
    {"name": "揖斐川町（岐阜県）- 西横山", "lat": 35.5645, "lon": 136.4719, "sqm_level": 20.56},
    {"name": "可児市（岐阜県）- 可児市天文台", "lat": 35.4150, "lon": 137.0658, "sqm_level": 18.23},
    {"name": "清水町（静岡県）", "lat": 35.1017, "lon": 138.9056, "sqm_level": 18.22},

    # 近畿
    {"name": "名古屋市中区（愛知県）- 名古屋市科学館", "lat": 35.1681, "lon": 136.8990, "sqm_level": 16.30},
    {"name": "豊田市（愛知県）", "lat": 35.0833, "lon": 137.1500, "sqm_level": 20.31},
    {"name": "新城市（愛知県）", "lat": 34.9000, "lon": 137.5000, "sqm_level": 20.10},
    {"name": "設楽町（愛知県）- つぐ高原グリーンパーク", "lat": 35.1983, "lon": 137.5684, "sqm_level": 20.68},
    {"name": "東栄町（愛知県）", "lat": 35.0667, "lon": 137.6667, "sqm_level": 20.59},
    {"name": "豊根村（愛知県）- 茶臼山高原", "lat": 35.2223, "lon": 137.6610, "sqm_level": 20.62},
    {"name": "亀山市（三重県）- 鈴鹿馬子唄の里自然の家", "lat": 34.8770, "lon": 136.3533, "sqm_level": 19.68},
    {"name": "和束町（京都府）", "lat": 34.7865, "lon": 135.9103, "sqm_level": 19.35},
    {"name": "枚方市（大阪府）- ひらかたパーク", "lat": 34.8105, "lon": 135.6429, "sqm_level": 17.41},
    {"name": "神戸市西区（兵庫県）- 西神南", "lat": 34.7088, "lon": 135.0396, "sqm_level": 19.36},
    {"name": "淡路市（兵庫県）- 久留麻", "lat": 34.4833, "lon": 134.9667, "sqm_level": 19.03},
    {"name": "香美町（兵庫県）", "lat": 35.6027, "lon": 134.6158, "sqm_level": 18.34},
    {"name": "紀美野町（和歌山県）- みさと天文台", "lat": 34.1200, "lon": 135.3444, "sqm_level": 20.59},
    {"name": "古座川町（和歌山県）", "lat": 33.5658, "lon": 135.6661, "sqm_level": 21.26},
    
    # 中国
    {"name": "鳥取市（鳥取県）- さじアストロパーク", "lat": 35.3524, "lon": 134.0538, "sqm_level": 21.29},
    {"name": "米子市（鳥取県）", "lat": 35.4283, "lon": 133.3314, "sqm_level": 20.33},
    {"name": "倉吉市（鳥取県）- 関金町", "lat": 35.3789, "lon": 133.7225, "sqm_level": 20.88},
    {"name": "境港市（鳥取県）", "lat": 35.5436, "lon": 133.2325, "sqm_level": 19.74},
    {"name": "若桜町（鳥取県）", "lat": 35.3400, "lon": 134.3986, "sqm_level": 20.31},
    {"name": "八頭町（鳥取県）", "lat": 35.3583, "lon": 134.2583, "sqm_level": 20.37},
    {"name": "大山町（鳥取県）", "lat": 35.4678, "lon": 133.5222, "sqm_level": 20.67},
    {"name": "伯耆町（鳥取県）", "lat": 35.3592, "lon": 133.4542, "sqm_level": 20.85},
    {"name": "日南町（鳥取県）- 上萩山", "lat": 35.1098, "lon": 133.2081, "sqm_level": 21.04},
    {"name": "日野町（鳥取県）", "lat": 35.2158, "lon": 133.3267, "sqm_level": 20.75},
    {"name": "江府町（鳥取県）", "lat": 35.2817, "lon": 133.4756, "sqm_level": 20.63},
    {"name": "松江市（島根県）- 八千代公園", "lat": 35.4950, "lon": 133.1556, "sqm_level": 20.50},
    {"name": "浜田市（島根県）- 海の見える公園", "lat": 34.8981, "lon": 132.0678, "sqm_level": 20.65},
    {"name": "出雲市（島根県）", "lat": 35.3650, "lon": 132.7564, "sqm_level": 20.98},
    {"name": "大田市（島根県）", "lat": 35.1931, "lon": 132.4967, "sqm_level": 21.28},
    {"name": "邑南町（島根県）", "lat": 34.8814, "lon": 132.6685, "sqm_level": 21.16},
    {"name": "吉備中央町（岡山県）- 賀陽憩いの森公園", "lat": 34.8464, "lon": 133.7258, "sqm_level": 19.98},
    {"name": "倉敷市（岡山県）- ライフパーク倉敷", "lat": 34.5678, "lon": 133.7820, "sqm_level": 20.74},
    {"name": "井原市（岡山県）- 美星天文台", "lat": 34.6934, "lon": 133.5518, "sqm_level": 17.07},
    {"name": "東広島市（広島県）- 憩いの森公園", "lat": 34.4092, "lon": 132.7447, "sqm_level": 18.83},
    {"name": "山口市（山口県）- 阿東嘉年", "lat": 34.4601, "lon": 131.5287, "sqm_level": 21.33},
    {"name": "周南市（山口県）", "lat": 34.0536, "lon": 131.8058, "sqm_level": 20.50},
    
    # 四国
    {"name": "徳島市（徳島県）", "lat": 34.0700, "lon": 134.5547, "sqm_level": 19.55},
    {"name": "石井町（徳島県）", "lat": 34.0722, "lon": 134.4658, "sqm_level": 19.32},
    {"name": "松山市（愛媛県）", "lat": 33.8392, "lon": 132.7656, "sqm_level": 17.94},
    {"name": "今治市（愛媛県）- 宮窪町", "lat": 34.1624, "lon": 133.0906, "sqm_level": 20.87},
    {"name": "新居浜市（愛媛県）- 愛媛県総合科学博物館", "lat": 33.9189, "lon": 133.2503, "sqm_level": 19.70},
    {"name": "西条市（愛媛県）", "lat": 33.9189, "lon": 133.1811, "sqm_level": 20.23},
    {"name": "四国中央市（愛媛県）", "lat": 33.9833, "lon": 133.5500, "sqm_level": 20.36},
    {"name": "久万高原町（愛媛県）- 天体観測館", "lat": 33.6823, "lon": 132.8953, "sqm_level": 21.08},
    {"name": "高知市（高知県）- 土佐塾中学・高等学校", "lat": 33.5583, "lon": 133.4922, "sqm_level": 20.18},
    {"name": "安芸市（高知県）", "lat": 33.5019, "lon": 133.9017, "sqm_level": 20.93},
    {"name": "四万十市（高知県）- 四万十天文台", "lat": 33.0017, "lon": 132.9338, "sqm_level": 21.14},
    {"name": "芸西村（高知県）- 芸西天文台", "lat": 33.5414, "lon": 133.8239, "sqm_level": 21.15},
    {"name": "津野町（高知県）", "lat": 33.4862, "lon": 133.0903, "sqm_level": 21.36},
    
    # 九州・沖縄
    {"name": "八女市（福岡県）- 星のふるさと公園", "lat": 33.2100, "lon": 130.7300, "sqm_level": 20.62},
    {"name": "佐世保市（長崎県）- 白岳自然公園", "lat": 33.2803, "lon": 129.6178, "sqm_level": 20.58},
    {"name": "熊本市北区（熊本県）", "lat": 32.8469, "lon": 130.7411, "sqm_level": 18.88},
    {"name": "天草市（熊本県）", "lat": 32.4497, "lon": 130.1917, "sqm_level": 21.05},
    {"name": "山都町（熊本県）", "lat": 32.7067, "lon": 131.0253, "sqm_level": 20.85},
    {"name": "都城市（宮崎県）- 高崎町", "lat": 31.9167, "lon": 130.9833, "sqm_level": 19.85},
    {"name": "奄美市（鹿児島県）", "lat": 28.3752, "lon": 129.4942, "sqm_level": 21.61},
    {"name": "宇検村（鹿児島県）", "lat": 28.3031, "lon": 129.3242, "sqm_level": 21.44},
    {"name": "瀬戸内町（鹿児島県）- 油井岳", "lat": 28.1705, "lon": 129.3243, "sqm_level": 21.66},
    {"name": "龍郷町（鹿児島県）- 赤尾木", "lat": 28.4350, "lon": 129.5800, "sqm_level": 21.60},
    {"name": "与論町（鹿児島県）", "lat": 27.0425, "lon": 128.4219, "sqm_level": 21.53},
    {"name": "石垣市（沖縄県）", "lat": 24.3444, "lon": 124.1572, "sqm_level": 20.97},
    {"name": "宮古島市（沖縄県）", "lat": 24.7915, "lon": 125.2844, "sqm_level": 21.41},
    {"name": "名護市（沖縄県）", "lat": 26.5917, "lon": 127.9678, "sqm_level": 20.76},
    {"name": "大宜味村（沖縄県）", "lat": 26.6978, "lon": 128.1364, "sqm_level": 21.23},
    {"name": "東村（沖縄県）", "lat": 26.6333, "lon": 128.1500, "sqm_level": 21.18},
    {"name": "今帰仁村（沖縄県）- 今帰仁城跡", "lat": 26.6917, "lon": 127.9272, "sqm_level": 21.07},
    {"name": "本部町（沖縄県）", "lat": 26.6339, "lon": 127.8794, "sqm_level": 20.60},
    {"name": "竹富町（沖縄県）- 波照間島", "lat": 24.0558, "lon": 123.7788, "sqm_level": 21.40},
]

# --- 関数エリア ---
@st.cache_data(ttl=600)
def get_astro_data(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&exclude=minutely,alerts&appid={api_key}&lang=ja&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def estimate_travel_time(distance_km):
    avg_speed_kmh = 40
    time_h = distance_km / avg_speed_kmh
    total_minutes = int(time_h * 60)
    if total_minutes < 60:
        return f"{total_minutes}分"
    else:
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}時間{minutes}分"

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_sqm_description(sqm_value):
    if sqm_value >= 21.75: return "光害が全くない最高の夜空。天の川が雲のように明るく見えるレベルです。"
    elif sqm_value >= 21.5: return "非常に暗い夜空。天の川の構造がはっきりと見えます。"
    elif sqm_value >= 21.0: return "天の川の複雑な構造が確認でき、星団などの観測ができます。"
    elif sqm_value >= 20.0: return "山や海などの暗さ。天の川がよく見られます。"
    elif sqm_value >= 19.0: return "郊外の暗さ。天の川が見え始めます。"
    elif sqm_value >= 18.0: return "住宅地の明るさ。星座の形がよく分かります。"
    else: return "市街地の明るさ。主要な星や星座しか見えません。"

def get_weather_emoji(cloudiness):
    if cloudiness <= 10: return "☀️"
    elif cloudiness <= 50: return "🌤️"
    elif cloudiness <= 80: return "☁️"
    else: return "🌧️"

# --- アプリ本体 ---
st.set_page_config(page_title="ホシドコ - 雲量、暗さを指定後、天体観測地をご案内！", page_icon="🌠")
st.title("🌠 ホシドコ 🔭")
st.subheader("雲量、暗さを指定後、天体観測地をご案内！")

try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("【開発者向けエラー】secrets.tomlファイルまたはAPIキーの設定が見つかりません。")
    st.stop()

# --- サイドバー ---
st.sidebar.header("運営者情報")
st.sidebar.markdown("[📝 使い方や開発背景はこちら(note)](https://note.com/mute_murre9731/n/n163fc351ed30)")
st.sidebar.markdown("---")
st.sidebar.markdown("ご意見・ご感想はこちらまで")
st.sidebar.markdown("`oshika0829zan@gmail.com`")

# --- メイン画面 ---
st.header("① あなたの希望の条件は？")
desired_sqm = st.slider("目標の空の暗さ（SQM値）", 15.0, 22.0, 19.0, 0.1, help="SQMは空の明るさを示す単位で、数値が高いほど暗く、星空観測に適しています。")
st.info(f"{get_sqm_description(desired_sqm)}")

cloud_slider_options = list(range(100, -1, -1))
desired_cloud_cover = st.select_slider(
    "許容できる雲の上限（%）",
    options=cloud_slider_options,
    value=30,
    help="スライダーを右に動かすほど、許容する雲の上限が下がります（より晴天を求めることになります）。"
)
st.info(f"雲が{desired_cloud_cover}%以下の場所を探します。")

st.header("② おすすめの場所を探す")
col1, col2 = st.columns([1, 4])
with col1:
    location_data = streamlit_geolocation()
with col2:
    st.markdown("##### 📍 位置情報の許可を！")
    st.caption("左のマークを押して、このサイトの位置情報利用を許可してください。")

if location_data:
    current_lat, current_lon = location_data.get('latitude'), location_data.get('longitude')

    if st.button("この条件に合う、一番近い場所を探す！"):
        if current_lat is None or current_lon is None:
            st.error("有効な位置情報が取得できませんでした。")
        else:
            search_radius_km = 500
            
            nearby_spots = []
            for spot in SPOTS:
                distance = calculate_distance(current_lat, current_lon, spot["lat"], spot["lon"])
                if distance <= search_radius_km:
                    spot['distance'] = distance
                    nearby_spots.append(spot)
            
            if not nearby_spots:
                st.warning(f"半径{search_radius_km}km以内に、登録されている観測スポットがありませんでした。")
            else:
                st.info(f"あなたの現在地から半径{search_radius_km}km以内にある{len(nearby_spots)}件の候補地を調査します...")
                with st.spinner("候補地の天気情報を収集中..."):
                    viable_spots = []
                    tf = TimezoneFinder()
                    for spot in nearby_spots:
                        if spot.get("sqm_level", 0) < desired_sqm:
                            continue

                        astro_data = get_astro_data(spot["lat"], spot["lon"], API_KEY)
                        if astro_data:
                            cloudiness = astro_data["current"]["clouds"]
                            if cloudiness > desired_cloud_cover:
                                continue
                            
                            viable_spots.append({
                                "name": spot["name"], "lat": spot["lat"], "lon": spot["lon"],
                                "distance": spot["distance"], "base_sqm": spot["sqm_level"],
                                "cloudiness": cloudiness,
                                "astro_data": astro_data 
                            })
                        time.sleep(0.1)
                
                st.header("③ 検索結果")
                if not viable_spots:
                    st.warning("残念ながら、現在の条件に合うスポットは見つかりませんでした。条件を緩めて再検索してみてください。")
                else:
                    top_spots = sorted(viable_spots, key=lambda x: x["distance"])[:3]
                    st.success(f"発見！あなたの条件に合う場所が {len(viable_spots)}件 見つかりました。近い順に最大3件表示します。")
                    
                    selected_timezone = tf.timezone_at(lng=current_lon, lat=current_lat)
                    if not selected_timezone:
                        selected_timezone = 'Asia/Tokyo'
                    
                    for i, spot in enumerate(top_spots):
                        st.subheader(f"🏆 おすすめ No.{i+1}： {spot['name']}")
                        st.write(f" - **あなたからの距離:** 約`{spot['distance']:.1f}` km")
                        travel_time_str = estimate_travel_time(spot['distance'])
                        travel_type = "🚗 車での移動時間"
                        st.write(f" - **{travel_type}:** 約`{travel_time_str}`")
                        st.markdown("---")
                        
                        st.write(f"**空の暗さ（SQM値）:** `{spot['base_sqm']}` SQM")
                        st.caption(get_sqm_description(spot['base_sqm']))
                        st.write(f"**現在の雲量:** `{spot['cloudiness']}` %")

                        if spot.get("astro_data"):
                            spot_tz_str = tf.timezone_at(lng=spot["lon"], lat=spot["lat"])
                            spot_tz = pytz.timezone(spot_tz_str if spot_tz_str else 'Asia/Tokyo')
                            
                            today_moon_data = spot["astro_data"]["daily"][0]
                            moonrise_ts = today_moon_data.get("moonrise")
                            moonset_ts = today_moon_data.get("moonset")

                            def format_time(timestamp, timezone):
                                return datetime.fromtimestamp(timestamp, tz=timezone).strftime('%H:%M') if timestamp else "N/A"

                            moonrise_time = format_time(moonrise_ts, spot_tz)
                            moonset_time = format_time(moonset_ts, spot_tz)
                            
                            st.write(f"**今日の月の動き:** 🌕 **月の出:** `{moonrise_time}` / **月の入り:** `{moonset_time}`")
                            st.caption("この時刻を参考に、月明かりを避ける計画を立てましょう。")

                        if spot.get("astro_data") and spot["astro_data"].get("hourly"):
                            st.write("**これからの天気（1時間ごと）**")
                            cols = st.columns(5)
                            hourly_data = spot["astro_data"]["hourly"]
                            user_tz = pytz.timezone(selected_timezone)

                            for j in range(min(5, len(hourly_data) - 1)):
                                hour_data = hourly_data[j+1]
                                utc_dt = datetime.fromtimestamp(hour_data["dt"], tz=pytz.utc)
                                local_dt = utc_dt.astimezone(user_tz)
                                time_str = local_dt.strftime('%H時')
                                with cols[j]:
                                    st.markdown(f"<div style='text-align: center;'>{time_str}</div>", unsafe_allow_html=True)
                                    emoji = get_weather_emoji(hour_data["clouds"])
                                    st.markdown(f"<div style='text-align: center; font-size: 2.5em; line-height: 1;'>{emoji}</div>", unsafe_allow_html=True)
                                    st.markdown(f"<div style='text-align: center;'>{hour_data['clouds']}%</div>", unsafe_allow_html=True)

                        maps_url = f"https://www.google.com/maps/search/?api=1&query={spot['lat']},{spot['lon']}"
                        st.markdown(f"**[🗺️ Googleマップで場所を確認する]({maps_url})**")

                        tag_name = spot['name'].split('（')[0].split('-')[0].strip()
                        instagram_url = f"https://www.instagram.com/explore/tags/{urllib.parse.quote(tag_name)}/"
                        st.markdown(f"**[📸 Instagramで「#{tag_name}」の写真を見る]({instagram_url})**")

                        st.markdown("---")
                        st.caption("この場所をシェアする")
                        share_text = f"おすすめの星空スポット【{spot['name']}】を見つけました！\n現在の雲量は{spot['cloudiness']}%、空の暗さは{spot['base_sqm']}SQMです。\nあなたも最高の星空を探しに行こう！\n#ホシドコ #星空観測 #天体観測\n"
                        app_url = "https://your-streamlit-app-url.com" # TODO: ここにデプロイしたアプリのURLを記載
                        
                        encoded_text = urllib.parse.quote(share_text)
                        encoded_app_url = urllib.parse.quote(app_url)
                        
                        button_style = "display: inline-block; text-decoration: none; color: white; padding: 6px 10px; border-radius: 8px; text-align: center; font-size: 14px;"

                        share_col1, share_col2, share_col3, _ = st.columns([1,1,1,1])
                        with share_col1:
                            st.markdown(f'<a href="https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_app_url}" target="_blank" style="{button_style} background-color: #1DA1F2;">Xでシェア</a>', unsafe_allow_html=True)
                        with share_col2:
                            st.markdown(f'<a href="https://www.facebook.com/sharer/sharer.php?u={encoded_app_url}" target="_blank" style="{button_style} background-color: #1877F2;">Facebook</a>', unsafe_allow_html=True)
                        with share_col3:
                            st.markdown(f'<a href="https://line.me/R/msg/text/?{encoded_text}{encoded_app_url}" target="_blank" style="{button_style} background-color: #06C755;">LINE</a>', unsafe_allow_html=True)
                        
                        st.divider()
else:
    st.info("ページ上部のマークを押して、位置情報の使用を許可してください。")

# --- 出典表示 ---
st.divider()
st.caption("""
観測地点のスカイクオリティ(SQM)基準値は、環境省「全国星空継続観察」の過去のデータを参考にしています。
参照元: https://www.env.go.jp/press/press_03979.html
""")
