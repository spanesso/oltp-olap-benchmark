interface QueryRow {
  label: string;
  question: string;
  oltp: number;
  olap: number;
  speedup: number;
}

interface Props {
  data: QueryRow[];
}

export function QueryTable({ data }: Props) {
  return (
    <div className="query-table-wrapper">
      <table className="query-table" aria-label="Query benchmark results">
        <thead>
          <tr>
            <th>Query</th>
            <th className="col-question">Question</th>
            <th className="col-number">OLTP (ms)</th>
            <th className="col-number">OLAP (ms)</th>
            <th className="col-number">Speedup</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.label}>
              <td>
                <strong>{row.label}</strong>
              </td>
              <td className="col-question">{row.question}</td>
              <td className="col-number">{row.oltp.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</td>
              <td className="col-number">{row.olap.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</td>
              <td className="col-number">
                <span className="speedup-badge">{row.speedup.toFixed(1)}x</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
