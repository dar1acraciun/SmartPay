import { User, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useState } from "react";

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-6 py-4">
        <nav className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <img 
              src="/smartpay_logo.png" 
              alt="SmartPay Logo" 
              className="h-12 w-auto"
            />
          </div>

          {/* Navigation Links - Desktop */}
          <div className="hidden md:flex items-center space-x-8">
            <a 
              href="/" 
              className="text-foreground hover:text-brand-blue transition-colors font-medium"
            >
              Home
            </a>
            <a 
              href="/interq-advisor" 
              className="text-foreground hover:text-brand-blue transition-colors font-medium"
            >
              InterQ Advisor
            </a>
            <a 
              href="/compliance-checker" 
              className="text-foreground hover:text-brand-blue transition-colors font-medium"
            >
              Compliance Checker
            </a>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <Sheet open={isOpen} onOpenChange={setIsOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="h-6 w-6" />
                  <span className="sr-only">Open menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[300px] sm:w-[400px]">
                <SheetHeader>
                  <SheetTitle>Navigation</SheetTitle>
                </SheetHeader>
                <nav className="flex flex-col space-y-4 mt-8">
                  <a 
                    href="/" 
                    className="text-foreground hover:text-brand-blue transition-colors font-medium py-2"
                    onClick={() => setIsOpen(false)}
                  >
                    Home
                  </a>
                  <a 
                    href="/interq-advisor" 
                    className="text-foreground hover:text-brand-blue transition-colors font-medium py-2"
                    onClick={() => setIsOpen(false)}
                  >
                    InterQ Advisor
                  </a>
                  <a 
                    href="/compliance-checker" 
                    className="text-foreground hover:text-brand-blue transition-colors font-medium py-2"
                    onClick={() => setIsOpen(false)}
                  >
                    Compliance Checker
                  </a>
                  
                  {/* User Section in Mobile Menu */}
                  <div className="pt-6 border-t border-border">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-full bg-brand-light">
                        <User className="h-5 w-5 text-brand-blue" />
                      </div>
                      <span className="text-sm font-medium text-foreground">
                        John Merchant
                      </span>
                    </div>
                  </div>
                </nav>
              </SheetContent>
            </Sheet>
          </div>

          {/* User Section - Desktop */}
          <div className="hidden md:flex items-center space-x-3 pl-6">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-full bg-brand-light">
                <User className="h-5 w-5 text-brand-blue" />
              </div>
              <span className="hidden sm:block text-sm font-medium text-foreground">
                John Merchant
              </span>
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
};

export default Navigation;