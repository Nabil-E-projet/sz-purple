import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle, ArrowRight, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import Homepage from './Homepage';

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [credits, setCredits] = useState<number | null>(null);
  const paymentStatus = searchParams.get('payment');

  useEffect(() => {
    const loadCreditsAndCheckPayments = async () => {
      try {
        // Vérifier et finaliser les paiements en attente
        await api.checkPaymentStatus();
        
        // Charger les crédits mis à jour
        const res = await api.getMyCredits();
        setCredits(res.credits);
        
        // Informer la navbar des crédits mis à jour
        window.dispatchEvent(new CustomEvent('creditsUpdated'));
      } catch (e) {
        console.error('Erreur chargement crédits:', e);
      }
    };
    
    // Si pas de paramètre payment, rediriger vers homepage
    if (!paymentStatus) {
      return;
    }
    
    loadCreditsAndCheckPayments();
  }, [paymentStatus]);

  // Si pas de paramètre payment, afficher la homepage
  if (!paymentStatus) {
    return <Homepage />;
  }

  if (paymentStatus === 'cancel') {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-background via-background to-red-500/5">
        <div className="max-w-2xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Card className="glass-card border-red-200">
              <CardContent className="p-8">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <div className="text-red-600 text-2xl">❌</div>
                </div>
                <h1 className="text-2xl font-bold text-red-800 mb-4">Paiement annulé</h1>
                <p className="text-red-600 mb-6">Votre paiement a été annulé. Aucun montant n'a été débité.</p>
                <div className="space-y-3">
                  <Button onClick={() => navigate('/buy-credits')} className="w-full">
                    Réessayer l'achat
                  </Button>
                  <Button variant="outline" onClick={() => navigate('/dashboard')} className="w-full">
                    Retour au dashboard
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-background via-background to-green-500/5">
      <div className="max-w-2xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Card className="glass-card border-green-200">
            <CardContent className="p-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                className="w-20 h-20 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6"
              >
                <CheckCircle className="w-10 h-10 text-white" />
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4, duration: 0.6 }}
              >
                <h1 className="text-3xl font-bold text-green-800 mb-4">
                  Paiement réussi ! 🎉
                </h1>
                <p className="text-green-700 mb-6">
                  Votre paiement a été traité avec succès. Vos crédits ont été ajoutés à votre compte.
                </p>
                
                {credits !== null && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.6, duration: 0.5 }}
                    className="bg-gradient-primary rounded-full px-6 py-3 inline-flex items-center mb-6"
                  >
                    <Sparkles className="w-5 h-5 text-primary-foreground mr-2" />
                    <span className="text-primary-foreground font-semibold">
                      Vous avez maintenant {credits} crédit{credits > 1 ? 's' : ''}
                    </span>
                  </motion.div>
                )}
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.6 }}
                className="space-y-3"
              >
                <Button 
                  onClick={() => navigate('/upload')} 
                  className="w-full bg-gradient-primary hover:opacity-90 border-0 group"
                  size="lg"
                >
                  Commencer une analyse
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => navigate('/dashboard')} 
                  className="w-full"
                >
                  Voir mes analyses
                </Button>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default PaymentSuccess;
