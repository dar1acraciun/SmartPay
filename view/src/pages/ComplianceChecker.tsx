import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import ComplianceTable, { ComplianceFile } from "@/components/Compliance Checker/ComplianceTable";
import ComplianceModal from "@/components/Compliance Checker/ComplianceModal";

import axios from "axios";
const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const ComplianceChecker = () => {
  const [files, setFiles] = useState<ComplianceFile[]>([]);
  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const res = await axios.get(`${API_BASE}/files/all`);
        // Map backend response to ComplianceFile[] structure
        const raw = res?.data?.files ?? [];
        const mapped: ComplianceFile[] = raw.map((f: any) => ({
          id: String(f.id),
          fileName: f.name ?? f.fileName ?? String(f.id),
          date: f.timestamp ? new Date(f.timestamp).toISOString().slice(0, 10) : "",
          transactions: [], // You can enrich this later with compliance results
        }));
        setFiles(mapped);
      } catch (err) {
        setFiles([]);
      }
    };
    fetchFiles();
  }, []);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFile, setSelectedFile] = useState<ComplianceFile | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [complianceData, setComplianceData] = useState<any>(null);

  const handleSortToggle = () => {
    setSortOrder(sortOrder === "asc" ? "desc" : "asc");
  };

  const handleCheckCompliance = async (file: ComplianceFile) => {
    setSelectedFile(file);
    setIsModalOpen(true);
    setComplianceData(null);
        try {
          // Prepare URL-encoded form data for POST request
          const params = new URLSearchParams();
          params.append("file_id", file.id);
          params.append("min_fail_severity", "MEDIUM");
          params.append("force_format", "auto");
          params.append("return_csv", "false");
          const res = await axios.post(
            "http://localhost:8001/api/compliance/check",
            params,
            {
              headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "accept": "application/json",
              },
            }
          );
          setComplianceData(res.data);
    } catch (err) {
      setComplianceData({ error: "Failed to fetch compliance data" });
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
    setComplianceData(null);
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
        complianceData={complianceData}
      />
    </div>
  );
};

export default ComplianceChecker;