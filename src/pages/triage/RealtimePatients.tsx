import { useNavigate } from "react-router-dom";
import { usePatients } from "@/contexts/PatientContext";
import { RiskBadge } from "@/components/RiskBadge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Activity } from "lucide-react";

const RealtimePatients = () => {
  const { patients, selectPatient } = usePatients();
  const navigate = useNavigate();

  const handleClick = (p: typeof patients[0]) => {
    selectPatient(p);
    navigate("/triage/analysis");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Real-Time Patient Data</h2>
          <p className="text-muted-foreground">Live patient arrivals — updates every 5 seconds</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-success">
          <Activity className="h-4 w-4 animate-pulse-soft" />
          Live
        </div>
      </div>

      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Patient ID</TableHead>
              <TableHead>Arrival Time</TableHead>
              <TableHead>Risk Level</TableHead>
              <TableHead>Assigned Department</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[...patients].reverse().map(p => (
              <TableRow key={p.id} className="cursor-pointer" onClick={() => handleClick(p)}>
                <TableCell className="font-medium">{p.id}</TableCell>
                <TableCell>{p.arrivalTime}</TableCell>
                <TableCell><RiskBadge level={p.riskLevel} /></TableCell>
                <TableCell>{p.department}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default RealtimePatients;
