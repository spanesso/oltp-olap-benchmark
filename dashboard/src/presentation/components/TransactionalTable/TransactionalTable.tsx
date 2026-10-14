import { useI18n } from "@/i18n";
import type { QueryResult } from "@domain/entities/BenchmarkResult";

interface Props {
  operations: QueryResult[];
}

function ms(value: number): string {
  return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// speedup = OLTP time / OLAP time, so a value below 1 means the transactional model wins.
function winner(speedup: number, t: (key: "tx_winner_oltp" | "tx_winner_olap") => string): string {
  const times = speedup < 1 ? 1 / speedup : speedup;
  const name = speedup < 1 ? t("tx_winner_oltp") : t("tx_winner_olap");
  return `${name}, ${times.toLocaleString(undefined, { maximumFractionDigits: 1 })}x`;
}

export function TransactionalTable({ operations }: Props) {
  const { t } = useI18n();

  return (
    <div>
      <p className="experiments-intro">{t("tx_intro")}</p>
      <div className="query-table-wrapper">
        <table className="query-table" aria-label={t("tx_title")}>
          <thead>
            <tr>
              <th>{t("tx_col_operation")}</th>
              <th className="col-number">{t("table_col_oltp")}</th>
              <th className="col-number">{t("table_col_olap")}</th>
              <th className="col-number">{t("tx_col_winner")}</th>
            </tr>
          </thead>
          <tbody>
            {operations.map((operation) => (
              <tr key={operation.id}>
                <td>
                  <strong>{operation.id.split("_")[0]}</strong> {operation.question}
                </td>
                <td className="col-number">{ms(operation.oltp.median_ms)}</td>
                <td className="col-number">{ms(operation.olap.median_ms)}</td>
                <td className="col-number">
                  <span className="speedup-badge">{winner(operation.speedup, t)}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
