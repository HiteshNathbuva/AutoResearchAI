import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ResearchProvider } from "./context/ResearchContext";
import MainLayout from "./layouts/MainLayout";
import Home from "./pages/Home";
import History from "./pages/History";
import Reports from "./pages/Reports";
import ReportDetail from "./pages/ReportDetail";
import KnowledgeHub from "./pages/KnowledgeHub";

export default function App() {
  return <BrowserRouter><ResearchProvider><MainLayout><Routes>
    <Route path="/" element={<Home />} /><Route path="/reports" element={<Reports />} />
    <Route path="/reports/:sessionId" element={<ReportDetail />} /><Route path="/history" element={<History />} />
    <Route path="/knowledge" element={<KnowledgeHub />} /><Route path="*" element={<Home />} />
  </Routes></MainLayout></ResearchProvider></BrowserRouter>;
}
