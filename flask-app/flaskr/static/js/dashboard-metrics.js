let metricsChart = null;

const metricConfig = {
  calories: { label: "Calories", color: "#2563eb" },
  fat: { label: "Fat (g)", color: "#ef4444" },
  protein: { label: "Protein (g)", color: "#16a34a" },
  carbs: { label: "Carbs (g)", color: "#f59e0b" }
};

let data = {
  labels: [],
  series: {
    calories: [],
    fat: [],
    protein: [],
    carbs: []
  },
  percentages: {
    calories: 0,
    fat: 0,
    protein: 0,
    carbs: 0
  }
};

async function fetchMetrics() {
  try {
    const response = await fetch('/api/dashboard/weekly-metrics');
    if (!response.ok) {
      console.error('Failed to load weekly metrics', response.statusText);
      return;
    }

    const payload = await response.json();
    data = payload;
    renderChart();
    renderFeedback();
    renderDailyAmounts();
    renderStreak(payload.streak);
  } catch (error) {
    console.error('Error fetching weekly metrics:', error);
  }
}

function renderStreak(streak = 0) {
  const streakCount = document.getElementById('streak-count');
  if (!streakCount) return;
  streakCount.textContent = streak;
}

function renderChart() {
  const canvas = document.getElementById("weeklyMetricsChart");
  if (!canvas || typeof Chart === "undefined") return;

  const datasets = Object.keys(metricConfig).map((key) => ({
    label: metricConfig[key].label,
    data: data.series[key] || [],
    borderColor: metricConfig[key].color,
    backgroundColor: metricConfig[key].color,
    borderWidth: 2,
    pointRadius: 3,
    tension: 0.25
  }));

  if (metricsChart) metricsChart.destroy();

  metricsChart = new Chart(canvas, {
    type: "line",
    data: { labels: data.labels, datasets },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
  });
}

function bindFilters() {
  document.querySelectorAll(".metric-toggle").forEach((toggle) => {
    toggle.addEventListener("change", () => {
      if (!metricsChart) return;
      const selected = new Set(
        [...document.querySelectorAll(".metric-toggle:checked")].map((el) => el.value)
      );

      metricsChart.data.datasets.forEach((ds) => {
        const key = Object.keys(metricConfig).find((k) => metricConfig[k].label === ds.label);
        ds.hidden = !selected.has(key);
      });

      metricsChart.update();
    });
  });
}

function renderFeedback() {
  const list = document.getElementById("nhsFeedbackList");
  if (!list) return;

  const feedbackItems = Object.keys(data.percentages).map(key => {
    const percentage = data.percentages[key];
    const isOut = Math.abs(percentage - 100) > 10;
    const className = isOut ? 'highlight-red' : '';
    return `<li>${metricConfig[key].label}: <strong class="${className}">${percentage}%</strong> of recommended weekly amount.</li>`;
  }).join('');

  list.innerHTML = feedbackItems;
}

function renderDailyAmounts() {
  const container = document.getElementById("daily-amounts");
  if (!container) return;

  let html = '<h4>Daily Amounts</h4><table style="width:100%; border-collapse:collapse;"><thead><tr>';
  html += '<th style="border:1px solid #333; padding:8px;">Day</th>';
  Object.keys(metricConfig).forEach(key => {
    html += `<th style="border:1px solid #333; padding:8px;">${metricConfig[key].label}</th>`;
  });
  html += '</tr></thead><tbody>';

  data.labels.forEach((day, index) => {
    html += `<tr><td style="border:1px solid #333; padding:8px;">${day}</td>`;
    Object.keys(metricConfig).forEach(key => {
      html += `<td style="border:1px solid #333; padding:8px;">${data.series[key][index]}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';

  container.innerHTML = html;
}

document.addEventListener("DOMContentLoaded", () => {
  bindFilters();
  fetchMetrics();
});