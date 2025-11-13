// ✅ 검색 기능
function searchFiles() {
  const filter = document.getElementById("searchBox").value.toLowerCase();
  const rows = document.querySelectorAll("#fileTable tbody tr");
  rows.forEach(row => {
    const name = row.cells[0].innerText.toLowerCase();
    row.style.display = name.includes(filter) ? "" : "none";
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const searchBox = document.getElementById("searchBox");
  if (searchBox) searchBox.addEventListener("input", searchFiles);
});

// ✅ 정렬 기능
function sortTable(n) {
  const table = document.getElementById("fileTable");
  const tbody = table.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr"));
  const th = table.querySelectorAll("th")[n];
  const currentDir = th.dataset.sortDir === "asc" ? "desc" : "asc";
  th.dataset.sortDir = currentDir;

  rows.sort((a, b) => {
    let x = a.cells[n].innerText.trim().toLowerCase();
    let y = b.cells[n].innerText.trim().toLowerCase();

    // 숫자 비교 (크기)
    if (n === 2) {
      const numX = parseFloat(x.replace(/[^\d.]/g, "")) || 0;
      const numY = parseFloat(y.replace(/[^\d.]/g, "")) || 0;
      return currentDir === "asc" ? numX - numY : numY - numX;
    }

    // 문자열 비교
    if (x < y) return currentDir === "asc" ? -1 : 1;
    if (x > y) return currentDir === "asc" ? 1 : -1;
    return 0;
  });

  // ✅ 정렬된 행 다시 삽입
  rows.forEach(row => tbody.appendChild(row));

  // ✅ 헤더 아이콘 갱신
  table.querySelectorAll("th").forEach((header, i) => {
    header.innerText = header.innerText.replace(/[\u25B2\u25BC]/g, ""); // ▲▼ 제거
    if (i === n) {
      header.innerText += currentDir === "asc" ? " ▲" : " ▼";
    }
  });
}

// ✅ 보기 전환 (선택)
function setView(mode) {
  const table = document.getElementById("fileTable");
  table.classList.toggle("table-grid", mode === "grid");
}

// ✅ 다크모드 (선택)
function toggleDarkMode() {
  document.body.dataset.bsTheme =
    document.body.dataset.bsTheme === "dark" ? "light" : "dark";
}
