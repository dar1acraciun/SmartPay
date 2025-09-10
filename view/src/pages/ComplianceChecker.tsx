import { useState } from "react";
import { Search } from "lucide-react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import ComplianceTable, { ComplianceFile } from "@/components/Compliance Checker/ComplianceTable";
import ComplianceModal from "@/components/Compliance Checker/ComplianceModal";

// Mock data for demonstration
const mockFiles: ComplianceFile[] = [
  {
    id: "1",
    fileName: "file_name.csv",
    date: "2024-01-15",
    transactions: [
      {
        id: "transaction_id_1",
        riskLevel: "High",
        findings: ["finding text 1", "finding text 2"]
      },
      {
        id: "transaction_id_2", 
        riskLevel: "High",
        findings: ["finding text 1", "finding text 2"]
      }
    ]
  },
  {
    id: "2",
    fileName: "transactions_q1_2024.csv",
    date: "2024-02-20",
    transactions: [
      {
        id: "transaction_id_3",
        riskLevel: "Medium",
        findings: ["Incomplete documentation", "Minor validation issues"]
      }
    ]
  },
  {
    id: "3", 
    fileName: "payments_data.csv",
    date: "2024-03-10",
    transactions: [
      {
        id: "transaction_id_4",
        riskLevel: "Low",
        findings: ["All checks passed", "No issues found"]
      },
      {
        id: "transaction_id_5",
        riskLevel: "Medium", 
        findings: ["Minor formatting issues", "Timestamps need adjustment"]
      }
    ]
  }
];

const ComplianceChecker = () => {
  const [files] = useState<ComplianceFile[]>(mockFiles);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFile, setSelectedFile] = useState<ComplianceFile | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSortToggle = () => {
    setSortOrder(sortOrder === "asc" ? "desc" : "asc");
  };

  const handleCheckCompliance = (file: ComplianceFile) => {
    setSelectedFile(file);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center space-y-4 mb-12">
            <div className="flex items-center justify-center gap-3">
              <Search className="h-8 w-8 text-brand-blue" />
              <h1 className="text-4xl lg:text-5xl font-bold text-brand-blue">
                Compliance Checker
              </h1>
            </div>
            <p className="text-lg text-brand-charcoal max-w-2xl mx-auto">
              Automated scheme compliance validation for your transaction data.
            </p>
          </div>

          <ComplianceTable
            files={files}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            sortOrder={sortOrder}
            onSortToggle={handleSortToggle}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            onCheckCompliance={handleCheckCompliance}
          />
        </div>
      </main>
      <Footer />

      <ComplianceModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        file={selectedFile}
      />
    </div>
  );
};

export default ComplianceChecker;