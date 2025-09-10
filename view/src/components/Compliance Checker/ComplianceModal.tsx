import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import RiskLevelBadge from "./RiskLevelBadge";
import { ComplianceFile } from "./ComplianceTable";

interface ComplianceModalProps {
  isOpen: boolean;
  onClose: () => void;
  file: ComplianceFile | null;
}

export default function ComplianceModal({ isOpen, onClose, file }: ComplianceModalProps) {
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
          {file.transactions.map((transaction, index) => (
            <div key={transaction.id} className="border-b border-border pb-6 last:border-b-0">
              <h2 className="text-xl font-semibold text-brand-charcoal mb-4">
                {transaction.id}
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-brand-charcoal mb-2">
                    Risk level
                  </h3>
                  <RiskLevelBadge level={transaction.riskLevel} />
                </div>
                
                <div>
                  <h3 className="text-lg font-medium text-brand-charcoal mb-3">
                    What we found
                  </h3>
                  <ul className="list-disc list-inside space-y-1">
                    {transaction.findings.map((finding, findingIndex) => (
                      <li key={findingIndex} className="text-muted-foreground">
                        {finding}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}