import { useEffect, useState } from "react";

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
            Midiendo 6 queries × 2 motores&hellip;&nbsp;
            <span className="live-run-elapsed">{fmtElapsed(elapsed)}</span>
          </span>
        </div>
      ) : (
        <button className="live-run-btn" onClick={onRun} type="button">
          <span aria-hidden="true">▶</span> Actualizar medición en vivo
        </button>
      )}
      <p className="live-run-hint">
        {running
          ? "Espera — esto puede tardar ~3 min con el perfil full"
          : "Requiere: python dashboard/api_server.py · ~3 min"}
      </p>
      {runError && !running && (
        <p className="live-run-error">
          {runError.includes("fetch") || runError.includes("Failed to fetch")
            ? "No se pudo conectar al servidor. Ejecuta: python dashboard/api_server.py"
            : runError}
        </p>
      )}
    </div>
  );
}
