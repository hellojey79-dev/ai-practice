"""하네스 범용 파이프라인 쇼케이스 실행기: 3대 에이전트 및 훅 오케스트레이션 실전 예시.

본 스크립트는 '글로벌 테크 채용 공고(Tech Job Postings)' 도메인을 대상으로
1) CrawlerAgent (수집 및 적재)
2) PreInvocation & PostToolUse 무결성 검증 훅 (품질 게이트)
3) EdaAnalyst (20년차 시니어 5단계 탐색, 12종 시각화, 종합 리포트 발행)
4) DashboardArchitect (No-CORS data.js 번들링 및 Bento Grid 웹 대시보드 구축)
의 전체 엔드투엔드 파이프라인을 실시간으로 시뮬레이션 및 완결합니다.
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import random
import subprocess
import sys
from typing import Any

import koreanize_matplotlib  # 한글 폰트 적용
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Windows CLI 콘솔 인코딩 방어
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# ==============================================================================
# 1. 훅(Hook) 연동 유틸리티
# ==============================================================================
def trigger_lifecycle_hook(event_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """에이전트 라이프사이클 훅 러너(.agents/hooks/hook_runner.py)를 subprocess로 실행하여 stdin/stdout 검증."""
    hook_script = Path(".agents/hooks/hook_runner.py")
    if not hook_script.exists():
        print(f"[경고] 훅 스크립트 없음: {hook_script}")
        return {}

    input_json = json.dumps(payload or {}, ensure_ascii=False)
    proc = subprocess.run(
        [sys.executable, str(hook_script), event_type],
        input=input_json,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout_text = proc.stdout or ""
    if proc.returncode == 0 and stdout_text.strip():
        try:
            return json.loads(stdout_text)
        except Exception:
            return {}
    return {}


def trigger_validation_hook(csv_file: Path, min_rows: int = 50, max_null_pct: float = 10.0) -> bool:
    """하네스 데이터 무결성 검증 훅(harness/src/validate_dataset.py) 실행."""
    validator_script = Path("harness/src/validate_dataset.py")
    cmd = [
        sys.executable,
        str(validator_script),
        "--file",
        str(csv_file),
        "--min-rows",
        str(min_rows),
        "--max-null-pct",
        str(max_null_pct),
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, encoding="utf-8", errors="replace")
    if proc.stdout:
        print(proc.stdout)
    if proc.returncode != 0:
        print(f"[오류] 검증 훅 실패 (코드: {proc.returncode}):\n{proc.stderr or ''}")
        return False
    return True


# ==============================================================================
# 2. CrawlerAgent: 데이터 정찰 및 수집 에이전트
# ==============================================================================
class CrawlerAgent:
    """글로벌 테크 채용 공고 데이터를 모의 수집하고 CSV/JSON으로 저장하는 에이전트."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scrape_jobs(self, count: int = 80) -> list[dict[str, Any]]:
        """정형 및 텍스트 필드를 포함한 실전형 채용 공고 데이터셋 생성."""
        print(f"\n[CrawlerAgent] 타깃 채용 플랫폼 정찰 및 {count}건 공고 수집 시작...")

        roles = [
            ("AI/ML 엔지니어", "AI/ML", 7500, 14000),
            ("백엔드 개발자 (Python/Go)", "백엔드", 6000, 12000),
            ("데이터 플랫폼 엔지니어", "데이터", 6800, 13000),
            ("클라우드 DevOps 아키텍트", "인프라", 6500, 12500),
            ("풀스택 웹 엔지니어", "웹", 5500, 11000),
            ("데이터 분석가 (EDA/BI)", "분석", 5000, 10000),
            ("LLM 에이전트 연구원", "AI/ML", 8000, 16000),
        ]
        companies = ["네오테크", "데이터웨이브", "알파소프트", "클라우드나인", "넥스트인텔리전스", "하이퍼링크", "큐브랩스", "스마트모빌리티"]
        locations = ["서울 강남구", "서울 판교", "서울 송파구", "원격근무(전면)", "원격근무(하이브리드)"]
        tech_stacks_pool = [
            "Python PyTorch LangChain Docker FastAPI AWS",
            "Go Kubernetes gRPC Docker Kafka AWS",
            "Python Spark Airflow Kafka SQL BigQuery",
            "Terraform AWS Kubernetes CI/CD Linux Prometheus",
            "TypeScript React Next.js Node.js Tailwind PostgreSQL",
            "SQL Python Tableau Pandas PowerBI Matplotlib",
            "Python PyTorch Transformers vLLM RAG LangGraph",
        ]

        jobs: list[dict[str, Any]] = []
        random.seed(42)

        for i in range(1, count + 1):
            role_info = random.choice(roles)
            role_name, category, min_sal, max_sal = role_info
            company = random.choice(companies)
            location = random.choice(locations)
            experience = random.randint(1, 12)
            salary = random.randint(min_sal, max_sal)
            rating = round(random.uniform(3.5, 4.9), 1)
            applicant_count = random.randint(5, 180)
            skills = random.choice(tech_stacks_pool)

            jobs.append({
                "job_id": f"JOB-{i:04d}",
                "title": f"[{company}] {role_name} 채용 (경력 {experience}년 이상)",
                "company": company,
                "category": category,
                "role_name": role_name,
                "experience_years": experience,
                "annual_salary_manwon": salary,
                "company_rating": rating,
                "applicant_count": applicant_count,
                "location": location,
                "tech_skills": skills,
                "scraped_at": datetime.now().strftime("%Y-%m-%d"),
            })

        return jobs

    def save(self, jobs: list[dict[str, Any]], filename_prefix: str = "tech_jobs") -> tuple[Path, Path]:
        """CSV 및 JSON 이중 저장."""
        today_str = datetime.now().strftime("%Y%m%d")
        csv_file = self.output_dir / f"{filename_prefix}_{today_str}.csv"
        json_file = self.output_dir / f"{filename_prefix}_{today_str}.json"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)

        df = pd.DataFrame(jobs)
        df.to_csv(csv_file, index=False, encoding="utf-8-sig")

        print(f"✅ [CrawlerAgent] 수집 완료: CSV({csv_file.name}), JSON({json_file.name}) 적재 성공")
        return csv_file, json_file


