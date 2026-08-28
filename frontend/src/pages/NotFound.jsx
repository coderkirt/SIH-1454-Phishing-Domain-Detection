import { Link } from "react-router-dom";
import DotMatrixLogo from "../components/DotMatrixLogo";

export default function NotFound() {
  return (
    <div className="grid min-h-screen place-items-center bg-page px-4 text-center">
      <div>
        <DotMatrixLogo className="mx-auto" />
        <p className="mt-6 label-tech">System error</p>
        <p className="mt-2 font-mono text-4xl text-ink">404</p>
        <h1 className="mt-4 font-display text-3xl font-semibold uppercase text-ink">Resource not found</h1>
        <p className="mt-2 text-muted">That path does not exist in PHISHEYE.</p>
        <Link to="/dashboard" className="btn-primary mt-8 inline-flex px-5 py-3">Return to dashboard</Link>
      </div>
    </div>
  );
}
