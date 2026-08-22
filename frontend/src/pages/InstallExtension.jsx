import PageHeader from "../components/PageHeader";
import TechnicalPanel from "../components/TechnicalPanel";

const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const steps = [
  {
    title: "Download the production zip",
    body: "Use the button below. The zip already points at the live FastAPI engine and this dashboard. Chrome cannot install an extension from a website URL — you load a local folder.",
  },
  {
    title: "Extract the folder",
    body: "Unzip so you see manifest.json inside. Do not load the zip file itself.",
  },
  {
    title: "Load unpacked",
    body: "Open chrome://extensions → turn on Developer mode → Load unpacked → select that folder. Pin PHISHEYE.",
  },
  {
    title: "Prove the gate",
    body: "Visit github.com. The gate should scan first and auto-open if LOW. A lookalike such as sbi-login.xyz stays closed. Do not open a live phishing kit.",
  },
];

export default function InstallExtension() {
  return (
    <div className="mx-auto max-w-3xl space-y-8 px-4 py-10">
      <PageHeader
        section="00 / Extension"
        title="Browser protection"
        subtitle="The main product: scan before the other site opens. Same FastAPI engine as this dashboard."
      />

      <div className="panel space-y-4 p-5">
        <p className="text-sm leading-6 text-ink-soft">
          PHISHEYE is not only a website. The Manifest V3 extension intercepts navigation, scores the URL on the gate page, auto-opens clear sites, and keeps HIGH or CRITICAL closed.
        </p>
        <a href="/phisheye-extension.zip" download className="btn-primary inline-flex px-5 py-3">
          Download PHISHEYE extension
        </a>
        <p className="meta-tech">Packaged API {apiUrl}</p>
      </div>

      {steps.map((step, index) => (
        <TechnicalPanel key={step.title} title={`${String(index + 1).padStart(2, "0")} / ${step.title}`}>
          <p className="text-sm leading-6 text-ink-soft">{step.body}</p>
        </TechnicalPanel>
      ))}

      <TechnicalPanel title="Privacy">
        <p className="text-sm leading-6 text-ink-soft">
          The extension does not read passwords, OTPs, cookies, or phone SMS. It sends the URL to the FastAPI engine. Chrome may flash a blank page on a typed address; link clicks are blocked before load.
        </p>
      </TechnicalPanel>
    </div>
  );
}
