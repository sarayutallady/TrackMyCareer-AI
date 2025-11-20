import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export default function ExportButtons() {
  const handlePDF = async () => {
    const dashboard = document.body; // FULL PAGE EXPORT

    const canvas = await html2canvas(dashboard, {
      scale: 2,
      useCORS: true,
    });

    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF("p", "mm", "a4");
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

    pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
    pdf.save("TrackMyCareerAI_Report.pdf");
  };

  return (
    <div className="flex justify-center gap-6 mt-4">
      <button
        onClick={handlePDF}
        className="px-6 py-3 rounded-xl bg-cyan-500 text-black font-semibold hover:bg-cyan-400 transition"
      >
        Download PDF
      </button>
    </div>
  );
}
