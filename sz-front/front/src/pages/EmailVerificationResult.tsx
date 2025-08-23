import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  CheckCircle, 
  AlertTriangle, 
  Loader2,
  Home,
  LogIn
} from 'lucide-react';

const EmailVerificationResult = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    const token = searchParams.get('token');
    const redirectToken = searchParams.get('redirect_token');
    const statusParam = searchParams.get('status');
    
    const actualToken = redirectToken || token;
    
    if (!actualToken) {
      setStatus('error');
      setMessage('Token de vérification manquant');
      return;
    }

    // Si on a un redirect_token, faire l'appel API pour vérifier
    if (redirectToken) {
      const verifyEmail = async () => {
        try {
          const response = await fetch(`http://localhost:8000/api/verify-email/?token=${encodeURIComponent(redirectToken)}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          const data = await response.json();

          if (response.ok) {
            setStatus('success');
            setMessage(data.message || 'Email vérifié avec succès');
          } else {
            setStatus('error');
            setMessage(data.error || 'Erreur lors de la vérification');
          }
        } catch (error) {
          setStatus('error');
          setMessage('Erreur de connexion lors de la vérification');
        }
      };

      verifyEmail();
      return;
    }

    // Gérer les différents statuts depuis l'URL (ancien système)
    switch (statusParam) {
      case 'success':
        setStatus('success');
        setMessage('Email vérifié avec succès');
        break;
      case 'expired':
        setStatus('error');
        setMessage('Le lien de vérification a expiré (valable 24 heures)');
        break;
      case 'invalid':
        setStatus('error');
        setMessage('Le lien de vérification est invalide');
        break;
      case 'not_found':
        setStatus('error');
        setMessage('Utilisateur non trouvé');
        break;
      default:
        // Si pas de statut dans l'URL, faire l'appel API classique
        const verifyEmail = async () => {
          try {
            const response = await fetch(`http://localhost:8000/api/verify-email/?token=${encodeURIComponent(actualToken)}`, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
              },
            });

            const data = await response.json();

            if (response.ok) {
              setStatus('success');
              setMessage(data.message || 'Email vérifié avec succès');
            } else {
              setStatus('error');
              setMessage(data.error || 'Erreur lors de la vérification');
            }
          } catch (error) {
            setStatus('error');
            setMessage('Erreur de connexion lors de la vérification');
          }
        };

        verifyEmail();
        break;
    }
  }, [searchParams]);

  const renderContent = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-4">
              <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Vérification en cours...
            </h1>
            <p className="text-gray-600">
              Nous vérifions votre adresse email
            </p>
          </div>
        );

      case 'success':
        return (
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Email vérifié avec succès ! 🎉
            </h1>
            <p className="text-gray-600 mb-6">
              Votre compte Salariz est maintenant actif. Vous pouvez vous connecter et commencer à analyser vos fiches de paie.
            </p>
            
            <div className="space-y-3">
              <Link to="/login">
                <Button className="w-full">
                  <LogIn className="w-4 h-4 mr-2" />
                  Se connecter maintenant
                </Button>
              </Link>
              
              <Link to="/home">
                <Button variant="outline" className="w-full">
                  <Home className="w-4 h-4 mr-2" />
                  Retour à l'accueil
                </Button>
              </Link>
            </div>
          </div>
        );

      case 'error':
        return (
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Erreur de vérification
            </h1>
            <p className="text-gray-600 mb-6">
              {message}
            </p>
            
            <div className="space-y-3">
              <Link to="/email-verification">
                <Button className="w-full">
                  Renvoyer un email de vérification
                </Button>
              </Link>
              
              <Link to="/login">
                <Button variant="outline" className="w-full">
                  Retour à la connexion
                </Button>
              </Link>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-medium text-blue-900 mb-2">
                💡 Causes possibles
              </h3>
              <ul className="text-sm text-blue-800 space-y-1 text-left">
                <li>• Le lien a expiré (valable 24h)</li>
                <li>• Le lien a déjà été utilisé</li>
                <li>• Le token de vérification est invalide</li>
              </ul>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 pt-20 pb-12">
      <div className="container mx-auto px-4">
        <div className="max-w-md mx-auto">
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-6">
              <CardTitle className="text-lg font-semibold text-center">
                Vérification d'email
              </CardTitle>
              <CardDescription className="text-center">
                Activation de votre compte Salariz
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              {renderContent()}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default EmailVerificationResult;
