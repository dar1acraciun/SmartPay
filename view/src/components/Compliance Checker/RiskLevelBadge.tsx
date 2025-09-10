import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface RiskLevelBadgeProps {
  level: "High" | "Medium" | "Low";
  className?: string;
}

export default function RiskLevelBadge({ level, className }: RiskLevelBadgeProps) {
  const getBadgeStyles = (riskLevel: string) => {
    switch (riskLevel) {
      case "High":
        return "bg-red-100 text-red-800 hover:bg-red-100";
      case "Medium":
        return "bg-yellow-100 text-yellow-800 hover:bg-yellow-100";
      case "Low":
        return "bg-green-100 text-green-800 hover:bg-green-100";
      default:
        return "bg-gray-100 text-gray-800 hover:bg-gray-100";
    }
  };

  return (
    <Badge 
      variant="secondary" 
      className={cn(getBadgeStyles(level), className)}
    >
      {level}
    </Badge>
  );
}