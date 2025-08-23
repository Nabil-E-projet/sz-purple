import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { getFrenchError } from '@/lib/errorUtils';
import { motion } from 'framer-motion';
import { 
  CreditCard, 
  Sparkles, 
  Star, 
  Zap, 
  CheckCircle, 
  ArrowRight,
  Shield,
  Clock,
  TrendingUp,
  Award,
  Gift
} from 'lucide-react';

const BuyCredits = () => {
  const [loading, setLoading] = useState<string | null>(null);
  const [billingStatus, setBillingStatus] = useState<any>(null);
  const [credits, setCredits] = useState<number>(0);
  const { toast } = useToast();

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const [statusRes, creditsRes] = await Promise.all([
          api.getBillingStatus(),
          api.getMyCredits()
        ]);
        setBillingStatus(statusRes);
        setCredits(creditsRes.credits || 0);
      } catch (e: any) {
        console.error('Erreur chargement status:', e);
      }
    };
    loadStatus();
  }, []);

  const startCheckout = async (pack: 'single' | 'pack_5' | 'pack_20') => {
    setLoading(pack);
    try {
      const res = await api.createCheckoutSession(pack);
      const url = (res as any)?.checkout_url;
      if (url) {
        window.location.href = url;
      } else {
        throw new Error('URL de paiement indisponible');
      }
    } catch (e: any) {
      const t = getFrenchError(e);
      toast({ title: t.title || 'Erreur', description: t.description || 'Paiement indisponible', variant: t.variant });
    } finally {
      setLoading(null);
    }
  };

  const claimFreeCredit = async () => {
    setLoading('free');
    try {
      const res = await api.getFreeCreditsDailyBonus();
      toast({ title: 'Succès !', description: '1 crédit gratuit ajouté à votre compte' });
      setCredits(res.new_credits || credits + 1);
      
      // Forcer le refresh des crédits dans la navbar
      window.dispatchEvent(new CustomEvent('creditsUpdated'));
    } catch (e: any) {
      const t = getFrenchError(e);
      toast({ 
        title: t.title || 'Déjà réclamé', 
        description: t.description || 'Vous avez déjà réclamé votre crédit gratuit aujourd\'hui',
        variant: t.variant,
      });
    } finally {
      setLoading(null);
    }
  };

  const simulatePayment = async (pack: 'single' | 'pack_5' | 'pack_20') => {
    setLoading(`sim_${pack}`);
    try {
      const res = await api.simulatePayment(pack);
      toast({ title: 'Test réussi !', description: `${res.message} (Mode test)` });
      setCredits(res.new_credits || credits);
      
      // Forcer le refresh des crédits dans la navbar
      window.dispatchEvent(new CustomEvent('creditsUpdated'));
    } catch (e: any) {
      const t = getFrenchError(e);
      toast({ title: t.title || 'Erreur test', description: t.description || 'Simulation échouée', variant: t.variant });
    } finally {
      setLoading(null);
    }
  };

  const plans = [
    {
      id: 'single',
      name: '1 Crédit',
      description: 'Pour une analyse ponctuelle',
      price: '1,99€',
      credits: 1,
      icon: Zap,
      color: 'from-blue-500 to-cyan-500',
      features: ['1 analyse complète', 'Rapport détaillé', 'Support par email'],
      popular: false
    },
    {
      id: 'pack_5',
      name: 'Pack Essentiel',
      description: 'Le choix optimal pour commencer',
      price: '4,90€',
      originalPrice: '9,95€',
      credits: 5,
      icon: Star,
      color: 'from-purple-500 to-pink-500',
      features: ['5 analyses complètes', 'Économie de 51%', 'Rapports détaillés', 'Support prioritaire'],
      popular: true,
      savings: '5,05€'
    },
    {
      id: 'pack_20',
      name: 'Pack Professionnel',
      description: 'Pour les utilisateurs réguliers',
      price: '15,90€',
      originalPrice: '39,80€',
      credits: 20,
      icon: Award,
      color: 'from-orange-500 to-red-500',
      features: ['20 analyses complètes', 'Économie de 60%', 'Analyses prioritaires', 'Support VIP', 'Historique illimité'],
      popular: false,
      savings: '23,90€'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Hero Section */}
      <div className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center justify-center mb-6">
              <div className="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center mb-4">
                <CreditCard className="w-8 h-8 text-primary-foreground" />
              </div>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-6">
              Rechargez vos crédits
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
              Analysez vos fiches de paie avec notre IA avancée. Chaque analyse consomme 1 crédit et vous donne un rapport complet.
            </p>
            
            {/* Current Credits Display */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="inline-flex items-center bg-gradient-primary rounded-full px-6 py-3 mb-8"
            >
              <Sparkles className="w-5 h-5 text-primary-foreground mr-2" />
              <span className="text-primary-foreground font-semibold">
                Vous avez {credits} crédit{credits > 1 ? 's' : ''} disponible{credits > 1 ? 's' : ''}
              </span>
            </motion.div>
          </motion.div>

          {/* Status Alerts */}
          {billingStatus && !billingStatus.stripe_configured && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="max-w-2xl mx-auto mb-8"
            >
              <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center mr-4">
                    <Shield className="w-5 h-5 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-red-800">Configuration requise</h3>
                    <p className="text-red-700">Les paiements ne sont pas encore configurés. Contactez l'administrateur.</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Crédit gratuit quotidien */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="max-w-md mx-auto mb-8"
          >
            <Card className="glass-card border-2 border-green-200 bg-gradient-to-r from-green-50 to-emerald-50">
              <CardContent className="p-6 text-center">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <Gift className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-green-800 mb-2">Crédit gratuit quotidien</h3>
                <p className="text-sm text-green-700 mb-4">Réclamez 1 crédit gratuit par jour !</p>
                <Button
                  onClick={claimFreeCredit}
                  disabled={loading === 'free'}
                  className="bg-gradient-to-r from-green-500 to-emerald-500 hover:opacity-90 text-white border-0"
                >
                  {loading === 'free' ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                      Réclamation...
                    </>
                  ) : (
                    <>
                      <Gift className="w-4 h-4 mr-2" />
                      Réclamer
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="pb-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                className="relative"
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                    <Badge className="bg-gradient-primary text-primary-foreground px-4 py-1 rounded-full">
                      <Star className="w-4 h-4 mr-1" />
                      Le plus populaire
                    </Badge>
                  </div>
                )}
                
                <Card className={`glass-card border-0 h-full flex flex-col transition-all duration-300 hover:scale-105 hover:shadow-2xl ${
                  plan.popular ? 'ring-2 ring-primary/20 shadow-xl' : ''
                }`}>
                  <CardHeader className="text-center pb-6 pt-8 flex-shrink-0">
                    <div className={`w-20 h-20 bg-gradient-to-br ${plan.color} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg`}>
                      <plan.icon className="w-10 h-10 text-white" />
                    </div>
                    <CardTitle className="text-2xl font-bold mb-2">{plan.name}</CardTitle>
                    <p className="text-muted-foreground">{plan.description}</p>
                    
                    {plan.savings && (
                      <div className="mt-3">
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                          <TrendingUp className="w-3 h-3 mr-1" />
                          Économisez {plan.savings}
                        </Badge>
                      </div>
                    )}
                  </CardHeader>
                  
                  <CardContent className="flex-1 flex flex-col">
                    {/* Price */}
                    <div className="text-center mb-6">
                      <div className="flex items-baseline justify-center gap-2">
                        <span className="text-4xl font-bold text-foreground">{plan.price}</span>
                        {plan.originalPrice && (
                          <span className="text-lg text-muted-foreground line-through">{plan.originalPrice}</span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {plan.credits} crédit{plan.credits > 1 ? 's' : ''} • {(parseFloat(plan.price.replace(',', '.').replace('€', '')) / plan.credits).toFixed(2)}€ par crédit
                      </p>
                    </div>

                    {/* Features */}
                    <ul className="space-y-3 flex-1 mb-6">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="flex items-start text-sm">
                          <CheckCircle className="w-4 h-4 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                          <span className="leading-5">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    {/* CTA Buttons - Alignés en bas */}
                    <div className="space-y-3 mt-auto">
                      <Button 
                        size="lg"
                        className={`w-full h-12 font-semibold ${
                          plan.popular 
                            ? 'bg-gradient-primary hover:opacity-90 border-0 shadow-lg text-white' 
                            : 'bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700 text-white border-0 shadow-lg'
                        } transition-all duration-300 group`}
                        disabled={loading === plan.id || (billingStatus && !billingStatus.stripe_configured)} 
                        onClick={() => startCheckout(plan.id as 'single' | 'pack_5' | 'pack_20')}
                      >
                        {loading === plan.id ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                            Redirection...
                          </>
                        ) : (
                          <>
                            Acheter maintenant
                            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                          </>
                        )}
                      </Button>
                      
                      {/* Bouton de test (développement) */}
                      {billingStatus && !billingStatus.stripe_configured && (
                        <Button 
                          size="sm"
                          variant="outline"
                          className="w-full h-10 border-2 border-blue-200 text-blue-700 hover:bg-blue-50"
                          disabled={loading === `sim_${plan.id}`}
                          onClick={() => simulatePayment(plan.id as 'single' | 'pack_5' | 'pack_20')}
                        >
                          {loading === `sim_${plan.id}` ? 'Test...' : '🧪 Test (Mode démo)'}
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="pb-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold mb-4">Pourquoi choisir Salariz ?</h2>
            <p className="text-muted-foreground">Une analyse complète et professionnelle de vos fiches de paie</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: Sparkles,
                title: 'IA Avancée',
                description: 'Notre intelligence artificielle analyse chaque détail de votre fiche de paie avec précision'
              },
              {
                icon: Shield,
                title: 'Sécurisé',
                description: 'Vos données sont protégées et traitées en toute confidentialité'
              },
              {
                icon: Clock,
                title: 'Instantané',
                description: 'Obtenez votre analyse complète en moins de 30 secondes'
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 + index * 0.1, duration: 0.6 }}
                className="glass-card p-6 text-center hover:scale-105 transition-all duration-300"
              >
                <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-6 h-6 text-primary-foreground" />
                </div>
                <h3 className="font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyCredits;


