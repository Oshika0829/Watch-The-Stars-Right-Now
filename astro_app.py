import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
import math
import time
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# --- データ定義 ---
# ★★★ 環境省「全国星空継続観察」の全データを反映 ★★★
SPOTS = [
    # 出典：環境省「全国星空継続観察」結果 https://www.env.go.jp/press/press_00833.html
    # PDF記載の日本の観測地全リスト
    {"name": "弟子屈町（北海道）", "lat": 43.4867, "lon": 144.4538, "sqm_level": 21.73},
    {"name": "足寄町（北海道）", "lat": 43.2453, "lon": 143.5517, "sqm_level": 21.81},
    {"name": "西目屋村（青森県）", "lat": 40.5517, "lon": 140.2858, "sqm_level": 21.43},
    {"name": "田野畑村（岩手県）", "lat": 39.9272, "lon": 141.9056, "sqm_level": 21.49},
    {"name": "東成瀬村（秋田県）", "lat": 39.1557, "lon": 140.6626, "sqm_level": 21.36},
    {"name": "片品村（群馬県）", "lat": 36.7686, "lon": 139.3621, "sqm_level": 21.48},
    {"name": "神津島村（東京都）", "lat": 34.2155, "lon": 139.1360, "sqm_level": 21.69},
    {"name": "山北町（神奈川県）", "lat": 35.3789, "lon": 139.0287, "sqm_level": 21.01},
    {"name": "聖籠町（新潟県）", "lat": 37.9546, "lon": 139.2435, "sqm_level": 19.39},
    {"name": "朝日町（富山県）", "lat": 36.9535, "lon": 137.5900, "sqm_level": 21.13},
    {"name": "能登町（石川県）", "lat": 37.3328, "lon": 137.1517, "sqm_level": 21.21},
    {"name": "南牧村（長野県）", "lat": 35.9754, "lon": 138.5621, "sqm_level": 21.52},
    {"name": "川上村（長野県）", "lat": 35.9189, "lon": 138.6508, "sqm_level": 21.45},
    {"name": "上松町（長野県）", "lat": 35.7725, "lon": 137.6974, "sqm_level": 21.37},
    {"name": "白川村（岐阜県）", "lat": 36.2570, "lon": 136.9037, "sqm_level": 21.28},
    {"name": "東伊豆町（静岡県）", "lat": 34.7709, "lon": 139.0560, "sqm_level": 21.15},
    {"name": "上北山村（奈良県）", "lat": 34.1378, "lon": 136.0381, "sqm_level": 21.54},
    {"name": "香美町（兵庫県）", "lat": 35.6027, "lon": 134.6158, "sqm_level": 21.20},
    {"name": "若桜町（鳥取県）", "lat": 35.3400, "lon": 134.3986, "sqm_level": 21.26},
    {"name": "隠岐の島町（島根県）", "lat": 36.2078, "lon": 133.3325, "sqm_level": 21.40},
    {"name": "井原市（岡山県）", "lat": 34.5986, "lon": 133.4578, "sqm_level": 21.42},
    {"name": "神石高原町（広島県）", "lat": 34.6644, "lon": 133.2750, "sqm_level": 21.25},
    {"name": "上関町（山口県）", "lat": 33.8211, "lon": 132.0969, "sqm_level": 21.25},
    {"name": "三好市（徳島県）", "lat": 33.9482, "lon": 133.8569, "sqm_level": 21.06},
    {"name": "久万高原町（愛媛県）", "lat": 33.6823, "lon": 132.8953, "sqm_level": 21.32},
    {"name": "大川村（高知県）", "lat": 33.7915, "lon": 133.3981, "sqm_level": 21.28},
    {"name": "東峰村（福岡県）", "lat": 33.4475, "lon": 130.8716, "sqm_level": 21.05},
    {"name": "上峰町（佐賀県）", "lat": 33.3242, "lon": 130.4079, "sqm_level": 18.99},
    {"name": "対馬市（長崎県）", "lat": 34.2074, "lon": 129.2882, "sqm_level": 21.47},
    {"name": "産山村（熊本県）", "lat": 32.9922, "lon": 131.1818, "sqm_level": 21.24},
    {"name": "国東市（大分県）", "lat": 33.5601, "lon": 131.6963, "sqm_level": 21.07},
    {"name": "高千穂町（宮崎県）", "lat": 32.7093, "lon": 131.3090, "sqm_level": 21.39},
    {"name": "屋久島町（鹿児島県）", "lat": 30.3551, "lon": 130.5222, "sqm_level": 21.61},
    {"name": "国頭村（沖縄県）", "lat": 26.7441, "lon": 128.1741, "sqm_level": 21.63},
    {"name": "竹富町（沖縄県）", "lat": 24.3323, "lon": 123.8123, "sqm_level": 21.77},
]

