import React, { useEffect, useRef, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";

/** ---- PALETA ---- */
const PALETTE = {
  ORANGE: "#D5520B",     // Syracuse Red Orange
  TEAL: "#14B8A6",       // Keppel
  CHARCOAL: "#374151",   // Charcoal
  BLUE: "#1E3A8A",       // Marian Blue
  WHITE: "#F3F4F6",      // Anti-flash white
};
const BORDER_RGBA = "rgba(55, 65, 81, 0.18)"; // CHARCOAL @ ~18%

/** ---- TIPURI DE DATE (după API-ul /report/{id}) ---- */
type Feature = {
  feature_name: string;
  feature_reason: string;
  importance_normalized: string;
};
type TransactionFeature = {
  feature_name: string;
  feature_value: string;
  feature_reason: string;
  importance_normalized: string;
};
type Tx = {
  transaction_index: string;
  predicted_fee: string;
  actual_fee: string;
  downgrade: boolean;
  transaction_features: TransactionFeature[];
};
type ReportData = {
  overall: { features: Feature[] };
  per_transaction: Tx[];
};

const InterchangeFeeReport: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const reportRef = useRef<HTMLDivElement>(null);
  const [searchParams] = useSearchParams();
  const autoDownload = searchParams.get("download") === "1";
  const [data, setData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  /** ---- FETCH /report/{id} ---- */
  useEffect(() => {
    if (!id) {
      setError("Lipsește id-ul din URL.");
      setLoading(false);
      return;
    }
    const ac = new AbortController();
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(`http://localhost:8000/reports/${id}`);
        if (!res.ok) throw new Error(`Request failed (${res.status})`);
        const json: ReportData = await res.json();
        setData(json);
      } catch (e: any) {
        if (e.name !== "AbortError") setError(e.message || "Eroare la încărcare.");
      } finally {
        setLoading(false);
      }
    })();
    return () => ac.abort();
  }, [id]);

  useEffect(() => {
  if (!autoDownload) return;
  if (!data) return;                  // wait for API
  if (!reportRef.current) return;     // wait for DOM

  // Give the charts a beat to paint before snapshotting
  const t = setTimeout(() => {
    handleDownloadPDF();
  }, 350);

  return () => clearTimeout(t);
}, [autoDownload, data]);


  /** ---- EXPORT PDF ---- */
  const handleDownloadPDF = async () => {
    if (!reportRef.current) return;
    const canvas = await html2canvas(reportRef.current, { scale: 2 });
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const imgWidth = pageWidth;
    const imgHeight = (canvas.height * pageWidth) / canvas.width;
    let position = 0;
    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
    let remainingHeight = imgHeight;
    while (remainingHeight > pageHeight) {
      position -= pageHeight;
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      remainingHeight -= pageHeight;
    }
    pdf.save("InterchangeFeeReport.pdf");
  };

  /** ---- UI: loading / error ---- */
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center"
           style={{ backgroundColor: PALETTE.WHITE, color: PALETTE.CHARCOAL }}>
        Generating report...
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center"
           style={{ backgroundColor: PALETTE.WHITE }}>
        <div className="px-4 py-3 rounded-lg"
             style={{ color: PALETTE.WHITE, backgroundColor: PALETTE.ORANGE }}>
          {error ?? "Could not load report data."}
        </div>
      </div>
    );
  }

  /** ---- PRELUCRARE DATE PENTRU CHARTS ---- */
  const overallFeatureData = data.overall.features.map((f) => ({
    name: f.feature_name.replace(/mc_|_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
    importance: parseFloat(f.importance_normalized),
    reason: f.feature_reason
  }));

  const transactionComparisonData = data.per_transaction.map((t) => {
    const totalImportance = t.transaction_features.reduce(
      (sum, f) => sum + parseFloat(f.importance_normalized), 0
    );
    return {
      name: `Transaction ${parseInt(t.transaction_index) + 1}`,
      importance: totalImportance,
      features: t.transaction_features.length
    };
  });

  const PIE_COLORS = [PALETTE.ORANGE, PALETTE.TEAL, PALETTE.BLUE, PALETTE.CHARCOAL];
  const tickStyle = { fill: PALETTE.CHARCOAL };

  const formatFeatureName = (name: string) =>
    name.replace(/mc_|_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());

  /** ---- RENDER ---- */
  return (
    <div>
      {/* Download button */}
      <div className="flex justify-end max-w-7xl mx-auto pt-8">
        <button
          onClick={handleDownloadPDF}
          className="mb-4 px-4 py-2 rounded-lg shadow hover:opacity-90 transition"
          style={{ backgroundColor: PALETTE.BLUE, color: PALETTE.WHITE }}
        >
          Download PDF
        </button>
      </div>

      <div
        ref={reportRef}
        className="max-w-7xl mx-auto p-8 min-h-screen"
        style={{ backgroundColor: PALETTE.WHITE, color: PALETTE.CHARCOAL }}
      >
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-4">Interchange Fee Analysis Report</h1>
          <p className="text-lg max-w-3xl mx-auto" style={{ opacity: 0.9 }}>
            Comprehensive analysis of feature importance in interchange fee determination,
            examining both overall patterns and individual transaction characteristics.
          </p>
        </div>

        {/* Executive Summary */}
        <div className="rounded-xl p-6 mb-8" style={{ border: `1px solid ${BORDER_RGBA}`, backgroundColor: PALETTE.WHITE }}>
          <h2 className="text-2xl font-bold mb-4">Executive Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-lg p-4" style={{ border: `1px solid ${BORDER_RGBA}` }}>
              <h3 className="font-semibold" style={{ color: PALETTE.BLUE }}>Total Features Analyzed</h3>
              <p className="text-3xl font-bold" style={{ color: PALETTE.BLUE }}>{data.overall.features.length}</p>
            </div>
            <div className="rounded-lg p-4" style={{ border: `1px solid ${BORDER_RGBA}` }}>
              <h3 className="font-semibold" style={{ color: PALETTE.TEAL }}>Transactions Reviewed</h3>
              <p className="text-3xl font-bold" style={{ color: PALETTE.TEAL }}>{data.per_transaction.length}</p>
            </div>
            <div className="rounded-lg p-4" style={{ border: `1px solid ${BORDER_RGBA}` }}>
              <h3 className="font-semibold" style={{ color: PALETTE.ORANGE }}>Primary Driver</h3>
              <p className="text-lg font-bold" style={{ color: PALETTE.ORANGE }}>Channel Type (65%)</p>
            </div>
          </div>
        </div>

        {/* Overall Feature Importance */}
        <div className="rounded-xl p-6 mb-8" style={{ border: `1px solid ${BORDER_RGBA}`, backgroundColor: PALETTE.WHITE }}>
          <h2 className="text-2xl font-bold mb-6">Overall Feature Importance</h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Bar Chart */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Importance Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={overallFeatureData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={BORDER_RGBA} />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} tick={tickStyle} />
                  <YAxis tick={tickStyle} />
                  <Tooltip formatter={(v: any) => `${(Number(v) * 100).toFixed(1)}%`} />
                  <Bar dataKey="importance" fill={PALETTE.TEAL} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Pie Chart */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Relative Impact</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={overallFeatureData.filter((d) => d.importance > 0.01)}
                    cx="50%" cy="50%" outerRadius={80} dataKey="importance"
                    label={({ name, value }) => `${name}: ${(Number(value) * 100).toFixed(1)}%`}
                  >
                    {overallFeatureData.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any) => `${(Number(value) * 100).toFixed(2)}%`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Feature Details Table */}
          <div className="mt-8">
            <h3 className="text-lg font-semibold mb-4">Feature Analysis Details</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse" style={{ border: `1px solid ${BORDER_RGBA}` }}>
                <thead>
                  <tr style={{ backgroundColor: PALETTE.WHITE }}>
                    <th className="px-4 py-2 text-left" style={{ borderBottom: `1px solid ${BORDER_RGBA}` }}>Feature</th>
                    <th className="px-4 py-2 text-left" style={{ borderBottom: `1px solid ${BORDER_RGBA}` }}>Importance</th>
                    <th className="px-4 py-2 text-left" style={{ borderBottom: `1px solid ${BORDER_RGBA}` }}>Business Impact</th>
                  </tr>
                </thead>
                <tbody>
                  {data.overall.features.map((feature, index) => {
                    const importance = parseFloat(feature.importance_normalized);
                    return (
                      <tr key={index}>
                        <td className="px-4 py-2 font-medium" style={{ borderTop: `1px solid ${BORDER_RGBA}` }}>
                          {formatFeatureName(feature.feature_name)}
                        </td>
                        <td className="px-4 py-2" style={{ borderTop: `1px solid ${BORDER_RGBA}` }}>
                          <div className="flex items-center">
                            <div className="w-16 h-2 mr-2 rounded-full" style={{ backgroundColor: BORDER_RGBA }}>
                              <div className="h-2 rounded-full" style={{ width: `${importance * 100}%`, backgroundColor: PALETTE.BLUE }} />
                            </div>
                            {(importance * 100).toFixed(1)}%
                          </div>
                        </td>
                        <td className="px-4 py-2 text-sm" style={{ borderTop: `1px solid ${BORDER_RGBA}` }}>
                          {feature.feature_reason}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Transaction Analysis */}
        <div className="rounded-xl p-6 mb-8" style={{ border: `1px solid ${BORDER_RGBA}`, backgroundColor: PALETTE.WHITE }}>
          <h2 className="text-2xl font-bold mb-6">Transaction-Level Analysis</h2>

          {/* Transaction Comparison */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4">Transaction Risk Comparison</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={transactionComparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke={BORDER_RGBA} />
                <XAxis dataKey="name" tick={tickStyle} />
                <YAxis tick={tickStyle} />
                <Tooltip
                  formatter={(value: any, name: any) => [
                    name === "importance" ? `${(Number(value) * 100).toFixed(1)}%` : value,
                    name === "importance" ? "Total Risk Score" : "Features Count"
                  ]}
                />
                <Bar dataKey="importance" name="importance" fill={PALETTE.BLUE} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Individual Transaction Details */}
          <div className="space-y-6">
            {data.per_transaction.map((t, idx) => (
              <div key={idx} className="rounded-lg p-6" style={{ border: `1px solid ${BORDER_RGBA}` }}>
                <h3 className="text-xl font-semibold mb-4">Transaction {parseInt(t.transaction_index) + 1} Analysis</h3>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Key Features */}
                  <div>
                    <h4 className="font-semibold mb-3">Key Features</h4>
                    <div className="space-y-3">
                      {t.transaction_features.map((f, i) => (
                        <div key={i} className="rounded-lg p-3" style={{ backgroundColor: PALETTE.WHITE, border: `1px solid ${BORDER_RGBA}` }}>
                          <div className="flex justify-between items-center mb-2">
                            <span className="font-medium text-sm">{formatFeatureName(f.feature_name)}</span>
                            <span className="text-lg font-bold" style={{ color: PALETTE.TEAL }}>
                              {(parseFloat(f.importance_normalized) * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="text-xs mb-2"><strong>Value:</strong> {f.feature_value}</div>
                          <div className="text-xs">{f.feature_reason}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Transaction Summary */}
                  <div>
                    <h4 className="font-semibold mb-3">Transaction Summary</h4>
                    <div className="rounded-lg p-4" style={{ backgroundColor: PALETTE.WHITE, border: `1px solid ${BORDER_RGBA}` }}>
                      <div className="mb-3">
                        <span className="text-sm">Total Risk Score:</span>
                        <span className="text-2xl font-bold" style={{ color: PALETTE.BLUE, marginLeft: 8 }}>
                          {(t.transaction_features.reduce((s, f) => s + parseFloat(f.importance_normalized), 0) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="mb-3">
                        <span className="text-sm">Active Features:</span>
                        <span className="text-lg font-semibold" style={{ marginLeft: 8 }}>
                          {t.transaction_features.length}
                        </span>
                      </div>
                      <div className="mb-3">
                        <span className="text-sm">Predicted Fee:</span>
                        <span className="text-lg font-semibold" style={{ marginLeft: 8, color: PALETTE.TEAL }}>
                          {t.predicted_fee} RON
                        </span>
                      </div>
                      <div className="mb-3">
                        <span className="text-sm">Actual Fee:</span>
                        <span className="text-lg font-semibold" style={{ marginLeft: 8, color: PALETTE.BLUE }}>
                          {t.actual_fee} RON
                        </span>
                      </div>
                      <div className="mb-1">
                        <span className="text-sm">Downgrade:</span>
                        <span
                          className="ml-2 px-2 py-1 rounded text-xs font-semibold"
                          style={{
                            backgroundColor: t.downgrade ? PALETTE.ORANGE : PALETTE.TEAL,
                            color: PALETTE.WHITE
                          }}
                        >
                          {t.downgrade ? "True" : "False"}
                        </span>
                      </div>
                      {/* Fără risk category (conform cerinței) */}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Insights & Recommendations */}
        <div className="rounded-xl p-6" style={{ border: `1px solid ${BORDER_RGBA}`, backgroundColor: PALETTE.WHITE }}>
          <h2 className="text-2xl font-bold mb-6">Key Insights & Recommendations</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="rounded-lg p-4" style={{ backgroundColor: PALETTE.ORANGE, color: PALETTE.WHITE }}>
              <h3 className="font-semibold mb-2">🔍 Primary Risk Drivers</h3>
              <ul className="text-sm space-y-1">
                <li>• Channel Type dominates with 65% importance</li>
                <li>• CVV2 verification contributes 20% to risk assessment</li>
                <li>• Cross-border transactions add 10% risk premium</li>
              </ul>
            </div>

            <div className="rounded-lg p-4" style={{ backgroundColor: PALETTE.TEAL, color: PALETTE.WHITE }}>
              <h3 className="font-semibold mb-2">💡 Optimization Opportunities</h3>
              <ul className="text-sm space-y-1">
                <li>• Implement stronger CVV2 validation processes</li>
                <li>• Focus on channel-specific fraud prevention</li>
                <li>• Enhanced authentication for cross-border transactions</li>
              </ul>
            </div>

            <div className="rounded-lg p-4" style={{ backgroundColor: PALETTE.CHARCOAL, color: PALETTE.WHITE }}>
              <h3 className="font-semibold mb-2">📊 Transaction Patterns</h3>
              <ul className="text-sm space-y-1">
                <li>• E-commerce transactions show higher risk profiles</li>
                <li>• Card-present transactions demonstrate lower risk</li>
                <li>• CVV2 matching significantly reduces interchange fees</li>
              </ul>
            </div>

            <div className="rounded-lg p-4" style={{ backgroundColor: PALETTE.BLUE, color: PALETTE.WHITE }}>
              <h3 className="font-semibold mb-2">🎯 Strategic Focus Areas</h3>
              <ul className="text-sm space-y-1">
                <li>• Invest in channel security improvements</li>
                <li>• Strengthen cardholder authentication methods</li>
                <li>• Monitor cross-border transaction patterns closely</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterchangeFeeReport;
