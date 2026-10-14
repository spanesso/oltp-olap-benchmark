import { useI18n } from "@/i18n";
import type { ExperimentsReport, RatioSummary } from "@domain/entities/Experiments";

interface Props {
  report: ExperimentsReport;
}

function ratio(summary: RatioSummary): string {
  return `${summary.median.toLocaleString(undefined, { maximumFractionDigits: 1 })}x`;
}

function range(summary: RatioSummary): string {
  const format = (value: number) =>
    value.toLocaleString(undefined, { maximumFractionDigits: 1 });
  return `${format(summary.min)}–${format(summary.max)}`;
}

function ms(value: number): string {
  return value.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 });
}

export function ExperimentsPanel({ report }: Props) {
  const { t } = useI18n();
  const { repeatability, method } = report;

  return (
    <div>
      <p className="experiments-intro">{t("experiments_intro")}</p>

      <h3 className="experiments-subtitle">{t("experiments_effects_title")}</h3>
      <div className="query-table-wrapper">
        <table className="query-table" aria-label={t("experiments_effects_title")}>
          <thead>
            <tr>
              <th>{t("table_col_query")}</th>
              <th className="col-number">{t("experiments_col_engine_normalized")}</th>
              <th className="col-number">{t("experiments_col_engine_star")}</th>
              <th className="col-number">{t("experiments_col_schema_postgres")}</th>
              <th className="col-number">{t("experiments_col_schema_duckdb")}</th>
              <th className="col-number">{t("experiments_col_combined")}</th>
            </tr>
          </thead>
          <tbody>
            {report.queries.map((query) => {
              const effects = [
                query.effects.engine_on_normalized,
                query.effects.engine_on_star,
                query.effects.schema_on_postgres,
                query.effects.schema_on_duckdb,
                query.effects.combined,
              ];
              return (
                <tr key={query.id}>
                  <td>
                    <strong>{query.id.split("_")[0]}</strong>
                  </td>
                  {effects.map((effect, index) => (
                    <td className="col-number" key={index}>
                      <span className="speedup-badge">{ratio(effect)}</span>
                      <div className="experiments-range">{range(effect)}</div>
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <h3 className="experiments-subtitle">{t("experiments_times_title")}</h3>
      <div className="query-table-wrapper">
        <table className="query-table" aria-label={t("experiments_times_title")}>
          <thead>
            <tr>
              <th>{t("table_col_query")}</th>
              {report.cells.map((cell) => (
                <th className="col-number" key={cell.key}>
                  {cell.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {report.queries.map((query) => (
              <tr key={query.id}>
                <td>
                  <strong>{query.id.split("_")[0]}</strong>
                </td>
                {report.cells.map((cell) => (
                  <td className="col-number" key={cell.key}>
                    {ms(query.cells[cell.key].median_ms)}
                    <div className="experiments-range">
                      CV {query.cells[cell.key].cv_percent}%
                    </div>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="experiments-note">
        {t("experiments_repeatability")
          .replace("{within}", String(repeatability.within_limit))
          .replace("{series}", String(repeatability.series))
          .replace("{limit}", String(repeatability.limit_percent))
          .replace("{repeats}", String(method.repeats))
          .replace("{worst}", String(repeatability.worst))}
      </p>
    </div>
  );
}
