import type { ReactElement } from "react";
import { render } from "@testing-library/react";
import { I18nProvider } from "../src/i18n";

// Renders a component inside the I18nProvider with a fixed language.
// The provider reads the language from localStorage, so it is set beforehand.
export function renderWithI18n(ui: ReactElement, lang: "en" | "es" = "en") {
  localStorage.setItem("bench_lang", lang);
  return render(<I18nProvider>{ui}</I18nProvider>);
}
