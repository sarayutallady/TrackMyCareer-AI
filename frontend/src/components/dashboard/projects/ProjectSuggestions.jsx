// components/projects/ProjectSuggestions.jsx
export default function ProjectSuggestions({ projects = [] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {projects.map((p, idx) => (
        <div
          key={idx}
          className="p-6 rounded-2xl bg-[#071224]/70 border border-green-500/20"
        >
          <h3 className="text-xl font-semibold text-green-300">{p.title}</h3>
          <p className="text-gray-300 mt-2">{p.description}</p>

          <h4 className="text-green-400 font-semibold mt-4">Tech Stack:</h4>
          <ul className="list-disc list-inside text-gray-200 mt-1">
            {p.tech_stack && p.tech_stack.length > 0 ? (
              p.tech_stack.map((t) => <li key={t}>{t}</li>)
            ) : (
              <li>No tech stack provided.</li>
            )}
          </ul>
        </div>
      ))}
    </div>
  );
}
