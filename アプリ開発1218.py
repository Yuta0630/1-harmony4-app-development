import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# GPT APIキーとSpotify APIのクライアントIDとクライアントシークレット
GPT_API_KEY = "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"
CLIENT_ID = "89cef7dc100d4199b9f320ee47655774"
CLIENT_SECRET = "c63119ab71664937914ada066e223b4a"


# GPT APIでコメントを生成する関数を作成
def get_gpt_response(keyword, prompt_type="応援コメント"):
    headers = {"Authorization": f"Bearer {GPT_API_KEY}"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": f"キーワード: {keyword}\n{prompt_type}を生成してください。"}
        ],
        "max_tokens": 500
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        st.write(f"GPT APIエラー: {response.status_code}, {response.text}")
        return None
    
# GPT APIでおすすめ音楽を生成する関数を作成
def get_gpt_recommend(keyword, prompt_type="おすすめの音楽"):
    headers = {"Authorization": f"Bearer {GPT_API_KEY}"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": f"キーワード: {keyword}\n{prompt_type}を3つ以内で生成してください。"}
        ],
        "max_tokens": 100
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]
    else:
        st.write(f"GPT APIエラー: {response.status_code}, {response.text}")
        return None


# Spotify APIでアクセストークンを取得する関数を作成
def get_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        st.write(f"Spotify APIエラー: {response.status_code}, {response.text}")
        return None

# Spotify APIで曲を検索する関数を作成
def search_track(track_name, access_token):
    url = f"https://api.spotify.com/v1/search?q={track_name}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json()
        if results.get("tracks") and results["tracks"]["items"]:
            return results["tracks"]["items"][0]
        else:
            return None
    else:
        st.write(f"Spotify検索エラー: {response.status_code}, {response.text}")
        return None

# Streamlitでアプリの構築

import streamlit as st


st.markdown('<h1 style="color:orangered;font-size:80px;">～今の1曲目～</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="color:orangered;font-size:28px;">あなたの今の気分にぴったりの音楽を提案します！</h3>', unsafe_allow_html=True)
st.image("https://i.imgur.com/awOzYRc.png", caption="音楽で今の気分を盛り上げましょう！", width=450)


# 全体の色の定義

backgroundColor = "#ffe4b5"  # 全体の背景色
sidebarBackgroundColor = "#ffe4b5"  # サイドバーの背景色
textColor = "#000000"  # テキストカラー

# カスタムCSSを使用して背景色やスタイルを設定
st.markdown(
    f"""
    <style>
    /* 全体の背景色 */
    .stApp {{
        background-color: {backgroundColor};
    }}

    /* サイドバーの背景色 */
    .css-1d391kg {{
        background-color: {sidebarBackgroundColor};
    }}

    /* テキストの色 */
    .stMarkdown, .css-1d391kg {{
        color: {textColor};
    }}
        /* ページ全体のフォント */
    html, body, .stApp {{
        font-family: 'Times New Roman', serif;  /* フォントを指定 */
    }}

    /* サイドバーのフォント */
    .css-1d391kg {{
        font-family: 'Times New Roman', serif;  /* サイドバー用フォント */
    }}


    </style>
    """,
    unsafe_allow_html=True
)


# 天気→先にCitycodelistを設定しとく
city_code_list = {"東京都": "130010", "大阪": "270000"}

# サイドバーで設定入力する箇所作成
# サイドバーに画像と文字を挿入
st.sidebar.markdown("""
    <div style="text-align: center; padding: 50px; margin-top: -50px;">
        <img src="https://i.imgur.com/o2oztzK.png" alt="Logo" style="width: 100px; margin-bottom: 10px;">
        <h2 style="margin: 0; color: black; font-size: 18px;">【運営会社】株式会社Harmony4</h2>
    </div>
""", unsafe_allow_html=True)


