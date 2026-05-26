import math
from datetime import datetime

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="야행성 Nocturnal", page_icon="🌙", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');
* {font-family: 'Noto Sans KR', sans-serif;}
.stApp {background: radial-gradient(circle at 10% 10%, #2b1b64 0, transparent 28%), linear-gradient(135deg, #090b1a 0%, #13172f 52%, #201333 100%); color:#f7f3ff;}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px;}
[data-testid="stSidebar"] {background: rgba(12,14,34,.88); border-right: 1px solid rgba(255,255,255,.08);}
.hero {border:1px solid rgba(255,255,255,.14); background: linear-gradient(135deg, rgba(129,92,255,.22), rgba(255,84,155,.13)); border-radius:28px; padding:28px; box-shadow:0 24px 60px rgba(0,0,0,.35);}
.hero h1 {font-size:3.1rem; margin:0; line-height:1.05; letter-spacing:-.04em;}
.hero p {color:#d8d2ff; font-size:1.05rem; margin-top:12px; max-width:820px;}
.metric-card {padding:18px; border-radius:22px; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.12);}
.metric-card b {font-size:1.7rem; color:#fff;}
.metric-card span {color:#bdb6df; font-size:.9rem;}
.place-card {background:rgba(255,255,255,.075); border:1px solid rgba(255,255,255,.12); border-radius:24px; padding:20px; margin:12px 0; box-shadow:0 16px 40px rgba(0,0,0,.22);}
.place-title {font-size:1.35rem; font-weight:800; margin-bottom:6px;}
.badge {display:inline-block; padding:5px 10px; margin:3px 4px 3px 0; border-radius:999px; background:rgba(129,92,255,.22); border:1px solid rgba(180,160,255,.28); color:#efeaff; font-size:.82rem;}
.status-open {background:rgba(46,213,115,.18); color:#adffd0; border-color:rgba(46,213,115,.35);}
.status-soon {background:rgba(255,177,66,.18); color:#ffe0a3; border-color:rgba(255,177,66,.35);}
.status-closed {background:rgba(255,82,82,.15); color:#ffb6b6; border-color:rgba(255,82,82,.35);}
.small-muted {color:#bdb6df; font-size:.9rem;}
.section-title {font-size:1.55rem; font-weight:800; margin:24px 0 10px;}
div[data-testid="stMetric"] {background:rgba(255,255,255,.075); padding:14px; border-radius:18px; border:1px solid rgba(255,255,255,.10);}
</style>
""", unsafe_allow_html=True)

PLACES = [
    dict(name="문라이트 루프탑", category="카페/바", lat=37.5559, lon=126.9237, area="홍대", open=18, close=2, is24=False, rating=4.7, reviews=328, price="3-5만원", crowd="보통", noise="활기참", tags=["루프탑 뷰", "DJ 세트", "칵테일", "데이트"], activities=["라이브 DJ", "시그니처 칵테일", "야경 포토존"], group=["2인", "3-5인"], mood=["활발한", "실외", "여가"], weather=["맑음", "더운 날씨"], scores=[4.8,4.5,4.1,4.3,4.6], trend=[4.4,4.5,4.6,4.7,4.7,4.8]),
    dict(name="네온 보드게임 카페", category="카페", lat=37.5572, lon=126.9254, area="홍대", open=13, close=5, is24=False, rating=4.5, reviews=211, price="1-3만원", crowd="여유", noise="보통", tags=["보드게임", "단체", "프라이빗 룸"], activities=["보드게임 대여", "팀전 이벤트", "음료 무제한"], group=["3-5인", "6인 이상"], mood=["조용한", "실내", "여가"], weather=["흐림", "비/눈", "추운 날씨"], scores=[4.2,4.6,4.7,4.4,4.3], trend=[4.1,4.2,4.3,4.4,4.5,4.5]),
    dict(name="심야 스터디 라운지", category="스터디 카페", lat=37.4983, lon=127.0276, area="강남", open=0, close=24, is24=True, rating=4.6, reviews=189, price="1만원 이하", crowd="여유", noise="조용함", tags=["24시간", "콘센트", "수면실"], activities=["집중석", "회의룸", "프린트"], group=["혼자", "2인"], mood=["조용한", "실내", "문화"], weather=["흐림", "비/눈", "추운 날씨", "더운 날씨"], scores=[4.7,4.4,4.8,4.6,4.4], trend=[4.3,4.4,4.5,4.5,4.6,4.6]),
    dict(name="VR 아케이드 밤샘존", category="오락시설", lat=37.5008, lon=127.0261, area="강남", open=16, close=3, is24=False, rating=4.3, reviews=154, price="1-3만원", crowd="혼잡", noise="시끄러움", tags=["VR존", "PC방", "게임 대회"], activities=["VR 슈팅", "e스포츠석", "콘솔 게임"], group=["2인", "3-5인", "6인 이상"], mood=["활발한", "실내", "여가"], weather=["흐림", "비/눈", "더운 날씨"], scores=[4.4,4.1,4.2,4.0,4.5], trend=[4.0,4.1,4.2,4.2,4.3,4.3]),
    dict(name="한강 나이트 피크닉", category="야외공간", lat=37.5285, lon=126.9328, area="여의도", open=18, close=1, is24=False, rating=4.8, reviews=402, price="1만원 이하", crowd="보통", noise="보통", tags=["한강", "야경", "배달 가능"], activities=["돗자리 대여", "야경 산책", "푸드트럭"], group=["혼자", "2인", "3-5인"], mood=["조용한", "실외", "문화"], weather=["맑음", "더운 날씨"], scores=[4.9,4.2,4.8,4.3,4.7], trend=[4.5,4.6,4.7,4.7,4.8,4.8]),
    dict(name="블루 사우나 스파", category="찜질방/스파", lat=37.5610, lon=127.0370, area="왕십리", open=0, close=24, is24=True, rating=4.2, reviews=97, price="1-3만원", crowd="여유", noise="조용함", tags=["24시간", "사우나", "수면실"], activities=["찜질방", "안마의자", "심야식당"], group=["혼자", "2인", "3-5인"], mood=["조용한", "실내", "여가"], weather=["비/눈", "추운 날씨"], scores=[4.0,4.2,4.5,4.1,4.0], trend=[4.0,4.0,4.1,4.2,4.2,4.2]),
]

WEATHER_RULES = {
    "맑음": "루프탑, 야외 카페, 한강 공원처럼 야경과 개방감이 좋은 장소를 우선 추천합니다.",
    "흐림": "실내 복합문화공간, 방탈출, 보드게임처럼 날씨 영향이 적은 장소를 우선 추천합니다.",
    "비/눈": "영화관, 노래방, 찜질방, 실내 술집처럼 이동 부담이 낮은 실내 장소를 우선 추천합니다.",
    "추운 날씨": "따뜻한 실내 카페, 스파, 사우나처럼 체온 유지가 쉬운 장소를 우선 추천합니다.",
    "더운 날씨": "에어컨이 있는 실내 공간과 강변 야간 활동을 우선 추천합니다.",
}

def is_open(place, hour):
    if place["is24"]: return "영업 중", "status-open"
    o, c = place["open"], place["close"]
    open_now = (o <= hour < c) if c > o else (hour >= o or hour < c)
    if not open_now: return "영업 종료", "status-closed"
    close_hour = c if c > o else c + 24
    h = hour if hour >= o else hour + 24
    if close_hour - h <= 1: return "마감 임박", "status-soon"
    return "영업 중", "status-open"

def score_place(p, group, budget, activity, indoor, weather, radius):
    score = p["rating"] * 12
    if group in p["group"]: score += 15
    if budget == p["price"]: score += 12
    if activity in p["mood"]: score += 10
    if indoor in p["mood"]: score += 10
    if weather in p["weather"]: score += 18
    if radius in ["2km", "5km"] or p["area"] in ["홍대", "강남"]: score += 4
    if p["crowd"] == "여유": score += 3
    return round(score, 1)

def badge(text, klass=""):
    return f'<span class="badge {klass}">{text}</span>'

st.markdown("""
<div class="hero">
  <h1>🌙 야행성 Nocturnal</h1>
  <p>청년 야간 활동 장소 추천 플랫폼. 지도 기반 PGIS, 실시간 영업 상태, 날씨 연동 추천, 놀거리 정보, 검증된 평판 시스템을 하나의 Streamlit 앱으로 구현했습니다.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("조건 설정")
    now_hour = st.slider("현재 시간", 0, 23, datetime.now().hour)
    weather = st.selectbox("날씨", list(WEATHER_RULES.keys()))
    group = st.selectbox("인원 구성", ["혼자", "2인", "3-5인", "6인 이상"])
    age = st.selectbox("나이대", ["20대 초반", "20대 후반", "30대"])
    gender = st.selectbox("성별 구성", ["남성", "여성", "혼성"])
    activity = st.radio("선호 분위기", ["조용한", "활발한"], horizontal=True)
    indoor = st.radio("공간 선호", ["실내", "실외"], horizontal=True)
    budget = st.select_slider("예산", options=["1만원 이하", "1-3만원", "3-5만원", "5만원 이상"], value="1-3만원")
    radius = st.selectbox("반경", ["500m", "1km", "2km", "5km"], index=2)
    category_filter = st.multiselect("카테고리", sorted({p["category"] for p in PLACES}), default=sorted({p["category"] for p in PLACES}))

places = []
for p in PLACES:
    if p["category"] in category_filter:
        q = p.copy()
        q["recommend_score"] = score_place(q, group, budget, activity, indoor, weather, radius)
        q["status"], q["status_class"] = is_open(q, now_hour)
        places.append(q)
places = sorted(places, key=lambda x: (x["status"] != "영업 중", -x["recommend_score"]))
df = pd.DataFrame(places)

m1,m2,m3,m4 = st.columns(4)
m1.metric("추천 가능 장소", f"{len(df)}곳")
m2.metric("영업 중", f"{(df['status']=='영업 중').sum()}곳" if len(df) else "0곳")
m3.metric("평균 평점", f"{df['rating'].mean():.1f}" if len(df) else "-")
m4.metric("현재 날씨", weather)
st.info(WEATHER_RULES[weather])

tab_map, tab_reco, tab_detail, tab_review = st.tabs(["🗺️ 지도", "✨ 추천 리스트", "📊 장소 상세", "📝 리뷰/평판"])

with tab_map:
    col_map, col_rank = st.columns([1.35, .65])
    with col_map:
        fmap = folium.Map(location=[37.535, 126.99], zoom_start=12, tiles="CartoDB dark_matter")
        for p in places:
            color = "green" if p["status"] == "영업 중" else "orange" if p["status"] == "마감 임박" else "red"
            folium.CircleMarker([p["lat"], p["lon"]], radius=10, color=color, fill=True, fill_opacity=.8,
                popup=f"<b>{p['name']}</b><br>{p['category']} · {p['rating']}점<br>{p['status']}<br>추천점수 {p['recommend_score']}").add_to(fmap)
        st_folium(fmap, width=None, height=560)
    with col_rank:
        st.markdown('<div class="section-title">실시간 추천 Top</div>', unsafe_allow_html=True)
        for i,p in enumerate(places[:5], 1):
            st.markdown(f"""
            <div class="place-card">
              <div class="place-title">{i}. {p['name']}</div>
              {badge(p['status'], p['status_class'])}{badge(p['category'])}{badge(p['price'])}
              <div class="small-muted">⭐ {p['rating']} · 리뷰 {p['reviews']} · 추천점수 {p['recommend_score']}</div>
            </div>
            """, unsafe_allow_html=True)

with tab_reco:
    for p in places:
        st.markdown(f"""
        <div class="place-card">
          <div class="place-title">{p['name']} <span class="small-muted">· {p['area']}</span></div>
          {badge(p['status'], p['status_class'])}{badge(p['category'])}{badge(p['crowd'])}{badge(p['noise'])}{badge(p['price'])}
          <p class="small-muted">추천점수 <b>{p['recommend_score']}</b> · ⭐ {p['rating']} ({p['reviews']}개 리뷰)</p>
          <p>{' '.join([badge(t) for t in p['tags']])}</p>
          <p><b>놀거리</b> · {', '.join(p['activities'])}</p>
        </div>
        """, unsafe_allow_html=True)

with tab_detail:
    selected = st.selectbox("상세 확인 장소", [p["name"] for p in places]) if places else None
    p = next((x for x in places if x["name"] == selected), None)
    if p:
        c1,c2 = st.columns([.9,1.1])
        with c1:
            st.markdown(f"### {p['name']}")
            st.write(f"{p['category']} · {p['area']} · {p['open']:02d}:00 ~ {'24:00' if p['close']==24 else str(p['close']).zfill(2)+':00'}")
            st.markdown(' '.join([badge(t) for t in p['tags']]), unsafe_allow_html=True)
            st.write("**시설/활동**", ", ".join(p["activities"]))
            st.write("**추천 대상**", f"{group} · {age} · {gender} · {activity}/{indoor}")
            st.progress(min(p["recommend_score"] / 90, 1.0), text=f"추천 적합도 {p['recommend_score']}점")
        with c2:
            radar = go.Figure()
            radar.add_trace(go.Scatterpolar(r=p["scores"], theta=["분위기","서비스","가성비","청결도","접근성"], fill="toself", name=p["name"]))
            radar.update_layout(height=330, margin=dict(l=30,r=30,t=30,b=30), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", polar=dict(radialaxis=dict(range=[0,5], color="white")))
            st.plotly_chart(radar, use_container_width=True)
        trend_df = pd.DataFrame({"월":["1월","2월","3월","4월","5월","6월"], "평점":p["trend"]})
        fig = px.line(trend_df, x="월", y="평점", markers=True, range_y=[3.8,5.0], title="최근 평점 추이")
        fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.04)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)

with tab_review:
    review_df = pd.DataFrame([
        ["방문 인증", "야경이 좋고 직원 응대가 빨라요. 데이트 코스로 추천합니다.", 4.8, 42, "문라이트 루프탑"],
        ["방문 인증", "게임 종류가 많아서 단체 모임에 좋았습니다. 주말엔 예약 추천.", 4.5, 31, "네온 보드게임 카페"],
        ["일반", "조용하고 콘센트가 많아 심야 작업하기 좋습니다.", 4.6, 22, "심야 스터디 라운지"],
        ["방문 인증", "비 오는 날 실내에서 놀기 좋고 VR 장비 상태가 괜찮아요.", 4.2, 17, "VR 아케이드 밤샘존"],
    ], columns=["인증", "리뷰", "평점", "도움됨", "장소"])
    only_verified = st.checkbox("방문 인증 리뷰만 보기", value=True)
    sort = st.selectbox("정렬", ["도움됨", "평점"])
    view = review_df[review_df["인증"].eq("방문 인증")] if only_verified else review_df
    view = view.sort_values(sort, ascending=False)
    for _, r in view.iterrows():
        st.markdown(f"""
        <div class="place-card">
          {badge(r['인증'])}{badge(r['장소'])}
          <div class="place-title">⭐ {r['평점']} <span class="small-muted">도움됨 {r['도움됨']}</span></div>
          <p>{r['리뷰']}</p>
        </div>
        """, unsafe_allow_html=True)
    keyword_df = pd.DataFrame({"키워드":["야경","조용함","가성비","단체","청결","혼잡"], "빈도":[36,28,24,21,18,14]})
    fig = px.bar(keyword_df, x="키워드", y="빈도", title="자주 언급되는 키워드")
    fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,.04)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

st.caption("Demo MVP · Streamlit Cloud 배포용 · 실제 API 연동 전 샘플 데이터 기반")
