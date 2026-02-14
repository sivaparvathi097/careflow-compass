import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  variant?: "default" | "primary" | "success" | "warning" | "destructive";
}

const variantStyles: Record<string, string> = {
  default: "bg-card text-card-foreground",
  primary: "bg-accent text-accent-foreground",
  success: "bg-success/10 text-success",
  warning: "bg-warning/10 text-warning",
  destructive: "bg-destructive/10 text-destructive",
};

const iconStyles: Record<string, string> = {
  default: "bg-muted text-muted-foreground",
  primary: "bg-primary/15 text-primary",
  success: "bg-success/15 text-success",
  warning: "bg-warning/15 text-warning",
  destructive: "bg-destructive/15 text-destructive",
};

export function StatCard({ title, value, icon: Icon, trend, variant = "default" }: StatCardProps) {
  return (
    <Card className={cn("transition-shadow hover:shadow-md", variantStyles[variant])}>
      <CardContent className="flex items-center gap-4 p-5">
        <div className={cn("rounded-lg p-3", iconStyles[variant])}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
          {trend && <p className="text-xs text-muted-foreground mt-0.5">{trend}</p>}
        </div>
      </CardContent>
    </Card>
  );
}
