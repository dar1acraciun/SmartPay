import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Shield, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

const FeaturesSection = () => {
  return (
    <section className="py-20 bg-brand-light/50">
      <div className="container mx-auto px-6">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-brand-blue">
            How can we help?
          </h2>
          <p className="text-lg text-brand-charcoal max-w-2xl mx-auto">
            Our AI-powered platform delivers two powerful tools to optimize payment
            processing and protect your bottom line.
          </p>
        </div>

        {/* Z-Layout Design */}
        <div className="space-y-20 max-w-7xl mx-auto">
          {/* InterQ Advisor - Left Content, Right Visual */}
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <div className="space-y-6 text-center lg:text-left">
              <div className="w-14 h-14 bg-brand-teal/10 rounded-xl flex items-center justify-center mx-auto lg:mx-0">
                <Brain className="h-7 w-7 text-brand-teal" />
              </div>
              <div className="space-y-4">
                <h3 className="text-2xl lg:text-3xl font-bold text-brand-blue">
                  InterQ Advisor
                </h3>
                <p className="text-lg text-brand-charcoal leading-relaxed">
                  InterQ Advisor automatically analyzes your transactions, identifies downgrade risks, and shows you how to optimize qualification rates.
                  Cut costs without lifting a finger - let AI spot hidden savings opportunities in real time.
                </p>
              </div>
              <div className="flex justify-center lg:justify-start">
                <Button
                  asChild
                  variant="outline"
                  size="lg"
                  className="border-brand-teal text-brand-teal hover:bg-brand-teal hover:text-white transition-colors group"
                >
                  <Link to="/interq-advisor">
                    Unlock Savings
                    <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </Button>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-brand-teal/10 to-brand-teal/5 rounded-xl p-4 sm:p-6 flex items-center justify-center">
                <img 
                  src="/feature-section-1.svg" 
                  alt="Cost savings and optimization illustration" 
                  className="w-2/3 max-w-[220px] h-auto object-contain"
                />
              </div>
            </div>
          </div>

          {/* Compliance Checker - Right Content, Left Visual */}
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <div className="relative lg:order-1 order-2">
              <div className="bg-gradient-to-br from-brand-orange/10 to-brand-orange/5 rounded-xl p-4 sm:p-6 flex items-center justify-center">
                <img 
                  src="/feature-section-2.svg" 
                  alt="Financial growth and compliance monitoring illustration" 
                  className="w-2/3 max-w-[220px] h-auto object-contain"
                />
              </div>
            </div>
            <div className="space-y-6 lg:order-2 order-1 text-center lg:text-left">
              <div className="w-14 h-14 bg-brand-orange/10 rounded-xl flex items-center justify-center mx-auto lg:mx-0">
                <Shield className="h-7 w-7 text-brand-orange" />
              </div>
              <div className="space-y-4">
                <h3 className="text-2xl lg:text-3xl font-bold text-brand-blue">
                  Compliance Checker
                </h3>
                <p className="text-lg text-brand-charcoal leading-relaxed">
                  Our tool validates every transaction against scheme rules — in real time.
                  By preventing errors before they happen, you’ll avoid costly downgrades, penalties, and 
                  lost processing privileges while maintaining customer trust.
                </p>
              </div>
              <div className="flex justify-center lg:justify-start">
                <Button
                  asChild
                  variant="outline"
                  size="lg"
                  className="border-brand-orange text-brand-orange hover:bg-brand-orange hover:text-white transition-colors group"
                >
                  <Link to="/compliance-checker">
                    Check Compliance
                    <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
