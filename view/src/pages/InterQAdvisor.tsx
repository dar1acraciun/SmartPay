import { useState } from "react";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import ReportsHeader from "@/components/InterQ Advisor/ReportsHeader";
import UploadSection from "@/components/InterQ Advisor/UploadSection";
import ReportsTable from "@/components/InterQ Advisor/ReportsTable";
import { toast } from "@/hooks/use-toast";

type Status = "completed" | "processing" | "failed";

interface Report {
  id: string;
  fileName: string;
  date: string; // YYYY-MM-DD
  downgradedTransactions: number;
  status: Status;
}

const InterQAdvisor = () => {
  const [reports, setReports] = useState<Report[]>([
    { id: "1", fileName: "transactions_march_2024.csv", date: "2024-03-15", downgradedTransactions: 42, status: "completed" },
    { id: "2", fileName: "lol.csv",          date: "2024-03-10", downgradedTransactions: 28, status: "completed" },
    { id: "3", fileName: "weekly_report_10.csv",         date: "2024-03-05", downgradedTransactions: 15, status: "completed" },
    { id: "4", fileName: "february_batch.csv",           date: "2024-02-28", downgradedTransactions: 67, status: "completed" },
    { id: "5", fileName: "te_rog_batch.csv",           date: "2024-02-28", downgradedTransactions: 67, status: "completed" },
    { id: "6", fileName: "numesuperlungvaleuwow.csv",           date: "2024-02-28", downgradedTransactions: 67, status: "completed" },
  ]);

  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [searchTerm, setSearchTerm] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [generating, setGenerating] = useState(false);
  
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".csv")) {
      toast({
        title: "Invalid file type",
        description: "Please upload a CSV file.",
        variant: "destructive",
      });
      // reset input so same file can be selected again
      event.currentTarget.value = "";
      return;
    }

    toast({
      title: "File received",
      description: `Processing ${file.name}…`,
    });
    setUploading(true);

    // ---- Mock processing (replace with real API later) ----
    setTimeout(() => {
      setUploadedFile(file);
      setUploading(false);

      toast({
        title: "Uploaded successfully!",
        description: "File is ready for report generation.",
      });

      // allow selecting the same file again if desired
      event.currentTarget.value = "";
    }, 2000);
    // ------------------------------------------------------
  };

  const handleGenerateReport = () => {
    if (!uploadedFile) return;

    setGenerating(true);
    toast({
      title: "Generating report",
      description: `Analyzing ${uploadedFile.name}…`,
    });

    setTimeout(() => {
      const newReport: Report = {
        id: Date.now().toString(),
        fileName: uploadedFile.name,
        date: new Date().toISOString().split("T")[0],
        downgradedTransactions: Math.floor(Math.random() * 100) + 1,
        status: "completed",
      };
      setReports((prev) => [newReport, ...prev]);
      setGenerating(false);
      setUploadedFile(null); // Reset for next upload
      setCurrentPage(1); // jump to first page so the new item is visible

      toast({
        title: "Analysis complete",
        description: "Your transaction analysis is ready.",
      });
    }, 3000);
  };
  
  const handleSortToggle = () => {
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    setCurrentPage(1);
  };
  
  const handleDownloadFormat = (type: 'visa' | 'mastercard') => {
    // Different CSV templates for Visa and Mastercard
    const visaCsvContent = 
      "transaction_id,amount,currency,merchant_category,card_type,visa_interchange_category,visa_qualification\n" +
      "1,100.50,USD,5411,credit,CPS/Retail,Qualified\n" +
      "2,25.00,USD,5812,debit,CPS/Small Ticket,Basic\n" +
      "3,75.25,USD,5541,credit,CPS/Supermarket,Standard";
    
    const mastercardCsvContent = 
      "transaction_id,amount,currency,merchant_category,card_type,mastercard_product_type,mastercard_rate_type\n" +
      "1,100.50,USD,5411,credit,World Elite,Enhanced\n" +
      "2,25.00,USD,5812,debit,Standard,Basic\n" +
      "3,75.25,USD,5541,credit,World,Standard";

    const csvContent = type === 'visa' ? visaCsvContent : mastercardCsvContent;
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${type}_transaction_format_template.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };
  
  const handleOpenReport = (reportId: string) => {
    toast({
      title: "Opening report",
      description: `Report ${reportId} will open in a new tab (stub).`,
    });
    // window.open(`/reports/${reportId}`, "_blank"); // real route later
  };

  const handleDownloadReport = (reportId: string) => {
    toast({
      title: "Exporting report (PDF)",
      description: `Starting download for report ${reportId} (stub).`,
    });
    // trigger real download later
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="py-8">
        <div className="container mx-auto px-6 max-w-7xl">
          <ReportsHeader />

          {/* Upload with loading state */}
          <UploadSection
            onFileUpload={handleFileUpload}
            onDownloadFormat={handleDownloadFormat}
            onGenerateReport={handleGenerateReport}
            uploading={uploading}
            generating={generating}
            uploadedFile={uploadedFile}
          />

          {/* Table with pagination + loading row */}
          <ReportsTable
            reports={reports}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            sortOrder={sortOrder}
            onSortToggle={handleSortToggle}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            onOpenReport={handleOpenReport}
            onDownloadReport={handleDownloadReport}
            loading={generating}
            perPage={5}
          />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default InterQAdvisor;