interface Props {
  label: string;
  value: string | number;
  unit?: string;
  accent?: string;
}

export function StatTile({ label, value, unit, accent }: Props) {
  const formatted =
    typeof value === "number" ? value.toLocaleString() : value;

  return (
    <div className="stat-tile">
      <span className="stat-label">{label}</span>
      <span className="stat-value" style={accent ? { color: accent } : undefined}>
        {formatted}
        {unit && <span className="stat-unit">{unit}</span>}
      </span>
    </div>
  );
}
