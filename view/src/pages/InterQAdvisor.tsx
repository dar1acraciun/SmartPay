import { useEffect, useState } from "react";
import axios from "axios";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import ReportsHeader from "@/components/InterQ Advisor/ReportsHeader";
import UploadSection from "@/components/InterQ Advisor/UploadSection";
import ReportsTable from "@/components/InterQ Advisor/ReportsTable";
import { toast } from "@/hooks/use-toast";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

type Status = "completed" | "processing" | "failed";

interface Report {
  id: string;
  fileName: string;
  date: string; // YYYY-MM-DD
  downgradedTransactions: number;
  status: Status;
}

const InterQAdvisor = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [searchTerm, setSearchTerm] = useState("");

  // upload + generate state (drives UploadSection + table loading row)
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [generating, setGenerating] = useState(false);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [lastUploadedFileId, setLastUploadedFileId] = useState<string | null>(null);

  // ---------------------------
  // Helpers
  // ---------------------------
  const toYYYYMMDD = (ts?: string) => {
    if (!ts) return "";
    // Avoid timezone surprises: parse and take date portion
    const d = new Date(ts);
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 10);
  };

  // Fetch a file by id to read downgraded_transaction (from your files controller)
  const fetchFileMeta = async (fileId?: string | null) => {
    if (!fileId) return 0;
    try {
      // assuming GET /files/{id}
      const res = await axios.get(`${API_BASE}/files/${fileId}`);
      const n =
        res?.data?.downgraded_transaction ??
        res?.data?.downgradedTransactions ??
        0;
      return typeof n === "number" ? n : Number(n) || 0;
    } catch {
      return 0;
    }
  };

  // ---------------------------
  // Load reports from backend
  // ---------------------------
  const loadReports = async () => {
    setReportsLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/reports/all`);
      const raw = res?.data?.reports ?? [];

      // Map to table rows + enrich with downgraded count from files/{source_file}
      const rows: Report[] = await Promise.all(
        raw.map(async (r: any) => {
          // backend may return "source_file_id" or "source_file"
          const sourceId = r?.source_file_id ?? r?.source_file ?? null;
          const downgraded = await fetchFileMeta(sourceId);
          return {
            id: String(r.id),
            fileName: String(r.id), // you asked to show the report id as the "file name"
            date: toYYYYMMDD(r.timestamp),
            downgradedTransactions: downgraded,
            status: "completed",
          };
        })
      );

      // Default sort newest first (desc)
      rows.sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
      setReports(rows);
      setCurrentPage(1);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || "Load failed";
      toast({
        title: "Failed to load reports",
        description: String(detail),
        variant: "destructive",
      });
    } finally {
      setReportsLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------------------------
  // Upload: parent owns API/state
  // ---------------------------
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".csv")) {
      toast({
        title: "Invalid file type",
        description: "Please upload a CSV file.",
        variant: "destructive",
      });
      event.currentTarget.value = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const res = await axios.post(`${API_BASE}/files/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const data = res.data; // { message, file_id, path, brand, downgraded_transaction }
      setUploadedFile(file);
      if (data?.file_id) {
        setLastUploadedFileId(data.file_id);
      }

      toast({
        title: "Upload successful",
        description: `Detected brand: ${data?.brand ?? "unknown"}. File saved.`,
      });
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || "Upload failed";
      toast({
        title: "Upload failed",
        description: String(detail),
        variant: "destructive",
      });
    } finally {
      setUploading(false);
      event.currentTarget.value = ""; // allow same file again
    }
  };

  // ---------------------------
  // Generate report (mock now)
  // Later, call your POST generate endpoint, then reload reports
  // ---------------------------
  const handleGenerateReport = async () => {
    if (!uploadedFile) return;

    setGenerating(true);
    toast({
      title: "Generating report",
      description: `Analyzing ${uploadedFile.name}…`,
    });

    try {
      // Use the most recent successfully uploaded file ID
      const fileId = lastUploadedFileId;

      if (!fileId) {
        toast({
          title: "File ID not found",
          description: "Could not determine uploaded file ID.",
          variant: "destructive",
        });
        setGenerating(false);
        return;
      }

      // Call the real generate endpoint
      await axios.post(`${API_BASE}/reports/generate/${fileId}`);

      // After real generation completes server-side, re-fetch reports:
      await loadReports();

      toast({
        title: "Analysis complete",
        description: "Your transaction analysis is ready.",
      });
      setUploadedFile(null);
      setCurrentPage(1);
    } catch (err: any) {
      if (err?.response?.status === 500) {
        toast({
          title: "Report generation failed",
          description: "A server error occurred (500). The report could not be generated. Please check your file and try again.",
          variant: "destructive",
        });
      } else {
        toast({
          title: "Report generation failed",
          description: err?.response?.data?.detail || err?.message || "Unknown error.",
          variant: "destructive",
        });
      }
    } finally {
      setGenerating(false);
    }
  // Ensure lastUploadedFileId always reflects the most recent successful upload
  useEffect(() => {
    // Optionally, you could fetch /files/all and set the last file ID here if needed
    // But for now, we rely on upload response to set lastUploadedFileId
  }, [uploadedFile]);
  };

  // ---------------------------
  // Sort toggle
  // ---------------------------
  const handleSortToggle = () => {
    setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    setReports((prev) =>
      [...prev].sort((a, b) =>
        sortOrder === "asc"
          ? a.date > b.date ? 1 : a.date < b.date ? -1 : 0
          : a.date < b.date ? 1 : a.date > b.date ? -1 : 0
      )
    );
    setCurrentPage(1);
  };

  // CSV templates (headers match backend validators)
  const mastercardFields = [
    "mc_mti","mc_processing_code","mc_acquirer_bin","mc_issuer_bin","mc_merchant_category_code",
    "mc_merchant_country_code","mc_card_acceptor_id_code","mc_card_acceptor_name_location",
    "mc_transaction_currency_code","mc_settlement_currency_code","mc_transaction_amount","mc_settlement_amount",
    "mc_exchange_rate","mc_presentment_date","mc_pos_entry_mode","mc_eci_indicator","mc_ucaf_collection_indicator",
    "mc_cvv2_result_code","mc_avs_result_code","mc_cross_border_indicator","mc_retrieval_reference_number",
    "mc_auth_id_response","interchange_fee","rate_pct","fixed_fee","mcc_group","downgraded","channel_type",
    "cross_border_flag","eci_3ds_auth"
  ];
  const visaFields = [
    "visa_mti","visa_processing_code","visa_acquirer_bin","visa_issuer_bin","visa_merchant_category_code",
    "visa_merchant_country_code","visa_card_acceptor_id_code","visa_card_acceptor_name_location",
    "visa_transaction_currency_code","visa_settlement_currency_code","visa_transaction_amount","visa_settlement_amount",
    "visa_exchange_rate","visa_presentment_date","visa_pos_entry_mode","visa_eci_indicator","visa_cavv_result_code",
    "visa_cvv2_result_code","visa_avs_result_code","visa_cross_border_indicator","visa_retrieval_reference_number",
    "visa_auth_id_response","visa_arn","visa_interchange_fee","visa_rate_pct","visa_fixed_fee","visa_downgraded",
    "visa_channel_type","merchant_name","issuer_country","visa_transaction_identifier","visa_product_code",
    "visa_cvm_used","visa_pos_condition_code","visa_terminal_capability_code","visa_sca_exemption_reason",
    "visa_region_code","visa_eci_3ds_auth"
  ];

  const handleDownloadFormat = (type: "visa" | "mastercard") => {
    const header = (type === "visa" ? visaFields : mastercardFields).join(",");
    const blob = new Blob([header + "\n"], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${type}_template.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleOpenReport = (reportId: string) => {
  if (!reportId) return;
  window.open(`/interchangeFee-report/${encodeURIComponent(reportId)}`, "_blank", "noopener,noreferrer");
};

  const handleDownloadReport = (reportId: string) => {
  if (!reportId) return;

  // Create a hidden iframe that loads the report page with auto-download enabled.
  const iframe = document.createElement("iframe");
  iframe.style.position = "absolute";
  iframe.style.width = "0";
  iframe.style.height = "0";
  iframe.style.border = "0";
  iframe.style.left = "-9999px";
  iframe.src = `/interchangeFee-report/${encodeURIComponent(
    reportId
  )}?download=1&embed=1`;

  // Cleanup when the iframe tells us it’s done
  const onMsg = (e: MessageEvent) => {
    if (e?.data === "report-pdf-ready") {
      window.removeEventListener("message", onMsg);
      if (iframe.parentNode) iframe.parentNode.removeChild(iframe);
    }
  };
  window.addEventListener("message", onMsg);

  // Fallback cleanup in case something goes wrong (20s)
  const timer = setTimeout(() => {
    window.removeEventListener("message", onMsg);
    if (iframe.parentNode) iframe.parentNode.removeChild(iframe);
  }, 20000);

  // If cleanup ran normally, ensure timer is cleared
  const clear = () => clearTimeout(timer);
  window.addEventListener("message", function once(e) {
    if (e?.data === "report-pdf-ready") {
      window.removeEventListener("message", once as any);
      clear();
    }
  });

  document.body.appendChild(iframe);
};


  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="py-8">
        <div className="container mx-auto px-6 max-w-7xl">
          <ReportsHeader />

          <UploadSection
            onFileUpload={handleFileUpload}
            onDownloadFormat={handleDownloadFormat}
            onGenerateReport={handleGenerateReport}
            uploading={uploading}
            generating={generating}
            uploadedFile={uploadedFile}
          />

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
            loading={reportsLoading || generating}
            perPage={5}
          />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default InterQAdvisor;
