import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
import math
import time
from datetime import datetime
import pytz

# --- データ定義 ---
SPOTS = [
    # 日本 - 北海道・東北
    {"name": "摩周湖（北海道）", "lat": 43.5855, "lon": 144.5694, "darkness_level": 9},
    {"name": "浄土ヶ浜（岩手県）", "lat": 39.6425, "lon": 141.9723, "darkness_level": 8},
    # 日本 - 関東
    {"name": "奥日光・戦場ヶ原（栃木県）", "lat": 36.7915, "lon": 139.4210, "darkness_level": 9},
    {"name": "筑波山（茨城県）", "lat": 36.2239, "lon": 140.1130, "darkness_level": 8},
    {"name": "陣馬高原（東京/神奈川）", "lat": 35.6517, "lon": 139.1698, "darkness_level": 5},
    {"name": "手賀沼公園（千葉県）", "lat": 35.8649, "lon": 140.0229, "darkness_level": 4},
    {"name": "犬吠埼（千葉県）", "lat": 35.7084, "lon": 140.8603, "darkness_level": 7},
    # 日本 - 中部
    {"name": "富士山五合目（山梨/静岡）", "lat": 35.3620, "lon": 138.7303, "darkness_level": 9},
    {"name": "野辺山高原（長野県）", "lat": 35.9525, "lon": 138.4766, "darkness_level": 9},
    {"name": "阿智村（長野県）", "lat": 35.4372, "lon": 137.7567, "darkness_level": 9},
    # 日本 - 関西
    {"name": "大台ヶ原（奈良/三重）", "lat": 34.1923, "lon": 136.0883, "darkness_level": 8},
    # 日本 - 中国・四国
    {"name": "鳥取砂丘（鳥取県）", "lat": 35.5422, "lon": 134.2285, "darkness_level": 7},
    {"name": "四国カルスト（愛媛/高知）", "lat": 33.4975, "lon": 132.8953, "darkness_level": 8},
    # 日本 - 九州・沖縄
    {"name": "えびの高原（宮崎/鹿児島）", "lat": 31.9442, "lon": 130.8544, "darkness_level": 8},
    {"name": "石西礁湖（沖縄県・星空保護区）", "lat": 24.3350, "lon": 123.9930, "darkness_level": 9},
    # 世界 - 北米
    {"name": "デスバレー国立公園（アメリカ）", "lat": 36.5054, "lon": -117.0794, "darkness_level": 10},
    {"name": "ジャスパー国立公園（カナダ）", "lat": 52.8734, "lon": -117.9543, "darkness_level": 9},
    # 世界 - 南米
    {"name": "アタカマ砂漠（チリ）", "lat": -24.5759, "lon": -69.2152, "darkness_level": 10},
    # 世界 - オセアニア
    {"name": "アオラキ/マウント・クック（ニュージーランド）", "lat": -43.5950, "lon": 170.1419, "darkness_level": 9},
    {"name": "ワラバンバングル国立公園（オーストラリア）", "lat": -31.2720, "lon": 149.0060, "darkness_level": 9},
    # 世界 - ヨーロッパ
    {"name": "テイデ国立公園（スペイン・カナリア諸島）", "lat": 28.2721, "lon": -16.6435, "darkness_level": 9},
    # 世界 - アフリカ
    {"name": "ナミブランド自然保護区（ナミビア）", "lat": -25.2638, "lon": 16.0355, "darkness_level": 10},
    # 世界 - アジア
    {"name": "サガルマータ国立公園（ネパール・エベレスト）", "lat": 27.9791, "lon": 86.7214, "darkness_level": 10},
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

# ★★★ 飛行機での移動時間を計算する新しい関数 ★★★
def estimate_flight_time(distance_km):
    avg_speed_kmh = 850 # 飛行機の平均速度
    buffer_hours = 4 # 空港での手続きなどの時間
    flight_hours = distance_km / avg_speed_kmh
    total_hours = flight_hours + buffer_hours
    return f"{int(total_hours)}時間（フライト）"

# (ここから下の大部分の関数は変更なし)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1); dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)); return R * c
def calculate_star_index(cloudiness):
    if cloudiness <= 10: return 100
    elif cloudiness <= 40: return 70
    elif cloudiness <= 70: return 40
    else: return 10
def estimate_limiting_magnitude(darkness_level, cloudiness, moon_phase):
    base_mag = 2 + (darkness_level / 2)
    cloud_penalty = (cloudiness / 100) * 4
    moon_penalty = (1 - abs(moon_phase - 0.5) * 2) * 2
    limiting_magnitude = base_mag - cloud_penalty - moon_penalty
    return max(1.0, limiting_magnitude)
def get_magnitude_description(magnitude):
    if magnitude < 2.0: return "都会の中心部レベル：1等星など、ごく明るい星がいくつか見える程度です。"
    elif magnitude < 3.0: return "都会の空レベル：オリオン座や北斗七星など、有名な星座の形が分かります。"
    elif magnitude < 4.0: return "郊外の空レベル：主要な星座はほとんど見え、天の川の存在がうっすら分かるかもしれません。"
    elif magnitude < 5.0: return "暗い田舎の空レベル：たくさんの星が見え、天の川もぼんやりと見え始めます。"
    elif magnitude < 6.0: return "絶好の観測地レベル：天の川がはっきりと見え、流れ星にも期待が持てます。"
    else: return "最高クラスの星空：天の川の濃淡まで分かり、無数の星に圧倒される、一生に一度レベルの空です。"
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
timezones = pytz.common_timezones
default_tz_index = timezones.index('Asia/Tokyo') if 'Asia/Tokyo' in timezones else 0
selected_timezone = st.selectbox(
    'あなたのタイムゾーンを選んでください', options=timezones, index=default_tz_index
)
desired_magnitude = st.slider("目標の星の等級（数字が大きいほど暗い星）", 1.0, 7.0, 4.0, 0.1)
st.info(f"目標の明るさ： **{get_magnitude_description(desired_magnitude)}**")
stargazing_index_threshold = st.slider("最低限の空の晴れ具合（星空指数）", 0, 100, 70)
st.info(f"目標の晴れ具合： **{get_star_index_description(stargazing_index_threshold)}**")

st.header("② おすすめの場所を探す")
col1, col2 = st.columns([1, 4])
with col1:
    location_data = streamlit_geolocation()
with col2:
    st.markdown("##### 📍 位置情報の許可を！")
    st.caption("左のマークを押して、このサイトの位置情報利用を許可してください。")
if location_data:
    if st.button("この条件に合う、一番近い場所を探す！"):
        current_lat, current_lon = location_data.get('latitude'), location_data.get('longitude')
        if current_lat is None or current_lon is None:
            st.error("有効な位置情報が取得できませんでした。")
        else:
            with st.spinner("各候補地の天気情報を収集中...（少し時間がかかります）"):
                viable_spots = []
                for spot in SPOTS:
                    astro_data = get_astro_data(spot["lat"], spot["lon"], API_KEY)
                    if astro_data:
                        cloudiness, moon_phase = astro_data["current"]["clouds"], astro_data["daily"][0]["moon_phase"]
                        limiting_mag = estimate_limiting_magnitude(spot["darkness_level"], cloudiness, moon_phase)
                        if limiting_mag < desired_magnitude: continue
                        star_index = calculate_star_index(cloudiness)
                        if star_index < stargazing_index_threshold: continue
                        distance = calculate_distance(current_lat, current_lon, spot["lat"], spot["lon"])
                        viable_spots.append({
                            "name": spot["name"], "lat": spot["lat"], "lon": spot["lon"], "distance": distance, "star_index": star_index,
                            "limiting_mag": limiting_mag, "moon_phase": moon_phase, "hourly_data": astro_data.get("hourly", [])
                        })
                    time.sleep(0.1)
            st.header("③ 検索結果")
            if not viable_spots:
                st.warning("残念ながら、現在の条件に合うスポットは見つかりませんでした。条件を緩めて再検索してみてください。")
            else:
                top_spots = sorted(viable_spots, key=lambda x: x["distance"])[:3]
                st.success(f"発見！あなたの条件に合う場所が {len(top_spots)}件 見つかりました。")
                for i, spot in enumerate(top_spots):
                    st.subheader(f"🏆 おすすめ No.{i+1}： {spot['name']}")
                    st.write(f" - **あなたからの距離:** 約`{spot['distance']:.1f}` km")
                    
                    # ★★★ ここで移動時間を自動で切り替える ★★★
                    if spot['distance'] > 2500:
                        travel_time_str = estimate_flight_time(spot['distance'])
                        travel_type = "飛行機での移動時間"
                    else:
                        travel_time_str = estimate_travel_time(spot['distance'])
                        travel_type = "車での移動時間"
                    st.write(f" - **{travel_type}:** 約`{travel_time_str}`")

                    st.markdown("---")
                    st.write(f"**星空指数:** `{spot['star_index']}` / 100点 ({get_star_index_description(spot['star_index'])})")
                    st.write(f"**見える星の明るさ:** 約`{spot['limiting_mag']:.1f}` 等級まで期待できます")
                    st.caption(get_magnitude_description(spot['limiting_mag']))
                    if spot["hourly_data"]:
                        st.write("**これからの天気（1時間ごと）**")
                        cols = st.columns(3)
                        for j in range(min(3, len(spot["hourly_data"]))):
                            hour_data = spot["hourly_data"][j+1]
                            utc_dt = datetime.fromtimestamp(hour_data["dt"], tz=pytz.utc)
                            user_tz = pytz.timezone(selected_timezone)
                            local_dt = utc_dt.astimezone(user_tz)
                            time_str = local_dt.strftime('%H時')
                            with cols[j]:
                                st.markdown(f"<div style='text-align: center;'>{time_str}</div>", unsafe_allow_html=True)
                                emoji = get_weather_emoji(hour_data["clouds"])
                                st.markdown(f"<div style='text-align: center; font-size: 2.5em; line-height: 1;'>{emoji}</div>", unsafe_allow_html=True)
                                st.markdown(f"<div style='text-align: center;'>{hour_data['clouds']}%</div>", unsafe_allow_html=True)
                    Maps_url = f"https://www.google.com/maps/search/?api=1&query={spot['lat']},{spot['lon']}"
                    st.markdown(f"[🗺️ Googleマップで場所を確認する]({Maps_url})")
                    st.divider()

st.divider()
st.header("今日の月の様子 🌕")
AMI_LAT, AMI_LON = 36.0317, 140.2107 
moon_data = get_astro_data(AMI_LAT, AMI_LON, API_KEY)
if moon_data:
    moon_phase = moon_data["daily"][0]["moon_phase"]
    moon_name, moon_advice = get_moon_advice(moon_phase)
    st.info(f"今夜は『**{moon_name}**』です。\n\n{moon_advice}")
else:
    st.warning("月齢情報を取得できませんでした。")