import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import RiskLevelBadge from "./RiskLevelBadge";
import { ComplianceFile } from "./ComplianceTable";
import { Pie } from "react-chartjs-2";
import { Chart, ArcElement, Tooltip, Legend } from "chart.js";
Chart.register(ArcElement, Tooltip, Legend);
 
interface ComplianceModalProps {
  isOpen: boolean;
  onClose: () => void;
  file: ComplianceFile | null;
  complianceData?: any;
}
 
export default function ComplianceModal({ isOpen, onClose, file, complianceData }: ComplianceModalProps) {
  // Pie chart data for compliance summary
  const pieData = complianceData
    ? {
        labels: ["Compliant", "Non-compliant"],
        datasets: [
          {
            data: [
              (complianceData.rows ?? 0) - (complianceData.non_compliant ?? 0),
              complianceData.non_compliant ?? 0,
            ],
            backgroundColor: ["#14b8a6", "#d5520b"],
            borderWidth: 1,
          },
        ],
      }
    : null;
  if (!file) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-brand-blue">
            {file.fileName}
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-8 mt-6">
          <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-3">
            <div>
              {complianceData && (
            <div className="border-b border-border pb-6 last:border-b-0">
              <h2 className="text-xl font-semibold text-brand-charcoal mb-4">Compliance Summary</h2>
              <div className="space-y-2">
                <div>Rows: <span className="font-bold">{complianceData.rows}</span></div>
                <div>Non-compliant: <span className="font-bold">{complianceData.non_compliant}</span></div>
                <div>Compliance Rate: <span className="font-bold">{complianceData.compliance_rate}</span></div>
                <div>Total Estimated Impact: <span className="font-bold">{complianceData.total_estimated_impact}</span></div>
                {complianceData.rule_counts && (
                  <div>
                    <h3 className="text-lg font-medium text-brand-charcoal mb-2">Rule Counts</h3>
                    <ul className="list-disc ml-6">
                      {Object.entries(complianceData.rule_counts).map(([rule, count]) => (
                        <li key={rule}>{rule}: {String(count)}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {complianceData.download && (
                  <div>
                    <a href={complianceData.download} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">Download CSV</a>
                  </div>
                )}
              </div>
            </div>
          )}
            </div>
            <div>
              {pieData && (
            <div className="flex flex-col items-center mb-6">
              <h3 className="text-lg font-medium text-brand-charcoal mb-2">Compliance Distribution</h3>
              <div style={{ width: 220, height: 220 }}>
                <Pie data={pieData} options={{ plugins: { legend: { position: "bottom" } } }} />
              </div>
            </div>
          )}
            </div>
          </div>
          
          {complianceData && complianceData.results && complianceData.results.length > 0 ? (
            complianceData.results.map((transaction: any, index: number) => (
              <div key={transaction.id || index} className="border-b border-border pb-6 last:border-b-0">
                <h2 className="text-xl font-semibold text-brand-charcoal mb-4">
                  {transaction.id || `Transaction ${index + 1}`}
                </h2>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium text-brand-charcoal mb-2">Risk level</h3>
                    <RiskLevelBadge level={transaction.riskLevel || transaction.risk_level || "Unknown"} />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-brand-charcoal mb-3">What we found</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {transaction.findings.map((finding: any, findingIndex: number) => (
                        <li key={findingIndex} className="text-muted-foreground">
                          <span className="font-semibold">{finding.title}</span>: {finding.message}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))
          ) : (
            file.transactions.map((transaction, index) => (
              <div key={transaction.id} className="border-b border-border pb-6 last:border-b-0">
                <h2 className="text-xl font-semibold text-brand-charcoal mb-4">
                  {transaction.id}
                </h2>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium text-brand-charcoal mb-2">Risk level</h3>
                    <RiskLevelBadge level={transaction.riskLevel} />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-brand-charcoal mb-3">What we found</h3>
                    <ul className="list-disc list-inside space-y-1">
                      {transaction.findings.map((finding, findingIndex) => (
                        <li key={findingIndex} className="text-muted-foreground">{finding}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}