function loadIframe(url) {
  const mainContent = document.getElementById("main-content");
  if (mainContent) {
    mainContent.innerHTML = '';
    const iframe = document.createElement("iframe");
    iframe.src = url;
    iframe.width = "100%";
    iframe.height = "1000px";
    iframe.style.border = "none";
    iframe.loading = "lazy";
    mainContent.appendChild(iframe);
  }
}

function loadDashboard() {
  loadIframe("http://localhost:11001/dashboard");
}

function toggleAlerts() {
  const popup = document.getElementById("alert-popup");
  popup.classList.toggle("show");
}