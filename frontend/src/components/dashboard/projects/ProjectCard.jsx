export default function ProjectCard({ title, description, stack }) {
  return (
    <div className="bg-[#0b1120] border border-green-500/20 rounded-2xl p-5 shadow-lg hover:bg-[#0f1629] transition">
      <h3 className="text-xl font-semibold text-green-300 mb-2">{title}</h3>
      <p className="text-gray-300 text-sm mb-3">{description}</p>

      <h4 className="text-green-400 font-medium mb-1">Tech Stack:</h4>
      <ul className="text-gray-300 text-sm list-disc ml-5 space-y-1">
        {stack.map((tech, index) => (
          <li key={index}>{tech}</li>
        ))}
      </ul>
    </div>
  );
}
