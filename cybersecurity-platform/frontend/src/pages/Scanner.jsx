import UrlScanner from "../components/UrlScanner";
import PageHeader from "../components/PageHeader";

export default function Scanner() {
  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <PageHeader
        section="02 / Scan URL"
        title="Analyze target"
        subtitle="Enter a website URL for security analysis."
      />
      <UrlScanner />
    </div>
  );
}
