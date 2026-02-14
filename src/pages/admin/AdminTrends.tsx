import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { adminAPI } from "@/api";

const timeOfDay = [
  { hour: "6AM", arrivals: 8 }, { hour: "9AM", arrivals: 22 }, { hour: "12PM", arrivals: 30 },
  { hour: "3PM", arrivals: 25 }, { hour: "6PM", arrivals: 18 }, { hour: "9PM", arrivals: 14 },
  { hour: "12AM", arrivals: 6 },
];

type SymptomTrendResponse = {
  time_window_days: number;
  symptom_counts: Record<string, number>;
};

type DepartmentTrendResponse = {
  department_distribution: Record<string, number>;
};

const COLORS = ["hsl(199,89%,48%)", "hsl(168,60%,42%)", "hsl(38,92%,50%)", "hsl(0,72%,51%)", "hsl(270,60%,50%)"];

const AdminTrends = () => {
  const [symptoms, setSymptoms] = useState<SymptomTrendResponse | null>(null);
  const [departments, setDepartments] = useState<DepartmentTrendResponse | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadTrends = async () => {
      try {
        const [symptomData, departmentData] = await Promise.all([
          adminAPI.getSymptomTrends(),
          adminAPI.getDepartmentTrends(),
        ]);

        if (!isMounted) {
          return;
        }

        setSymptoms(symptomData);
        setDepartments(departmentData);
      } catch (error) {
        console.error("Failed to load trend analytics", error);
      }
    };

    loadTrends();

    return () => {
      isMounted = false;
    };
  }, []);

  const symptomChartData = useMemo(() => {
    const entries = Object.entries(symptoms?.symptom_counts ?? {})
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([symptom, count]) => ({ symptom, count }));
    return entries;
  }, [symptoms]);

  const deptComparison = useMemo(() => {
    const distribution = departments?.department_distribution ?? {};
    return Object.entries(distribution).map(([dept, cases]) => ({ dept, cases }));
  }, [departments]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Disease & Symptom Trends</h2>
        <p className="text-muted-foreground">Symptom pattern aggregation — no diagnosis</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Symptom Trends (Last {symptoms?.time_window_days ?? 7} Days)</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={symptomChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(214,20%,88%)" />
                <XAxis dataKey="symptom" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {symptomChartData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
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
                  {deptComparison.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
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
};

export default AdminTrends;
