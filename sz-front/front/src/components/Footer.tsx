import { Link } from 'react-router-dom';
import { FileText, Shield, BarChart3, Upload, Eye, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';

const Footer = () => {
  const { isAuthenticated } = useAuth();

  return (
    <footer className="mt-16 border-t border-border/40">
      <div className="glass-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Brand & Description */}
            <div className="space-y-4">
              <Link to="/home" className="flex items-center gap-3 group">
                <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
                  <FileText className="w-5 h-5 text-primary-foreground" />
                </div>
                <div>
                  <span className="font-bold text-xl bg-gradient-primary bg-clip-text text-transparent">
                    Salariz
                  </span>
                  <p className="text-xs text-muted-foreground">Analyse IA de fiches de paie</p>
                </div>
              </Link>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Détection d'erreurs automatique et vérification de conformité pour vos bulletins de salaire.
              </p>
              <div className="flex items-center gap-2 text-xs text-primary">
                <Shield className="w-4 h-4" />
                <span>Sécurisé & Conforme RGPD</span>
              </div>
            </div>

            {/* Navigation */}
            <div className="space-y-4">
              <h3 className="font-semibold text-foreground">Navigation</h3>
              <nav className="space-y-2">
                <Link to="/home" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors group">
                  <Eye className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  Accueil
                </Link>
                <Link to="/upload" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors group">
                  <Upload className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  Nouvelle analyse
                </Link>
                {isAuthenticated && (
                  <>
                    <Link to="/dashboard" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors group">
                      <BarChart3 className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Tableau de bord
                    </Link>
                    <Link to="/buy-credits" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors group">
                      <FileText className="w-4 h-4 group-hover:scale-110 transition-transform" />
                      Acheter des crédits
                    </Link>
                  </>
                )}
              </nav>
            </div>

            {/* Features & Stats */}
            <div className="space-y-4">
              <h3 className="font-semibold text-foreground">Fonctionnalités</h3>
              <div className="space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                  Détection d'erreurs automatique
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                  Vérification de conformité
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                  Rapports détaillés
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                  Support multi-conventions
                </div>
              </div>
            </div>
          </div>

          {/* Bottom bar */}
          <div className="border-t border-border/40 mt-8 pt-6">
            {/* CTA Button */}
            <div className="flex justify-center mb-6">
              <Link to="/upload">
                <Button className="bg-gradient-primary hover:opacity-90 text-primary-foreground px-6 py-2 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group">
                  <Zap className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                  Analyser maintenant
                </Button>
              </Link>
            </div>
            
            {/* Footer info */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <p className="text-sm text-muted-foreground">
                © {new Date().getFullYear()} Salariz. Tous droits réservés.
              </p>
              <div className="flex items-center gap-4">
                <Link to="/buy-credits" className="text-xs text-primary hover:text-primary/80 transition-colors">
                  Acheter des crédits
                </Link>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <span>Propulsé par l'IA</span>
                  <div className="w-2 h-2 bg-gradient-primary rounded-full animate-pulse"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;