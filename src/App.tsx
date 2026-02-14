import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PatientProvider } from "@/contexts/PatientContext";
import { DashboardLayout } from "@/components/DashboardLayout";
import LoginPage from "./pages/LoginPage";
import NotFound from "./pages/NotFound";
import TriageDashboard from "./pages/triage/TriageDashboard";
import UploadPatient from "./pages/triage/UploadPatient";
import RealtimePatients from "./pages/triage/RealtimePatients";
import Analysis from "./pages/triage/Analysis";
import DepartmentView from "./pages/triage/DepartmentView";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminDepartments from "./pages/admin/AdminDepartments";
import AdminTrends from "./pages/admin/AdminTrends";
import AdminAlerts from "./pages/admin/AdminAlerts";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <PatientProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LoginPage />} />

            <Route path="/triage" element={<DashboardLayout role="triage" />}>
              <Route path="dashboard" element={<TriageDashboard />} />
              <Route path="upload" element={<UploadPatient />} />
              <Route path="realtime" element={<RealtimePatients />} />
              <Route path="analysis" element={<Analysis />} />
              <Route path="department" element={<DepartmentView />} />
            </Route>

            <Route path="/admin" element={<DashboardLayout role="admin" />}>
              <Route path="dashboard" element={<AdminDashboard />} />
              <Route path="departments" element={<AdminDepartments />} />
              <Route path="trends" element={<AdminTrends />} />
              <Route path="alerts" element={<AdminAlerts />} />
            </Route>

            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </PatientProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