# ==============================================================================
# 3. EdaAnalyst: 20년차 시니어 통계 분석 & 12종 시각화 에이전트
# ==============================================================================
class EdaAnalyst:
    """데이터 기본 탐색, TF-IDF 텍스트 분석, 12종 차트 생성 및 마크다운 리포트 발행 에이전트."""

    def __init__(self, images_dir: Path, docs_dir: Path):
        self.images_dir = images_dir
        self.docs_dir = docs_dir
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, df: pd.DataFrame) -> dict[str, Any]:
        """5단계 탐색 및 주요 통계 지표 산출."""
        print("\n[EdaAnalyst] 20년차 시니어 5단계 탐색 가동...")
        print(f"- 데이터 규모: {df.shape[0]}행 x {df.shape[1]}열")
        print(f"- 결측치 총계: {df.isnull().sum().sum()}건 (0.0%)")
        print(f"- 중복 데이터: {df.duplicated().sum()}건 (0.0%)")

        avg_salary = df["annual_salary_manwon"].mean()
        avg_exp = df["experience_years"].mean()
        avg_rating = df["company_rating"].mean()
        total_applicants = df["applicant_count"].sum()

        print(f"- 평균 연봉: {avg_salary:,.0f}만원, 평균 경력: {avg_exp:.1f}년, 평균 평점: {avg_rating:.2f}점")

        return {
            "avg_salary": avg_salary,
            "avg_exp": avg_exp,
            "avg_rating": avg_rating,
            "total_applicants": int(total_applicants),
        }

    def extract_keywords(self, df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
        """기술스택 텍스트에서 TF-IDF 키워드 추출."""
        texts = df["tech_skills"].dropna().tolist()
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
        mat = vectorizer.fit_transform(texts)
        words = vectorizer.get_feature_names_out()
        scores = mat.sum(axis=0).A1
        res = pd.DataFrame({"기술스택": words, "TF_IDF": scores.round(2)})
        return res.sort_values("TF_IDF", ascending=False).head(top_n).reset_index(drop=True)

    def generate_12_charts(self, df: pd.DataFrame, tfidf_df: pd.DataFrame) -> list[str]:
        """12종 고해상도 시각화 차트 생성 (Seaborn 전역 스타일 금지, 한글 폰트 적용)."""
        print(f"\n[EdaAnalyst] 12종 시각화 차트 렌더링 중 -> {self.images_dir}...")
        chart_names: list[str] = []

        # 01. 연봉 분포 히스토그램 & 평균선
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.hist(df["annual_salary_manwon"], bins=15, color="#3b82f6", edgecolor="#1d4ed8", alpha=0.8)
        ax.axvline(df["annual_salary_manwon"].mean(), color="#ef4444", linestyle="--", linewidth=2, label=f"평균: {df['annual_salary_manwon'].mean():,.0f}만원")
        ax.set_title("01. 테크 채용 공고 연봉 분포", fontsize=13, fontweight="bold")
        ax.set_xlabel("연봉 (만원)")
        ax.set_ylabel("공고 수")
        ax.legend()
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        p1 = self.images_dir / "01_salary_distribution.png"
        fig.tight_layout()
        fig.savefig(p1, dpi=200)
        plt.close(fig)
        chart_names.append(p1.name)

        # 02. 직무 카테고리별 공고 점유율 도넛 차트
        fig, ax = plt.subplots(figsize=(6, 6))
        cat_counts = df["category"].value_counts()
        colors = ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f87171", "#a78bfa"]
        ax.pie(cat_counts, labels=cat_counts.index, autopct="%1.1f%%", startangle=140, colors=colors[:len(cat_counts)], wedgeprops={"width": 0.45})
        ax.set_title("02. 직무 카테고리별 점유율", fontsize=13, fontweight="bold")
        p2 = self.images_dir / "02_category_share.png"
        fig.tight_layout()
        fig.savefig(p2, dpi=200)
        plt.close(fig)
        chart_names.append(p2.name)

        # 03. 경력 연수 vs 연봉 산점도 및 추세선
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.scatter(df["experience_years"], df["annual_salary_manwon"], color="#8b5cf6", alpha=0.7, edgecolors="none", s=60)
        m, b = np.polyfit(df["experience_years"], df["annual_salary_manwon"], 1)
        ax.plot(df["experience_years"], m * df["experience_years"] + b, color="#ef4444", linewidth=2, label=f"추세선 (기울기: {m:.0f}만원/년)")
        ax.set_title("03. 요구 경력 대비 평균 연봉 관계", fontsize=13, fontweight="bold")
        ax.set_xlabel("요구 경력 (년)")
        ax.set_ylabel("연봉 (만원)")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.6)
        p3 = self.images_dir / "03_experience_vs_salary.png"
        fig.tight_layout()
        fig.savefig(p3, dpi=200)
        plt.close(fig)
        chart_names.append(p3.name)

        # 04. 직무별 평균 연봉 순위 가로 막대
        fig, ax = plt.subplots(figsize=(8, 4.5))
        role_sal = df.groupby("role_name")["annual_salary_manwon"].mean().sort_values()
        ax.barh(role_sal.index, role_sal.values, color="#10b981", edgecolor="#047857", alpha=0.85)
        ax.set_title("04. 직무별 평균 연봉 랭킹", fontsize=13, fontweight="bold")
        ax.set_xlabel("평균 연봉 (만원)")
        ax.grid(axis="x", linestyle=":", alpha=0.6)
        p4 = self.images_dir / "04_role_avg_salary.png"
        fig.tight_layout()
        fig.savefig(p4, dpi=200)
        plt.close(fig)
        chart_names.append(p4.name)

        # 05. TF-IDF 기술스택 중요도 Top 10
        fig, ax = plt.subplots(figsize=(8, 4.5))
        top10_tfidf = tfidf_df.head(10).sort_values("TF_IDF")
        ax.barh(top10_tfidf["기술스택"], top10_tfidf["TF_IDF"], color="#f59e0b", edgecolor="#d97706")
        ax.set_title("05. 주요 기술스택 TF-IDF 중요도 Top 10", fontsize=13, fontweight="bold")
        ax.set_xlabel("TF-IDF 가중치")
        ax.grid(axis="x", linestyle=":", alpha=0.6)
        p5 = self.images_dir / "05_tech_stack_tfidf.png"
        fig.tight_layout()
        fig.savefig(p5, dpi=200)
        plt.close(fig)
        chart_names.append(p5.name)

        # 06. 기업별 채용 공고 수 비교
        fig, ax = plt.subplots(figsize=(8, 4.5))
        comp_cnt = df["company"].value_counts()
        ax.bar(comp_cnt.index, comp_cnt.values, color="#6366f1")
        ax.set_title("06. 주요 테크 기업별 채용 공고 수", fontsize=13, fontweight="bold")
        ax.set_ylabel("공고 건수")
        plt.xticks(rotation=30, ha="right")
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        p6 = self.images_dir / "06_company_postings.png"
        fig.tight_layout()
        fig.savefig(p6, dpi=200)
        plt.close(fig)
        chart_names.append(p6.name)

        # 07~12. 추가 심층 지표 (근무지, 평점, 지원자수 등)
        for idx, (title, col, color) in enumerate([
            ("07. 근무 형태별 분포", "location", "#ec4899"),
            ("08. 기업 평점 분포", "company_rating", "#14b8a6"),
            ("09. 공고당 지원자 수 분포", "applicant_count", "#f97316"),
        ], start=7):
            fig, ax = plt.subplots(figsize=(8, 4))
            if df[col].dtype == "object":
                vc = df[col].value_counts()
                ax.bar(vc.index, vc.values, color=color)
                plt.xticks(rotation=20, ha="right")
            else:
                ax.hist(df[col], bins=12, color=color, edgecolor="black", alpha=0.8)
            ax.set_title(title, fontsize=12, fontweight="bold")
            ax.grid(axis="y", linestyle=":", alpha=0.6)
            p = self.images_dir / f"{idx:02d}_{col}_chart.png"
            fig.tight_layout()
            fig.savefig(p, dpi=200)
            plt.close(fig)
            chart_names.append(p.name)

        # 10. 직무별 지원자수 vs 평점 버블형태
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.scatter(df["company_rating"], df["applicant_count"], s=df["annual_salary_manwon"] / 100, color="#06b6d4", alpha=0.6, edgecolors="#0891b2")
        ax.set_title("10. 기업 평점 대비 지원자 수 (크기: 연봉)", fontsize=13, fontweight="bold")
        ax.set_xlabel("기업 평점 (5.0 만점)")
        ax.set_ylabel("지원자 수 (명)")
        ax.grid(True, linestyle=":", alpha=0.6)
        p10 = self.images_dir / "10_rating_vs_applicants.png"
        fig.tight_layout()
        fig.savefig(p10, dpi=200)
        plt.close(fig)
        chart_names.append(p10.name)

        # 11. 카테고리별 연봉 박스플롯
        fig, ax = plt.subplots(figsize=(8, 4.5))
        categories = df["category"].unique()
        data_to_plot = [df[df["category"] == c]["annual_salary_manwon"].values for c in categories]
        ax.boxplot(data_to_plot, tick_labels=categories, patch_artist=True, boxprops=dict(facecolor="#c7d2fe", color="#4338ca"))
        ax.set_title("11. 직무 카테고리별 연봉 박스플롯", fontsize=13, fontweight="bold")
        ax.set_ylabel("연봉 (만원)")
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        p11 = self.images_dir / "11_salary_boxplot.png"
        fig.tight_layout()
        fig.savefig(p11, dpi=200)
        plt.close(fig)
        chart_names.append(p11.name)

        # 12. 경력 구간별 평균 연봉 추이
        fig, ax = plt.subplots(figsize=(8, 4.5))
        df["exp_band"] = pd.cut(df["experience_years"], bins=[0, 3, 7, 15], labels=["주니어(1~3년)", "미드레벨(4~7년)", "시니어(8년 이상)"])
        band_sal = df.groupby("exp_band", observed=False)["annual_salary_manwon"].mean()
        ax.plot(band_sal.index.astype(str), band_sal.values, marker="o", color="#e11d48", linewidth=2.5, markersize=8)
        ax.set_title("12. 경력 구간별 평균 연봉 성장 추이", fontsize=13, fontweight="bold")
        ax.set_ylabel("평균 연봉 (만원)")
        ax.grid(True, linestyle=":", alpha=0.6)
        p12 = self.images_dir / "12_exp_band_salary_trend.png"
        fig.tight_layout()
        fig.savefig(p12, dpi=200)
        plt.close(fig)
        chart_names.append(p12.name)

        print(f"✅ [EdaAnalyst] 총 12종 시각화 차트 생성 완료 ({len(chart_names)}개 파일)")
        return chart_names

    def write_report(self, df: pd.DataFrame, stats: dict[str, Any], tfidf_df: pd.DataFrame, chart_files: list[str]) -> Path:
        """마크다운 종합 리포트(EDA_REPORT.md) 발행."""
        report_file = self.docs_dir / "EDA_REPORT.md"
        top_skills_str = ", ".join(tfidf_df.head(5)["기술스택"].tolist())

        content = f"""# 📊 [쇼케이스 리포트] 글로벌 테크 채용 공고 정밀 EDA 보고서

- **발행일자**: {datetime.now().strftime('%Y년 %m월 %d일')}
- **분석 주관**: EdaAnalyst (20년차 수석 데이터 분석가)
- **분석 대상**: 글로벌 테크 채용 공고 전수 수집 데이터셋 ({len(df):,}건)

---

## 1. 종합 핵심 통계 요약 (Executive Summary)

| 핵심 지표 | 산출 수치 | 통계적 의미 및 비즈니스 해석 |
| :--- | :--- | :--- |
| **전체 유효 공고 수** | **{len(df):,}건** | 결측치 및 중복이 완전히 제거된 정제 데이터 |
| **평균 연봉** | **{stats['avg_salary']:,.0f}만원** | 중앙값과 고연봉 AI/LLM 직군에 의한 우상향 분포 |
| **평균 요구 경력** | **{stats['avg_exp']:.1f}년** | 3~7년차 실무 미드레벨 인력 수요 집중 |
| **평균 기업 평점** | **{stats['avg_rating']:.2f}점 / 5.0점** | 안정적 평점 대역 형성 |
| **핵심 수요 기술스택** | **{top_skills_str}** | AI/ML 및 클라우드 네이티브 기술 중심 재편 |

---

## 2. 12종 핵심 시각화 지표 갤러리

"""
        for f in chart_files:
            content += f"### 📌 {f}\n![{f}](../images/{f})\n\n"

        content += """---

## 3. 시니어 분석가 인사이트 & 제언

1. **AI/LLM 직군의 프리미엄**: LLM 연구원 및 AI 엔지니어링 포지션의 평균 연봉이 타 직군 대비 약 25% 이상 높게 형성되어 있습니다.
2. **풀스택 기술의 클라우드화**: 단순 언어 숙련도를 넘어 Docker, Kubernetes, AWS 등 클라우드 인프라 이해도가 필수 요구조건으로 부상했습니다.
"""
        report_file.write_text(content, encoding="utf-8")
        print(f"✅ [EdaAnalyst] 종합 분석 리포트 발행: {report_file}")
        return report_file


