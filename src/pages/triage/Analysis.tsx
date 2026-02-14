import { useNavigate } from "react-router-dom";
import { usePatients } from "@/contexts/PatientContext";
import { RiskBadge } from "@/components/RiskBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Brain, Shield, Stethoscope } from "lucide-react";

const Analysis = () => {
  const { selectedPatient } = usePatients();
  const navigate = useNavigate();

  if (!selectedPatient) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-20">
        <p className="text-muted-foreground">No patient selected.</p>
        <Button variant="outline" onClick={() => navigate("/triage/realtime")}>Go to Real-Time Data</Button>
      </div>
    );
  }

  const p = selectedPatient;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Patient Analysis — {p.id}</h2>
        <p className="text-muted-foreground">{p.gender}, Age {p.age}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex-row items-center gap-3 space-y-0">
            <Shield className="h-5 w-5 text-primary" />
            <CardTitle>Risk Assessment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Risk Score</span>
              <span className="text-3xl font-bold">{p.riskScore}</span>
            </div>
            <Progress value={p.riskScore} className="h-3" />
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Risk Level</span>
              <RiskBadge level={p.riskLevel} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center gap-3 space-y-0">
            <Brain className="h-5 w-5 text-primary" />
            <CardTitle>Explainable AI</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Contributing Factors</p>
              <div className="flex flex-wrap gap-2">
                {p.contributingFactors.map((f, i) => (
                  <span key={i} className="rounded-full bg-accent px-3 py-1 text-xs font-medium text-accent-foreground">{f}</span>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-1">Reason Summary</p>
              <p className="text-sm">{p.reasonSummary}</p>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Confidence</span>
              <span className="font-bold text-primary">{p.confidenceScore}%</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center gap-3 space-y-0">
            <Stethoscope className="h-5 w-5 text-primary" />
            <CardTitle>Department Classification</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-xl font-semibold">{p.department}</p>
            <p className="text-sm text-muted-foreground">Symptoms: {p.symptoms}</p>
            <Button onClick={() => navigate("/triage/department")} className="w-full">View Department</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Vitals Summary</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {[
                ["Blood Pressure", p.bloodPressure],
                ["Heart Rate", `${p.heartRate} bpm`],
                ["Temperature", `${p.temperature} °C`],
                ["Conditions", p.preExistingConditions],
              ].map(([label, val]) => (
                <div key={label as string} className="rounded-md bg-muted p-3">
                  <p className="text-xs text-muted-foreground">{label}</p>
                  <p className="text-sm font-semibold">{val}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Analysis;
