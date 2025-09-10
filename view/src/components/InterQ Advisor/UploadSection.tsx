import { useRef } from "react";
import {
  Upload,
  Info,
  Loader2,
  Check,
  ChevronDown,
  CreditCard,
  Lightbulb,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export interface UploadSectionProps {
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onDownloadFormat: (type: "visa" | "mastercard") => void;
  onGenerateReport: () => void;
  uploading?: boolean;
  generating?: boolean;
  uploadedFile?: File | null;
}

const UploadSection = ({
  onFileUpload,
  onDownloadFormat,
  onGenerateReport,
  uploading = false,
  generating = false,
  uploadedFile,
}: UploadSectionProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <Card className="mb-8 border-2 border-muted shadow-lg">
      <CardHeader className="bg-gradient-to-r from-brand-blue/5 to-brand-teal/5 border-b">
        <CardTitle className="text-xl font-semibold text-brand-orange flex items-center gap-2">
          Need some transaction-related advice?
        </CardTitle>
        <p className="text-sm text-muted-foreground mt-2">
          Upload your CSV file containing transaction data for analysis and
          optimization insights.
        </p>
      </CardHeader>

      <CardContent className="pt-6">
        {!uploadedFile ? (
          // Initial upload state
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <input
              type="file"
              ref={fileInputRef}
              onChange={onFileUpload}
              accept=".csv"
              className="hidden"
              disabled={uploading}
            />

            <Button
              onClick={() => !uploading && fileInputRef.current?.click()}
              className="bg-brand-orange hover:bg-brand-orange/90 text-white flex items-center gap-2 shadow-md"
              size="lg"
              disabled={uploading}
            >
              {uploading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
              {uploading ? "Uploading…" : "Upload Transactions for Analysis"}
            </Button>

            <div className="flex items-center gap-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    className="border-brand-teal text-brand-teal hover:bg-brand-teal hover:text-white flex items-center gap-2"
                    size="lg"
                    disabled={uploading}
                  >
                    <Lightbulb className="h-4 w-4" />
                    Download CSV Template
                    <ChevronDown className="h-4 w-4 ml-auto mt-0.5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem
                    onClick={() => onDownloadFormat("visa")}
                    className="flex items-center gap-2"
                  >
                    <CreditCard className="h-4 w-4" />
                    Visa Format (first column must start with <code>visa_</code>)
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onDownloadFormat("mastercard")}
                    className="flex items-center gap-2"
                  >
                    <CreditCard className="h-4 w-4" />
                    Mastercard Format (first column must start with{" "}
                    <code>mc_</code>)
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      disabled={uploading}
                    >
                      <Info className="h-4 w-4 text-muted-foreground" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="right" className="max-w-xs">
                    <p className="text-sm">
                      <span className="font-medium">Important:</span> the first
                      column name must indicate the brand (<code>mc_…</code> for
                      Mastercard or <code>visa_…</code> for Visa). Your file
                      must include the required headers for that brand.
                    </p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          </div>
        ) : (
          // Uploaded file state with generate button
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-brand-teal">
                <Check className="h-5 w-5" />
                <span className="font-medium">{uploadedFile.name}</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <input
                type="file"
                ref={fileInputRef}
                onChange={onFileUpload}
                accept=".csv"
                className="hidden"
                disabled={generating}
              />
              <Button
                onClick={() => !generating && fileInputRef.current?.click()}
                variant="outline"
                size="lg"
                disabled={generating}
                className="border-gray-300 text-gray-600 hover:bg-gray-50"
              >
                Upload Different File
              </Button>

              <Button
                onClick={onGenerateReport}
                className="bg-brand-orange hover:bg-brand-orange-hover text-white flex items-center gap-2 shadow-md"
                size="lg"
                disabled={generating}
              >
                {generating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : null}
                {generating ? "Generating…" : "Generate Report"}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UploadSection;