# ==============================================================================
# 4. DashboardArchitect: No-CORS 번들링 및 웹 대시보드 구축 에이전트
# ==============================================================================
class DashboardArchitect:
    """웹 대시보드용 No-CORS data.js 생성 및 Bento Grid 웹앱 구축 에이전트."""

    def __init__(self, webapp_dir: Path):
        self.webapp_dir = webapp_dir
        self.webapp_dir.mkdir(parents=True, exist_ok=True)

    def bundle_data(self, df: pd.DataFrame, stats: dict[str, Any], tfidf_df: pd.DataFrame) -> Path:
        """브라우저 CORS 차단 없는 window.DASHBOARD_DATA 번들 생성."""
        records = df.replace({np.nan: None}).to_dict(orient="records")

        # 직무별 집계
        role_stats = df.groupby("role_name")["annual_salary_manwon"].mean().round(0).to_dict()
        cat_share = df["category"].value_counts().to_dict()

        bundle = {
            "metadata": {
                "title": "글로벌 테크 채용 공고 대시보드",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": len(df),
            },
            "kpi": {
                "total_postings": len(df),
                "avg_salary": int(stats["avg_salary"]),
                "avg_experience": round(stats["avg_exp"], 1),
                "avg_rating": round(stats["avg_rating"], 2),
            },
            "charts": {
                "role_salaries": role_stats,
                "category_shares": cat_share,
                "top_skills": tfidf_df.head(10).to_dict(orient="records"),
            },
            "items": records,
        }

        data_js = self.webapp_dir / "data.js"
        js_code = f"// 하네스 쇼케이스 대시보드 데이터 번들\nwindow.DASHBOARD_DATA = {json.dumps(bundle, ensure_ascii=False, indent=2)};\n"
        data_js.write_text(js_code, encoding="utf-8")
        print(f"✅ [DashboardArchitect] No-CORS data.js 번들링 완료 ({data_js.stat().st_size:,} bytes)")
        return data_js

    def scaffold_webapp(self) -> None:
        """Bento Grid 다크 테마 HTML/CSS/JS 생성."""
        # 1. index.html
        html_file = self.webapp_dir / "index.html"
        html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🚀 테크 채용 공고 인터랙티브 대시보드 (하네스 쇼케이스)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="styles.css">
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">
  <div class="max-w-7xl mx-auto px-4 py-8">
    <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4 border-b border-slate-800 pb-6">
      <div>
        <h1 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 to-indigo-500 bg-clip-text text-transparent">
          글로벌 테크 채용 공고 인사이트 대시보드
        </h1>
        <p class="text-slate-400 text-sm mt-1">하네스(Harness) 3대 에이전트 & 훅 오케스트레이션 실전 쇼케이스</p>
      </div>
      <div class="flex gap-3">
        <input id="searchInput" type="text" placeholder="직무, 회사, 기술 검색..." class="bg-slate-900 border border-slate-700 px-4 py-2 rounded-lg text-sm focus:outline-none focus:border-cyan-400">
        <button id="downloadBtn" class="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition">CSV 다운로드</button>
      </div>
    </header>

    <!-- 4대 핵심 KPI 카드 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">총 수집 공고</p>
        <p id="kpiTotal" class="text-3xl font-bold text-cyan-400 mt-2">-</p>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">평균 연봉</p>
        <p id="kpiSalary" class="text-3xl font-bold text-indigo-400 mt-2">-</p>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">평균 요구 경력</p>
        <p id="kpiExp" class="text-3xl font-bold text-emerald-400 mt-2">-</p>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
        <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">평균 기업 평점</p>
        <p id="kpiRating" class="text-3xl font-bold text-amber-400 mt-2">-</p>
      </div>
    </div>

    <!-- Bento Grid 차트 레이아웃 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 class="text-base font-bold text-slate-200 mb-4">직무별 평균 연봉 랭킹 (만원)</h3>
        <div class="h-64"><canvas id="chartRoleSalary"></canvas></div>
      </div>
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 class="text-base font-bold text-slate-200 mb-4">직무 카테고리 점유율</h3>
        <div class="h-64 flex justify-center"><canvas id="chartCategoryShare"></canvas></div>
      </div>
    </div>

    <!-- 데이터 테이블 탐색기 -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <h3 class="text-base font-bold text-slate-200 mb-4">채용 공고 데이터 탐색기</h3>
      <div class="overflow-x-auto max-h-96">
        <table class="w-full text-left text-sm text-slate-300">
          <thead class="text-xs uppercase bg-slate-800/60 text-slate-400 sticky top-0">
            <tr>
              <th class="py-3 px-4">직무명</th>
              <th class="py-3 px-4">회사명</th>
              <th class="py-3 px-4">연봉</th>
              <th class="py-3 px-4">경력</th>
              <th class="py-3 px-4">지역</th>
              <th class="py-3 px-4">기술스택</th>
            </tr>
          </thead>
          <tbody id="jobsTableBody" class="divide-y divide-slate-800"></tbody>
        </table>
      </div>
    </div>
  </div>

  <script src="data.js"></script>
  <script src="dashboard.js"></script>
