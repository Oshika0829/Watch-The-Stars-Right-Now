import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
import math
import time
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder

# --- データ定義 ---
# ★★★ 日本全国・世界のスポットを、実用的な上限まで大幅に拡充 ★★★
SPOTS = [
    # 日本 - 北海道・東北
    {"name": "摩周湖（北海道）", "lat": 43.5855, "lon": 144.5694, "sqm_level": 21.7},
    {"name": "浄土ヶ浜（岩手県）", "lat": 39.6425, "lon": 141.9723, "sqm_level": 20.8},
    {"name": "蔵王（宮城県）", "lat": 38.1423, "lon": 140.4497, "sqm_level": 21.0},
    {"name": "裏磐梯（福島県）", "lat": 37.6599, "lon": 140.0910, "sqm_level": 21.2},
    # 日本 - 関東
    {"name": "奥日光・戦場ヶ原（栃木県）", "lat": 36.7915, "lon": 139.4210, "sqm_level": 21.5},
    {"name": "筑波山（茨城県）", "lat": 36.2239, "lon": 140.1130, "sqm_level": 20.5},
    {"name": "陣馬高原（東京/神奈川）", "lat": 35.6517, "lon": 139.1698, "sqm_level": 19.5},
    {"name": "堂平山（埼玉県）", "lat": 36.0195, "lon": 139.1838, "sqm_level": 20.8},
    {"name": "犬吠埼（千葉県）", "lat": 35.7084, "lon": 140.8603, "sqm_level": 20.7},
    # 日本 - 中部
    {"name": "富士山五合目（山梨/静岡）", "lat": 35.3620, "lon": 138.7303, "sqm_level": 21.3},
    {"name": "野辺山高原（長野県）", "lat": 35.9525, "lon": 138.4766, "sqm_level": 21.4},
    {"name": "阿智村（長野県）", "lat": 35.4372, "lon": 137.7567, "sqm_level": 21.6},
    {"name": "上高地（長野県）", "lat": 36.2494, "lon": 137.6335, "sqm_level": 21.7},
    {"name": "白米千枚田（石川県）", "lat": 37.3896, "lon": 137.2915, "sqm_level": 21.1},
    # 日本 - 関西
    {"name": "大台ヶ原（奈良/三重）", "lat": 34.1923, "lon": 136.0883, "sqm_level": 21.2},
    {"name": "星のブランコ（大阪府）", "lat": 34.8016, "lon": 135.7335, "sqm_level": 18.9},
    # 日本 - 中国・四国
    {"name": "鳥取砂丘（鳥取県）", "lat": 35.5422, "lon": 134.2285, "sqm_level": 20.9},
    {"name": "四国カルスト（愛媛/高知）", "lat": 33.4975, "lon": 132.8953, "sqm_level": 21.3},
    # 日本 - 九州・沖縄
    {"name": "えびの高原（宮崎/鹿児島）", "lat": 31.9442, "lon": 130.8544, "sqm_level": 21.2},
    {"name": "石垣島（沖縄県・星空保護区）", "lat": 24.4105, "lon": 124.1922, "sqm_level": 21.7},
    {"name": "波照間島（沖縄県）", "lat": 24.0560, "lon": 123.7745, "sqm_level": 21.8},

    # --- 世界 ---
    # 北米
    {"name": "マウナケア山頂（アメリカ・ハワイ）", "lat": 19.8206, "lon": -155.4681, "sqm_level": 21.9},
    {"name": "デスバレー国立公園（アメリカ）", "lat": 36.5054, "lon": -117.0794, "sqm_level": 21.9},
    {"name": "チェリー・スプリングス州立公園（アメリカ）", "lat": 41.6601, "lon": -77.8251, "sqm_level": 21.8},
    {"name": "ジャスパー国立公園（カナダ）", "lat": 52.8734, "lon": -117.9543, "sqm_level": 21.8},
    # 南米
    {"name": "アタカマ砂漠（チリ）", "lat": -24.5759, "lon": -69.2152, "sqm_level": 22.0},
    {"name": "セロ・トロロ汎米天文台（チリ）", "lat": -30.1691, "lon": -70.8062, "sqm_level": 21.9},
    {"name": "ウユニ塩湖（ボリビア）", "lat": -20.2582, "lon": -67.4891, "sqm_level": 21.8},
    # オセアニア
    {"name": "アオラキ/マウント・クック（ニュージーランド）", "lat": -43.5950, "lon": 170.1419, "sqm_level": 21.8},
    {"name": "ワラバンバングル国立公園（オーストラリア）", "lat": -31.2720, "lon": 149.0060, "sqm_level": 21.7},
    # ヨーロッパ
    {"name": "テイデ国立公園（スペイン・カナリア諸島）", "lat": 28.2721, "lon": -16.6435, "sqm_level": 21.6},
    {"name": "ギャロウェイ森林公園（スコットランド）", "lat": 55.1380, "lon": -4.4079, "sqm_level": 21.5},
    {"name": "ホルトバージ国立公園（ハンガリー）", "lat": 47.5800, "lon": 21.0600, "sqm_level": 21.4},
    # アフリカ
    {"name": "ナミブランド自然保護区（ナミビア）", "lat": -25.2638, "lon": 16.0355, "sqm_level": 21.9},
    {"name": "南アフリカ大型望遠鏡（南アフリカ）", "lat": -32.3811, "lon": 20.8115, "sqm_level": 21.8},
    # アジア
    {"name": "サガルマータ国立公園（ネパール・エベレスト）", "lat": 27.9791, "lon": 86.7214, "sqm_level": 22.0},
    {"name": "ゴビ砂漠（モンゴル）", "lat": 44.8863, "lon": 103.5874, "sqm_level": 21.9},
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
            nearby_spots = []
            for spot in SPOTS:
                distance = calculate_distance(current_lat, current_lon, spot["lat"], spot["lon"])
                # 飛行機で行くような場所は、距離フィルターの対象外とする
                if distance <= 2500:
                    nearby_spots.append(spot)
                    spot['distance'] = distance
                # 海外のダークスカイサイトは常に候補に入れる
                elif spot['sqm_level'] >= 21.5:
                    nearby_spots.append(spot)
                    spot['distance'] = distance
            
            st.info(f"あなたの現在地から、{len(nearby_spots)}件の候補地を調査します...")
            
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
                    if spot['distance'] > 2500:
                        travel_time_str = estimate_flight_time(spot['distance']); travel_type = "✈️ 飛行機での移動時間"
                    else:
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