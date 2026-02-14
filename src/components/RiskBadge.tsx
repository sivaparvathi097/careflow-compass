import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { RiskLevel } from "@/contexts/PatientContext";

const riskStyles: Record<RiskLevel, string> = {
  Low: "bg-success/15 text-success border-success/30",
  Medium: "bg-warning/15 text-warning border-warning/30",
  High: "bg-destructive/15 text-destructive border-destructive/30",
};

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <Badge variant="outline" className={cn("font-semibold", riskStyles[level])}>
      {level}
    </Badge>
  );
}
