import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeImage, getErrorMessage } from "../services/api";
import { saveLastScan } from "../utils/risk";

const MAX_BYTES = 5_000_000;

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ScreenshotUploader({ mode = "screenshot", compact = false }) {
  const isQr = mode === "qr";
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [hint, setHint] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [drag, setDrag] = useState(false);
  const inputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  const takeFile = (next) => {
    if (!next) return;
    const namedImage = /\.(png|jpe?g|webp|gif|bmp|heic|heif)$/i.test(next.name || "");
    const typedImage = !next.type || next.type.startsWith("image/") || next.type === "application/octet-stream";
    if (!typedImage && !namedImage) {
      setError("Choose a PNG, JPG, WEBP, or GIF image.");
      return;
    }
    if (next.size > MAX_BYTES) {
      setError("Image is too large (max 5 MB).");
      return;
    }
    setError("");
    setFile(next);
    setPreview((old) => {
      if (old) URL.revokeObjectURL(old);
      return URL.createObjectURL(next);
    });
  };

  const onDrop = (event) => {
    event.preventDefault();
    setDrag(false);
    takeFile(event.dataTransfer.files?.[0]);
  };

  const onPaste = (event) => {
    const item = [...(event.clipboardData?.items || [])].find((entry) => entry.type.startsWith("image/"));
    if (item) {
      event.preventDefault();
      takeFile(item.getAsFile());
    }
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError(isQr ? "Choose a QR image first." : "Choose a screenshot first.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const { data } = await analyzeImage(isQr ? "/api/v1/analyze/qr" : "/api/v1/analyze/screenshot", file, hint);
      saveLastScan(data);
      navigate("/scan-result");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} className={compact ? "" : "w-full"} onPaste={onPaste}>
      <div className="panel p-4">
        <p className="label-tech">{isQr ? "QR image" : "Screenshot"}</p>
        <p className="mt-2 text-sm text-muted">
          {isQr
            ? "Upload a photo of a QR code. PHISHEYE decodes the URL, then scores it. The image is not stored."
            : "Upload a WhatsApp, SMS, email, or website screenshot. PHISHEYE looks for QR codes and visible links. The image is not stored."}
        </p>

        <div
          className={`relative mt-4 flex min-h-[180px] cursor-pointer flex-col items-center justify-center overflow-hidden border border-dashed px-4 py-6 text-center ${
            drag ? "border-accent bg-[var(--nav-active)]" : "border-line bg-surface-2"
          }`}
          onDragOver={(event) => {
            event.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={onDrop}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*,.png,.jpg,.jpeg,.webp,.gif,.bmp"
            className="absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0"
            onChange={(event) => {
              takeFile(event.target.files?.[0] || null);
              event.target.value = "";
            }}
          />
          {preview ? (
            <img src={preview} alt="Selected screenshot preview" className="relative z-0 max-h-48 w-auto max-w-full border border-line object-contain" />
          ) : (
            <>
              <p className="font-display text-sm uppercase tracking-[0.14em] text-ink">
                {isQr ? "Drop QR image here" : "Drop screenshot here"}
              </p>
              <p className="mt-2 text-xs text-muted">PNG JPG WEBP GIF · max 5 MB · or paste with Ctrl+V</p>
              <button
                type="button"
                className="btn-secondary relative z-20 mt-4 px-4 py-2"
                onClick={(event) => {
                  event.preventDefault();
                  event.stopPropagation();
                  inputRef.current?.click();
                }}
              >
                {isQr ? "Choose QR image" : "Choose screenshot"}
              </button>
            </>
          )}
        </div>

        {file ? (
          <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border border-line px-3 py-2">
            <p className="truncate font-mono text-xs text-ink-soft">
              {file.name} · {formatSize(file.size)}
            </p>
            <button
              type="button"
              className="btn-secondary px-3 py-1 text-xs"
              onClick={() => {
                setFile(null);
                setPreview((old) => {
                  if (old) URL.revokeObjectURL(old);
                  return "";
                });
                if (inputRef.current) inputRef.current.value = "";
              }}
            >
              Remove
            </button>
          </div>
        ) : null}

        {!isQr ? (
          <>
            <label htmlFor="screenshot-hint" className="mt-4 block label-tech">
              Link shown in the screenshot (optional)
            </label>
            <input
              id="screenshot-hint"
              value={hint}
              onChange={(event) => setHint(event.target.value)}
              placeholder="https://…"
              className="field field-mono mt-2 w-full"
            />
            <p className="mt-2 text-xs text-muted">
              If the screenshot has a URL in the address bar or message, paste it here so analysis can still run when OCR is unavailable.
            </p>
          </>
        ) : null}

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-line pt-4">
          <p className="flex items-center gap-2 text-xs uppercase tracking-[0.12em] text-muted">
            <span className={`dot ${loading ? "dot-critical scan-pulse" : file ? "dot-active" : "dot-inactive"}`} aria-hidden="true" />
            {loading ? "Analyzing" : file ? "Ready" : "Awaiting image"}
          </p>
          <button type="submit" disabled={loading} className="btn-primary px-5 py-2.5">
            {loading ? "Analyze" : isQr ? "Analyze QR" : "Analyze screenshot"}
          </button>
        </div>
      </div>
      {error ? (
        <div className="mt-3 panel border border-[rgba(255,0,0,0.35)] p-3">
          <p className="flex items-center gap-2 text-sm text-[var(--risk-high)]">
            <span className="dot dot-critical" aria-hidden="true" />
            {error}
          </p>
        </div>
      ) : null}
    </form>
  );
}
