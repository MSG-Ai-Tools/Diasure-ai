function analyze() {
  const sugar = document.getElementById("sugar").value;

  fetch("/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sugar })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("result").innerHTML = data.result;
    document.getElementById("modal").style.display = "flex";
  });
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}
