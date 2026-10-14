import { useI18n } from "@/i18n";

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
  const { t } = useI18n();
  return (
    <div className="query-table-wrapper">
      <table className="query-table" aria-label={t("table_aria")}>
        <thead>
          <tr>
            <th>{t("table_col_query")}</th>
            <th className="col-question">{t("table_col_question")}</th>
            <th className="col-number">{t("table_col_oltp")}</th>
            <th className="col-number">{t("table_col_olap")}</th>
            <th className="col-number">{t("table_col_speedup")}</th>
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
