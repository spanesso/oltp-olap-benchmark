import { useI18n } from "@/i18n";
import type { TKey } from "@/i18n/translations/en";

const API_COLUMNS: { name: string; example: string; descKey: TKey }[] = [
  { name: "unique_key",               example: "62458321",                  descKey: "api_unique_key" },
  { name: "created_date",             example: "2024-03-15T10:30:00",       descKey: "api_created_date" },
  { name: "closed_date",              example: "2024-03-17T14:00:00",       descKey: "api_closed_date" },
  { name: "agency",                   example: "NYPD",                      descKey: "api_agency" },
  { name: "agency_name",              example: "New York City Police Dept", descKey: "api_agency_name" },
  { name: "complaint_type",           example: "Noise - Residential",       descKey: "api_complaint_type" },
  { name: "descriptor",               example: "Loud Music/Party",          descKey: "api_descriptor" },
  { name: "borough",                  example: "BROOKLYN",                  descKey: "api_borough" },
  { name: "incident_zip",             example: "11201",                     descKey: "api_incident_zip" },
  { name: "community_board",          example: "01 BROOKLYN",               descKey: "api_community_board" },
  { name: "open_data_channel_type",   example: "PHONE",                     descKey: "api_open_data_channel_type" },
  { name: "status",                   example: "Closed",                    descKey: "api_status" },
];

export function ApiColumnsTable() {
  const { t } = useI18n();
  return (
    <div>
      <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", margin: "0 0 16px" }}>
        Socrata API (<code>erm2-nwe9</code>) — all columns arrive as text and are transformed in the pipeline.
      </p>
      <div className="query-table-wrapper">
        <table className="query-table">
          <thead>
            <tr>
              <th>{t("api_col_name")}</th>
              <th>{t("api_col_example")}</th>
              <th>{t("api_col_desc")}</th>
            </tr>
          </thead>
          <tbody>
            {API_COLUMNS.map((c) => (
              <tr key={c.name}>
                <td>
                  <code style={{ fontSize: "0.78rem", background: "var(--color-code-bg)", padding: "1px 5px", borderRadius: 3 }}>
                    {c.name}
                  </code>
                </td>
                <td style={{ fontFamily: "'SF Mono','Fira Code',monospace", fontSize: "0.78rem", color: "var(--color-olap)", whiteSpace: "nowrap" }}>
                  {c.example}
                </td>
                <td style={{ fontSize: "0.82rem" }}>{t(c.descKey)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
