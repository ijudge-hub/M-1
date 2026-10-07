"""TSA 보안검색 통과자 수 대시보드 (보너스 과제)

실행: streamlit run dashboard.py
기간, 집계 단위, 이동평균, 요일을 바꿔 가며 데이터를 탐색한다.
"""
import pandas as pd
import streamlit as st

DATA_PATH = "data/tsa_daily.csv"
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]

st.set_page_config(page_title="TSA 통과자 수 대시보드", layout="wide")


@st.cache_data
def load():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).set_index("date")
    df["weekday"] = [WEEKDAYS[d] for d in df.index.dayofweek]
    return df


df = load()

st.title("미국 TSA 보안검색 통과자 수")
st.caption(f"출처: tsa.gov · {df.index.min():%Y-%m-%d} ~ {df.index.max():%Y-%m-%d} · {len(df):,}일")

# 필터
with st.sidebar:
    st.header("조건")
    start, end = st.slider(
        "기간",
        min_value=df.index.min().date(),
        max_value=df.index.max().date(),
        value=(pd.Timestamp("2023-01-01").date(), df.index.max().date()),
        format="YYYY-MM-DD",
    )
    unit = st.radio("집계 단위", ["일", "주", "월"], horizontal=True)
    ma = st.select_slider("이동평균 (일 단위일 때)", options=[1, 7, 14, 30], value=7)
    days = st.multiselect("요일", WEEKDAYS, default=WEEKDAYS)

view = df.loc[str(start):str(end)]
view = view[view["weekday"].isin(days)]

if view.empty:
    st.warning("선택한 조건에 맞는 데이터가 없어요.")
    st.stop()

# 요약 지표
prev = df["passengers"].shift(364).reindex(view.index)
yoy = (view["passengers"].sum() / prev.sum() - 1) * 100 if prev.notna().all() else None
c1, c2, c3, c4 = st.columns(4)
c1.metric("일평균", f"{view['passengers'].mean() / 1e6:.2f}백만 명")
c2.metric("최고", f"{view['passengers'].max() / 1e6:.2f}백만 명", view["passengers"].idxmax().strftime("%Y-%m-%d"), delta_color="off")
c3.metric("최저", f"{view['passengers'].min() / 1e6:.2f}백만 명", view["passengers"].idxmin().strftime("%Y-%m-%d"), delta_color="off")
c4.metric("전년 같은 기간 대비", f"{yoy:+.1f}%" if yoy is not None else "비교 불가")

# 추이
st.subheader("추이")
if unit == "일":
    series = view["passengers"].rolling(ma, min_periods=1).mean() if ma > 1 else view["passengers"]
    label = f"{ma}일 이동평균" if ma > 1 else "일별"
else:
    series = view["passengers"].resample("W" if unit == "주" else "MS").mean()
    label = f"{unit}별 일평균"
st.line_chart(series.rename(label) / 1e6, y_label="백만 명")

# 요일별 · 월별
left, right = st.columns(2)
with left:
    st.subheader("요일별 평균")
    by_day = view.groupby("weekday")["passengers"].mean().reindex([d for d in WEEKDAYS if d in days])
    st.bar_chart(by_day / 1e6, y_label="백만 명")
with right:
    st.subheader("월별 평균")
    by_month = view.groupby(view.index.month)["passengers"].mean()
    by_month.index = [f"{m}월" for m in by_month.index]
    st.bar_chart(by_month / 1e6, y_label="백만 명", sort=False)

# 가장 붐빈 날 / 한산한 날
st.subheader("가장 붐빈 날 · 한산한 날 Top 5")
top = view.nlargest(5, "passengers")[["passengers", "weekday"]]
low = view.nsmallest(5, "passengers")[["passengers", "weekday"]]
t1, t2 = st.columns(2)
t1.dataframe(top.rename(columns={"passengers": "통과자 수", "weekday": "요일"}), width="stretch")
t2.dataframe(low.rename(columns={"passengers": "통과자 수", "weekday": "요일"}), width="stretch")
