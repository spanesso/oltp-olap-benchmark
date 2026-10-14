import React from "react";
import { useI18n } from "@/i18n";

export function LanguageToggle() {
  const { lang, setLang, t } = useI18n();

  return (
    <div style={{ display: "flex", gap: 4 }}>
      <button
        onClick={() => setLang("es")}
        style={{
          padding: "4px 10px",
          borderRadius: 6,
          border: "1px solid var(--border)",
          background: lang === "es" ? "var(--color-speedup)" : "transparent",
          color: lang === "es" ? "#fff" : "var(--text-muted)",
          fontWeight: lang === "es" ? 700 : 400,
          cursor: "pointer",
          fontSize: 13,
          transition: "all 0.15s",
        }}
        aria-pressed={lang === "es"}
      >
        {t("lang_es")}
      </button>
      <button
        onClick={() => setLang("en")}
        style={{
          padding: "4px 10px",
          borderRadius: 6,
          border: "1px solid var(--border)",
          background: lang === "en" ? "var(--color-speedup)" : "transparent",
          color: lang === "en" ? "#fff" : "var(--text-muted)",
          fontWeight: lang === "en" ? 700 : 400,
          cursor: "pointer",
          fontSize: 13,
          transition: "all 0.15s",
        }}
        aria-pressed={lang === "en"}
      >
        {t("lang_en")}
      </button>
    </div>
  );
}
