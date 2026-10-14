import { useState } from "react";

interface Col {
  name: string;
  type: string;
  role: "PK" | "FK" | null;
}

interface Tbl {
  id: string;
  schema: string;
  name: string;
  cols: Col[];
  x: number;
  y: number;
  w?: number;
}

interface Rel {
  from: string;
  to: string;
  // which sides to connect: "right"|"left"|"top"|"bottom"
  fromSide: "left" | "right" | "top" | "bottom";
  toSide: "left" | "right" | "top" | "bottom";
}

const ROW_H = 24;
const HDR_H = 50;
const PAD_B = 8;

function tblH(t: Tbl) { return HDR_H + t.cols.length * ROW_H + PAD_B; }
function tblW(t: Tbl) { return t.w ?? 220; }
function edgeX(t: Tbl, side: "left" | "right") {
  return side === "left" ? t.x : t.x + tblW(t);
}
function edgeY(t: Tbl, side: "top" | "bottom") {
  return side === "top" ? t.y : t.y + tblH(t);
}
function midY(t: Tbl) { return t.y + tblH(t) / 2; }
function midX(t: Tbl) { return t.x + tblW(t) / 2; }

function makePath(t1: Tbl, rel: Rel, t2: Tbl): string {
  let x1: number, y1: number, x2: number, y2: number;

  if (rel.fromSide === "left" || rel.fromSide === "right") {
    x1 = edgeX(t1, rel.fromSide);
    y1 = midY(t1);
  } else {
    x1 = midX(t1);
    y1 = edgeY(t1, rel.fromSide);
  }

  if (rel.toSide === "left" || rel.toSide === "right") {
    x2 = edgeX(t2, rel.toSide);
    y2 = midY(t2);
  } else {
    x2 = midX(t2);
    y2 = edgeY(t2, rel.toSide);
  }

  const dx = Math.abs(x2 - x1);
  const dy = Math.abs(y2 - y1);

  if (rel.fromSide === "right" && rel.toSide === "right") {
    // Both right edges: go right then loop
    const ox = Math.max(x1, x2) + 60;
    return `M ${x1},${y1} C ${ox},${y1} ${ox},${y2} ${x2},${y2}`;
  }
  if (rel.fromSide === "left" && rel.toSide === "left") {
    const ox = Math.min(x1, x2) - 60;
    return `M ${x1},${y1} C ${ox},${y1} ${ox},${y2} ${x2},${y2}`;
  }
  if (rel.fromSide === "bottom" && rel.toSide === "top") {
    const cp = dy * 0.5;
    return `M ${x1},${y1} C ${x1},${y1 + cp} ${x2},${y2 - cp} ${x2},${y2}`;
  }

  // Horizontal bezier
  const cp = Math.max(60, dx * 0.5);
  const cx1 = rel.fromSide === "right" ? x1 + cp : x1 - cp;
  const cx2 = rel.toSide === "left" ? x2 - cp : x2 + cp;
  return `M ${x1},${y1} C ${cx1},${y1} ${cx2},${y2} ${x2},${y2}`;
}

// ─── OLTP ────────────────────────────────────────────────────────────────────

const OLTP_TABLES: Tbl[] = [
  {
    id: "agency", schema: "oltp", name: "agency", x: 20, y: 20,
    cols: [
      { name: "agency_id", type: "int", role: "PK" },
      { name: "code", type: "text", role: null },
      { name: "name", type: "text", role: null },
    ],
  },
  {
    id: "complaint_type", schema: "oltp", name: "complaint_type", x: 20, y: 210,
    cols: [
      { name: "complaint_type_id", type: "int", role: "PK" },
      { name: "name", type: "text", role: null },
    ],
  },
  {
    id: "complaint_descriptor", schema: "oltp", name: "complaint_descriptor", x: 20, y: 375,
    cols: [
      { name: "descriptor_id", type: "int", role: "PK" },
      { name: "complaint_type_id", type: "int", role: "FK" },
      { name: "name", type: "text", role: null },
    ],
  },
  {
    id: "service_request", schema: "oltp", name: "service_request", x: 375, y: 140, w: 265,
    cols: [
      { name: "request_id", type: "bigint", role: "PK" },
      { name: "created_at", type: "timestamp", role: null },
      { name: "closed_at", type: "timestamp", role: null },
      { name: "agency_id", type: "int", role: "FK" },
      { name: "descriptor_id", type: "int", role: "FK" },
      { name: "location_id", type: "int", role: "FK" },
      { name: "channel_id", type: "int", role: "FK" },
      { name: "status_id", type: "int", role: "FK" },
    ],
  },
  {
    id: "location", schema: "oltp", name: "location", x: 740, y: 20,
    cols: [
      { name: "location_id", type: "int", role: "PK" },
      { name: "borough_id", type: "int", role: "FK" },
      { name: "zip_code", type: "text", role: null },
      { name: "community_board", type: "text", role: null },
    ],
  },
  {
    id: "borough", schema: "oltp", name: "borough", x: 740, y: 240,
    cols: [
      { name: "borough_id", type: "int", role: "PK" },
      { name: "name", type: "text", role: null },
    ],
  },
  {
    id: "channel", schema: "oltp", name: "channel", x: 740, y: 410,
    cols: [
      { name: "channel_id", type: "int", role: "PK" },
      { name: "name", type: "text", role: null },
    ],
  },
  {
    id: "status", schema: "oltp", name: "status", x: 740, y: 570,
    cols: [
      { name: "status_id", type: "int", role: "PK" },
      { name: "name", type: "text", role: null },
    ],
  },
];

