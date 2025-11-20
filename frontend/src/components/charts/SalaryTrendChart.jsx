import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const ROLE_SALARY_MAP = {
  "Data Analyst": [4, 5, 6, 7, 8],
  "Data Scientist": [6, 8, 10, 12, 14],
  "Machine Learning Engineer": [7, 9, 12, 14, 16],
  "Frontend Developer": [5, 6, 7, 8, 9],
  "Backend Developer": [6, 7.5, 9, 11, 13],
  "Full Stack Developer": [6, 7, 8, 9.5, 11],
  "MLOps Engineer": [7, 9, 11, 13, 15],
  "Cloud Engineer": [7, 8.5, 10, 12, 14],
};

export default function SalaryTrendChart({ role }) {
  const fallback = [6, 6.5, 7.2, 8.1, 9];
  const values = ROLE_SALARY_MAP[role] || fallback;

  const data = {
    labels: ["2021", "2022", "2023", "2024", "2025"],
    datasets: [
      {
        label: "Salary Trend (₹ LPA)",
        data: values,
        borderColor: "rgba(56,189,248,1)",
        backgroundColor: "rgba(56,189,248,0.3)",
        borderWidth: 2,
        tension: 0.4,
        pointBackgroundColor: "rgba(56,189,248,1)",
      },
    ],
  };

  const options = {
    plugins: { legend: { labels: { color: "white" } } },
    scales: {
      x: { ticks: { color: "#e2e8f0" } },
      y: { ticks: { color: "#e2e8f0" } },
    },
    responsive: true,
    maintainAspectRatio: false,
  };

  return <div className="h-[300px]"><Line data={data} options={options} /></div>;
}
