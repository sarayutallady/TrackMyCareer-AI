import { motion } from "framer-motion";

export default function IntroSection({ onStart }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1 }}
      className="text-center px-6 max-w-3xl mx-auto"
    >

      {/* MAIN TITLE WITH NEON GLOW */}
      <h1
        className="
          text-5xl font-bold text-cyan-300 mb-8
          drop-shadow-[0_0_20px_rgba(0,255,255,0.75)]
        "
      >
        TrackMyCareer-AI
      </h1>

      {/* DESCRIPTION WITH BLUR + GLOW */}
      <p
        className="
          text-lg text-gray-200 mb-10 leading-relaxed 
          px-6 py-5 rounded-xl

          bg-white/5                /* frosted glass layer */
          backdrop-blur-md          /* BLUR EFFECT */

          drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]
          drop-shadow-[0_0_22px_rgba(0,255,255,0.7)]
        "
      >
        Your AI-powered career partner that analyzes your resume, identifies
        your skill gaps, and builds a personalized roadmap to help you reach
        your dream job faster.
      </p>

      {/* BUTTON WITH NEON GLOW */}
      <button
        onClick={onStart}
        className="
          px-10 py-3 rounded-xl font-semibold text-lg 
          bg-cyan-600 hover:bg-cyan-500 transition-all

          shadow-[0_0_20px_rgba(0,255,255,0.65)]
          hover:shadow-[0_0_35px_rgba(0,255,255,1)]
        "
      >
        Get Started
      </button>
    </motion.div>
  );
}