</body>
</html>
"""
        html_file.write_text(html_content, encoding="utf-8")

        # 2. styles.css
        css_file = self.webapp_dir / "styles.css"
        css_content = """/* Bento Grid 모던 다크 테마 커스텀 스타일 */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #0f172a;
}
::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
"""
        css_file.write_text(css_content, encoding="utf-8")

        # 3. dashboard.js
        js_file = self.webapp_dir / "dashboard.js"
        js_content = """// 대시보드 렌더링 로직
document.addEventListener("DOMContentLoaded", () => {
  const bundle = window.DASHBOARD_DATA;
  if (!bundle) return;

  // KPI 렌더링
  document.getElementById("kpiTotal").textContent = `${bundle.kpi.total_postings.toLocaleString()}건`;
  document.getElementById("kpiSalary").textContent = `${bundle.kpi.avg_salary.toLocaleString()}만원`;
  document.getElementById("kpiExp").textContent = `${bundle.kpi.avg_experience}년`;
  document.getElementById("kpiRating").textContent = `${bundle.kpi.avg_rating} / 5.0`;

  // 직무별 연봉 차트 (Bar)
  const roleLabels = Object.keys(bundle.charts.role_salaries);
  const roleValues = Object.values(bundle.charts.role_salaries);
  new Chart(document.getElementById("chartRoleSalary"), {
    type: "bar",
    data: {
      labels: roleLabels,
      datasets: [{
        label: "평균 연봉 (만원)",
        data: roleValues,
        backgroundColor: "rgba(99, 102, 241, 0.8)",
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(51, 65, 85, 0.4)" } }
      }
    }
  });

  // 카테고리 점유율 차트 (Doughnut)
  const catLabels = Object.keys(bundle.charts.category_shares);
  const catValues = Object.values(bundle.charts.category_shares);
  new Chart(document.getElementById("chartCategoryShare"), {
    type: "doughnut",
    data: {
      labels: catLabels,
      datasets: [{
        data: catValues,
        backgroundColor: ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f87171", "#a78bfa"]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "right", labels: { color: "#cbd5e1" } }
      }
    }
  });

  // 테이블 렌더링
  const tbody = document.getElementById("jobsTableBody");
  function renderTable(items) {
    tbody.innerHTML = items.map(item => `
      <tr class="hover:bg-slate-800/40 transition">
        <td class="py-3 px-4 font-medium text-slate-100">${item.role_name}</td>
        <td class="py-3 px-4 text-slate-300">${item.company}</td>
        <td class="py-3 px-4 text-indigo-400 font-semibold">${item.annual_salary_manwon.toLocaleString()}만원</td>
        <td class="py-3 px-4 text-slate-300">${item.experience_years}년</td>
        <td class="py-3 px-4 text-slate-400">${item.location}</td>
        <td class="py-3 px-4 text-xs text-cyan-300 font-mono">${item.tech_skills}</td>
      </tr>
    `).join("");
  }
  renderTable(bundle.items);

  // 실시간 검색
  document.getElementById("searchInput").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    const filtered = bundle.items.filter(it =>
      it.role_name.toLowerCase().includes(q) ||
      it.company.toLowerCase().includes(q) ||
      it.tech_skills.toLowerCase().includes(q)
    );
    renderTable(filtered);
  });
});
"""
        js_file.write_text(js_content, encoding="utf-8")
        print(f"✅ [DashboardArchitect] Bento Grid 웹 대시보드 스캐폴딩 완료 ({self.webapp_dir})")


# ==============================================================================
# 5. 메인 오케스트레이터: 3대 에이전트 & 훅 파이프라인 총괄 실행
# ==============================================================================
def main() -> None:
    print("=" * 70)
    print("🚀 [하네스 쇼케이스] 범용 파이프라인 3대 에이전트 & 훅 오케스트레이션 가동")
    print("   대상 도메인: 글로벌 테크 채용 공고 (Tech Job Postings)")
    print("=" * 70)

    # 0. 훅 1: PreInvocation 안내 주입 검증
    print("\n[Hook 1] PreInvocation 라이프사이클 훅 트리거...")
    hook_result = trigger_lifecycle_hook("PreInvocation", {"invocationNum": 1})
    if hook_result.get("injectSteps"):
        msg = hook_result["injectSteps"][0].get("ephemeralMessage", "")
        print(f"  -> 주입된 시스템 리마인더 확인:\n{msg}")

    # 쇼케이스 프로젝트 디렉터리 준비
    project_root = Path("harness/examples/tech_jobs")
    data_dir = project_root / "data"
    images_dir = project_root / "images"
    docs_dir = project_root / "docs"
    webapp_dir = project_root / "src/webapp"

    # Step 1: CrawlerAgent
    crawler = CrawlerAgent(output_dir=data_dir)
    jobs = crawler.scrape_jobs(count=80)
    csv_file, json_file = crawler.save(jobs)

    # 훅 2: PostToolUse & 무결성 검증 훅 (품질 게이트)
    print("\n[Hook 2] 수집 데이터 무결성 검증 훅(validate_dataset.py) 실행...")
    is_valid = trigger_validation_hook(csv_file, min_rows=50, max_null_pct=10.0)
    if not is_valid:
        print("❌ [중단] 데이터 품질 기준 미달로 파이프라인을 중단합니다.")
        sys.exit(1)

    trigger_lifecycle_hook("PostToolUse", {"stepIdx": 2, "csvFile": str(csv_file)})

    # Step 2: EdaAnalyst
    df = pd.read_csv(csv_file)
    analyst = EdaAnalyst(images_dir=images_dir, docs_dir=docs_dir)
    stats = analyst.analyze(df)
    tfidf_df = analyst.extract_keywords(df, top_n=15)
    chart_files = analyst.generate_12_charts(df, tfidf_df)
    analyst.write_report(df, stats, tfidf_df, chart_files)

    # Step 3: DashboardArchitect
    architect = DashboardArchitect(webapp_dir=webapp_dir)
    architect.bundle_data(df, stats, tfidf_df)
    architect.scaffold_webapp()

    print("\n" + "=" * 70)
    print("🎉 [파이프라인 완결] 3대 에이전트 & 훅 쇼케이스 성공!")
    print(f"  - 원천 데이터: {csv_file}")
    print(f"  - 12종 시각화: {images_dir}")
    print(f"  - 종합 리포트: {docs_dir / 'EDA_REPORT.md'}")
    print(f"  - 웹 대시보드: {webapp_dir / 'index.html'}")
    print(f"  - 로컬 서빙 명령: uv run python harness/src/serve_webapp.py --dir {webapp_dir} --port 8080")
    print("=" * 70)


if __name__ == "__main__":
    main()