st.sidebar.header("あなたの情報をおしえてください")
age = st.sidebar.slider("あなたの年齢は？", 10, 100, 25)
gender = st.sidebar.selectbox("あなたの性別は？", ["男", "女", "未回答"])
music_genre = st.sidebar.multiselect(
    "好きな音楽ジャンルは？", ["洋楽", "KPOP", "JPOP", "クラシック", "ロック", "アニメソング", "ヒップホップ", "ジャズ"]
)
selected_city = st.sidebar.selectbox("どこに住んでいますか？", city_code_list.keys())

city_code = city_code_list[selected_city]

# 気分入力する箇所を作成
st.markdown('<h2 style="color:orangered; font-size:30px; font-weight:bold;">■■ いまの気分を教えて下さい ■■</h2>', unsafe_allow_html=True)

mood = st.selectbox("いまの気分は？", ["リラックス","疲れ気味", "ハッピー", "アクティブ", "ねむたい", "ゆううつ", "ふあん", "かなしい", "いらいら"])
mood_mapping = {"疲れ気味": "リラックス","アクティブ": "アップテンポ","リラックス": "穏やか","ねむたい": "静かな","ゆううつ": "癒しの","ふあん": "安心できる","かなしい": "慰めの","いらいら": "気分転換","ハッピー": "気分転換"}
activity = st.selectbox("いまどこいる？", ["家", "カフェ", "会社", "ジム", "おでかけ中"])
activity_mapping = {"家": "今家にいる", "カフェ": "今カフェに居る", "会社": "今会社にいる", "ジム": "今ジムにいる", "おでかけ中": "今お出かけ中"}
time_of_day = st.selectbox("いまの時間帯は？", ["朝", "昼", "夜"])
time_of_day_mapping = {"朝": "最近の曲", "昼": "少し昔の曲", "夜": "昔の曲"}

# 以下、天気の箇所の出力処理

url = "https://weather.tsukumijima.net/api/forecast/city/" + city_code # APIにリクエストするURLを作成

response = requests.get(url) # 作成したリクエスト用URLでアクセスして、responseに代入

weather_json = response.json() # responseにjson形式の天気のデータが返ってくるので、response.json()をweather_jsonに代入
now_hour = datetime.now().hour # 現在の天気情報取得のために、現在時刻の時間をnow_hourに代入

# 今日の天気はweather_json['forecasts'][0]['chanceOfRain']
# 明日の天気はweather_json['forecasts'][1]['chanceOfRain']
# 明後日の天気はweather_json['forecasts'][2]['chanceOfRain']
# にそれぞれ格納されている

# 天気の情報を0-6時、6-12時、12-18時、18-24時の4つに分けて降水確率を今日、明日、明後日の３日間の天気を返すため、場合分けする。
if 0 <= now_hour and now_hour < 6:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T00_06'] # 今日の0-6時の降水確率を取得し、weather_nowに代入
elif 6 <= now_hour and now_hour < 12:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T06_12'] # 今日の6-12時の降水確率を取得し、weather_nowに代入
elif 12 <= now_hour and now_hour < 18:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T12_18'] # 今日の12-18時の降水確率を取得し、weather_nowに代入
else:
    weather_now = weather_json['forecasts'][0]['chanceOfRain']['T18_24'] # 今日の18-24時の降水確率を取得し、weather_nowに代入

def get_weather_info(city_code):
    url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.write("天気情報の取得に失敗しました。")
        return None

weather_data = get_weather_info(city_code)

if weather_data:
    st.sidebar.markdown(f'<h3 style="color:orangered;font-size:20px; font-weight:bold;">■■　 {selected_city}　の天気 ■■</h3>', unsafe_allow_html=True)
    st.sidebar.write(f"◯ 今日の天気: {weather_data['forecasts'][0]['telop']}")
    st.sidebar.write(f"◯ 明日の天気: {weather_data['forecasts'][1]['telop']}")

weather_now_text = "◯ 現在の降水確率 : " + weather_now
st.sidebar.write(weather_now_text) # 現在時刻の降水確率を表示

