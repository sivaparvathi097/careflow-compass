import { useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Upload, Activity, Building2,
  TrendingUp, AlertTriangle, Heart, LogOut,
} from "lucide-react";

interface SidebarItem {
  label: string;
  path: string;
  icon: React.ElementType;
}

const triageItems: SidebarItem[] = [
  { label: "Main Dashboard", path: "/triage/dashboard", icon: LayoutDashboard },
  { label: "Upload Patient Data", path: "/triage/upload", icon: Upload },
  { label: "Real-Time Patient Data", path: "/triage/realtime", icon: Activity },
];

const adminItems: SidebarItem[] = [
  { label: "Overview", path: "/admin/dashboard", icon: LayoutDashboard },
  { label: "Departments", path: "/admin/departments", icon: Building2 },
  { label: "Disease Trends", path: "/admin/trends", icon: TrendingUp },
  { label: "Risk & Alerts", path: "/admin/alerts", icon: AlertTriangle },
];

export function AppSidebar({ role }: { role: "triage" | "admin" }) {
  const location = useLocation();
  const navigate = useNavigate();
  const items = role === "triage" ? triageItems : adminItems;

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col bg-sidebar text-sidebar-foreground border-r border-sidebar-border">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-sidebar-border">
        <Heart className="h-7 w-7 text-sidebar-primary" />
        <div>
          <h1 className="text-lg font-bold text-sidebar-primary-foreground">CareFlow AI</h1>
          <p className="text-xs text-sidebar-foreground/60 capitalize">{role} Staff</p>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-thin">
        {items.map((item) => {
          const active = location.pathname === item.path;
          return (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-sidebar-accent text-sidebar-primary"
                  : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="border-t border-sidebar-border p-3">
        <button
          onClick={() => navigate("/")}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Switch Role
        </button>
      </div>
    </aside>
  );
}
