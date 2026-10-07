"""TSA 보안검색 통과자 수 대시보드 (보너스 과제)

실행: streamlit run dashboard.py
기간, 집계 단위, 이동평균, 요일을 바꿔 가며 데이터를 탐색한다.
"""
import altair as alt
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

# 필터 (주소 뒤에 ?start=2020-01-01&end=2021-12-31&unit=월&days=화,일 처럼 조건을 넘길 수도 있음)
qp = st.query_params
min_d, max_d = df.index.min().date(), df.index.max().date()


def qp_date(key, default):
    try:
        return min(max(pd.Timestamp(qp[key]).date(), min_d), max_d)
    except (KeyError, ValueError):
        return default


with st.sidebar:
    st.header("조건")
    start, end = st.slider(
        "기간",
        min_value=min_d,
        max_value=max_d,
        value=(qp_date("start", pd.Timestamp("2023-01-01").date()), qp_date("end", max_d)),
        format="YYYY-MM-DD",
    )
    units = ["일", "주", "월"]
    unit = st.radio("집계 단위", units, index=units.index(qp.get("unit", "일")) if qp.get("unit") in units else 0, horizontal=True)
    ma_options = [1, 7, 14, 30]
    ma_default = int(qp["ma"]) if qp.get("ma", "").isdigit() and int(qp["ma"]) in ma_options else 7
    ma = st.select_slider("이동평균 (일 단위일 때)", options=ma_options, value=ma_default)
    default_days = [d for d in qp.get("days", "").split(",") if d in WEEKDAYS] or WEEKDAYS
    days = st.multiselect("요일", WEEKDAYS, default=default_days)

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
c2.metric(f"최고 ({view['passengers'].idxmax():%Y-%m-%d})", f"{view['passengers'].max() / 1e6:.2f}백만 명")
c3.metric(f"최저 ({view['passengers'].idxmin():%Y-%m-%d})", f"{view['passengers'].min() / 1e6:.2f}백만 명")
c4.metric("전년 같은 기간 대비", f"{yoy:+.1f}%" if yoy is not None else "비교 불가")

# 추이
st.subheader("추이 (백만 명)")
if unit == "일":
    series = view["passengers"].rolling(ma, min_periods=1).mean() if ma > 1 else view["passengers"]
    label = f"{ma}일 이동평균" if ma > 1 else "일별"
else:
    series = view["passengers"].resample("W" if unit == "주" else "MS").mean()
    label = f"{unit}별 일평균"
st.line_chart(series.rename(label) / 1e6)

# 요일별 · 월별
def bar(data, x_title):
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X("label:N", sort=None, title=x_title, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("value:Q", title=None),
            tooltip=[alt.Tooltip("label:N", title=x_title), alt.Tooltip("value:Q", title="백만 명", format=".2f")],
        )
    )
    st.altair_chart(chart, width="stretch")


left, right = st.columns(2)
with left:
    st.subheader("요일별 평균 (백만 명)")
    by_day = view.groupby("weekday")["passengers"].mean().reindex([d for d in WEEKDAYS if d in days]) / 1e6
    bar(pd.DataFrame({"label": by_day.index, "value": by_day.values}), "요일")
with right:
    st.subheader("월별 평균 (백만 명)")
    by_month = view.groupby(view.index.month)["passengers"].mean() / 1e6
    bar(pd.DataFrame({"label": [f"{m}월" for m in by_month.index], "value": by_month.values}), "월")

# 가장 붐빈 날 / 한산한 날
st.subheader("가장 붐빈 날 · 한산한 날 Top 5")
def table(rows):
    return pd.DataFrame({
        "날짜": rows.index.strftime("%Y-%m-%d"),
        "요일": rows["weekday"].values,
        "통과자 수": [f"{n:,}" for n in rows["passengers"]],
    })


t1, t2 = st.columns(2)
t1.caption("가장 붐빈 날")
t1.dataframe(table(view.nlargest(5, "passengers")), hide_index=True, width="stretch")
t2.caption("가장 한산한 날")
t2.dataframe(table(view.nsmallest(5, "passengers")), hide_index=True, width="stretch")
