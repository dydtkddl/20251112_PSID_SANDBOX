// ✅ 테이블 정렬
function sortTable(n) {
  let table = document.getElementById("fileTable");
  let switching = true;
  let dir = "asc";
  while (switching) {
    switching = false;
    let rows = table.rows;
    for (let i = 1; i < rows.length - 1; i++) {
      let shouldSwitch = false;
      let x = rows[i].getElementsByTagName("TD")[n];
      let y = rows[i + 1].getElementsByTagName("TD")[n];
      if (dir === "asc" && x.innerText.toLowerCase() > y.innerText.toLowerCase()) shouldSwitch = true;
      else if (dir === "desc" && x.innerText.toLowerCase() < y.innerText.toLowerCase()) shouldSwitch = true;
      if (shouldSwitch) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        break;
      }
    }
    if (!switching && dir === "asc") dir = "desc", switching = true;
  }
}

// ✅ 검색 기능
function searchFiles(e) {
  e.preventDefault();
  const filter = document.getElementById("searchBox").value.toLowerCase();
  const rows = document.querySelectorAll("#fileTable tbody tr");
  rows.forEach(row => {
    const name = row.cells[0].innerText.toLowerCase();
    row.style.display = name.includes(filter) ? "" : "none";
  });
}
