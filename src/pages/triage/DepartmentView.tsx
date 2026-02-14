import { usePatients } from "@/contexts/PatientContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { RiskBadge } from "@/components/RiskBadge";

const DEPT_DATA: Record<string, { totalBeds: number; occupied: number }> = {
  Cardiology: { totalBeds: 40, occupied: 28 },
  Neurology: { totalBeds: 30, occupied: 18 },
  "General Medicine": { totalBeds: 60, occupied: 42 },
  Emergency: { totalBeds: 25, occupied: 20 },
  Gynecology: { totalBeds: 20, occupied: 12 },
};

const DepartmentView = () => {
  const { selectedPatient, patients } = usePatients();
  const dept = selectedPatient?.department || "General Medicine";
  const data = DEPT_DATA[dept] || { totalBeds: 30, occupied: 15 };
  const queue = patients.filter(p => p.department === dept);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">{dept}</h2>
        <p className="text-muted-foreground">Department details and patient queue</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          ["Total Beds", data.totalBeds],
          ["Available", data.totalBeds - data.occupied],
          ["Occupied", data.occupied],
        ].map(([label, val]) => (
          <Card key={label as string}>
            <CardContent className="p-5 text-center">
              <p className="text-sm text-muted-foreground">{label}</p>
              <p className="text-3xl font-bold">{val}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>Current Patient Queue ({queue.length})</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient ID</TableHead>
                <TableHead>Risk Level</TableHead>
                <TableHead>Arrival</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {queue.slice(0, 15).map(p => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.id}</TableCell>
                  <TableCell><RiskBadge level={p.riskLevel} /></TableCell>
                  <TableCell>{p.arrivalTime}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default DepartmentView;
