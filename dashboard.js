/**
 * 교보문고 IT 베스트셀러 Chart.js 인터랙티브 대시보드 로직
 * 20년차 시니어 데이터 분석가 방법론 기반 상태 관리 및 시각화 엔진
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. 데이터 유효성 검사
  if (!window.KYOBO_DATA || !window.KYOBO_DATA.books) {
    console.error("데이터 번들(data.js)을 불러오지 못했습니다.");
    alert("데이터를 로드할 수 없습니다. data.js 파일이 올바르게 생성되었는지 확인해주세요.");
    return;
  }

  const allBooks = window.KYOBO_DATA.books;
  const metadata = window.KYOBO_DATA.metadata;

  // 2. 대시보드 전역 상태
  const state = {
    filters: {
      publisher: "all",
      priceTier: "all",
      discount: "all",
      year: "all",
      search: "",
    },
    table: {
      currentPage: 1,
      pageSize: 15,
      sortCol: "rank",
      sortAsc: true,
    },
    charts: {},
  };

  // 3. 차트 글로벌 기본 스타일 설정 (Chart.js v4)
  Chart.defaults.color = "#94a3b8"; // slate-400
  Chart.defaults.font.family = "'Pretendard', sans-serif";
  Chart.defaults.plugins.tooltip.backgroundColor = "rgba(15, 23, 42, 0.95)";
  Chart.defaults.plugins.tooltip.titleColor = "#f8fafc";
  Chart.defaults.plugins.tooltip.bodyColor = "#cbd5e1";
  Chart.defaults.plugins.tooltip.borderColor = "rgba(56, 189, 248, 0.3)";
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;

  // 4. 출판사 필터 드롭다운 옵션 자동 생성
  function initPublisherOptions() {
    const pubSelect = document.getElementById("filterPublisher");
    if (!pubSelect) return;

    // 상위 출판사 빈도순 정렬
    const pubCounts = {};
    allBooks.forEach(b => {
      pubCounts[b.publisher] = (pubCounts[b.publisher] || 0) + 1;
    });

    const sortedPubs = Object.entries(pubCounts).sort((a, b) => b[1] - a[1]);

    sortedPubs.slice(0, 25).forEach(([pub, count]) => {
      const opt = document.createElement("option");
      opt.value = pub;
      opt.textContent = `${pub} (${count}권)`;
      pubSelect.appendChild(opt);
    });
  }

  // 5. 데이터 필터링 파이프라인
  function getFilteredBooks() {
    const { publisher, priceTier, discount, year, search } = state.filters;
    const query = search.trim().toLowerCase();

    return allBooks.filter(book => {
      // 출판사 필터
      if (publisher !== "all" && book.publisher !== publisher) return false;

      // 가격대 필터
      if (priceTier !== "all" && book.price_tier !== priceTier) return false;

      // 할인율 필터
      if (discount === "10" && book.discount_rate !== 10) return false;
      if (discount === "0" && book.discount_rate !== 0) return false;

      // 연도 필터
      if (year === "2026" && book.pub_year !== 2026) return false;
      if (year === "2025" && book.pub_year !== 2025) return false;
      if (year === "2024_earlier" && book.pub_year >= 2025) return false;

      // 검색어 필터 (도서명 또는 저자)
      if (query) {
        const titleMatch = book.title.toLowerCase().includes(query);
        const authorMatch = book.author.toLowerCase().includes(query);
        if (!titleMatch && !authorMatch) return false;
      }

      return true;
    });
  }

  // 6. 상단 5대 핵심 KPI 카드 업데이트
  function updateKPIs(filtered) {
    const totalCount = filtered.length;
    const allTotal = allBooks.length;
    const pctOfAll = ((totalCount / allTotal) * 100).toFixed(1);

    document.getElementById("kpiTotalBooks").textContent = `${totalCount.toLocaleString()}권`;
    document.getElementById("kpiTotalSub").textContent = `전체 ${allTotal}권 중 ${pctOfAll}% 반영`;

    if (totalCount === 0) {
      document.getElementById("kpiAvgPrice").textContent = "-";
      document.getElementById("kpiAvgRating").textContent = "-";
      document.getElementById("kpiAvgReviews").textContent = "-";
      document.getElementById("kpiNewRate").textContent = "-";
      return;
    }

    // 평균 가격 및 중앙값
    const prices = filtered.map(b => b.sale_price).sort((a, b) => a - b);
    const avgPrice = Math.round(prices.reduce((sum, p) => sum + p, 0) / totalCount);
    const medianPrice = prices[Math.floor(totalCount / 2)];
    document.getElementById("kpiAvgPrice").textContent = `${avgPrice.toLocaleString()}원`;
    document.getElementById("kpiPriceSub").textContent = `중앙값 ${medianPrice.toLocaleString()}원`;

    // 평점
    const rated = filtered.filter(b => b.rating > 0);
    const avgRating = rated.length > 0 
      ? (rated.reduce((sum, b) => sum + b.rating, 0) / rated.length).toFixed(2)
      : "-";
    const perfectCount = filtered.filter(b => b.rating === 10).length;
    document.getElementById("kpiAvgRating").textContent = `${avgRating}점`;
    document.getElementById("kpiRatingSub").textContent = `10점 만점 도서 ${perfectCount}권 (${((perfectCount / totalCount) * 100).toFixed(1)}%)`;

    // 리뷰
    const totalReviews = filtered.reduce((sum, b) => sum + b.review_count, 0);
    const avgReviews = (totalReviews / totalCount).toFixed(1);
    const maxReviews = Math.max(...filtered.map(b => b.review_count));
    document.getElementById("kpiAvgReviews").textContent = `${avgReviews}개`;
    document.getElementById("kpiReviewSub").textContent = `총 누적 ${totalReviews.toLocaleString()}개 / 최다 ${maxReviews}개`;

    // 2026년 신간 비율
    const count2026 = filtered.filter(b => b.pub_year === 2026).length;
    const pct2026 = ((count2026 / totalCount) * 100).toFixed(1);
    document.getElementById("kpiNewRate").textContent = `${pct2026}%`;
    document.getElementById("kpiNewSub").textContent = `2026년 신간 ${count2026}권 진입`;
  }

  // 7. Chart.js 7종 차트 초기화 및 업데이트 함수
  function initCharts() {
    // 공통 격자선 스타일
    const gridStyle = { color: "rgba(255, 255, 255, 0.05)", drawBorder: false };

    // 차트 1: 가격대 분포 (Bar)
    const ctx1 = document.getElementById("chartPriceDist").getContext("2d");
    state.charts.price = new Chart(ctx1, {
      type: "bar",
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` 도서 수: ${ctx.parsed.y}권`
            }
          }
        },
        scales: {
          x: { grid: gridStyle, ticks: { font: { size: 11 } } },
          y: { grid: gridStyle, ticks: { stepSize: 20 } }
        }
      }
    });

    // 차트 2: 상위 출판사 점유율 (Horizontal Bar)
    const ctx2 = document.getElementById("chartPublishers").getContext("2d");
    state.charts.publisher = new Chart(ctx2, {
      type: "bar",
      data: { labels: [], datasets: [] },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` 진입 도서: ${ctx.parsed.x}권`
            }
          }
        },
        scales: {
          x: { grid: gridStyle },
          y: { grid: gridStyle, ticks: { font: { size: 11 } } }
        }
      }
    });

    // 차트 3: 할인율 정책 (Doughnut)
    const ctx3 = document.getElementById("chartDiscount").getContext("2d");
    state.charts.discount = new Chart(ctx3, {
      type: "doughnut",
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "68%",
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 12, padding: 15 } }
        }
      }
    });

    // 차트 4: 출간 연도별 추이 (Line with Area)
    const ctx4 = document.getElementById("chartYearTrend").getContext("2d");
    state.charts.year = new Chart(ctx4, {
      type: "line",
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: gridStyle },
          y: { grid: gridStyle }
        }
      }
    });

    // 차트 5: 판매가 vs 평점 산점도 (Scatter/Bubble)
    const ctx5 = document.getElementById("chartScatter").getContext("2d");
    state.charts.scatter = new Chart(ctx5, {
      type: "scatter",
      data: { datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const item = ctx.raw;
                return ` [${item.title.substring(0, 18)}...] 판매가: ${item.x.toLocaleString()}원 | 평점: ${item.y}점 (리뷰 ${item.reviews}개)`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: gridStyle,
            title: { display: true, text: "판매가 (원)", color: "#64748b" },
            ticks: { callback: (v) => `${(v / 1000).toFixed(0)}k` }
          },
          y: {
            grid: gridStyle,
            min: 8.0,
            max: 10.2,
            title: { display: true, text: "독자 평점 (10점 만점)", color: "#64748b" }
          }
        }
      }
    });

    // 차트 6: 순위 구간(Tier)별 비교 (Grouped Bar)
    const ctx6 = document.getElementById("chartTier").getContext("2d");
    state.charts.tier = new Chart(ctx6, {
      type: "bar",
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12 } }
        },
        scales: {
          x: { grid: gridStyle },
          y: {
            type: "linear",
            display: true,
            position: "left",
            grid: gridStyle,
            title: { display: true, text: "평균 판매가 (원)" }
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",
            grid: { drawOnChartArea: false },
            title: { display: true, text: "평균 리뷰 수 (개)" }
          }
        }
      }
    });

    // 차트 7: TF-IDF 핵심 키워드 (Horizontal Bar)
    const ctx7 = document.getElementById("chartKeywords").getContext("2d");
    state.charts.keywords = new Chart(ctx7, {
      type: "bar",
      data: { labels: [], datasets: [] },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` TF-IDF 가중치: ${ctx.parsed.x}`
            }
          }
        },
        scales: {
          x: { grid: gridStyle },
          y: { grid: gridStyle, ticks: { font: { size: 11, weight: "bold" } } }
        }
      }
    });
  }

  function updateCharts(filtered) {
    // 1. 가격대 분포 업데이트
    const priceBins = {
      "1.5만 이하": 0,
      "1.5만~2만": 0,
      "2만~2.5만": 0,
      "2.5만~3만": 0,
      "3만~3.5만": 0,
      "3.5만~4만": 0,
      "4만 초과": 0,
    };
    filtered.forEach(b => {
      const p = b.sale_price;
      if (p <= 15000) priceBins["1.5만 이하"]++;
      else if (p <= 20000) priceBins["1.5만~2만"]++;
      else if (p <= 25000) priceBins["2만~2.5만"]++;
      else if (p <= 30000) priceBins["2.5만~3만"]++;
      else if (p <= 35000) priceBins["3만~3.5만"]++;
      else if (p <= 40000) priceBins["3.5만~4만"]++;
      else priceBins["4만 초과"]++;
    });

    state.charts.price.data = {
      labels: Object.keys(priceBins),
      datasets: [{
        data: Object.values(priceBins),
        backgroundColor: "rgba(56, 189, 248, 0.7)",
        borderColor: "#38bdf8",
        borderWidth: 1,
        borderRadius: 6,
      }]
    };
    state.charts.price.update();

    // 2. 상위 출판사 점유율 업데이트
    const pubCounts = {};
    filtered.forEach(b => { pubCounts[b.publisher] = (pubCounts[b.publisher] || 0) + 1; });
    const topPubs = Object.entries(pubCounts).sort((a, b) => b[1] - a[1]).slice(0, 8);

    state.charts.publisher.data = {
      labels: topPubs.map(p => p[0]),
      datasets: [{
        data: topPubs.map(p => p[1]),
        backgroundColor: "rgba(129, 140, 248, 0.75)",
        borderColor: "#818cf8",
        borderWidth: 1,
        borderRadius: 6,
      }]
    };
    state.charts.publisher.update();

    // 3. 할인율 정책 도넛 업데이트
    let disc10 = 0, disc0 = 0, discOther = 0;
    filtered.forEach(b => {
      if (b.discount_rate === 10) disc10++;
      else if (b.discount_rate === 0) disc0++;
      else discOther++;
    });

    state.charts.discount.data = {
      labels: ["10% 할인", "0% 무할인", "기타"],
      datasets: [{
        data: [disc10, disc0, discOther],
        backgroundColor: ["#10b981", "#64748b", "#f59e0b"],
        borderWidth: 0,
      }]
    };
    state.charts.discount.update();

    // 4. 연도별 추이 라인 업데이트
    const yearCounts = {};
    filtered.forEach(b => {
      if (b.pub_year >= 2020) {
        yearCounts[b.pub_year] = (yearCounts[b.pub_year] || 0) + 1;
      }
    });
    const sortedYears = Object.keys(yearCounts).sort();

    state.charts.year.data = {
      labels: sortedYears.map(y => `${y}년`),
      datasets: [{
        data: sortedYears.map(y => yearCounts[y]),
        borderColor: "#f97316",
        backgroundColor: "rgba(249, 115, 22, 0.15)",
        borderWidth: 3,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: "#fb923c",
        pointRadius: 4,
      }]
    };
    state.charts.year.update();

    // 5. 판매가 vs 평점 산점도 업데이트
    const scatterPoints = filtered
      .filter(b => b.rating > 0)
      .map(b => ({
        x: b.sale_price,
        y: b.rating,
        title: b.title,
        reviews: b.review_count,
      }));

    state.charts.scatter.data = {
      datasets: [{
        data: scatterPoints,
        backgroundColor: "rgba(168, 85, 247, 0.6)",
        borderColor: "#c084fc",
        borderWidth: 1,
        pointRadius: (ctx) => {
          const rev = ctx.raw ? ctx.raw.reviews : 0;
          return Math.min(12, Math.max(4, Math.log2(rev + 2) * 1.5));
        }
      }]
    };
    state.charts.scatter.update();

    // 6. 순위 Tier별 비교 바 업데이트
    const tiers = ["1~50위 (최상위)", "51~100위 (상위)", "101~200위 (중위)", "201위 이상 (하위)"];
    const tierStats = tiers.map(t => {
      const items = filtered.filter(b => b.rank_tier === t);
      if (items.length === 0) return { price: 0, reviews: 0 };
      const avgP = items.reduce((s, b) => s + b.sale_price, 0) / items.length;
      const avgR = items.reduce((s, b) => s + b.review_count, 0) / items.length;
      return { price: Math.round(avgP), reviews: Number(avgR.toFixed(1)) };
    });

    state.charts.tier.data = {
      labels: ["1~50위", "51~100위", "101~200위", "201위+"],
      datasets: [
        {
          label: "평균 판매가",
          data: tierStats.map(s => s.price),
          backgroundColor: "rgba(56, 189, 248, 0.75)",
          yAxisID: "y",
          borderRadius: 4,
        },
        {
          label: "평균 리뷰 수",
          data: tierStats.map(s => s.reviews),
          backgroundColor: "rgba(244, 63, 94, 0.8)",
          yAxisID: "y1",
          borderRadius: 4,
        }
      ]
    };
    state.charts.tier.update();

    // 7. TF-IDF 키워드 (메타데이터 기준 상위 12개)
    const keywords = (metadata.tfidf_keywords || []).slice(0, 12);
    state.charts.keywords.data = {
      labels: keywords.map(k => k.keyword),
      datasets: [{
        data: keywords.map(k => k.score),
        backgroundColor: "rgba(52, 211, 153, 0.75)",
        borderColor: "#34d399",
        borderWidth: 1,
        borderRadius: 4,
      }]
    };
    state.charts.keywords.update();
  }

  // 8. 인터랙티브 데이터 테이블 렌더링
  function renderTable(filtered) {
    const tableBody = document.getElementById("booksTableBody");
    const countInfo = document.getElementById("tableCountInfo");
    if (!tableBody) return;

    // 정렬 수행
    const { sortCol, sortAsc, currentPage, pageSize } = state.table;
    const sorted = [...filtered].sort((a, b) => {
      let valA = a[sortCol];
      let valB = b[sortCol];

      if (typeof valA === "string") {
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortAsc ? valA - valB : valB - valA;
    });

    // 페이지네이션 슬라이스
    const totalItems = sorted.length;
    const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
    const safePage = Math.min(currentPage, totalPages);
    state.table.currentPage = safePage;

    const startIdx = (safePage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, totalItems);
    const pageItems = sorted.slice(startIdx, endIdx);

    // 테이블 행 마크업
    if (pageItems.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center py-12 text-slate-400">
            검색 및 필터 조건에 부합하는 도서가 없습니다.
          </td>
        </tr>
      `;
    } else {
      tableBody.innerHTML = pageItems.map(book => `
        <tr class="border-b border-slate-800 hover:bg-slate-800/40 transition">
          <td class="py-3 px-3 text-center font-bold text-sky-400 font-mono">${book.rank}</td>
          <td class="py-3 px-3 font-medium text-slate-100 max-w-xs truncate" title="${book.title}">
            ${book.title}
          </td>
          <td class="py-3 px-3 text-slate-300 max-w-[140px] truncate" title="${book.author}">
            ${book.author}
          </td>
          <td class="py-3 px-3 text-slate-300">${book.publisher}</td>
          <td class="py-3 px-3 text-right font-mono text-slate-200">
            ${book.sale_price.toLocaleString()}원
            <span class="text-xs text-emerald-400 ml-1">(${book.discount_rate}%)</span>
          </td>
          <td class="py-3 px-3 text-center">
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold font-mono ${book.rating >= 9.5 ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-700 text-slate-300'}">
              ⭐ ${book.rating > 0 ? book.rating.toFixed(2) : '-'}
            </span>
          </td>
          <td class="py-3 px-3 text-right font-mono text-slate-300">${book.review_count.toLocaleString()}개</td>
          <td class="py-3 px-3 text-center">
            <a href="${book.link}" target="_blank" rel="noopener noreferrer" 
               class="text-xs inline-flex items-center gap-1 text-sky-400 hover:text-sky-300 hover:underline">
              <span>상세</span>
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
            </a>
          </td>
        </tr>
      `).join("");
    }

    // 카운트 정보
    if (countInfo) {
      countInfo.textContent = `총 ${totalItems.toLocaleString()}건 중 ${totalItems > 0 ? startIdx + 1 : 0} ~ ${endIdx}건 표시 (페이지 ${safePage} / ${totalPages})`;
    }

    // 페이지네이션 버튼 제어
    const prevBtn = document.getElementById("btnPrevPage");
    const nextBtn = document.getElementById("btnNextPage");
    if (prevBtn) prevBtn.disabled = safePage <= 1;
    if (nextBtn) nextBtn.disabled = safePage >= totalPages;
  }

  // 9. CSV 파일 내보내기 함수
  function downloadCSV(filtered) {
    if (filtered.length === 0) {
      alert("다운로드할 데이터가 없습니다.");
      return;
    }

    const headers = ["순위", "도서명", "저자", "출판사", "출간일", "정가", "판매가", "할인율(%)", "평점", "리뷰수", "ISBN", "링크"];
    const rows = filtered.map(b => [
      b.rank,
      `"${b.title.replace(/"/g, '""')}"`,
      `"${b.author.replace(/"/g, '""')}"`,
      `"${b.publisher.replace(/"/g, '""')}"`,
      b.pub_date,
      b.original_price,
      b.sale_price,
      b.discount_rate,
      b.rating,
      b.review_count,
      b.isbn,
      b.link,
    ]);

    const csvContent = "\uFEFF" + [headers.join(","), ...rows.map(r => r.join(","))].join("\r\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `kyobo_it_bestsellers_filtered_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // 10. 통합 UI 갱신 파이프라인
  function refreshDashboard() {
    const filtered = getFilteredBooks();
    updateKPIs(filtered);
    updateCharts(filtered);
    renderTable(filtered);
  }

  // 11. 이벤트 바인딩
  function bindEvents() {
    // 출판사 선택 드롭다운
    const pubSelect = document.getElementById("filterPublisher");
    if (pubSelect) {
      pubSelect.addEventListener("change", (e) => {
        state.filters.publisher = e.target.value;
        state.table.currentPage = 1;
        refreshDashboard();
      });
    }

    // 가격대 칩 버튼 그룹
    document.querySelectorAll(".chip-price").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".chip-price").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.filters.priceTier = btn.dataset.tier;
        state.table.currentPage = 1;
        refreshDashboard();
      });
    });

    // 할인율 칩 버튼 그룹
    document.querySelectorAll(".chip-discount").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".chip-discount").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.filters.discount = btn.dataset.discount;
        state.table.currentPage = 1;
        refreshDashboard();
      });
    });

    // 출간연도 칩 버튼 그룹
    document.querySelectorAll(".chip-year").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".chip-year").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.filters.year = btn.dataset.year;
        state.table.currentPage = 1;
        refreshDashboard();
      });
    });

    // 검색창 입력 이벤트 (디바운스 250ms)
    const searchInput = document.getElementById("searchInput");
    let debounceTimer;
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          state.filters.search = e.target.value;
          state.table.currentPage = 1;
          refreshDashboard();
        }, 250);
      });
    }

    // 필터 초기화 버튼
    const resetBtn = document.getElementById("btnResetFilters");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        state.filters = { publisher: "all", priceTier: "all", discount: "all", year: "all", search: "" };
        if (pubSelect) pubSelect.value = "all";
        if (searchInput) searchInput.value = "";
        document.querySelectorAll(".filter-chip").forEach(b => b.classList.remove("active"));
        document.querySelectorAll("[data-tier='all'], [data-discount='all'], [data-year='all']").forEach(b => b.classList.add("active"));
        state.table.currentPage = 1;
        refreshDashboard();
      });
    }

    // 테이블 헤더 정렬 클릭 이벤트
    document.querySelectorAll("[data-sort]").forEach(th => {
      th.addEventListener("click", () => {
        const col = th.dataset.sort;
        if (state.table.sortCol === col) {
          state.table.sortAsc = !state.table.sortAsc;
        } else {
          state.table.sortCol = col;
          state.table.sortAsc = true;
        }
        renderTable(getFilteredBooks());
      });
    });

    // 페이지네이션 버튼
    const prevBtn = document.getElementById("btnPrevPage");
    const nextBtn = document.getElementById("btnNextPage");
    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        if (state.table.currentPage > 1) {
          state.table.currentPage--;
          renderTable(getFilteredBooks());
        }
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        state.table.currentPage++;
        renderTable(getFilteredBooks());
      });
    }

    // 페이지 크기 변경
    const pageSizeSelect = document.getElementById("pageSizeSelect");
    if (pageSizeSelect) {
      pageSizeSelect.addEventListener("change", (e) => {
        state.table.pageSize = parseInt(e.target.value, 10);
        state.table.currentPage = 1;
        renderTable(getFilteredBooks());
      });
    }

    // CSV 다운로드 버튼
    const csvBtn = document.getElementById("btnExportCSV");
    if (csvBtn) {
      csvBtn.addEventListener("click", () => {
        downloadCSV(getFilteredBooks());
      });
    }
  }

  // 12. 부트스트랩 실행
  initPublisherOptions();
  initCharts();
  bindEvents();
  refreshDashboard();
});
