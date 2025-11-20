// Dashboard.jsx

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

// keep your existing subcomponents (must exist)
import ReadinessCarousel from "./readiness/ReadinessCarousel";
import RadarSkillChart from "../charts/RadarSkillChart";
import ATSGauge from "../charts/ATSGauge";
import LearningPlan from "./learning/LearningPlan";

// Updated charts — now accept props
import SalaryTrendChart from "../charts/SalaryTrendChart";
import DemandBarChart from "../charts/DemandBarChart";

import ProjectSuggestions from "./projects/ProjectSuggestions";

// Export button WITHOUT "Share Link"
import ExportButtons from "./export/ExportButtons";

export default function Dashboard({ analysis = {} }) {
  const [skills, setSkills] = useState([]);
  const [ats, setAts] = useState({ ats_score: 0, matched: 0, total: 0, matched_keywords: [] });
  const [roles, setRoles] = useState([]);
  const [plan, setPlan] = useState({});
  const [projects, setProjects] = useState([]);
  const [missingSkills, setMissingSkills] = useState([]);
  const [matchPercent, setMatchPercent] = useState(0);
  const [summaryText, setSummaryText] = useState("");
  const [selectedRole, setSelectedRole] = useState(null);
  const [activeDay, setActiveDay] = useState("30_days");

  // NEW: dynamic chart data
  const [salaryData, setSalaryData] = useState([6, 6.5, 7.2, 8.1, 9]);
  const [demandData, setDemandData] = useState([70, 85]);

  useEffect(() => {
    if (!analysis || Object.keys(analysis).length === 0) return;

    setSkills(Array.isArray(analysis.skills) ? analysis.skills : []);
    setAts(typeof analysis.ats === "object" ? analysis.ats : { ats_score: 0, matched: 0, total: 0 });
    setRoles(Array.isArray(analysis.role_recommendations) ? analysis.role_recommendations : []);
    setPlan(typeof analysis.learning_plan === "object" ? analysis.learning_plan : {});
    setProjects(Array.isArray(analysis.projects) ? analysis.projects : []);
    setMissingSkills(Array.isArray(analysis.missing_skills) ? analysis.missing_skills : []);
    setMatchPercent(typeof analysis.match_percent === "number" ? analysis.match_percent : 0);
    setSummaryText(analysis.summary_text || "");

    // Select first recommended role by default
    if (Array.isArray(analysis.role_recommendations) && analysis.role_recommendations.length > 0) {
      setSelectedRole(analysis.role_recommendations[0].title || analysis.role_recommendations[0]);
    }

    // NEW → Dynamic chart data (safe fallback)
    if (analysis.chart?.salary && Array.isArray(analysis.chart.salary)) {
      setSalaryData(analysis.chart.salary);
    }
    if (analysis.chart?.demand && Array.isArray(analysis.chart.demand)) {
      setDemandData(analysis.chart.demand);
    }
  }, [analysis]);

  const handleRoleClick = (r) => {
    const title = r.title || r;
    setSelectedRole(title);

    const el = document.getElementById("role-summary");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  };

  const percentAway = 100 - (matchPercent || 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      className="w-full max-w-6xl mx-auto py-10 px-6 relative z-10"
    >
      <h1 className="text-4xl font-semibold text-cyan-300 text-center">Your Career Analysis</h1>
      <p className="text-center text-gray-400 mt-2">{summaryText}</p>

      {/* ROLE RECOMMENDATIONS */}
      <section className="mt-10 bg-[#0f1629]/70 p-6 rounded-2xl border border-cyan-500/20">
        <h2 className="text-2xl mb-4 font-semibold text-cyan-200">Recommended Roles</h2>

        {roles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {roles.map((r, idx) => (
              <div key={r.title + idx} className={`p-6 rounded-xl bg-[#071224]/70 border ${selectedRole === r.title ? "border-cyan-400/60" : "border-white/5"}`}>
                <h3 className="text-xl text-cyan-300 mb-2">{r.title}</h3>
                <p className="text-gray-300 mb-4">{r.reason || ""}</p>

                <div className="flex items-center justify-between">
                  <div className="text-cyan-200 font-semibold text-lg">{r.readiness}% ready</div>
                  <button
                    onClick={() => handleRoleClick(r)}
                    className="py-2 px-4 rounded bg-cyan-400 text-black font-medium"
                  >
                    Select
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">Loading role recommendations...</p>
        )}
      </section>

      {/* MAIN GRID */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          
          {/* SKILL RADAR */}
          <section className="bg-[#0f1629]/70 p-6 rounded-2xl border border-purple-500/20">
            <h2 className="text-2xl mb-4 font-semibold text-purple-300">Skill Radar Chart</h2>
            {skills.length > 0 ? (
              <RadarSkillChart data={skills.map((s) => ({ skill: s, user: Math.floor(Math.random() * 5) + 1, role: Math.floor(Math.random() * 5) + 1 }))} />
            ) : <p className="text-gray-400">No skills detected yet.</p>}
          </section>

          {/* DYNAMIC MARKET INSIGHTS */}
          <section className="bg-[#0f1629]/70 p-6 rounded-2xl border border-yellow-500/20">
            <h2 className="text-2xl mb-4 font-semibold text-yellow-300">Salary & Market Demand Insights</h2>

            <SalaryTrendChart data={salaryData} />
            <DemandBarChart data={demandData} />
          </section>

          {/* PROJECTS */}
          <section className="bg-[#0f1629]/70 p-6 rounded-2xl border border-green-500/20">
            <h2 className="text-2xl mb-4 font-semibold text-green-300">Recommended Projects (Top 3)</h2>
            {projects.length > 0 ? <ProjectSuggestions projects={projects} /> : <p className="text-gray-400">Project suggestions loading...</p>}
          </section>
        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-6">
          
          {/* ATS SCORE */}
          <section className="bg-[#0f1629]/70 p-6 rounded-2xl border border-pink-500/20">
            <h2 className="text-2xl mb-4 font-semibold text-pink-300">ATS Compatibility Score</h2>
            <ATSGauge score={Number(ats.ats_score || 0)} matched={ats.matched || 0} total={ats.total || 0} />
            {ats.matched_keywords?.length > 0 && (
              <p className="mt-3 text-sm text-gray-300">Matched keywords: {ats.matched_keywords.join(", ")}</p>
            )}
          </section>

          {/* ROLE SUMMARY + LEARNING PLAN */}
          <section id="role-summary" className="bg-[#0f1629]/70 p-6 rounded-2xl border border-cyan-500/20">
            
            <h2 className="text-2xl mb-4 font-semibold text-cyan-300">Role Summary</h2>

            {selectedRole ? (
              <>
                <p className="text-gray-300">
                  Selected role: <span className="text-white font-semibold">{selectedRole}</span>
                </p>

                <p className="mt-2 text-gray-300">
                  Match: <span className="text-cyan-200 font-semibold">{matchPercent}%</span>
                </p>

                <p className="mt-2 text-gray-300">
                  You are <span className="text-yellow-300 font-semibold">{percentAway}%</span> away from your dream job.
                </p>

                {/* Missing Skills */}
                <div className="mt-4">
                  <h4 className="text-md text-gray-200 font-semibold mb-2">Missing Skills</h4>
                  {missingSkills.length > 0 ? (
                    <ul className="list-disc list-inside text-gray-300">
                      {missingSkills.map((m) => <li key={m}>{m}</li>)}
                    </ul>
                  ) : <p className="text-gray-400">No missing skills detected.</p>}
                </div>

                {/* Learning Plan Section with Heading */}
                <div className="mt-8">
                  <h3 className="text-xl font-semibold text-cyan-300 mb-3">Learning Plan</h3>

                  {/* Buttons */}
                  <div className="flex gap-3 mb-4">
                    {["30_days", "60_days", "90_days"].map((key) => (
                      <button
                        key={key}
                        onClick={() => setActiveDay(key)}
                        className={`px-4 py-2 rounded-full ${
                          activeDay === key ? "bg-cyan-400 text-black" : "bg-[#0b1120] text-gray-300"
                        }`}
                      >
                        {key.replace("_days", " Days")}
                      </button>
                    ))}
                  </div>

                  <div className="mt-4">
                    {plan?.[activeDay] ? (
                      <LearningPlan plan={plan} dayKey={activeDay} />
                    ) : (
                      <p className="text-gray-400">Learning plan not available yet.</p>
                    )}
                  </div>
                </div>
              </>
            ) : <p className="text-gray-400">No role selected — click a recommended role to see details.</p>}
          </section>
        </div>
      </div>

      {/* Export */}
      <div className="mt-10">
        <ExportButtons />
      </div>
    </motion.div>
  );
}
