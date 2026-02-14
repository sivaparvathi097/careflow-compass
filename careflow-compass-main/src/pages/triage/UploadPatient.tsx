import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { usePatients, type Department } from "@/contexts/PatientContext";
import { Upload } from "lucide-react";

const DEPARTMENTS: Department[] = ["Cardiology", "Neurology", "General Medicine", "Emergency", "Gynecology"];

const UploadPatient = () => {
  const navigate = useNavigate();
  const { addPatient, selectPatient } = usePatients();
  const [form, setForm] = useState({
    patientId: "",
    age: "",
    gender: "Male",
    symptoms: "",
    bloodPressure: "",
    heartRate: "",
    temperature: "",
    preExistingConditions: "",
  });

  const handleChange = (field: string, value: string) => setForm(prev => ({ ...prev, [field]: value }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const riskScore = Math.floor(Math.random() * 80) + 15;
    const riskLevel = riskScore >= 70 ? "High" : riskScore >= 40 ? "Medium" : "Low";
    const dept = DEPARTMENTS[Math.floor(Math.random() * DEPARTMENTS.length)];
    const patient = {
      id: form.patientId || `MAN-${Date.now()}`,
      age: parseInt(form.age) || 30,
      gender: form.gender,
      symptoms: form.symptoms,
      bloodPressure: form.bloodPressure || "120/80",
      heartRate: parseInt(form.heartRate) || 75,
      temperature: parseFloat(form.temperature) || 37.0,
      preExistingConditions: form.preExistingConditions || "None",
      arrivalTime: new Date().toLocaleTimeString(),
      riskScore,
      riskLevel: riskLevel as any,
      department: dept,
      contributingFactors: ["Manual entry", "Symptoms reported", "Vitals recorded"],
      reasonSummary: `Patient manually entered with symptoms: ${form.symptoms}`,
      confidenceScore: Math.floor(Math.random() * 20) + 75,
      synthetic: false,
    };
    addPatient(patient);
    selectPatient(patient);
    navigate("/triage/analysis");
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Upload Patient Data</h2>
        <p className="text-muted-foreground">Enter patient information or upload a file</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Patient Information</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="patientId">Patient ID</Label>
                <Input id="patientId" placeholder="e.g. PAT-001" value={form.patientId} onChange={e => handleChange("patientId", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input id="age" type="number" placeholder="Age" value={form.age} onChange={e => handleChange("age", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label>Gender</Label>
                <Select value={form.gender} onValueChange={v => handleChange("gender", v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Male">Male</SelectItem>
                    <SelectItem value="Female">Female</SelectItem>
                    <SelectItem value="Other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="bp">Blood Pressure</Label>
                <Input id="bp" placeholder="120/80" value={form.bloodPressure} onChange={e => handleChange("bloodPressure", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="hr">Heart Rate</Label>
                <Input id="hr" type="number" placeholder="bpm" value={form.heartRate} onChange={e => handleChange("heartRate", e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="temp">Temperature (°C)</Label>
                <Input id="temp" type="number" step="0.1" placeholder="37.0" value={form.temperature} onChange={e => handleChange("temperature", e.target.value)} />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label htmlFor="symptoms">Symptoms</Label>
                <Textarea id="symptoms" placeholder="Describe symptoms..." value={form.symptoms} onChange={e => handleChange("symptoms", e.target.value)} />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label htmlFor="conditions">Pre-Existing Conditions</Label>
                <Input id="conditions" placeholder="e.g. Diabetes, Hypertension" value={form.preExistingConditions} onChange={e => handleChange("preExistingConditions", e.target.value)} />
              </div>
              <div className="sm:col-span-2">
                <Button type="submit" className="w-full">Upload and Analyze</Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>File Upload</CardTitle>
          </CardHeader>
          <CardContent>
            <label className="flex flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed border-border p-8 cursor-pointer hover:border-primary/50 transition-colors">
              <Upload className="h-8 w-8 text-muted-foreground" />
              <span className="text-sm text-muted-foreground text-center">CSV, JSON, TXT, EHR/EMR</span>
              <input type="file" className="hidden" accept=".csv,.json,.txt,.ehr,.emr" />
            </label>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UploadPatient;
