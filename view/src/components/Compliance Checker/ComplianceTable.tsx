import { ChevronDown, ChevronUp, FileText, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Pagination, PaginationContent, PaginationEllipsis, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";

export interface ComplianceFile {
  id: string;
  fileName: string;
  date: string;
  transactions: Array<{
    id: string;
    riskLevel: "High" | "Medium" | "Low";
    findings: string[];
  }>;
}

interface ComplianceTableProps {
  files: ComplianceFile[];
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  sortOrder: "asc" | "desc";
  onSortToggle: () => void;
  currentPage: number;
  setCurrentPage: (page: number) => void;
  onCheckCompliance: (file: ComplianceFile) => void;
  loading?: boolean;
  perPage?: number;
}

export default function ComplianceTable({
  files,
  searchTerm,
  setSearchTerm,
  sortOrder,
  onSortToggle,
  currentPage,
  setCurrentPage,
  onCheckCompliance,
  loading = false,
  perPage = 10,
}: ComplianceTableProps) {
  
  // Filter + sort
  const filtered = files
    .filter((f) => f.fileName.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => {
      const da = new Date(a.date).getTime();
      const db = new Date(b.date).getTime();
      return sortOrder === "asc" ? da - db : db - da;
    });

  const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));
  const start = (currentPage - 1) * perPage;
  const pageSlice = filtered.slice(start, start + perPage);

  // Keep current page in range when filtering
  if (currentPage > totalPages && totalPages !== 0) {
    setCurrentPage(totalPages);
  }

  // Compute compact page list with ellipsis
  const pages = getPageList(currentPage, totalPages);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <CardTitle className="text-xl font-semibold text-brand-blue">
            Your Uploaded Transaction Data
          </CardTitle>
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search files…"
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-10"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-b border-border">
                <TableHead className="font-semibold text-brand-charcoal">File name</TableHead>
                <TableHead className="font-semibold text-brand-charcoal">
                  <Button
                    variant="ghost"
                    onClick={onSortToggle}
                    className="h-auto p-0 font-semibold text-brand-charcoal hover:text-brand-blue flex items-center gap-1"
                  >
                    Date
                    {sortOrder === "asc" ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </TableHead>
                <TableHead className="font-semibold text-brand-charcoal text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading && (
                <TableRow>
                  <TableCell colSpan={3} className="py-10 text-center text-muted-foreground">
                    Loading…
                  </TableCell>
                </TableRow>
              )}

              {!loading && pageSlice.map((file) => (
                <TableRow key={file.id} className="hover:bg-muted/50">
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-brand-teal" />
                      {file.fileName}
                    </div>
                  </TableCell>

                  <TableCell className="text-muted-foreground">
                    {new Date(file.date).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}
                  </TableCell>

                  <TableCell className="text-right">
                    <Button
                      onClick={() => onCheckCompliance(file)}
                      variant="outline"
                      size="sm"
                      className="border-brand-blue text-brand-blue hover:bg-brand-blue hover:text-white"
                    >
                      Check Compliance
                    </Button>
                  </TableCell>
                </TableRow>
              ))}

              {!loading && pageSlice.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3} className="py-10 text-center text-muted-foreground">
                    No files found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center py-6 border-t border-border">
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious 
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                  />
                </PaginationItem>
                
                {pages.map((p, i) =>
                  p === "…" ? (
                    <PaginationItem key={`e-${i}`}>
                      <PaginationEllipsis />
                    </PaginationItem>
                  ) : (
                    <PaginationItem key={p}>
                      <PaginationLink
                        onClick={() => setCurrentPage(p)}
                        isActive={currentPage === p}
                        className="cursor-pointer"
                      >
                        {p}
                      </PaginationLink>
                    </PaginationItem>
                  )
                )}
                
                <PaginationItem>
                  <PaginationNext 
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    className={currentPage === totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        )}
        
      </CardContent>
    </Card>
  );
}

/** Returns a compact page list like: [1,2,3,4,5] or [1,'…',4,5,6,'…',20] */
function getPageList(current: number, total: number): Array<number | "…"> {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages = new Set<number>();
  pages.add(1);
  pages.add(2);
  pages.add(total - 1);
  pages.add(total);
  pages.add(current);
  if (current - 1 > 2) pages.add(current - 1);
  if (current + 1 < total - 1) pages.add(current + 1);

  const sorted = Array.from(pages).sort((a, b) => a - b);
  const out: Array<number | "…"> = [];
  for (let i = 0; i < sorted.length; i++) {
    out.push(sorted[i]);
    const next = sorted[i + 1];
    if (next && next - sorted[i] > 1) out.push("…");
  }
  return out;
}
