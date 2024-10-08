function filterData() {
  const itemName = document.getElementById("item").value;
  const tableRows = document.querySelectorAll("#stockTableBody tr");

  tableRows.forEach((row) => {
    const itemCell = row.children[1].textContent.trim();

    if (itemName === "" || itemCell === itemName) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}

function searchItem() {
  const searchInput = document
    .getElementById("searchInput")
    .value.toLowerCase();
  const tableRows = document.querySelectorAll("#stockTableBody tr");

  if (searchInput !== "") {
    tableRows.forEach((row) => {
      const itemCell = row.children[1].textContent.toLowerCase();
      if (itemCell.includes(searchInput)) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }
}
