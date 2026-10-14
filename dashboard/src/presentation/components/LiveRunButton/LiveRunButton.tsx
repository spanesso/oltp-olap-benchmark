import { useEffect, useState } from "react";
import { useI18n } from "@/i18n";

interface Props {
  running: boolean;
  onRun: () => void;
  runError: string | null;
}

function fmtElapsed(s: number): string {
  const m = Math.floor(s / 60);
  const sec = String(s % 60).padStart(2, "0");
  return `${m}:${sec}`;
}

export function LiveRunButton({ running, onRun, runError }: Props) {
  const [elapsed, setElapsed] = useState(0);
  const { t } = useI18n();

  useEffect(() => {
    if (!running) {
      setElapsed(0);
      return;
    }
    const id = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(id);
  }, [running]);

  return (
    <div className="live-run-wrap">
      {running ? (
        <div className="live-run-status">
          <span className="live-run-spinner" aria-hidden="true" />
          <span>
            {t("live_running")}&nbsp;
            <span className="live-run-elapsed">{fmtElapsed(elapsed)}</span>
          </span>
        </div>
      ) : (
        <button className="live-run-btn" onClick={onRun} type="button">
          <span aria-hidden="true">▶</span> {t("live_btn")}
        </button>
      )}
      <p className="live-run-hint">
        {running ? t("live_hint_running") : t("live_hint_idle")}
      </p>
      {runError && !running && (
        <p className="live-run-error">
          {runError.includes("fetch") || runError.includes("Failed to fetch")
            ? t("live_error_connect")
            : runError}
        </p>
      )}
    </div>
  );
}
