import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";
import { Radar } from "react-chartjs-2";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

export default function RadarSkillChart({ data }) {
  const chartData = {
    labels: data.map((item) => item.skill),
    datasets: [
      {
        label: "Your Skills",
        data: data.map((item) => item.user),
        borderColor: "rgba(56, 189, 248, 1)",
        backgroundColor: "rgba(56, 189, 248, 0.25)",
        borderWidth: 2,
        pointBackgroundColor: "rgba(56, 189, 248, 1)",
      },
      {
        label: "Target Role Skills",
        data: data.map((item) => item.role),
        borderColor: "rgba(249, 115, 22, 1)",
        backgroundColor: "rgba(249, 115, 22, 0.25)",
        borderWidth: 2,
        pointBackgroundColor: "rgba(249, 115, 22, 1)",
      },
    ],
  };

  const chartOptions = {
    scales: {
      r: {
        angleLines: { color: "rgba(255,255,255,0.2)" },
        grid: { color: "rgba(255,255,255,0.1)" },
        suggestedMin: 0,
        suggestedMax: 5,
        ticks: { display: false },
        pointLabels: {
          color: "#e2e8f0",
          font: { size: 14 },
        },
      },
    },
    plugins: {
      legend: {
        labels: { color: "white" },
      },
    },
    responsive: true,
    maintainAspectRatio: false,
  };

  return (
    <div className="h-[360px]">
      <Radar data={chartData} options={chartOptions} />
    </div>
  );
}
