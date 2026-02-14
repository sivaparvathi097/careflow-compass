import { Users, UserPlus, UserMinus, Bed } from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { usePatients } from "@/contexts/PatientContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

const weeklyData = [
  { day: "Mon", cases: 42 }, { day: "Tue", cases: 58 }, { day: "Wed", cases: 51 },
  { day: "Thu", cases: 67 }, { day: "Fri", cases: 72 }, { day: "Sat", cases: 45 }, { day: "Sun", cases: 38 },
];

const COLORS = ["hsl(199,89%,48%)", "hsl(168,60%,42%)", "hsl(38,92%,50%)", "hsl(0,72%,51%)", "hsl(270,60%,50%)"];

const AdminDashboard = () => {
  const { patients } = usePatients();
  const deptDist = patients.reduce<Record<string, number>>((acc, p) => {
    acc[p.department] = (acc[p.department] || 0) + 1;
    return acc;
  }, {});
  const deptChartData = Object.entries(deptDist).map(([name, value]) => ({ name, value }));

  const riskCounts = { Low: 0, Medium: 0, High: 0 };
  patients.forEach(p => riskCounts[p.riskLevel]++);
  const riskData = [
    { name: "Low", value: riskCounts.Low },
    { name: "Medium", value: riskCounts.Medium },
    { name: "High", value: riskCounts.High },
  ];
  const riskColors = ["hsl(152,60%,42%)", "hsl(38,92%,50%)", "hsl(0,72%,51%)"];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Admin Overview</h2>
        <p className="text-muted-foreground">Hospital operations at a glance</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Patients" value={patients.length} icon={Users} variant="primary" />
        <StatCard title="Admitted Today" value={Math.floor(patients.length * 0.6)} icon={UserPlus} variant="success" />
        <StatCard title="Discharged Today" value={Math.floor(patients.length * 0.2)} icon={UserMinus} variant="warning" />
        <StatCard title="Beds Available" value={63} icon={Bed} />
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
