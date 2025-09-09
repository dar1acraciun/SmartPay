import { Search } from "lucide-react";

const ReportsHeader = () => {
  return (
    <div className="mb-8 text-center">
      <h1 className="text-3xl lg:text-4xl font-bold text-brand-blue mb-4 flex items-center justify-center gap-3">
        <Search className="h-8 w-8 lg:h-10 lg:w-10" />
        InterQ Advisor
      </h1>
      <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
       Upload your transaction files to get AI-powered analysis of qualification, downgrades, and compliance risks. Identify savings opportunities and minimize costly downgrades.
      </p>
    </div>
  );
};

export default ReportsHeader;