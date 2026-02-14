import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const weeklySymptoms = [
  { week: "W1", "Chest pain": 18, Fever: 32, Headache: 24, Cough: 15 },
  { week: "W2", "Chest pain": 22, Fever: 28, Headache: 30, Cough: 20 },
  { week: "W3", "Chest pain": 15, Fever: 35, Headache: 22, Cough: 28 },
  { week: "W4", "Chest pain": 25, Fever: 30, Headache: 26, Cough: 18 },
];

const deptComparison = [
  { dept: "Cardiology", cases: 45 },
  { dept: "Neurology", cases: 28 },
  { dept: "General Med", cases: 62 },
  { dept: "Emergency", cases: 38 },
  { dept: "Gynecology", cases: 22 },
];

const timeOfDay = [
  { hour: "6AM", arrivals: 8 }, { hour: "9AM", arrivals: 22 }, { hour: "12PM", arrivals: 30 },
  { hour: "3PM", arrivals: 25 }, { hour: "6PM", arrivals: 18 }, { hour: "9PM", arrivals: 14 },
  { hour: "12AM", arrivals: 6 },
];

const COLORS = ["hsl(199,89%,48%)", "hsl(168,60%,42%)", "hsl(38,92%,50%)", "hsl(0,72%,51%)", "hsl(270,60%,50%)"];
const LINE_COLORS = ["hsl(0,72%,51%)", "hsl(38,92%,50%)", "hsl(199,89%,48%)", "hsl(168,60%,42%)"];

const AdminTrends = () => (
  <div className="space-y-6">
    <div>
      <h2 className="text-2xl font-bold">Disease & Symptom Trends</h2>
      <p className="text-muted-foreground">Symptom pattern aggregation — no diagnosis</p>
    </div>

    <div className="grid gap-6 lg:grid-cols-2">
      <Card className="lg:col-span-2">
        <CardHeader><CardTitle>Weekly Symptom Trends</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={weeklySymptoms}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(214,20%,88%)" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              {["Chest pain", "Fever", "Headache", "Cough"].map((s, i) => (
                <Line key={s} type="monotone" dataKey={s} stroke={LINE_COLORS[i]} strokeWidth={2} dot={{ r: 3 }} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Department Comparison</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={deptComparison}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(214,20%,88%)" />
              <XAxis dataKey="dept" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="cases" radius={[4, 4, 0, 0]}>
                {deptComparison.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Time-of-Day Arrivals</CardTitle></CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={timeOfDay}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(214,20%,88%)" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="arrivals" fill="hsl(199,89%,48%)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  </div>
);

export default AdminTrends;
