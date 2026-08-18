import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { NegotiationDraftProvider } from './lib/negotiation-draft-context';
import { UploadedDataProvider } from './lib/uploaded-data-context';
import { AnalyticsPage, UploadedAnalyticsPage } from './pages/AnalyticsPage';
import { CaseFilePage } from './pages/CaseFilePage';
import { CasesPage } from './pages/CasesPage';
import { HomePage } from './pages/HomePage';
import { NegotiatePage } from './pages/NegotiatePage';

function App() {
  return (
    <UploadedDataProvider>
      <NegotiationDraftProvider>
        <BrowserRouter>
          <AppShell>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/negotiate" element={<NegotiatePage />} />
              <Route path="/cases" element={<CasesPage />} />
              <Route path="/case/:caseId" element={<CaseFilePage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/analytics/uploaded" element={<UploadedAnalyticsPage />} />
            </Routes>
          </AppShell>
        </BrowserRouter>
      </NegotiationDraftProvider>
    </UploadedDataProvider>
  );
}

export default App;
