/**
 * 하네스 범용 웹 대시보드 로직
 */

document.addEventListener("DOMContentLoaded", () => {
  const dataBundle = window.DASHBOARD_DATA || window.KYOBO_DATA;
  if (!dataBundle) {
    console.warn("데이터 번들(data.js)이 없습니다. 샘플 데이터를 대기 중입니다.");
    return;
  }

  const items = dataBundle.items || dataBundle.books || [];
  console.log(`[하네스 대시보드] 총 ${items.length}건 데이터 로드 완료`);

  const kpiTotal = document.getElementById("kpiTotal");
  if (kpiTotal) kpiTotal.textContent = `${items.length.toLocaleString()}건`;

  const kpiPct = document.getElementById("kpiPct");
  if (kpiPct) kpiPct.textContent = "100.0%";
});
