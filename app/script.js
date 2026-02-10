const btn = document.getElementById("activate");
const status = document.getElementById("status");

btn.addEventListener("click", () => {
  btn.innerText = "Processing...";
  btn.style.opacity = "0.7";

  setTimeout(() => {
    status.innerText = "✅ Access activated";
    btn.innerText = "Activated";
    btn.disabled = true;
    btn.style.opacity = "0.5";
  }, 1200);
});
