import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Menu, X, FileText, User, LogOut } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();
  const { isAuthenticated, logout } = useAuth();
  const [credits, setCredits] = useState<number | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        if (isAuthenticated) {
          const res = await api.getMyCredits();
          setCredits(res.credits ?? 0);
        } else {
          setCredits(null);
        }
      } catch {
        setCredits(null);
      }
    };
    run();

    // Écouter les mises à jour de crédits
    const handleCreditsUpdate = () => {
      if (isAuthenticated) {
        run();
      }
    };
    
    window.addEventListener('creditsUpdated', handleCreditsUpdate);
    return () => window.removeEventListener('creditsUpdated', handleCreditsUpdate);
  }, [isAuthenticated]);

  const navItems = [
    { name: 'Accueil', href: '/home', icon: FileText },
    { name: 'Tableau de bord', href: '/dashboard', icon: User, authRequired: true },
    { name: 'Nouvelle Analyse', href: '/upload', icon: FileText, authRequired: true },
  ];

  const filteredNavItems = navItems.filter(item => 
    !item.authRequired || isAuthenticated
  );

  return (
    <nav className="glass-nav fixed w-full top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/home" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-bold text-xl bg-gradient-primary bg-clip-text text-transparent">
                Salariz
              </span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {filteredNavItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  location.pathname === item.href
                    ? 'text-primary bg-primary/10'
                    : 'text-foreground hover:text-primary hover:bg-primary/5'
                }`}
              >
                {item.name}
              </Link>
            ))}
            
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                {typeof credits === 'number' && (
                  <Link to="/buy-credits" className="px-3 py-2 rounded-md text-sm font-medium bg-primary/10 text-primary">
                    Crédits: {credits}
                  </Link>
                )}
                <div className="w-8 h-8 rounded-full bg-gradient-primary flex items-center justify-center">
                  <User className="w-4 h-4 text-primary-foreground" />
                </div>
                <Button variant="ghost" size="sm" onClick={() => logout()}>
                  <LogOut className="w-4 h-4 mr-2" />
                  Déconnexion
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    Se connecter
                  </Button>
                </Link>
                <Link to="/upload">
                  <Button size="sm" className="bg-gradient-primary hover:opacity-90 border-0">
                    Commencer
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              className="p-2"
            >
              {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden absolute top-16 left-0 right-0 bg-background border border-border shadow-lg animate-fade-in-up">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {filteredNavItems.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`block px-3 py-2 rounded-md text-base font-medium transition-all duration-200 ${
                    location.pathname === item.href
                      ? 'text-primary bg-primary/10'
                      : 'text-foreground hover:text-primary hover:bg-primary/5'
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  <div className="flex items-center space-x-2">
                    <item.icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </div>
                </Link>
              ))}
              
              <div className="pt-4 border-t border-border">
                {isAuthenticated ? (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => {
                      logout();
                      setIsOpen(false);
                    }}
                    className="w-full justify-start px-3 py-2"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Déconnexion
                  </Button>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="block px-3 py-2 text-base font-medium text-foreground hover:text-primary"
                      onClick={() => setIsOpen(false)}
                    >
                      Se connecter
                    </Link>
                    <Link
                      to="/upload"
                      className="block px-3 py-2 text-base font-medium"
                      onClick={() => setIsOpen(false)}
                    >
                      <Button size="sm" className="w-full bg-gradient-primary hover:opacity-90 border-0">
                        Commencer
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;