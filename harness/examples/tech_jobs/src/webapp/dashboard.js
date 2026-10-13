// 대시보드 렌더링 로직
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
