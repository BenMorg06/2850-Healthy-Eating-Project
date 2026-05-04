// Alex's code - start
let metricsChart = null;

const metricConfig = {
  calories: { label: "Calories", color: "#2563eb" },
  fat: { label: "Fat (g)", color: "#ef4444" },
  protein: { label: "Protein (g)", color: "#16a34a" },
  carbs: { label: "Carbs (g)", color: "#f59e0b" }
};

// Mock weekly data (frontend-only)
const data = {
  labels: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
  series: {
    calories: [1850, 2020, 1950, 2100, 1980, 2300, 1900],
    fat: [58, 72, 63, 76, 68, 80, 60],
    protein: [52, 48, 55, 50, 57, 46, 53],
    carbs: [240, 270, 250, 280, 260, 300, 245]
  },
  percentages: {
    calories: 101.4,
    fat: 97.6,
    carbs: 100.8,
    protein: 103.1
  }
};

function renderChart() {
  const canvas = document.getElementById("weeklyMetricsChart");
  if (!canvas || typeof Chart === "undefined") return;

  const datasets = Object.keys(metricConfig).map((key) => ({
    label: metricConfig[key].label,
    data: data.series[key],
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

  list.innerHTML = `
    <li>Calories: <strong>${data.percentages.calories}%</strong> of recommended weekly amount.</li>
    <li>Fats: <strong>${data.percentages.fat}%</strong> of recommended weekly amount.</li>
    <li>Carbs: <strong>${data.percentages.carbs}%</strong> of recommended weekly amount.</li>
    <li>Protein: <strong>${data.percentages.protein}%</strong> of recommended weekly amount.</li>
  `;
}

document.addEventListener("DOMContentLoaded", () => {
  renderChart();
  bindFilters();
  renderFeedback();
});
// Alex's code - end