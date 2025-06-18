import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
import math
import time
from datetime import datetime
import pytz

# --- データ定義 ---
# ★★★ 全スポットのデータを「SQM値」ベースに更新 ★★★
# sqm_level: 数値が高いほど暗い空
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
    {"name": "九十九里浜（千葉県）", "lat": 35.5828, "lon": 140.4578, "sqm_level": 20.2},
    {"name": "手賀沼公園（千葉県）", "lat": 35.8649, "lon": 140.0229, "sqm_level": 18.3},
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
        response = requests.get(url); response.raise_for_status(); return response.json()
    except requests.exceptions.RequestException: return None

def estimate_travel_time(distance_km):
    avg_speed_kmh = 40; time_h = distance_km / avg_speed_kmh; total_minutes = int(time_h * 60)
    if total_minutes < 60: return f"{total_minutes}分"
    else:
        hours = total_minutes // 60; minutes = total_minutes % 60
        return f"{hours}時間{minutes}分"

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

# ★★★ 等級計算の代わりに、推定SQMを計算する新しい関数 ★★★
def estimate_sky_quality(base_sqm, cloudiness, moon_phase):
    # 月の影響（満月で最大4等級分、空が明るくなるとして計算）
    moon_penalty = (1 - abs(moon_phase - 0.5) * 2) * 4
    # 雲の影響（雲100%で2等級分、空が明るくなるとして計算）
    cloud_penalty = (cloudiness / 100) * 2
    
    final_sqm = base_sqm - moon_penalty - cloud_penalty
    return max(16.0, final_sqm) # 最低値は16とする

# ★★★ あなたの資料を参考にした、SQMの解説を返す新しい関数 ★★★
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

try: API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("【開発者向けエラー】secrets.tomlファイルまたはAPIキーの設定が見つかりません。")
    st.stop()

st.header("① あなたの希望の条件は？")
# ★★★ 等級スライダーをSQMスライダーに変更 ★★★
desired_sqm = st.slider("目標の空の暗さ（SQM値）", 17.0, 22.0, 19.0, 0.1, help="SQMは空の明るさを示す単位で、数値が高いほど暗く、星空観測に適しています。")
st.info(f"目標の空： **{get_sqm_description(desired_sqm)}**")

stargazing_index_threshold = st.slider("最低限の空の晴れ具合（星空指数）", 0, 100, 70)
st.info(f"目標の晴れ具合： **{get_star_index_description(stargazing_index_threshold)}**")

st.header("② おすすめの場所を探す")
col1, col2 = st.columns([1, 4])
with col1: location_data = streamlit_geolocation()
with col2:
    st.markdown("##### 📍 位置情報の許可を！")
    st.caption("左のマークを押して、このサイトの位置情報利用を許可してください。")

if location_data:
    timezones = pytz.common_timezones
    default_tz_index = timezones.index('Asia/Tokyo') if 'Asia/Tokyo' in timezones else 0
    selected_timezone = st.selectbox(
        'あなたのタイムゾーンを選んでください', options=timezones, index=default_tz_index,
        help="検索結果の時刻表示を、あなたの地域の時間に合わせます。"
    )
    
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
                        # ★★★ ロジックを推定SQM計算に変更 ★★★
                        estimated_sqm = estimate_sky_quality(spot["sqm_level"], cloudiness, moon_phase)
                        if estimated_sqm < desired_sqm: continue
                        
                        star_index = calculate_star_index(cloudiness)
                        if star_index < stargazing_index_threshold: continue
                        
                        distance = calculate_distance(current_lat, current_lon, spot["lat"], spot["lon"])
                        viable_spots.append({
                            "name": spot["name"], "lat": spot["lat"], "lon": spot["lon"], "distance": distance, "star_index": star_index,
                            "estimated_sqm": estimated_sqm, "moon_phase": moon_phase, "hourly_data": astro_data.get("hourly", [])
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
                    if spot['distance'] > 2500:
                        travel_time_str = estimate_flight_time(spot['distance'])
                        travel_type = "飛行機での移動時間"
                    else:
                        travel_time_str = estimate_travel_time(spot['distance'])
                        travel_type = "車での移動時間"
                    st.write(f" - **{travel_type}:** 約`{travel_time_str}`")
                    st.markdown("---")
                    
                    # ★★★ 結果表示をSQMに変更 ★★★
                    st.write(f"**星空指数（晴れ具合）:** `{spot['star_index']}` / 100点")
                    st.caption(get_star_index_description(spot['star_index']))
                    
                    st.write(f"**推定スカイクオリティ:** 約`{spot['estimated_sqm']:.2f}` SQM")
                    st.caption(get_sqm_description(spot['estimated_sqm']))

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
                    st.markdown(f"**[🗺️ Googleマップで場所を確認する]({Maps_url})**")
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