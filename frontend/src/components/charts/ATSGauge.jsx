import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

export default function ATSGauge({ score = 0, matched = 0, total = 0 }) {
  const safeScore = Number.isFinite(score) ? Math.round(score) : 0;
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="w-40">
        <CircularProgressbar
          value={safeScore}
          text={`${safeScore}%`}
          styles={buildStyles({
            textColor: "#ec4899",
            pathColor: "#ec4899",
            trailColor: "rgba(255,255,255,0.1)",
            textSize: "18px",
          })}
        />
      </div>

      <p className="text-gray-300 text-lg">
        <span className="text-pink-400 font-semibold">{matched ?? 0}</span> / {total ?? 0} Keywords Matched
      </p>
    </div>
  );
}
