import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
import math
import time

# --- データ定義 ---
SPOTS = [
    {"name": "手賀沼公園", "lat": 35.8649, "lon": 140.0229, "darkness_level": 4},
    {"name": "筑波山（つつじヶ丘）", "lat": 36.2239, "lon": 140.1130, "darkness_level": 8},
    {"name": "九十九里浜（片貝中央海岸）", "lat": 35.5828, "lon": 140.4578, "darkness_level": 7},
    {"name": "犬吠埼", "lat": 35.7084, "lon": 140.8603, "darkness_level": 7},
    {"name": "鋸山（日本寺）", "lat": 35.1578, "lon": 139.8336, "darkness_level": 6},
]

# --- 関数エリア ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1); dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)); return R * c
def get_astro_data(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&exclude=minutely,hourly,alerts&appid={api_key}&lang=ja&units=metric"
    try:
        response = requests.get(url); response.raise_for_status(); return response.json()
    except requests.exceptions.RequestException: return None
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

# --- アプリ本体 ---
st.title("Watch The Stars Right Now!!!")
st.write("今すぐ星が見える場所へ")

try: API_KEY = st.secrets["OPENWEATHER_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("【開発者向けエラー】secrets.tomlファイルまたはAPIキーの設定が見つかりません。")
    st.stop()

st.header("① あなたの希望の条件は？")
desired_magnitude = st.slider("目標の星の等級（数字が大きいほど暗い星）", 1.0, 6.5, 4.0, 0.1)
st.info(f"目標の明るさ： **{get_magnitude_description(desired_magnitude)}**")

stargazing_index_threshold = st.slider("最低限の空の晴れ具合（星空指数）", 0, 100, 70)
st.info(f"目標の晴れ具合： **{get_star_index_description(stargazing_index_threshold)}**")

st.header("② おすすめの場所を探す")
# ★★★ ここを修正 ★★★
col1, col2 = st.columns([1, 5])
with col1:
    location_data = streamlit_geolocation()
with col2:
    st.write("← 位置情報を許可してください☆")


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
                    time.sleep(0.2)
                    if astro_data:
                        cloudiness, moon_phase = astro_data["current"]["clouds"], astro_data["daily"][0]["moon_phase"]
                        limiting_mag = estimate_limiting_magnitude(spot["darkness_level"], cloudiness, moon_phase)
                        if limiting_mag < desired_magnitude: continue
                        star_index = calculate_star_index(cloudiness)
                        if star_index < stargazing_index_threshold: continue
                        distance = calculate_distance(current_lat, current_lon, spot["lat"], spot["lon"])
                        viable_spots.append({
                            "name": spot["name"], "distance": distance, "star_index": star_index,
                            "limiting_mag": limiting_mag, "moon_phase": moon_phase
                        })
            st.header("③ 検索結果")
            if not viable_spots:
                st.warning("残念ながら、現在の条件に合うスポットは見つかりませんでした。条件を緩めて再検索してみてください。")
            else:
                best_spot = sorted(viable_spots, key=lambda x: x["distance"])[0]
                st.success(f"発見！あなたの条件に合う一番近い場所はこちらです！")
                st.subheader(f"🏆 {best_spot['name']}")
                st.write(f" - **あなたからの距離:** 約`{best_spot['distance']:.1f}` km")
                st.markdown("---")
                st.write(f"**星空指数:** `{best_spot['star_index']}` / 100点")
                st.caption(get_star_index_description(best_spot['star_index']))
                st.write(f"**見える星の明るさ:** 約`{best_spot['limiting_mag']:.1f}` 等級まで期待できます")
                st.caption(get_magnitude_description(best_spot['limiting_mag']))
                moon_name, moon_advice = get_moon_advice(best_spot['moon_phase'])
                st.markdown("---")
                st.subheader(f"🌕 月の様子")
                st.info(f"今夜は『**{moon_name}**』です。\n\n{moon_advice}")
                Maps_url = f"https://www.google.com/maps/search/?api=1&query={best_spot['name'].replace(' ', '+')}"
                st.markdown(f"### [🗺️ Googleマップで場所を確認する]({Maps_url})")
else:
    st.info("ページ上部のボタンを押して、位置情報の使用を許可してください。")

