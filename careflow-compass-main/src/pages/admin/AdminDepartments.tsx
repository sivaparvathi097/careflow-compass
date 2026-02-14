import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { cn } from "@/lib/utils";

type DeptName = "Cardiology" | "Neurology" | "General Medicine" | "Emergency" | "Gynecology";

interface Ward {
  name: string;
  totalBeds: number;
  occupied: number;
}

const DEPARTMENTS: Record<DeptName, Ward[]> = {
  Cardiology: [
    { name: "CCU", totalBeds: 12, occupied: 9 },
    { name: "Ward A", totalBeds: 16, occupied: 10 },
    { name: "Ward B", totalBeds: 12, occupied: 8 },
  ],
  Neurology: [
    { name: "Neuro ICU", totalBeds: 8, occupied: 7 },
    { name: "Ward C", totalBeds: 14, occupied: 8 },
  ],
  "General Medicine": [
    { name: "Ward D", totalBeds: 20, occupied: 14 },
    { name: "Ward E", totalBeds: 20, occupied: 16 },
    { name: "Ward F", totalBeds: 20, occupied: 12 },
  ],
  Emergency: [
    { name: "ER Bay", totalBeds: 15, occupied: 13 },
    { name: "Observation", totalBeds: 10, occupied: 7 },
  ],
  Gynecology: [
    { name: "Ward G", totalBeds: 10, occupied: 5 },
    { name: "Ward H", totalBeds: 10, occupied: 7 },
  ],
};

const AdminDepartments = () => {
  const [selected, setSelected] = useState<DeptName>("Cardiology");
  const wards = DEPARTMENTS[selected];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Departments & Wards</h2>
        <p className="text-muted-foreground">Manage beds and ward occupancy</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {(Object.keys(DEPARTMENTS) as DeptName[]).map(dept => (
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
              </TableRow>
            </TableHeader>
            <TableBody>
              {wards.map(w => {
                const occ = Math.round((w.occupied / w.totalBeds) * 100);
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
            <div key={w.name} className="mb-4">
              <p className="text-sm font-medium mb-2">{w.name}</p>
              <div className="flex flex-wrap gap-1.5">
                {Array.from({ length: w.totalBeds }).map((_, i) => (
                  <div
                    key={i}
                    className={cn(
                      "h-6 w-6 rounded-sm text-[10px] flex items-center justify-center font-medium",
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