const OLTP_RELS: Rel[] = [
  { from: "service_request", to: "agency",                fromSide: "left",  toSide: "right" },
  { from: "service_request", to: "complaint_descriptor",  fromSide: "left",  toSide: "right" },
  { from: "service_request", to: "location",              fromSide: "right", toSide: "left"  },
  { from: "service_request", to: "channel",               fromSide: "right", toSide: "left"  },
  { from: "service_request", to: "status",                fromSide: "right", toSide: "left"  },
  { from: "complaint_descriptor", to: "complaint_type",   fromSide: "right", toSide: "right" },
  { from: "location",             to: "borough",          fromSide: "right", toSide: "right" },
];

// ─── OLAP ────────────────────────────────────────────────────────────────────

const OLAP_TABLES: Tbl[] = [
  {
    id: "dim_date", schema: "olap", name: "dim_date", x: 340, y: 10, w: 225,
    cols: [
      { name: "date_key", type: "int", role: "PK" },
      { name: "date", type: "date", role: null },
      { name: "year", type: "smallint", role: null },
      { name: "quarter", type: "tinyint", role: null },
      { name: "month", type: "tinyint", role: null },
      { name: "day", type: "tinyint", role: null },
      { name: "day_of_week", type: "tinyint", role: null },
      { name: "is_weekend", type: "boolean", role: null },
    ],
  },
  {
    id: "dim_complaint", schema: "olap", name: "dim_complaint", x: 20, y: 190,
    cols: [
      { name: "complaint_key", type: "int", role: "PK" },
      { name: "complaint_type", type: "varchar", role: null },
      { name: "descriptor", type: "varchar", role: null },
    ],
  },
  {
    id: "dim_agency", schema: "olap", name: "dim_agency", x: 730, y: 100,
    cols: [
      { name: "agency_key", type: "int", role: "PK" },
      { name: "code", type: "varchar", role: null },
      { name: "name", type: "varchar", role: null },
    ],
  },
  {
    id: "fact_service_request", schema: "olap", name: "fact_service_request", x: 340, y: 280, w: 265,
    cols: [
      { name: "request_id", type: "bigint", role: "PK" },
      { name: "date_key", type: "int", role: "FK" },
      { name: "agency_key", type: "int", role: "FK" },
      { name: "complaint_key", type: "int", role: "FK" },
      { name: "location_key", type: "int", role: "FK" },
      { name: "channel_key", type: "int", role: "FK" },
      { name: "status_key", type: "int", role: "FK" },
      { name: "created_at", type: "timestamp", role: null },
      { name: "created_hour", type: "tinyint", role: null },
      { name: "closed_at", type: "timestamp", role: null },
      { name: "is_closed", type: "boolean", role: null },
      { name: "resolution_hours", type: "double", role: null },
      { name: "closed_within_30d", type: "boolean", role: null },
    ],
  },
  {
    id: "dim_status", schema: "olap", name: "dim_status", x: 20, y: 510,
    cols: [
      { name: "status_key", type: "int", role: "PK" },
      { name: "name", type: "varchar", role: null },
    ],
  },
  {
    id: "dim_location", schema: "olap", name: "dim_location", x: 730, y: 380,
    cols: [
      { name: "location_key", type: "int", role: "PK" },
      { name: "borough", type: "varchar", role: null },
      { name: "zip_code", type: "varchar", role: null },
      { name: "community_board", type: "varchar", role: null },
    ],
  },
  {
    id: "dim_channel", schema: "olap", name: "dim_channel", x: 370, y: 640,
    cols: [
      { name: "channel_key", type: "int", role: "PK" },
      { name: "name", type: "varchar", role: null },
    ],
  },
];

