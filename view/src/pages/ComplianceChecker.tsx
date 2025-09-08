import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

const ComplianceChecker = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center space-y-4">
            <h1 className="text-4xl lg:text-5xl font-bold text-brand-blue">
              Compliance Checker
            </h1>
            <p className="text-lg text-brand-charcoal max-w-2xl mx-auto">
              Automated scheme compliance validation coming soon.
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default ComplianceChecker;