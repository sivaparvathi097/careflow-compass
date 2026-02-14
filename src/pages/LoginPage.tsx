import { useNavigate } from "react-router-dom";
import { Heart, Stethoscope, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const LoginPage = () => {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-lg space-y-8">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center gap-2 mb-2">
            <Heart className="h-10 w-10 text-primary" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">CareFlow AI</h1>
          <p className="text-muted-foreground">AI-Powered Patient Triage &amp; Hospital Operations</p>
        </div>

        <div className="grid gap-4">
          <Card
            className="cursor-pointer border-2 border-transparent transition-all hover:border-primary hover:shadow-lg"
            onClick={() => navigate("/triage/dashboard")}
          >
            <CardHeader className="flex-row items-center gap-4 space-y-0">
              <div className="rounded-lg bg-primary/10 p-3">
                <Stethoscope className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg">Triage Staff</CardTitle>
                <CardDescription>Upload patient data, view real-time arrivals, and run AI analysis</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <Button className="w-full">Login as Triage Staff</Button>
            </CardContent>
          </Card>

          <Card
            className="cursor-pointer border-2 border-transparent transition-all hover:border-secondary hover:shadow-lg"
            onClick={() => navigate("/admin/dashboard")}
          >
            <CardHeader className="flex-row items-center gap-4 space-y-0">
              <div className="rounded-lg bg-secondary/10 p-3">
                <ShieldCheck className="h-6 w-6 text-secondary" />
              </div>
              <div>
                <CardTitle className="text-lg">Hospital Admin</CardTitle>
                <CardDescription>Monitor departments, trends, risk alerts, and hospital overview</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <Button variant="secondary" className="w-full">Login as Hospital Admin</Button>
            </CardContent>
          </Card>
        </div>

        <p className="text-center text-xs text-muted-foreground">Simulated login — no authentication required</p>
      </div>
    </div>
  );
};

export default LoginPage;
