"""TSA 공항 보안검색 통과자 수(일별) 수집 스크립트

출처: https://www.tsa.gov/travel/passenger-volumes
연도별 페이지(/2019 ~ 작년)와 올해 페이지의 표를 모아 data/tsa_daily.csv로 저장한다.
"""
import csv
import re
import urllib.request
from datetime import date, datetime
from pathlib import Path

BASE_URL = "https://www.tsa.gov/travel/passenger-volumes"
OUT_PATH = Path(__file__).parent / "data" / "tsa_daily.csv"
ROW = re.compile(r"<td[^>]*>\s*(\d{1,2}/\d{1,2}/\d{4})\s*</td>\s*<td[^>]*>\s*([\d,]+)\s*</td>")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8")


def main():
    urls = [f"{BASE_URL}/{y}" for y in range(2019, date.today().year)] + [BASE_URL]
    rows = {}
    for url in urls:
        found = ROW.findall(fetch(url))
        print(f"{url}: {len(found)}행")
        for d, n in found:
            rows[datetime.strptime(d, "%m/%d/%Y").date()] = int(n.replace(",", ""))

    OUT_PATH.parent.mkdir(exist_ok=True)
    with open(OUT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "passengers"])
        for d in sorted(rows):
            writer.writerow([d.isoformat(), rows[d]])
    print(f"저장: {OUT_PATH} ({len(rows)}일)")


if __name__ == "__main__":
    main()
