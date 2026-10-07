# 미국 TSA 보안검색 통과자 수 분석 (M1-1)

분석 리포트: [REPORT.md](REPORT.md)

## 폴더 구조

```
M1-1-project/
├── collect_data.py  데이터 수집 스크립트
├── dashboard.py     대시보드 (보너스)
├── data/            원본 데이터 (csv)
├── images/          리포트에 들어가는 그래프 (png)
├── analysis.ipynb   분석 노트북
├── REPORT.md        분석 리포트
└── requirements.txt
```

## 실행 방법

```bash
# 가상환경은 구글 드라이브 밖에 두는 게 좋음 (동기화 부담)
python3 -m venv ~/.venvs/m1-1
source ~/.venvs/m1-1/bin/activate
pip install -r requirements.txt
jupyter notebook analysis.ipynb
```

노트북을 위에서부터 순서대로 실행하면 `images/`에 그래프가 저장됨.

데이터를 최신으로 다시 받으려면 `python3 collect_data.py`.

## 보너스 과제

### 1. 대시보드 (로컬 실행)

```bash
streamlit run dashboard.py
```

브라우저에서 `http://localhost:8501`이 열림. 왼쪽 사이드바에서 조건을 바꿔 가며 탐색.

| 조건 | 설명 |
|---|---|
| 기간 | 슬라이더로 시작일~종료일 선택 |
| 집계 단위 | 일 / 주 / 월 |
| 이동평균 | 일 단위일 때 1·7·14·30일 |
| 요일 | 특정 요일만 골라 보기 |

화면 구성: 요약 지표(일평균, 최고, 최저, 전년 같은 기간 대비) → 추이 그래프 → 요일별·월별 평균 → 가장 붐빈 날·한산한 날 Top 5

탐색 시나리오 예시
1. 기간을 2020-01 ~ 2021-12, 집계 단위를 월로 → 코로나 급락과 회복 과정
2. 요일을 화요일만 vs 일요일만 → 요일 간 차이
3. 기간을 매년 11월로 좁히기 → 추수감사절 전후 피크와 당일 급감

### 2. 시계열 분해 · 간단 예측

`analysis.ipynb`의 "6. 보너스" 파트.

- 시계열 분해: 2022-01 ~ 2026-09 월평균을 추세 + 12개월 계절성 + 나머지로 분리 (`images/05_decompose.png`)
- 간단 예측: 마지막 4주를 숨기고 "작년 같은 요일" / "작년 같은 요일 × 최근 성장률" 두 베이스라인으로 예측 후 오차 비교 (`images/06_forecast.png`)

## 데이터

- 출처: [TSA Checkpoint Travel Numbers](https://www.tsa.gov/travel/passenger-volumes)
- 기간: 2019-01-01 ~ 2026-10-05 (일별, 2,835일)
- 수집 방법: `python3 collect_data.py` 실행 시 tsa.gov 연도별 표를 모아 `data/tsa_daily.csv`로 저장
- 라이선스/이용 조건: 미국 연방정부 공개 자료 (public domain)
