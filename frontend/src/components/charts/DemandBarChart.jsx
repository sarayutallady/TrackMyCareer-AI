import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const ROLE_DEMAND_MAP = {
  "Data Analyst": [70, 85],
  "Data Scientist": [65, 90],
  "Machine Learning Engineer": [60, 95],
  "Backend Developer": [75, 88],
  "Frontend Developer": [80, 85],
  "Full Stack Developer": [78, 92],
  "MLOps Engineer": [50, 80],
  "Cloud Engineer": [60, 90],
};

export default function DemandBarChart({ role }) {
  const fallback = [70, 85];
  const values = ROLE_DEMAND_MAP[role] || fallback;

  const data = {
    labels: ["Current Demand", "Projected 5yr Demand"],
    datasets: [
      {
        label: "Market Demand",
        data: values,
        backgroundColor: ["rgba(249,115,22,0.7)", "rgba(56,189,248,0.7)"],
        borderColor: ["rgba(249,115,22,1)", "rgba(56,189,248,1)"],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    plugins: { legend: { labels: { color: "white" } } },
    scales: {
      x: { ticks: { color: "#e2e8f0" }, grid: { color: "rgba(255,255,255,0.1)" } },
      y: { ticks: { color: "#e2e8f0" }, grid: { color: "rgba(255,255,255,0.1)" } },
    },
    responsive: true,
    maintainAspectRatio: false,
  };

  return <div className="h-[280px]"><Bar data={data} options={options} /></div>;
}
