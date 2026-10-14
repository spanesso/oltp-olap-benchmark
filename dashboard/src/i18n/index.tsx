import React, { createContext, useContext, useState } from "react";
import { en, type TKey } from "./translations/en";
import { es } from "./translations/es";

type Lang = "en" | "es";

const translations: Record<Lang, Record<TKey, string>> = { en, es };

interface I18nCtx {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: TKey) => string;
}

const I18nContext = createContext<I18nCtx | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    try {
      const stored = localStorage.getItem("bench_lang");
      if (stored === "en" || stored === "es") return stored;
    } catch {
      // ignore
    }
    return "es";
  });

  function setLang(l: Lang) {
    setLangState(l);
    try {
      localStorage.setItem("bench_lang", l);
    } catch {
      // ignore
    }
  }

  function t(key: TKey): string {
    return translations[lang][key] ?? en[key] ?? key;
  }

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n(): I18nCtx {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used inside I18nProvider");
  return ctx;
}
