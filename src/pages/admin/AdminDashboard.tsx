import { useEffect, useMemo, useState } from "react";
import { Users, UserPlus, UserMinus, Bed } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { adminAPI } from "@/api";

const COLORS = ["hsl(199,89%,48%)", "hsl(168,60%,42%)", "hsl(38,92%,50%)", "hsl(0,72%,51%)", "hsl(270,60%,50%)"];

type OverviewResponse = {
  total_patients: number;
  low_risk: number;
  medium_risk: number;
  high_risk: number;
};

type RiskSummaryResponse = {
  total: number;
  distribution: Array<{ risk_level: string; count: number; percentage: number }>;
};

type WeeklyRiskTrendResponse = {
  daily_trend: Record<string, { low: number; medium: number; high: number }>;
};

type DepartmentTrendResponse = {
  department_distribution: Record<string, number>;
};

const riskColors = ["hsl(152,60%,42%)", "hsl(38,92%,50%)", "hsl(0,72%,51%)"];

const AdminDashboard = () => {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [riskSummary, setRiskSummary] = useState<RiskSummaryResponse | null>(null);
  const [weeklyTrend, setWeeklyTrend] = useState<WeeklyRiskTrendResponse | null>(null);
  const [deptTrend, setDeptTrend] = useState<DepartmentTrendResponse | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadAnalytics = async () => {
      try {
        const [overviewData, riskData, weeklyData, departmentData] = await Promise.all([
          adminAPI.getOverview(),
          adminAPI.getRiskSummary(),
          adminAPI.getWeeklyRiskTrend(),
          adminAPI.getDepartmentTrends(),
        ]);

        if (!isMounted) {
          return;
        }

        setOverview(overviewData);
        setRiskSummary(riskData);
        setWeeklyTrend(weeklyData);
        setDeptTrend(departmentData);
      } catch (error) {
        console.error("Failed to load admin analytics", error);
      }
    };

    loadAnalytics();

    return () => {
      isMounted = false;
    };
  }, []);

  const totalPatients = overview?.total_patients ?? 0;
  const admittedToday = Math.floor(totalPatients * 0.6);
  const dischargedToday = Math.floor(totalPatients * 0.2);
  const bedsAvailable = 63;

  const deptChartData = useMemo(() => {
    const distribution = deptTrend?.department_distribution ?? {};
    return Object.entries(distribution).map(([name, value]) => ({ name, value }));
  }, [deptTrend]);

  const riskData = useMemo(() => {
    const distribution = riskSummary?.distribution ?? [];
    const lookup = new Map(distribution.map(item => [item.risk_level, item.count]));
    return [
      { name: "Low", value: lookup.get("low") ?? 0 },
      { name: "Medium", value: lookup.get("medium") ?? 0 },
      { name: "High", value: lookup.get("high") ?? 0 },
    ];
  }, [riskSummary]);

  const weeklyData = useMemo(() => {
    const trend = weeklyTrend?.daily_trend ?? {};
    return Object.entries(trend)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([date, counts]) => {
        const dayLabel = new Date(date).toLocaleDateString("en-US", { weekday: "short" });
        return {
          day: dayLabel,
          cases: counts.low + counts.medium + counts.high,
        };
      });
  }, [weeklyTrend]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Admin Overview</h2>
        <p className="text-muted-foreground">Hospital operations at a glance</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Patients" value={totalPatients} icon={Users} variant="primary" />
        <StatCard title="Admitted Today" value={admittedToday} icon={UserPlus} variant="success" />
        <StatCard title="Discharged Today" value={dischargedToday} icon={UserMinus} variant="warning" />
        <StatCard title="Beds Available" value={bedsAvailable} icon={Bed} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Weekly Case Trend</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(214,20%,88%)" />
                <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Line type="monotone" dataKey="cases" stroke="hsl(199,89%,48%)" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Department-wise Distribution</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={deptChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(214,20%,88%)" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {deptChartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Overall Risk Summary</CardTitle></CardHeader>
          <CardContent className="flex flex-col sm:flex-row items-center gap-6">
            <ResponsiveContainer width={200} height={200}>
              <PieChart>
                <Pie data={riskData} dataKey="value" cx="50%" cy="50%" outerRadius={80} label>
                  {riskData.map((_, i) => <Cell key={i} fill={riskColors[i]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="grid gap-3 flex-1">
              {riskData.map((r, i) => (
                <div key={r.name} className="flex items-center justify-between rounded-md bg-muted p-3">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: riskColors[i] }} />
                    <span className="text-sm font-medium">{r.name} Risk</span>
                  </div>
                  <span className="font-bold">{r.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;