const OLAP_RELS: Rel[] = [
  { from: "fact_service_request", to: "dim_date",      fromSide: "top",   toSide: "bottom" },
  { from: "fact_service_request", to: "dim_agency",    fromSide: "right", toSide: "left"   },
  { from: "fact_service_request", to: "dim_complaint", fromSide: "left",  toSide: "right"  },
  { from: "fact_service_request", to: "dim_location",  fromSide: "right", toSide: "left"   },
  { from: "fact_service_request", to: "dim_status",    fromSide: "left",  toSide: "right"  },
  { from: "fact_service_request", to: "dim_channel",   fromSide: "bottom", toSide: "top"   },
];

// ─── Staging ─────────────────────────────────────────────────────────────────

const STAGING_TABLES: Tbl[] = [
  {
    id: "service_request_raw", schema: "staging", name: "service_request_raw", x: 20, y: 40, w: 240,
    cols: [
      { name: "unique_key", type: "text", role: "PK" },
      { name: "created_date", type: "timestamp", role: null },
      { name: "closed_date", type: "timestamp", role: null },
      { name: "agency", type: "text", role: null },
      { name: "agency_name", type: "text", role: null },
      { name: "complaint_type", type: "text", role: null },
      { name: "descriptor", type: "text", role: null },
      { name: "borough", type: "text", role: null },
      { name: "incident_zip", type: "text", role: null },
      { name: "community_board", type: "text", role: null },
      { name: "open_data_channel_type", type: "text", role: null },
      { name: "status", type: "text", role: null },
    ],
  },
  {
    id: "ingest_checkpoint", schema: "staging", name: "ingest_checkpoint", x: 320, y: 40, w: 230,
    cols: [
      { name: "cut_start", type: "timestamp", role: "PK" },
      { name: "cut_end", type: "timestamp", role: "PK" },
      { name: "last_created_date", type: "timestamp", role: null },
      { name: "last_unique_key", type: "text", role: null },
      { name: "rows_loaded", type: "bigint", role: null },
      { name: "updated_at", type: "timestamptz", role: null },
    ],
  },
  {
    id: "rejected_row", schema: "staging", name: "rejected_row", x: 610, y: 40, w: 220,
    cols: [
      { name: "rejected_id", type: "bigint", role: "PK" },
      { name: "unique_key", type: "text", role: null },
      { name: "reason", type: "text", role: null },
      { name: "raw", type: "jsonb", role: null },
      { name: "rejected_at", type: "timestamptz", role: null },
    ],
  },
];

// ─── Rendering ───────────────────────────────────────────────────────────────

type Tab = "oltp" | "olap" | "staging";

const ACCENT: Record<Tab, string> = {
  oltp: "var(--color-oltp)",
  olap: "var(--color-olap)",
  staging: "var(--color-speedup)",
};

const PK_COLOR: Record<Tab, string> = {
  oltp: "#fbbf24",
  olap: "#fbbf24",
  staging: "#fbbf24",
};

const FK_COLOR: Record<Tab, string> = {
  oltp: "#60a5fa",
  olap: "#60a5fa",
  staging: "#60a5fa",
};

