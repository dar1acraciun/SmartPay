import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

const HeroSection = () => {
  return (
    <section className="py-10 lg:py-32 text-center lg:text-left">
      <div className="container mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Content */}
          <div className="space-y-8 flex flex-col items-center lg:items-start">
            <div className="space-y-6">
              <h1 className="text-4xl lg:text-6xl font-bold text-brand-blue leading-tight">
                Discover SmartPay
              </h1>
              <p className="text-lg lg:text-xl text-brand-charcoal leading-relaxed max-w-lg mx-auto lg:mx-0">
                We help your business with AI-driven payment intelligence to qualify for the
                lowest possible interchange fees, reduce penalties, and process every transaction
                with confidence.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Button
                asChild
                size="lg"
                className="bg-brand-orange hover:bg-brand-orange-hover text-white font-semibold px-8 py-4 rounded-lg transition-colors"
              >
                <Link to="/interq-advisor">
                  Start Saving Now
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
            </div>
          </div>

          {/* Illustration */}
          <div className="flex justify-center">
            <img
              src="/hero-credit-card.svg"
              alt="AI Payment Processing Illustration"
              className="w-2/3 sm:w-1/2 lg:w-3/4 h-auto object-contain"
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
