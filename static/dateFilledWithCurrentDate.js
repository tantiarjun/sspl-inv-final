document.addEventListener("DOMContentLoaded", function () {
  const currentDate = new Date();

  // Get current date in YYYY-MM-DD format
  const formattedCurrentDate = currentDate.toISOString().split("T")[0];

  document.getElementById("from_date").value = formattedCurrentDate;
  document.getElementById("to_date").value = formattedCurrentDate;
});
