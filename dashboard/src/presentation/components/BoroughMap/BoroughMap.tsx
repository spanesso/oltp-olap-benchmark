import { useEffect, useRef, useState } from "react";

// Static fallback data — approximate distribution from the 5M-row full profile.
// Used when the API server is not running.
const STATIC_BOROUGH_DATA: BoroughStat[] = [
  { borough: "BROOKLYN",     count: 1_280_000 },
  { borough: "QUEENS",       count: 1_140_000 },
  { borough: "MANHATTAN",    count: 850_000 },
  { borough: "BRONX",        count: 670_000 },
  { borough: "STATEN ISLAND",count: 210_000 },
];

const CENTROIDS: Record<string, { lat: number; lng: number }> = {
  "BROOKLYN":      { lat: 40.6782, lng: -73.9442 },
  "QUEENS":        { lat: 40.7282, lng: -73.7949 },
  "MANHATTAN":     { lat: 40.7831, lng: -73.9712 },
  "BRONX":         { lat: 40.8448, lng: -73.8648 },
  "STATEN ISLAND": { lat: 40.5795, lng: -74.1502 },
};

const NYC_CENTER = { lat: 40.7128, lng: -74.006 };

interface BoroughStat {
  borough: string;
  count: number;
}

declare global {
  interface Window {
    google: typeof google;
    _gmapsLoaded?: () => void;
  }
}

