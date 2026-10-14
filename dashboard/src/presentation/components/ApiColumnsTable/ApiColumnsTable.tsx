const API_COLUMNS = [
  { name: "unique_key",               example: "62458321",                 desc: "ID único de la queja. Nunca se repite. Es nuestra clave primaria." },
  { name: "created_date",             example: "2024-03-15T10:30:00",      desc: "Fecha y hora exacta en que el ciudadano registró la queja." },
  { name: "closed_date",              example: "2024-03-17T14:00:00",      desc: "Fecha en que se resolvió. Puede ser NULL si sigue abierta." },
  { name: "agency",                   example: "NYPD",                     desc: "Código corto de la agencia responsable (policía, sanidad, etc)." },
  { name: "agency_name",              example: "New York City Police Dept", desc: "Nombre completo de la agencia." },
  { name: "complaint_type",           example: "Noise - Residential",      desc: "Categoría de la queja. Hay ~290 tipos distintos." },
  { name: "descriptor",               example: "Loud Music/Party",         desc: "Subcategoría que detalla el tipo. Hay ~1,700 descriptores." },
  { name: "borough",                  example: "BROOKLYN",                 desc: 'Distrito de NYC. Hay 5 + "Unspecified": Manhattan, Brooklyn, Queens, Bronx, Staten Island.' },
  { name: "incident_zip",             example: "11201",                    desc: "Código postal donde ocurrió el incidente." },
  { name: "community_board",          example: "01 BROOKLYN",              desc: "Junta comunitaria local responsable del área." },
  { name: "open_data_channel_type",   example: "PHONE",                    desc: "Cómo se registró: PHONE, ONLINE, MOBILE, OTHER." },
  { name: "status",                   example: "Closed",                   desc: "Estado actual: Closed, Open, Pending, Started, etc." },
];

export function ApiColumnsTable() {
  return (
    <div>
      <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", margin: "0 0 16px" }}>
        Las 12 columnas que descargamos de la API Socrata (<code>erm2-nwe9</code>) — todas llegan como texto y se transforman en el pipeline.
      </p>
      <div className="query-table-wrapper">
        <table className="query-table">
          <thead>
            <tr>
              <th>Columna API</th>
              <th>Ejemplo real</th>
              <th>Qué significa</th>
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
                <td style={{ fontSize: "0.82rem" }}>{c.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
