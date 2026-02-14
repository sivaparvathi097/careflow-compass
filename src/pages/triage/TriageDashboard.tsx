import { Users, AlertTriangle, Building2 } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { usePatients } from "@/contexts/PatientContext";

const TriageDashboard = () => {
  const { patients } = usePatients();
  const highRisk = patients.filter(p => p.riskLevel === "High").length;
  const deptLoad: Record<string, number> = {};
  patients.forEach(p => { deptLoad[p.department] = (deptLoad[p.department] || 0) + 1; });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Triage Dashboard</h2>
        <p className="text-muted-foreground">Real-time patient overview</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard title="Total Patients" value={patients.length} icon={Users} variant="primary" />
        <StatCard title="High Risk" value={highRisk} icon={AlertTriangle} variant="destructive" />
        <StatCard title="Departments Active" value={Object.keys(deptLoad).length} icon={Building2} variant="success" />
      </div>

      <div className="rounded-lg border bg-card p-5">
        <h3 className="text-lg font-semibold mb-3">Department Load</h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(deptLoad).map(([dept, count]) => (
            <div key={dept} className="flex items-center justify-between rounded-md bg-muted p-3">
              <span className="text-sm font-medium">{dept}</span>
              <span className="text-sm font-bold text-primary">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TriageDashboard;