# 今日、明日、明後日の降水確率をDadaFrameに代入
df1 = pd.DataFrame(weather_json['forecasts'][0]['chanceOfRain'],index=["今日"]) # index名を今日という文字列に設定
df2 = pd.DataFrame(weather_json['forecasts'][1]['chanceOfRain'],index=["明日"]) # index名を明日という文字列に設定
df3 = pd.DataFrame(weather_json['forecasts'][2]['chanceOfRain'],index=["明後日"]) # index名を明後日という文字列に設定

df = pd.concat([df1,df2,df3]) # 今日、明日、明後日の降水確率を結合して一覧にしてdfに代入
st.sidebar.dataframe(df) # 一覧にした降水確率を表示

today_weather = weather_data['forecasts'][0]['telop']  # 今日の天気
weather_keyword = f"{today_weather}に合った"  # 天気情報をキーワードに追加

# 年齢とKeywordを紐づけ

if age < 20:
    age_group = "若者向け"
elif 20 <= age < 40:
    age_group = "大人向け"
else:
    age_group = "シニア向け"

# 性別を反映したキーワード
gender_keyword = "男性向け" if gender == "男" else "女性向け" if gender == "女" else "ジェンダーフリー"

# キーワードにいれる情報のまとめ

keyword = f"{time_of_day_mapping[time_of_day]} {mood_mapping[mood]} {activity_mapping[activity]} {age_group} {gender_keyword} {', '.join(music_genre)}"

# 音楽提案ボタンの処理を作成

# スクロールターゲットを設定
st.markdown('<div id="scroll-target"></div>', unsafe_allow_html=True)

if st.button("■クリックして音楽を提案■"):
    
    
    # GPT APIで応援コメントを取得
    comment = get_gpt_response(keyword, prompt_type="応援コメント")
    st.markdown('<h3 style="color:orangered; font-size:30px; font-weight:bold;">■■■　あなたへの応援コメント　■■■</h3>', unsafe_allow_html=True)
    st.write(comment)

    # Spotifyで曲情報を取得
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    recommend = get_gpt_recommend(keyword, prompt_type="おすすめ音楽タイトル")

    if access_token:
        track_info = search_track(recommend, access_token)
        if track_info:
            # 今の一曲目
            st.markdown('<h3 style="color:orangered; font-size:30px; font-weight:bold;">■■■　今の一曲目はこちら！　■■■</h3>', unsafe_allow_html=True)

            # レイアウトを列で分ける
            col1, col2 = st.columns([1, 3])  # col1: 画像, col2: テキスト

            with col1:
                album_images = track_info['album']['images']  # アルバム画像リストを取得
                if album_images:
                    # 最大サイズの画像を小さく表示
                    st.image(
                        album_images[0]['url'],
                        caption=track_info['album']['name'],
                        width=150  # 画像の幅を指定（px単位）
                    )

            with col2:
                # テキスト情報を表示
                st.write(f"**◯曲名:** {track_info['name']}")
                st.write(f"**◯アーティスト:** {', '.join(artist['name'] for artist in track_info['artists'])}")
                st.write(f"**◯アルバム:** {track_info['album']['name']}")
                st.write(f"**◯リリース日:** {track_info['album']['release_date']}")
                st.write(f"[Spotifyで聴く]({track_info['external_urls']['spotify']})")

        else:
            st.write("曲情報が見つかりませんでした。")

    # GPT APIでおすすめ音楽を取得
    recommend = get_gpt_recommend(keyword, prompt_type="おすすめ音楽タイトル")
    st.markdown('<h3 style="color:orangered; font-size:30px; font-weight:bold;">■■■　その他のおすすめ曲はこちら　■■■</h3>', unsafe_allow_html=True)
    st.write(recommend)

    # JavaScriptでスムーズスクロールを実行
    st.markdown(
        """
        <script>
            setTimeout(function() {
                document.getElementById("scroll-target").scrollIntoView({ behavior: "smooth" });
            }, 100);
        </script>
        """,
        unsafe_allow_html=True,
    )

