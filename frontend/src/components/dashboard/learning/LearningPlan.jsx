// frontend/src/components/dashboard/learning/LearningPlan.jsx
import React from "react";

export default function LearningPlan({ plan = {}, dayKey = "30_days" }) {
  const items = plan[dayKey] || [];

  if (!Array.isArray(items) || items.length === 0) {
    return <p className="text-gray-400">Your personalized learning roadmap is being generated...</p>;
  }

  const titleMap = {
    "30_days": "30-Day Roadmap",
    "60_days": "60-Day Roadmap",
    "90_days": "90-Day Roadmap",
  };

  const durationLabel = titleMap[dayKey] || "Learning Roadmap";

  return (
    <div className="w-full">
      <h3 className="text-xl font-semibold text-cyan-300 mb-4">{durationLabel}</h3>

      <div className="space-y-4">
        {items.map((week, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-[#0b1220]/60 border border-cyan-500/20 shadow-lg"
          >
            <p className="text-gray-200 text-sm leading-relaxed font-semibold">
              {week.task}
            </p>

            {week.notes && (
              <p className="text-gray-400 text-xs mt-1">
                {week.notes}
              </p>
            )}

            {week.estimated_hours && (
              <p className="text-gray-300 text-xs mt-1">
                ⏱ Estimated Hours: {week.estimated_hours}
              </p>
            )}

            {Array.isArray(week.resources) && week.resources.length > 0 && (
              <div className="mt-3">
                <p className="text-gray-300 text-sm font-semibold mb-1">Resources:</p>
                <ul className="list-disc list-inside text-gray-400 text-xs space-y-1">
                  {week.resources.map((r, rIdx) => (
                    <li key={rIdx}>
                      <span className="text-gray-300 font-medium">{r.type}: </span>
                      {r.title}
                      {r.url && (
                        <a
                          href={r.url}
                          target="_blank"
                          className="text-cyan-300 ml-1 underline"
                        >
                          (link)
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