function loadGoogleMaps(apiKey: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.google?.maps) { resolve(); return; }
    const existing = document.getElementById("gmaps-script");
    if (existing) { existing.addEventListener("load", () => resolve()); return; }
    window._gmapsLoaded = resolve;
    const script = document.createElement("script");
    script.id = "gmaps-script";
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=_gmapsLoaded`;
    script.async = true;
    script.onerror = () => reject(new Error("Failed to load Google Maps script"));
    document.head.appendChild(script);
  });
}

const BOROUGH_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#3b82f6", "#ec4899"];

const ENV_KEY = (import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string | undefined) ?? "";

export function BoroughMap() {
  const mapRef = useRef<HTMLDivElement>(null);
  const [apiKey, setApiKey] = useState(() => {
    if (ENV_KEY) return ENV_KEY;
    try { return localStorage.getItem("gmaps_api_key") ?? ""; } catch { return ""; }
  });
  const [keyDraft, setKeyDraft] = useState(apiKey);
  const [boroughData, setBoroughData] = useState<BoroughStat[] | null>(null);
  const [usingFallback, setUsingFallback] = useState(false);
  const [mapError, setMapError] = useState<string | null>(null);

  // Fetch borough stats from the API server (or fall back to static data)
  useEffect(() => {
    fetch("http://localhost:8788/api/borough-stats")
      .then((r) => r.json())
      .then((d: { boroughs: BoroughStat[] }) => {
        setBoroughData(d.boroughs);
        setUsingFallback(false);
      })
      .catch(() => {
        setBoroughData(STATIC_BOROUGH_DATA);
        setUsingFallback(true);
      });
  }, []);

  // Initialize the map once we have a key and data
  useEffect(() => {
    if (!apiKey || !boroughData || !mapRef.current) return;

    loadGoogleMaps(apiKey)
      .then(() => {
        if (!mapRef.current) return;
        const map = new window.google.maps.Map(mapRef.current, {
          center: NYC_CENTER,
          zoom: 10,
          mapTypeId: "roadmap",
          disableDefaultUI: false,
          styles: [
            { featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }] },
          ],
        });

        const maxCount = Math.max(...boroughData.map((b) => b.count));

        boroughData.forEach((stat, i) => {
          const pos = CENTROIDS[stat.borough];
          if (!pos) return;

          // Circle radius proportional to complaint count (max ~18km² = r ~2400m)
          const radius = 800 + (stat.count / maxCount) * 9000;
          const color = BOROUGH_COLORS[i % BOROUGH_COLORS.length];

          const circle = new window.google.maps.Circle({
            map,
            center: pos,
            radius,
            fillColor: color,
            fillOpacity: 0.35,
            strokeColor: color,
            strokeOpacity: 0.8,
            strokeWeight: 2,
          });

          const label = new window.google.maps.Marker({
            map,
            position: pos,
            label: {
              text: `${stat.borough}\n${(stat.count / 1_000).toFixed(0)}K`,
              color: "#ffffff",
              fontSize: "11px",
              fontWeight: "bold",
            },
            icon: {
              path: window.google.maps.SymbolPath.CIRCLE,
              scale: 0,
            },
          });

          const infoContent = `
            <div style="font-family:system-ui;padding:8px 4px">
              <strong>${stat.borough}</strong><br/>
              ${stat.count.toLocaleString()} complaints
              ${usingFallback ? "<br/><em style='color:#888;font-size:11px'>approximate — run API server for live data</em>" : ""}
            </div>`;
          const infoWindow = new window.google.maps.InfoWindow({ content: infoContent });
          circle.addListener("click", () => infoWindow.open({ map, anchor: label }));
        });
      })
      .catch((err: Error) => setMapError(err.message));
  }, [apiKey, boroughData, usingFallback]);

  function saveKey() {
    const k = keyDraft.trim();
    try { localStorage.setItem("gmaps_api_key", k); } catch { /* */ }
    setApiKey(k);
  }

  if (!apiKey) {
    return (
      <div className="borough-map-prompt">
        <div className="borough-map-prompt-inner">
          <div style={{ fontSize: "2rem", marginBottom: 12 }}>🗺️</div>
          <h3 style={{ margin: "0 0 8px", fontSize: "1rem" }}>Google Maps API Key required</h3>
          <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", margin: "0 0 16px" }}>
            Paste your key to see the NYC complaint map by borough. The key is stored only in
            your browser's localStorage, never sent anywhere except to maps.googleapis.com.
          </p>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              type="text"
              placeholder="AIzaSy..."
              value={keyDraft}
              onChange={(e) => setKeyDraft(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && saveKey()}
              className="map-key-input"
            />
            <button className="map-key-btn" onClick={saveKey} disabled={!keyDraft.trim()}>
              Load map
            </button>
          </div>
          <p style={{ fontSize: "0.72rem", color: "var(--color-text-secondary)", margin: "12px 0 0" }}>
            Get a free key at{" "}
            <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noreferrer"
              style={{ color: "var(--color-olap)" }}>
              Google Cloud Console
            </a>{" "}
            — enable the Maps JavaScript API.
          </p>
        </div>
      </div>
    );
  }

  if (mapError) {
    return (
      <div className="borough-map-error">
        <p>Failed to load Google Maps: {mapError}</p>
        <button className="map-key-btn" onClick={() => { setApiKey(""); setKeyDraft(""); try { localStorage.removeItem("gmaps_api_key"); } catch { /* */ } }}>
          Reset key
        </button>
      </div>
    );
  }

  return (
    <div>
      {usingFallback && (
        <p className="borough-map-fallback-note">
          ℹ️ Showing approximate borough data. Run <code>make api</code> for live complaint counts from DuckDB.
        </p>
      )}
      <div className="borough-map-wrap">
        <div ref={mapRef} className="borough-map-canvas" />
        {boroughData && (
          <div className="borough-map-legend">
            <div style={{ fontSize: "0.72rem", fontWeight: 600, marginBottom: 8, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Complaints
            </div>
            {[...boroughData]
              .sort((a, b) => b.count - a.count)
              .map((s, i) => (
                <div key={s.borough} className="borough-map-legend-row">
                  <span
                    className="borough-map-dot"
                    style={{ background: BOROUGH_COLORS[boroughData.indexOf(s) % BOROUGH_COLORS.length] }}
                  />
                  <span className="borough-map-legend-name">{s.borough}</span>
                  <span className="borough-map-legend-count">
                    {(s.count / 1_000).toFixed(0)}K
                  </span>
                </div>
              ))}
            {!ENV_KEY && (
              <button
                className="map-reset-key"
                onClick={() => { setApiKey(""); setKeyDraft(""); try { localStorage.removeItem("gmaps_api_key"); } catch { /* */ } }}
              >
                Change key
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
