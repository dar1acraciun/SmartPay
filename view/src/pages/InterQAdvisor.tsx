import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

const InterQAdvisor = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <main className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center space-y-4">
            <h1 className="text-4xl lg:text-5xl font-bold text-brand-blue">
              InterQ Advisor
            </h1>
            <p className="text-lg text-brand-charcoal max-w-2xl mx-auto">
              AI-powered interchange fee optimization coming soon.
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default InterQAdvisor;