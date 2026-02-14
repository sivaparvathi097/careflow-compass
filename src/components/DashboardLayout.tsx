import { Outlet } from "react-router-dom";
import { AppSidebar } from "./AppSidebar";

export function DashboardLayout({ role }: { role: "triage" | "admin" }) {
  return (
    <div className="min-h-screen bg-background">
      <AppSidebar role={role} />
      <main className="ml-64 p-6 lg:p-8">
        <Outlet />
      </main>
    </div>
  );
}
