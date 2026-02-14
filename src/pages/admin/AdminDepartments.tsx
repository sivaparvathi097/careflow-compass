import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Plus, Minus, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePatients, Department } from "@/contexts/PatientContext";

const AdminDepartments = () => {
  const [selected, setSelected] = useState<Department>("Cardiology");
  const { departments, incrementOccupied, decrementOccupied, getForecastHours } = usePatients();
  
  const wards = departments[selected];

  const handleIncrement = (wardName: string) => {
    incrementOccupied(selected, wardName);
  };

  const handleDecrement = (wardName: string) => {
    decrementOccupied(selected, wardName);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Departments & Wards</h2>
        <p className="text-muted-foreground">Manage beds and ward occupancy</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {(Object.keys(departments) as Department[]).map(dept => (
          <button
            key={dept}
            onClick={() => setSelected(dept)}
            className={cn(
              "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
              selected === dept ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-muted/80"
            )}
          >
            {dept}
          </button>
        ))}
      </div>

      <Card>
        <CardHeader><CardTitle>{selected} — Ward Table</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ward Name</TableHead>
                <TableHead>Total Beds</TableHead>
                <TableHead>Occupied</TableHead>
                <TableHead>Available</TableHead>
                <TableHead>Occupancy %</TableHead>
                <TableHead>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    Forecast
                  </span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {wards.map(w => {
                const occ = Math.round((w.occupied / w.totalBeds) * 100);
                const forecast = getForecastHours(selected, w.name, w);
                
                // Format forecast display
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
                  <TableRow key={w.name}>
                    <TableCell className="font-medium">{w.name}</TableCell>
                    <TableCell>{w.totalBeds}</TableCell>
                    <TableCell>{w.occupied}</TableCell>
                    <TableCell>{w.totalBeds - w.occupied}</TableCell>
                    <TableCell>
                      <span className={cn("font-semibold", occ > 85 ? "text-destructive" : occ > 60 ? "text-warning" : "text-success")}>
                        {occ}%
                      </span>
                    </TableCell>
                    <TableCell>
                      <span className={cn("font-semibold", forecastColor)}>
                        {forecastText}
                      </span>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Bed Grid — {selected}</CardTitle></CardHeader>
        <CardContent>
          {wards.map(w => (
            <div key={w.name} className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium">{w.name}</p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-7 w-7 rounded-full border-red-300 hover:bg-red-50 hover:border-red-400"
                    onClick={() => handleDecrement(w.name)}
                    disabled={w.occupied === 0}
                    title="Release bed (patient discharged)"
                  >
                    <Minus className="h-3.5 w-3.5 text-red-600" />
                  </Button>
                  <span className="text-xs font-medium w-16 text-center">
                    {w.occupied}/{w.totalBeds}
                  </span>
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-7 w-7 rounded-full border-green-300 hover:bg-green-50 hover:border-green-400"
                    onClick={() => handleIncrement(w.name)}
                    disabled={w.occupied >= w.totalBeds}
                    title="Occupy bed (patient admitted)"
                  >
                    <Plus className="h-3.5 w-3.5 text-green-600" />
                  </Button>
                </div>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {Array.from({ length: w.totalBeds }).map((_, i) => (
                  <div
                    key={i}
                    className={cn(
                      "h-6 w-6 rounded-sm text-[10px] flex items-center justify-center font-medium transition-colors",
                      i < w.occupied ? "bg-destructive/80 text-destructive-foreground" : "bg-success/80 text-success-foreground"
                    )}
                  >
                    {i + 1}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminDepartments;
