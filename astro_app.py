import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
import math
import time
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# --- データ定義 ---
SPOTS = [
    # 日本
    {"name": "摩周湖（北海道）", "lat": 43.5855, "lon": 144.5694, "sqm_level": 21.7},
    {"name": "奥日光・戦場ヶ原（栃木県）", "lat": 36.7915, "lon": 139.4210, "sqm_level": 21.5},
    {"name": "阿智村（長野県）", "lat": 35.4372, "lon": 137.7567, "sqm_level": 21.6},
    {"name": "野辺山高原（長野県）", "lat": 35.9525, "lon": 138.4766, "sqm_level": 21.4},
    {"name": "富士山五合目（山梨/静岡）", "lat": 35.3620, "lon": 138.7303, "sqm_level": 21.3},
    {"name": "大台ヶ原（奈良/三重）", "lat": 34.1923, "lon": 136.0883, "sqm_level": 21.2},
    {"name": "四国カルスト（愛媛/高知）", "lat": 33.4975, "lon": 132.8953, "sqm_level": 21.3},
    {"name": "石垣島（沖縄県・星空保護区）", "lat": 24.4105, "lon": 124.1922, "sqm_level": 21.7},
    {"name": "筑波山（茨城県）", "lat": 36.2239, "lon": 140.1130, "sqm_level": 20.5},
    # 世界
    {"name": "マウナケア山頂（アメリカ・ハワイ）", "lat": 19.8206, "lon": -155.4681, "sqm_level": 21.9},
    {"name": "デスバレー国立公園（アメリカ）", "lat": 36.5054, "lon": -117.0794, "sqm_level": 21.9},
    {"name": "アタカマ砂漠（チリ）", "lat": -24.5759, "lon": -69.2152, "sqm_level": 22.0},
    {"name": "ナミブランド自然保護区（ナミビア）", "lat": -25.2638, "lon": 16.0355, "sqm_level": 21.9},
    {"name": "アオラキ/マウント・クック（ニュージーランド）", "lat": -43.5950, "lon": 170.1419, "sqm_level": 21.8},
    {"name": "テイデ国立公園（スペイン・カナリア諸島）", "lat": 28.2721, "lon": -16.6435, "sqm_level": 21.6},
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
    avg_speed_kmh = 40; time_h = distance_km / avg_speed_kmh; total_minutes = int(time_h * 60)
    if total_minutes < 60: return f"{total_minutes}分"
    else: hours = total_minutes // 60; minutes = total_minutes % 60; return f"{hours}時間{minutes}分"

def estimate_flight_time(distance_km):
    avg_speed_kmh = 850; buffer_hours = 4; flight_hours = distance_km / avg_speed_kmh
    total_hours = flight_hours + buffer_hours; return f"{int(total_hours)}時間（フライト）"

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371; dLat = math.radians(lat2 - lat1); dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)); return R * c

def calculate_star_index(cloudiness):
    if cloudiness <= 10: return 100
    elif cloudiness <= 40: return 70
    elif cloudiness <= 70: return 40
    else: return 10

def estimate_sky_quality(base_sqm, cloudiness, moon_phase):
    moon_penalty = (1 - abs(moon_phase - 0.5) * 2) * 4
    cloud_penalty = (cloudiness / 100) * 2
    final_sqm = base_sqm - moon_penalty - cloud_penalty
    return max(16.0, final_sqm)

def get_sqm_description(sqm_value):
    if sqm_value >= 21: return "天の川の複雑な構造が確認でき、星団などの観測ができます。"
    elif sqm_value >= 20: return "山や海などの暗さ。天の川がよく見られます。"
    elif sqm_value >= 19: return "郊外の暗さ。天の川が見え始めます。"
    elif sqm_value >= 18: return "住宅地の明るさ。星座の形がよく分かります。"
    elif sqm_value >= 17: return "市街地の明るさ。星座の形が分かり始めます。"
    else: return "都心部の明るさ。星はほとんど見られません。"

def get_star_index_description(index_value):
    if index_value >= 95: return "雲量10%以下。ほぼ雲のない快晴の空です。"
    elif index_value >= 65: return "雲量40%以下。雲はありますが、十分な晴れ間が期待できます。"
    elif index_value >= 35: return "雲量70%以下。雲が多めで、晴れ間を探して観測するイメージです。"
    else: return "雲量71%以上。ほぼ曇り空で、星を見るのはかなり困難です。"
    
def get_moon_advice(moon_phase):
    if moon_phase == 0 or moon_phase == 1: name, advice = "新月", "月明かりがなく、星を見るには最高の条件です！"
    elif 0 < moon_phase < 0.25: name, advice = "三日月", "月は細く、星空への影響はほとんどありません。"
    elif moon_phase == 0.25: name, advice = "上弦の月", "夜半には月が沈むため、深夜以降の星空観測におすすめです。"
    elif 0.25 < moon_phase < 0.5: name, advice = "十三夜", "月が明るくなってきました。淡い星は見えにくいかもしれません。"
    elif moon_phase == 0.5: name, advice = "満月", "月が非常に明るく、天の川や淡い星を見るのは難しいでしょう。"
    elif 0.5 < moon_phase < 0.75: name, advice = "十六夜（いざよい）", "月が明るいため、星空観測には少し不向きな時期です。"
    elif moon_phase == 0.75: name, advice = "下弦の月", "夜明け前に昇ってくる月なので、夜半までは月明かりの影響がありません。"
    else: name, advice = "有明の月", "月が昇るのが遅く、夜の早い時間帯は星空観測のチャンスです。"
    return name, advice

def get_weather_emoji(cloudiness):
    if cloudiness < 20: return "☀️"
    elif cloudiness < 70: return "☁️"
    else: return "🌧️"

# --- アプリ本体 ---
st.set_page_config(page_title="Watch The Stars Right Now!!!", page_icon="🌠")
st.title("🌠 Watch The Stars Right Now!!! 🔭")
st.write("今すぐ星が見える場所へ")
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("【開発者向けエラー】secrets.tomlファイルまたはAPIキーの設定が見つかりません。")
    st.stop()

st.header("① あなたの希望の条件は？")
# ★★★ スライダー下の説明文を修正 ★★★
desired_sqm = st.slider("目標の空の暗さ（SQM値）", 17.0, 22.0, 19.0, 0.1, help="SQMは空の明るさを示す単位で、数値が高いほど暗く、星空観測に適しています。")
st.info(f"{get_sqm_description(desired_sqm)}")

stargazing_index_threshold = st.slider("最低限の空の晴れ具合（星空指数）", 0, 100, 70)
st.info(f"{get_star_index_description(stargazing_index_threshold)}")

st.header("② おすすめの場所を探す")
col1, col2 = st.columns([1, 4])
with col1:
    location_data = streamlit_geolocation()
with col2:
    st.markdown("##### 📍 位置情報の許可を！")
    st.caption("左のマークを押して、このサイトの位置情報利用を許可してください。")

if location_data:
    current_lat, current_lon = location_data.get('latitude'), location_data.get('longitude')
    if current_lat and current_lon:
        tf = TimezoneFinder()
        selected_timezone = tf.timezone_at(lng=current_lon, lat=current_lat)