function TableBox({ t, accent, pkColor, fkColor }: { t: Tbl; accent: string; pkColor: string; fkColor: string }) {
  const w = tblW(t);
  return (
    <div
      style={{
        position: "absolute",
        left: t.x,
        top: t.y,
        width: w,
        border: `1.5px solid ${accent}`,
        borderRadius: 8,
        background: "var(--color-surface-alt)",
        fontFamily: "'SF Mono','Fira Code',monospace",
        fontSize: 11,
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div style={{ padding: "6px 10px 4px", borderBottom: `1px solid ${accent}22` }}>
        <div style={{ fontSize: 10, color: accent, opacity: 0.75, marginBottom: 1 }}>{t.schema}.</div>
        <div style={{ fontWeight: 700, fontSize: 13, color: "var(--color-text)" }}>{t.name}</div>
      </div>
      {/* Columns */}
      {t.cols.map((c) => (
        <div
          key={c.name}
          style={{
            display: "flex",
            alignItems: "center",
            padding: "0 10px",
            height: ROW_H,
            borderBottom: "1px solid var(--color-border)",
            gap: 6,
          }}
        >
          <span style={{ width: 20, fontSize: 9, fontWeight: 700, color: c.role === "PK" ? pkColor : c.role === "FK" ? fkColor : "var(--color-text-secondary)", flexShrink: 0 }}>
            {c.role ?? "·"}
          </span>
          <span style={{ flex: 1, color: c.role === "PK" ? pkColor : c.role === "FK" ? fkColor : "var(--color-text)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {c.name}
          </span>
          <span style={{ color: "var(--color-text-secondary)", fontSize: 10, flexShrink: 0 }}>{c.type}</span>
        </div>
      ))}
    </div>
  );
}

function SchemaDiagram({
  tables,
  rels,
  tab,
  canvasW,
  canvasH,
  note,
}: {
  tables: Tbl[];
  rels: Rel[];
  tab: Tab;
  canvasW: number;
  canvasH: number;
  note?: string;
}) {
  const accent = ACCENT[tab];
  const byId = Object.fromEntries(tables.map((t) => [t.id, t]));

  return (
    <div style={{ overflowX: "auto", overflowY: "visible" }}>
      <div style={{ position: "relative", width: canvasW, height: canvasH, minWidth: canvasW }}>
        {/* SVG lines */}
        <svg
          style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
          width={canvasW}
          height={canvasH}
        >
          {rels.map((r, i) => {
            const f = byId[r.from];
            const t = byId[r.to];
            if (!f || !t) return null;
            return (
              <path
                key={i}
                d={makePath(f, r, t)}
                fill="none"
                stroke={accent}
                strokeWidth={1.5}
                strokeDasharray="6 3"
                opacity={0.65}
              />
            );
          })}
        </svg>
        {/* Table boxes */}
        {tables.map((t) => (
          <TableBox key={t.id} t={t} accent={accent} pkColor={PK_COLOR[tab]} fkColor={FK_COLOR[tab]} />
        ))}
      </div>
      {note && (
        <p style={{ fontSize: "0.75rem", color: "var(--color-text-secondary)", textAlign: "center", margin: "12px 0 0", fontStyle: "italic" }}>
          {note}
        </p>
      )}
    </div>
  );
}

// ─── Legend ──────────────────────────────────────────────────────────────────

function Legend() {
  return (
    <div style={{ display: "flex", gap: 20, flexWrap: "wrap", marginBottom: 16, fontSize: "0.78rem", color: "var(--color-text-secondary)" }}>
      <span><strong style={{ color: "#fbbf24" }}>PK</strong> — clave primaria</span>
      <span><strong style={{ color: "#60a5fa" }}>FK</strong> — clave foránea</span>
      <span><strong>·</strong> columna regular</span>
      <span style={{ borderTop: "2px dashed var(--color-text-secondary)", display: "inline-block", width: 28, verticalAlign: "middle", marginRight: 4 }} /> relación 1→N
    </div>
  );
}

// ─── Main export ─────────────────────────────────────────────────────────────

const TABS: { id: Tab; label: string }[] = [
  { id: "oltp", label: "OLTP (PostgreSQL 3NF)" },
  { id: "olap", label: "OLAP — Star Schema (DuckDB)" },
  { id: "staging", label: "Staging" },
];

export function SchemaViewer() {
  const [active, setActive] = useState<Tab>("oltp");

  return (
    <div>
      {/* Tab bar */}
      <div style={{ display: "flex", gap: 0, borderBottom: "2px solid var(--color-border)", marginBottom: 20 }}>
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setActive(t.id)}
            style={{
              background: "none",
              border: "none",
              borderBottom: active === t.id ? `2px solid ${ACCENT[t.id]}` : "2px solid transparent",
              marginBottom: -2,
              padding: "8px 20px",
              cursor: "pointer",
              fontWeight: active === t.id ? 700 : 400,
              fontSize: "0.875rem",
              color: active === t.id ? ACCENT[t.id] : "var(--color-text-secondary)",
              transition: "color 0.15s",
              whiteSpace: "nowrap",
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      <Legend />

      {active === "oltp" && (
        <SchemaDiagram
          tables={OLTP_TABLES}
          rels={OLTP_RELS}
          tab="oltp"
          canvasW={980}
          canvasH={690}
        />
      )}
      {active === "olap" && (
        <SchemaDiagram
          tables={OLAP_TABLES}
          rels={OLAP_RELS}
          tab="olap"
          canvasW={980}
          canvasH={760}
          note="Esquema estrella — fact_service_request en el centro · 6 dimensiones radiales"
        />
      )}
      {active === "staging" && (
        <SchemaDiagram
          tables={STAGING_TABLES}
          rels={[]}
          tab="staging"
          canvasW={860}
          canvasH={430}
          note="Las tablas de staging no tienen relaciones entre sí — cada una es independiente"
        />
      )}
    </div>
  );
}
