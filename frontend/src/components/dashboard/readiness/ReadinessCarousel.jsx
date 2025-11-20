import Slider from "react-slick";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

export default function ReadinessCarousel({ roles }) {
  const settings = {
    dots: false,
    infinite: true,
    speed: 500,
    slidesToShow: 2,
    slidesToScroll: 1,
    arrows: true,
  };

  return (
    <Slider {...settings}>
      {roles.map((role, index) => (
        <div key={index} className="px-3">
          <div className="bg-[#0b1120] border border-cyan-500/20 rounded-2xl p-6 shadow-lg hover:bg-[#0f1630] transition">
            <h3 className="text-xl font-semibold text-cyan-300 mb-4">
              {role.title}
            </h3>

            <div className="w-32 mx-auto">
              <CircularProgressbar
                value={role.score}
                text={`${role.score}%`}
                styles={buildStyles({
                  textColor: "#22d3ee",
                  pathColor: "#22d3ee",
                  trailColor: "#1e293b",
                })}
              />
            </div>

            <button className="mt-6 w-full py-2 rounded-xl bg-cyan-500 text-black font-semibold hover:bg-cyan-400 transition">
              View Full Plan
            </button>
          </div>
        </div>
      ))}
    </Slider>
  );
}