# --- 関数エリア (以下、変更なし) ---
@st.cache_data(ttl=600)
def get_astro_data(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&exclude=minutely,alerts&appid={api_key}&lang=ja&units=metric"
    try: response = requests.get(url); response.raise_for_status(); return response.json()
    except requests.exceptions.RequestException: return None
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
try: API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("【開発者向けエラー】secrets.tomlファイルまたはAPIキーの設定が見つかりません。")
    st.stop()
st.header("① あなたの希望の条件は？")
desired_sqm = st.slider("目標の空の暗さ（SQM値）", 17.0, 22.0, 19.0, 0.1, help="SQMは空の明るさを示す単位で、数値が高いほど暗く、星空観測に適しています。")
st.info(f"{get_sqm_description(desired_sqm)}")
stargazing_index_threshold = st.slider("最低限の空の晴れ具合（星空指数）", 0, 100, 70)
st.info(f"{get_star_index_description(stargazing_index_threshold)}")

st.header("② おすすめの場所を探す")
col1, col2 = st.columns([1, 4])
with col1: location_data = streamlit_geolocation()
with col2:
    st.markdown("##### 📍 位置情報の許可を！")
    st.caption("左のマークを押して、このサイトの位置情報利用を許可してください。")
if location_data:
    current_lat, current_lon = location_data.get('latitude'), location_data.get('longitude')
    if current_lat and current_lon:
        tf = TimezoneFinder(); selected_timezone = tf.timezone_at(lng=current_lon, lat=current_lat)
        if not selected_timezone: selected_timezone = 'Asia/Tokyo'
        with st.expander("今日のあなたの場所の月の様子は？ 🌕"):
            moon_data = get_astro_data(current_lat, current_lon, API_KEY)
            if moon_data:
                moon_phase = moon_data["daily"][0]["moon_phase"]
                moon_name, moon_advice = get_moon_advice(moon_phase)
                st.info(f"今夜は『**{moon_name}**』です。\n\n{moon_advice}")
            else: st.warning("月齢情報を取得できませんでした。")
    if st.button("この条件に合う、一番近い場所を探す！"):
        if current_lat is None or current_lon is None: st.error("有効な位置情報が取得できませんでした。")
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
                    for spot in nearby_spots:
                        astro_data = get_astro_data(spot["lat"], spot["lon"], API_KEY)
                        if astro_data:
                            cloudiness, moon_phase = astro_data["current"]["clouds"], astro_data["daily"][0]["moon_phase"]
                            estimated_sqm = estimate_sky_quality(spot["sqm_level"], cloudiness, moon_phase)
                            if estimated_sqm < desired_sqm: continue
                            star_index = calculate_star_index(cloudiness)
                            if star_index < stargazing_index_threshold: continue
                            viable_spots.append({
                                "name": spot["name"], "lat": spot["lat"], "lon": spot["lon"],
                                "distance": spot["distance"], "star_index": star_index,
                                "estimated_sqm": estimated_sqm, "hourly_data": astro_data.get("hourly", [])
                            })
                        time.sleep(0.1)
                
                st.header("③ 検索結果")
                if not viable_spots:
                    st.warning("残念ながら、現在の条件に合うスポットは見つかりませんでした。条件を緩めて再検索してみてください。")
                else:
                    top_spots = sorted(viable_spots, key=lambda x: x["distance"])[:3]
                    st.success(f"発見！あなたの条件に合う場所が {len(viable_spots)}件 見つかりました。近い順に最大3件表示します。")
                    for i, spot in enumerate(top_spots):
                        st.subheader(f"🏆 おすすめ No.{i+1}： {spot['name']}")
                        st.write(f" - **あなたからの距離:** 約`{spot['distance']:.1f}` km")
                        travel_time_str = estimate_travel_time(spot['distance']); travel_type = "🚗 車での移動時間"
                        st.write(f" - **{travel_type}:** 約`{travel_time_str}`")
                        st.markdown("---")
                        st.write(f"**星空指数（晴れ具合）:** `{spot['star_index']}` / 100点")
                        st.caption(get_star_index_description(spot['star_index']))
                        st.write(f"**推定スカイクオリティ:** 約`{spot['estimated_sqm']:.2f}` SQM")
                        st.caption(get_sqm_description(spot['estimated_sqm']))
                        if spot.get("hourly_data"):
                            st.write("**これからの天気（1時間ごと）**")
                            cols = st.columns(3)
                            for j in range(min(3, len(spot["hourly_data"]))):
                                if j + 1 < len(spot["hourly_data"]):
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
else:
    st.info("ページ上部のマークを押して、位置情報の使用を許可してください。")

# --- 出典表示 ---
st.divider()
st.caption("日本の観測地点のスカイクオリティ(SQM)基準値は、環境省「全国星空継続観察」の結果を参考にしています。")