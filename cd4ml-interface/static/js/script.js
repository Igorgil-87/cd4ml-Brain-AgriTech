function toggleAlerts() {
  const popup = document.getElementById('alert-popup');
  popup.style.display = (popup.style.display === 'block') ? 'none' : 'block';
}

window.onclick = function(e) {
  const popup = document.getElementById('alert-popup');
  if (!e.target.closest('.alert-button') && !e.target.closest('#alert-popup')) {
    popup.style.display = 'none';
  }
}

function loadDashboard() {
  const dashboardHTML = `
    <div class="dashboard-grid" id="dashboard">
      <div class="dashboard-card"><h3>Volume no Bucket (MinIO)</h3><canvas id="bucketChart"></canvas></div>
      <div class="dashboard-card"><h3>Data Drift</h3><canvas id="driftChart"></canvas></div>
      <div class="dashboard-card"><h3>Acurácia dos Modelos</h3><canvas id="accuracyChart"></canvas></div>
      <div class="dashboard-card"><h3>Saúde da Lavoura</h3><div class="placeholder">NDVI Médio: <strong>0.79</strong> (Bom)</div></div>
      <div class="dashboard-card"><h3>Logs de Pipeline</h3><div class="placeholder">Última execução: <strong>03/06 - 18h12</strong> (sucesso)</div></div>
    </div>`;
  document.getElementById('main-content').innerHTML = dashboardHTML;
  loadCharts();
}

function loadIframe(url) {
  const iframeHTML = `
    <div class="iframe-wrapper">
      <iframe src="${url}" onerror="this.parentNode.innerHTML='<div class=error-msg>Não foi possível carregar: ${url}</div>';"></iframe>
    </div>`;
  document.getElementById('main-content').innerHTML = iframeHTML;
}

function loadCharts() {
  new Chart(document.getElementById('bucketChart'), {
    type: 'doughnut',
    data: { labels: ['Usado', 'Livre'], datasets: [{ data: [400, 600], backgroundColor: ['#e60000', '#ccc'] }] }
  });
  new Chart(document.getElementById('driftChart'), {
    type: 'bar',
    data: { labels: ['Mai', 'Jun'], datasets: [{ label: 'Data Drift (%)', data: [12, 15], backgroundColor: '#e60000' }] }
  });
  new Chart(document.getElementById('accuracyChart'), {
    type: 'line',
    data: { labels: ['Modelo 1', 'Modelo 2', 'Rendimento'], datasets: [{ label: 'Acurácia (%)', data: [88, 91.3, 93], fill: false, borderColor: '#e60000', tension: 0.1 }] }
  });
}

window.onload = () => {
  setTimeout(() => {
    document.getElementById('splash').style.opacity = '0';
    setTimeout(() => {
      document.getElementById('splash').style.display = 'none';
      loadDashboard();
    }, 800);
  }, 3000);
}