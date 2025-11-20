// frontend/src/utils/skillsConfig.js
// Lightweight skills utility helpers for frontend.
// This is NOT a static role->skills map (you wanted unlimited roles).
// Use this for normalizing and basic client-side categorization.

export function normalizeSkill(skill) {
  if (!skill) return "";
  return String(skill).trim();
}

export function prettySkill(skill) {
  if (!skill) return "";
  // Keep capitalization more readable for display
  return String(skill)
    .split(/[\s-_]+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

/** Basic heuristic categories (same as backend heuristics) */
export function categorizeSkill(skill) {
  if (!skill) return "technical";
  const s = skill.toLowerCase();
  const tools = ["docker","kubernetes","git","github","jira","tableau","power bi","excel","aws","gcp","azure"];
  const soft = ["communication","leadership","teamwork","presentation","negotiation"];
  const domain = ["marketing","finance","healthcare","sales","product","operations"];

  for (const t of tools) {
    if (s.includes(t)) return "tools";
  }
  for (const so of soft) {
    if (s.includes(so)) return "soft";
  }
  for (const d of domain) {
    if (s.includes(d)) return "domain";
  }
  return "technical";
}

/** Format a percent safely */
export function formatPercent(n) {
  if (n === null || n === undefined || isNaN(n)) return "—";
  return `${Math.round(n)}%`;
}

export default {
  normalizeSkill,
  prettySkill,
  categorizeSkill,
  formatPercent,
};
