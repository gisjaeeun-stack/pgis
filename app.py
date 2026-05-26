import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 기본 설정 (지도 중심 UI를 위해 wide 모드 채택)
st.set_page_config(
    page_title="야행성 (Nocturnal)",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 스타일 (야간 테마 반영)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #262730; color: white; border: 1px solid #444; }
    .stButton>button:hover { background-color: #ff4b4b; border: 1px solid #ff4b4b; }
    .badge { background-color: #2e7d32; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
    </style>
""", unsafe_allowed_html=True)

# 2. Mock Data (Phase 1: 서울 주요 지역 데이터 샘플 5개)
@st.cache_data
def load_sample_data():
    return [
        {
            "id": 1, "name": "루프탑 클라우드", "category": "카페/바", "lat": 37.5055, "lon": 127.0244,
            "address": "서울 강남구 테헤란로", "operating_hours": "18:00 - 03:00 (라스트오더 02:00)", "status": "영업 중",
            "weather_tag": "맑음", "min_age": "20대 초반", "max_age": "30대", "gender": "혼성", "group_size": "2인", "budget": "3-5만원",
            "activity_type": "조용한", "facility": "루프탑 뷰, 라이브 공연, 프라이빗 룸", "tags": ["🌌 야경", "🍸 칵테일", "🎵 재즈"],
            "scores": {"분위기": 4.8, "서비스": 4.5, "가성비": 3.8, "청결도": 4.7, "접근성": 4.6}, "review_count": 142,
            "reviews": [
                {"user": "야간탐험가A", "badge": "인증됨", "score": 5, "text": "야경이 정말 끝내줍니다! 데이트 코스로 강추해요.", "date": "2026-05-24", "reply": "감사합니다! 다음에 오시면 더 좋은 자리로 안내해 드릴게요."},
                {"user": "혼술러", "badge": "인증됨", "score": 4, "text": "칵테일 클래스도 한대서 가봤는데 분위기 맛집이네요.", "date": "2026-05-20"}
            ]
        },
        {
            "id": 2, "name": "쉘터 이스케이프", "category": "방탈출 카페", "lat": 37.5562, "lon": 126.9227,
            "address": "서울 마포구 홍익로", "operating_hours": "12:00 - 24:00 (마감임박)", "status": "마감 임박",
            "weather_tag": "흐림", "min_age": "20대 초반", "max_age": "20대 후반", "gender": "혼성", "group_size": "3-5인", "budget": "1-3만원",
            "activity_type": "활발한", "facility": "VR존, 다양한 테마 룸, 음료 제공", "tags": ["🧩 스릴", "🧠 두뇌싸움", "🏃 액티비티"],
            "scores": {"분위기": 4.2, "서비스": 4.6, "가성비": 4.0, "청결도": 4.5, "접근성": 4.8}, "review_count": 98,
            "reviews": [
                {"user": "추리마스터", "badge": "인증됨", "score": 5, "text": "방 퀄리티 대박입니다. 흐린 날 실내 데이트로 딱이에요.", "date": "2026-05-25"}
            ]
        },
        {
            "id": 3, "name": "심야식당 한강", "category": "술집", "lat": 37.5115, "lon": 127.0595,
            "address": "서울 강남구 봉은사로", "operating_hours": "24시간 영업", "status": "24시간",
            "weather_tag": "비/눈", "min_age": "20대 후반", "max_age": "30대", "gender": "혼성", "group_size": "6인 이상 그룹", "budget": "3-5만원",
            "activity_type": "활발한", "facility": "단체 예약 가능, 단체석, 배달 가능", "tags": ["🍲 국물요리", "🍻 단체환영", "⏰ 24H"],
            "scores": {"분위기": 4.0, "서비스": 4.2, "가성비": 4.5, "청결도": 3.9, "접근성": 4.4}, "review_count": 210,
            "reviews": [
                {"user": "비오는날파전", "badge": "일반", "score": 4, "text": "안주 가성비 최고입니다. 빗소리 들으면서 술 한잔하기 너무 좋아요.", "date": "2026-05-22"}
            ]
        },
        {
            "id": 4, "name": "북올나잇 스터디", "category": "스터디 카페", "lat": 37.5895, "lon": 127.0325,
            "address": "서울 성북구 안암로", "operating_hours": "24시간 영업", "status": "24시간",
            "weather_tag": "추운 날씨", "min_age": "20대 초반", "max_age": "20대 후반", "gender": "혼성", "group_size": "혼자", "budget": "1만원 이하",
            "activity_type": "조용한", "facility": "개인 독서실형 좌석, 담요 대여, 무료 음료 바", "tags": ["📖 집중", "☕ 커피무한", "❄️ 아늑함"],
            "scores": {"분위기": 4.9, "서비스": 4.3, "가성비": 4.8, "청결도": 4.8, "접근성": 4.1}, "review_count": 76,
            "reviews": [
                {"user": "시험기간대학생", "badge": "인증됨", "score": 5, "text": "추운 겨울 밤에 밤샘 공부하기 여기만큼 아늑한 곳이 없어요.", "date": "2026-05-26"}
            ]
        },
        {
            "id": 5, "name": "힐링 24 스파", "category": "찜질방/스파", "lat": 37.5635, "lon": 126.9815,
            "address": "서울 중구 명동길", "operating_hours": "24시간 영업", "status": "24시간",
            "weather_tag": "더운 날씨", "min_age": "20대 초반", "max_age": "30대", "gender": "혼성", "group_size": "2인", "budget": "1-3만원",
            "activity_type": "조용한", "facility": "얼음방, 야간 수영장, 안마의자, 수면실", "tags": ["🛁 식혜", "🧊 얼음방", "😴 힐링"],
            "scores": {"분위기": 4.4, "서비스": 4.1, "가성비": 4.2, "청결도": 4.3, "접근성": 4.9}, "review_count": 320,
            "reviews": [
                {"user": "스파마스터", "badge": "인증됨", "score": 5, "text": "더운 여름날 에어컨 빵빵한 실내에서 식혜 마시며 굴러다니기 최고.", "date": "2026-05-15"}
            ]
        }
    ]

places = load_sample_data()

# 3. 사이드바: 메인 화면 및 조건 설정 화면
st.sidebar.title("🌙 야행성 (Nocturnal)")
st.sidebar.caption("청년 야간 활동 장소 추천 플랫폼")

st.sidebar.markdown("---")

# 실시간 날씨 연동 UI 선택 시스템
st.sidebar.subheader("☀️ 실시간 날씨 정보 연동")
current_weather = st.sidebar.selectbox("현재 날씨 상태를 선택하세요", ["맑음", "흐림", "비/눈", "추운 날씨", "더운 날씨"])

st.sidebar.markdown("---")

# 조건 설정 화면
st.sidebar.subheader("⚙️ 맞춤형 조건 설정")
selected_category = st.sidebar.multiselect(
    "카테고리 필터", 
    ["카페/바", "술집", "노래방", "PC방", "볼링장", "스터디 카페", "방탈출 카페", "찜질방/스파"],
    default=["카페/바", "술집", "노래방", "PC방", "볼링장", "스터디 카페", "방탈출 카페", "찜질방/스파"]
)

group_size = st.sidebar.select_slider("인원 구성", options=["혼자", "2인", "3-5인", "6인 이상 그룹"], value="2인")
age_group = st.sidebar.selectbox("나이대", ["20대 초반", "20대 후반", "30대"])
activity_pref = st.sidebar.radio("선호 활동 성향", ["전체", "조용한", "활발한"], index=0)
budget_range = st.sidebar.selectbox("예산 범위", ["전체", "1만원 이하", "1-3만원", "3-5만원", "5만원 이상"], index=0)

# 리워드/참여 유도 섹션 안내
st.sidebar.markdown("---")
st.sidebar.subheader("🏆 야행성 유저 리워드")
st.sidebar.info("💡 **방문 인증 리뷰** 작성 시 **포인트 지급!**\n⭐ 활동 점수에 따라 등급 업그레이드! (탐험가 ➔ 전문가 ➔ 마스터)")

# 4. 필터링 알고리즘 적용
filtered_places = []
for p in places:
    if p["category"] not in selected_category:
        continue
    weather_match = (p["weather_tag"] == current_weather)
    size_match = (p["group_size"] == group_size)
    act_match = True if activity_pref == "전체" else (p["activity_type"] == activity_pref)
    budget_match = True if budget_range == "전체" else (p["budget"] == budget_range)
    
    score = 0
    if weather_match: score += 3
    if size_match: score += 2
    if act_match: score += 1
    if budget_match: score += 1
    
    p['match_score'] = score
    filtered_places.append(p)

filtered_places = sorted(filtered_places, key=lambda x: x['match_score'], reverse=True)

# 5. 메인 레이아웃 세션
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📍 내 주변 야간 활동 지도 (PGIS)")
    
    if filtered_places:
        map_df = pd.DataFrame(filtered_places)
        
        view_state = pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=12,
            pitch=45
        )
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            map_df,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=30,
            radius_min_pixels=10,
            radius_max_pixels=30,
            line_width_min_pixels=1,
            get_position="[lon, lat]",
            get_color="[255, 75, 75 if match_score >= 3 else 100, 150, 255]",
            get_line_color=[255, 255, 255],
        )
        
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{name}\n카테고리: {category}\n영업상태: {status}"},
            map_style="mapbox://styles/mapbox/dark-v10"
        )
        st.pydeck_chart(r)
    else:
        st.warning("조건에 맞는 장소가 없습니다. 필터를 변경해 보세요.")

    st.markdown("### 🌙 실시간 맞춤 추천 플레이스")
    for p in filtered_places:
        with st.container():
            c_col1, c_col2, c_col3 = st.columns([2, 2, 1])
            with c_col1:
                st.markdown(f"#### **{p['name']}** `[{p['category']}]`")
                st.caption(f"📍 {p['address']} | 🕰️ {p['operating_hours']}")
            with c_col2:
                tags_str = " ".join([f"`{t}`" for t in p["tags"]])
                st.markdown(tags_str)
            with c_col3:
                status_color = "🔴" if "마감" in p["status"] else "🟢"
                st.markdown(f"{status_color} {p['status']}")
                if p['match_score'] >= 4:
                    st.markdown("✨ **강력 추천**")
            st.markdown("---")

# 6. 우측 칼럼: 장소 상세 화면 & 다차원 평판/리뷰 화면
with col2:
    st.subheader("🔍 장소 상세 정보 및 평판 검증")
    
    if filtered_places:
        selected_place_name = st.selectbox("상세 정보를 확인 할 장소를 선택하세요", [p["name"] for p in filtered_places])
        p_detail = next(p for p in filtered_places if p["name"] == selected_place_name)
        
        st.markdown(f"## **{p_detail['name']}**")
        
        f_col1, f_col2, f_col3 = st.columns(3)
        f_col1.metric("🔥 현재 혼잡도", "여유" if p_detail['id']%2==0 else "혼잡", "대기 약 10분")
        f_col2.metric("🔊 소음 수준", "조용함" if p_detail['activity_type']=="조용한" else "시끄러움")
        f_col3.metric("🎯 만족도 (평점)", f"⭐ {np.mean(list(p_detail['scores'].values())):.1f}/5.0")
        
        st.markdown(f"**ℹ️ 시설 상세 및 편의:** {p_detail['facility']}")
        
        categories = list(p_detail["scores"].keys())
        values = list(p_detail["scores"].values())
        values.append(values[0])
        categories.append(categories[0])

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=p_detail['name'],
            line_color='#ff4b4b'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20),
            height=250,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 💬 신뢰도 검증 리뷰 리스트")
        r_filter = st.radio("리뷰 정렬", ["최신순", "인증 리뷰만"], horizontal=True)
        
        for rev in p_detail["reviews"]:
            if r_filter == "인증 리뷰만" and rev["badge"] != "인증됨":
                continue
                
            with st.chat_message("user"):
                badge_html = '<span class="badge">📍 방문인증</span>' if rev["badge"] == "인증됨" else ''
                st.markdown(f"**{rev['user']}** {badge_html} | {'⭐'*rev['score']} | {rev['date']}")
                st.write(rev["text"])
                
                if "reply" in rev:
                    st.markdown(f"> **사장님 답변:** {rev['reply']}")
                    
        st.markdown("#### ✏️ 내 방문 리뷰 남기기")
        new_text = st.text_area("최소 20자 이상 입력해주세요.", placeholder="실제 방문 경험을 공유해주세요.")
        if st.button("인증 리뷰 등록하기 (GPS 기반)"):
            if len(new_text) >= 20:
                st.success("✅ GPS 방문 인증 성공! 리뷰가 등록되었으며 500포인트가 적립되었습니다. 🎁")
            else:
                st.error("❌ 텍스트를 20자 이상 작성해야 등록이 가능합니다.")
    else:
        st.info("왼쪽 필터 조건에 부합하는 장소가 존재하지 않아 상세정보를 표시할 수 없습니다.")
