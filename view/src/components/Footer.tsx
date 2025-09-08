const Footer = () => {
  return (
    <footer className="border-t border-border bg-background">
      <div className="container mx-auto px-6 py-12">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center space-y-8 lg:space-y-0">
          {/* Logo and Description */}
          <div className="space-y-4 max-w-md">
            <div className="text-xl font-bold text-brand-orange">
              SmartPay
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              AI-powered payment processing solutions for modern merchants. 
              Optimize interchange fees and ensure compliance with intelligent automation.
            </p>
          </div>

          {/* Links */}
          <div className="grid grid-cols-2 gap-8 lg:gap-16">
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-brand-blue">Products</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="/interq-advisor" className="text-muted-foreground hover:text-brand-blue transition-colors">
                    InterQ Advisor
                  </a>
                </li>
                <li>
                  <a href="/compliance-checker" className="text-muted-foreground hover:text-brand-blue transition-colors">
                    Compliance Checker
                  </a>
                </li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-brand-blue">Company</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="/about" className="text-muted-foreground hover:text-brand-blue transition-colors">
                    About
                  </a>
                </li>
                <li>
                  <a href="/contact" className="text-muted-foreground hover:text-brand-blue transition-colors">
                    Contact
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="border-t border-border mt-8 pt-8">
          <p className="text-xs text-muted-foreground text-center">
            © 2025 SmartPay. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;