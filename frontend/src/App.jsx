import { useState } from "react";
import Background3D from "./components/layout/Background3D.jsx";
import IntroSection from "./components/landing/IntroSection.jsx";
import OnboardingCard from "./components/onboarding/OnboardingCard.jsx";
import Dashboard from "./components/dashboard/Dashboard.jsx";

export default function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showIntro, setShowIntro] = useState(true);
  const [analysis, setAnalysis] = useState(null);

  const handleAnalyze = (data) => {
    setIsProcessing(false);
    setAnalysis(data);
    setShowIntro(false);
  };

  return (
    <div className="relative text-white min-h-screen">
      <Background3D />

      {/* ⭐ FIXED: Centered UI for Start Page & Onboarding Page */}
      <div className="relative z-20 flex items-center justify-center min-h-screen">
        {showIntro ? (
          <IntroSection onStart={() => setShowIntro(false)} />
        ) : !analysis ? (
          <OnboardingCard 
            onAnalyze={handleAnalyze} 
            setIsProcessing={setIsProcessing} 
          />
        ) : (
          <Dashboard analysis={analysis} />
        )}
      </div>
    </div>
  );
}
