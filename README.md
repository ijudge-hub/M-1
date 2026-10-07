# 미국 TSA 보안검색 통과자 수 분석 (M1-1)

분석 리포트: [REPORT.md](REPORT.md)

## 폴더 구조

```
M1-1-project/
├── collect_data.py  데이터 수집 스크립트
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

## 데이터

- 출처: [TSA Checkpoint Travel Numbers](https://www.tsa.gov/travel/passenger-volumes)
- 기간: 2019-01-01 ~ 2026-10-05 (일별, 2,835일)
- 수집 방법: `python3 collect_data.py` 실행 시 tsa.gov 연도별 표를 모아 `data/tsa_daily.csv`로 저장
- 라이선스/이용 조건: 미국 연방정부 공개 자료 (public domain)
