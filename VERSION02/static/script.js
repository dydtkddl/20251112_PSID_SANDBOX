function searchFiles() {
  const filter = document.getElementById("searchBox").value.toLowerCase();
  const rows = document.querySelectorAll("#fileTable tbody tr");
  rows.forEach(row => {
    const name = row.cells[0].innerText.toLowerCase();
    row.style.display = name.includes(filter) ? "" : "none";
  });
}

document.getElementById("searchBox")?.addEventListener("input", searchFiles);

function setView(mode) {
  const table = document.getElementById("fileTable");
  if (mode === "grid") {
    table.classList.add("table-grid");
  } else {
    table.classList.remove("table-grid");
  }
}

function toggleDarkMode() {
  document.body.dataset.bsTheme =
    document.body.dataset.bsTheme === "dark" ? "light" : "dark";
}
