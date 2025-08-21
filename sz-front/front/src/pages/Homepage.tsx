import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { 
  FileText, 
  Shield, 
  BarChart3, 
  CheckCircle, 
  AlertTriangle, 
  TrendingUp,
  Upload,
  Eye,
  Download
} from 'lucide-react';

const Homepage = () => {
  const features = [
    {
      icon: Shield,
      title: 'Détection d\'erreurs automatique',
      description: 'Notre IA analyse chaque ligne de votre fiche de paie pour détecter les erreurs de calcul et les non-conformités.'
    },
    {
      icon: BarChart3,
      title: 'Conformité légale',
      description: 'Vérification automatique de la conformité avec la convention collective et la réglementation en vigueur.'
    },
    {
      icon: TrendingUp,
      title: 'Rapport détaillé',
      description: 'Recevez un rapport complet avec recommandations et pistes d\'amélioration personnalisées.'
    }
  ];

  const analysisSteps = [
    {
      icon: Upload,
      title: 'Téléchargez',
      description: 'Importez votre fiche de paie en PDF ou image'
    },
    {
      icon: Eye,
      title: 'Analysez',
      description: 'Notre IA traite et vérifie automatiquement'
    },
    {
      icon: Download,
      title: 'Téléchargez',
      description: 'Récupérez votre rapport d\'analyse détaillé'
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 hero-gradient opacity-20"></div>
        <div className="relative max-w-7xl mx-auto">
          <div className="text-center animate-fade-in-up">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-primary bg-clip-text text-transparent">
                Analysez vos fiches de paie
              </span>
              <br />
              <span className="text-foreground">avec l'intelligence artificielle</span>
            </h1>
            <p className="text-sm text-muted-foreground mb-2">par <span className="font-semibold">Salariz</span></p>
            <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              Détectez automatiquement les erreurs, vérifiez la conformité légale et obtenez 
              des recommandations personnalisées pour vos fiches de paie.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/upload">
                <Button size="lg" className="bg-gradient-primary hover:opacity-90 border-0 px-8 py-6 text-lg font-semibold">
                  Commencer l'analyse
                  <FileText className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Link to="/login">
                <Button variant="outline" size="lg" className="btn-glass px-8 py-6 text-lg">
                  Se connecter
                </Button>
              </Link>
            </div>
          </div>

          {/* Preview mockup */}
          <div className="mt-16 animate-float">
            <div className="glass-card p-8 max-w-4xl mx-auto rounded-2xl">
              <div className="bg-gradient-card rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold">Analyse en cours...</h3>
                  <div className="flex space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse delay-75"></div>
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse delay-150"></div>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="glass-card p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-sm font-medium">Conformité</span>
                    </div>
                    <div className="text-2xl font-bold text-green-500">87%</div>
                  </div>
                  <div className="glass-card p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <AlertTriangle className="w-5 h-5 text-yellow-500" />
                      <span className="text-sm font-medium">Alertes</span>
                    </div>
                    <div className="text-2xl font-bold text-yellow-500">3</div>
                  </div>
                  <div className="glass-card p-4 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <TrendingUp className="w-5 h-5 text-primary" />
                      <span className="text-sm font-medium">Score global</span>
                    </div>
                    <div className="text-2xl font-bold text-primary">8.5/10</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-primary bg-clip-text text-transparent">
              Fonctionnalités principales
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Une analyse complète et automatisée de vos fiches de paie
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="glass-card border-0 hover:scale-105 transition-all duration-300">
                <CardContent className="p-8 text-center">
                  <div className="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <feature.icon className="w-8 h-8 text-primary-foreground" />
                  </div>
                  <h3 className="text-xl font-semibold mb-4">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-card">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-primary bg-clip-text text-transparent">
              Comment ça marche ?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Un processus simple en 3 étapes pour analyser votre fiche de paie
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {analysisSteps.map((step, index) => (
              <div key={index} className="text-center">
                <div className="relative">
                  <div className="w-20 h-20 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-6">
                    <step.icon className="w-10 h-10 text-primary-foreground" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-accent rounded-full flex items-center justify-center text-sm font-bold text-accent-foreground">
                    {index + 1}
                  </div>
                </div>
                <h3 className="text-xl font-semibold mb-4">{step.title}</h3>
                <p className="text-muted-foreground">{step.description}</p>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link to="/upload">
              <Button size="lg" className="bg-gradient-primary hover:opacity-90 border-0 px-8 py-6 text-lg font-semibold">
                Essayer maintenant
                <FileText className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Homepage;