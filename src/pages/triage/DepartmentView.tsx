import { usePatients, Department } from "@/contexts/PatientContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { RiskBadge } from "@/components/RiskBadge";
import { Clock } from "lucide-react";
import { cn } from "@/lib/utils";

const DepartmentView = () => {
  const { selectedPatient, patients, getDepartmentStats, departments, getForecastHours } = usePatients();
  const dept = (selectedPatient?.department || "General Medicine") as Department;
  const stats = getDepartmentStats(dept);
  const queue = patients.filter(p => p.department === dept);
  const wards = departments[dept] || [];

  // Calculate department-level forecast (average of all wards)
  const getDeptForecast = (): number | null => {
    const forecasts = wards.map(w => getForecastHours(dept, w.name, w)).filter((f): f is number => f !== null);
    if (forecasts.length === 0) return null;
    if (forecasts.some(f => f === 0)) return 0;
    return Math.round((forecasts.reduce((a, b) => a + b, 0) / forecasts.length) * 10) / 10;
  };

  const forecast = getDeptForecast();
  let forecastText: string;
  let forecastColor: string;
  if (forecast === 0) {
    forecastText = "Full";
    forecastColor = "text-destructive";
  } else if (forecast === null) {
    forecastText = "No data";
    forecastColor = "text-muted-foreground";
  } else if (forecast <= 2) {
    forecastText = `~${forecast} hrs`;
    forecastColor = "text-destructive";
  } else if (forecast <= 6) {
    forecastText = `~${forecast} hrs`;
    forecastColor = "text-warning";
  } else {
    forecastText = `~${forecast} hrs`;
    forecastColor = "text-success";
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">{dept}</h2>
        <p className="text-muted-foreground">Department details and patient queue</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="p-5 text-center">
            <p className="text-sm text-muted-foreground">Total Beds</p>
            <p className="text-3xl font-bold">{stats.totalBeds}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 text-center">
            <p className="text-sm text-muted-foreground">Available</p>
            <p className="text-3xl font-bold">{stats.available}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5 text-center">
            <p className="text-sm text-muted-foreground">Occupied</p>
            <p className="text-3xl font-bold">{stats.occupied}</p>
          </CardContent>
        </Card>
        <Card className="border-2 border-dashed">
          <CardContent className="p-5 text-center">
            <p className="text-sm text-muted-foreground flex items-center justify-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              Forecast
            </p>
            <p className={cn("text-2xl font-bold", forecastColor)}>{forecastText}</p>
            <p className="text-xs text-muted-foreground mt-1">to full capacity</p>
          </CardContent>
        </Card>
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
