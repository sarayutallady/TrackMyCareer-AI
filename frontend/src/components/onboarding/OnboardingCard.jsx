import { useState } from "react";
import Select from "react-select";
import axios from "axios";

export default function OnboardingCard({ onAnalyze, setIsProcessing }) {
  const [resumeText, setResumeText] = useState("");
  const [file, setFile] = useState(null);
  const [role, setRole] = useState(null);

  const roleOptions = [
    { value: "Data Analyst", label: "Data Analyst" },
    { value: "Business Analyst", label: "Business Analyst" },
    { value: "Frontend Developer", label: "Frontend Developer" },
    { value: "Backend Developer", label: "Backend Developer" },
    { value: "Full Stack Developer", label: "Full Stack Developer" },
    { value: "ML Engineer", label: "ML Engineer" },
    { value: "AI Engineer", label: "AI Engineer" },
    { value: "Data Scientist", label: "Data Scientist" },
    { value: "Cybersecurity Analyst", label: "Cybersecurity Analyst" },
    { value: "Cloud Engineer", label: "Cloud Engineer" },
    { value: "DevOps Engineer", label: "DevOps Engineer" },
    { value: "UI/UX Designer", label: "UI/UX Designer" },
    { value: "Product Manager", label: "Product Manager" },
    { value: "HR Associate", label: "HR Associate" },
    { value: "Finance Analyst", label: "Finance Analyst" },
    { value: "Marketing Specialist", label: "Marketing Specialist" },
    { value: "Other", label: "Other" },
  ];

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // ⭐ FIXED: Always send resume_text, always send file if present, always send role
  const handleSubmit = async () => {
    if (!role) return alert("Please select a target role");

    setIsProcessing(true);

    const formData = new FormData();

    // Always append resume_text (even empty)
    formData.append("resume_text", resumeText || "");

    // File overrides text when available
    if (file) {
      formData.append("resume", file);
    }

    formData.append("target_role", role.value);

    try {
      const response = await axios.post("https://trackmycareer-ai.onrender.com/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      onAnalyze(response.data);

    } catch (error) {
      console.error("ERROR:", error.response?.data || error.message);
      alert("Error analyzing resume. Check backend servers.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="w-[480px] bg-[#0f1629]/80 backdrop-blur-xl p-10 rounded-3xl shadow-2xl border border-white/10">
      <h1 className="text-3xl font-semibold text-cyan-300 text-center mb-8 tracking-wide">
        TrackMyCareer-AI
      </h1>

      {/* Upload Resume */}
      <div className="mb-6">
        <label className="block text-sm text-gray-300 mb-2">Upload Resume</label>

        <div
          className="border-2 border-dashed border-cyan-400/40 p-6 rounded-xl bg-[#0b1120]/60 
                     hover:border-cyan-300 hover:bg-[#0b1120]/80 transition cursor-pointer text-center"
          onClick={() => document.getElementById("fileInput").click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const dropped = e.dataTransfer.files[0];
            if (dropped) setFile(dropped);
          }}
        >
          <p className="text-gray-300">Drag & Drop Resume OR Click to Upload</p>

          {file && <p className="text-cyan-300 text-sm mt-2">Selected: {file.name}</p>}

          <input
            id="fileInput"
            type="file"
            className="hidden"
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
          />
        </div>
      </div>

      {/* Paste Resume */}
      <textarea
        className="w-full h-32 p-4 bg-[#0b1120] text-gray-200 rounded-xl border border-white/10 
                   focus:ring-2 focus:ring-cyan-400 outline-none transition mb-6"
        placeholder="Or paste your resume text here..."
        value={resumeText}
        onChange={(e) => setResumeText(e.target.value)}
      />

      {/* Select role */}
      <div className="mb-6">
        <Select
          options={roleOptions}
          onChange={setRole}
          placeholder="Select your target role"
          styles={{
            control: (base) => ({
              ...base,
              backgroundColor: "#0b1120",
              borderRadius: "12px",
              border: "1px solid rgba(255,255,255,0.12)",
              padding: "4px",
              color: "white",
            }),
            menu: (base) => ({ ...base, backgroundColor: "#0b1120" }),
            option: (base, state) => ({
              ...base,
              backgroundColor: state.isFocused ? "#1a2337" : "#0b1120",
              color: "white",
            }),
            singleValue: (base) => ({ ...base, color: "white", fontWeight: "500" }),
            placeholder: (base) => ({ ...base, color: "#94a3b8" }),
          }}
        />
      </div>

      <button
        onClick={handleSubmit}
        className="w-full py-4 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-xl 
                   text-white font-semibold text-lg shadow-md hover:opacity-90 transition"
      >
        Analyze My Career Path
      </button>
    </div>
  );
}
