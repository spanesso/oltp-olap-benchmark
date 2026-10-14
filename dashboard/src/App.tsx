import { I18nProvider } from "@/i18n";
import { Dashboard } from "@presentation/pages/Dashboard";

export default function App() {
  return (
    <I18nProvider>
      <Dashboard />
    </I18nProvider>
  );
}
