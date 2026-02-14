import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { AlertTriangle, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { adminAPI } from "@/api";

const deptRisk = [
  { dept: "Cardiology", highRiskPct: 35 },
  { dept: "Neurology", highRiskPct: 22 },
  { dept: "General Medicine", highRiskPct: 18 },
  { dept: "Emergency", highRiskPct: 45 },
  { dept: "Gynecology", highRiskPct: 12 },
];

type RiskSummaryResponse = {
  total: number;
  distribution: Array<{ risk_level: string; count: number; percentage: number }>;
};

type AlertResponse = {
  alerts: string[];
};
const riskColors = ["hsl(152,60%,42%)", "hsl(38,92%,50%)", "hsl(0,72%,51%)"];

const AdminAlerts = () => {
  const [riskSummary, setRiskSummary] = useState<RiskSummaryResponse | null>(null);
  const [alertData, setAlertData] = useState<AlertResponse | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadAlerts = async () => {
      try {
        const [riskData, alerts] = await Promise.all([
          adminAPI.getRiskSummary(),
          adminAPI.getAlerts(),
        ]);

        if (!isMounted) {
          return;
        }

        setRiskSummary(riskData);
        setAlertData(alerts);
      } catch (error) {
        console.error("Failed to load alert analytics", error);
      }
    };

    loadAlerts();

    return () => {
      isMounted = false;
    };
  }, []);

  const riskDistribution = useMemo(() => {
    const distribution = riskSummary?.distribution ?? [];
    const lookup = new Map(distribution.map(item => [item.risk_level, item.count]));
    return [
      { name: "Low", value: lookup.get("low") ?? 0 },
      { name: "Medium", value: lookup.get("medium") ?? 0 },
      { name: "High", value: lookup.get("high") ?? 0 },
    ];
  }, [riskSummary]);

  const alerts = alertData?.alerts ?? [];
  const hasAlerts = alerts.length > 0;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Risk & Alerts</h2>
        <p className="text-muted-foreground">Department risk monitoring and alert triggers</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Department High Risk %</CardTitle></CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Department</TableHead>
                  <TableHead>High Risk %</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {deptRisk.map(d => (
                  <TableRow key={d.dept}>
                    <TableCell className="font-medium">{d.dept}</TableCell>
                    <TableCell>{d.highRiskPct}%</TableCell>
                    <TableCell>
                      <div className={cn(
                        "inline-block h-3 w-3 rounded-full",
                        d.highRiskPct > 30 ? "bg-destructive" : d.highRiskPct > 20 ? "bg-warning" : "bg-success"
                      )} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Hospital Risk Distribution</CardTitle></CardHeader>
          <CardContent className="flex justify-center">
            <ResponsiveContainer width={250} height={250}>
              <PieChart>
                <Pie data={riskDistribution} dataKey="value" cx="50%" cy="50%" outerRadius={90} label>
                  {riskDistribution.map((_, i) => <Cell key={i} fill={riskColors[i]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Alert Triggers</CardTitle></CardHeader>
          <CardContent>
            {hasAlerts ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {alerts.map((alert, i) => (
                  <div key={i} className={cn(
                    "flex items-start gap-3 rounded-lg border p-4",
                    "border-destructive/30 bg-destructive/5"
                  )}>
                    <AlertTriangle className="h-5 w-5 text-destructive mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold">{alert}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className={cn(
                "flex items-start gap-3 rounded-lg border p-4",
                "border-success/30 bg-success/5"
              )}>
                <CheckCircle className="h-5 w-5 text-success mt-0.5" />
                <div>
                  <p className="text-sm font-semibold">No alerts triggered</p>
                  <p className="text-xs text-muted-foreground">All monitored conditions are within safe thresholds.</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminAlerts;
