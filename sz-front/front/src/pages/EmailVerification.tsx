import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Mail, 
  CheckCircle, 
  AlertTriangle, 
  RefreshCw,
  ArrowLeft
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '@/lib/api';

const EmailVerification = () => {
  const [email, setEmail] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleResendEmail = async () => {
    if (!email.trim()) {
      setError('Veuillez saisir votre adresse email');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      await api.resendVerificationEmail(email);
      
      setSuccess('Un nouvel email de vérification a été envoyé ! Vérifiez votre boîte de réception.');
      
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Aucun compte non vérifié trouvé avec cette adresse email.');
      } else {
        setError(err.response?.data?.error || 'Erreur lors de l\'envoi de l\'email de vérification.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 pt-20 pb-12">
      <div className="container mx-auto px-4">
        <div className="max-w-md mx-auto">
          
          {/* En-tête */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-full bg-gradient-primary flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-primary-foreground" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Vérification d'email
            </h1>
            <p className="text-gray-600">
              Renvoyer l'email de vérification pour activer votre compte
            </p>
          </div>

          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-6">
              <CardTitle className="text-lg font-semibold text-center">
                Compte non vérifié ?
              </CardTitle>
              <CardDescription className="text-center">
                Si vous n'avez pas reçu l'email de vérification ou s'il a expiré, 
                vous pouvez en demander un nouveau.
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Messages d'alerte */}
              {error && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              {success && (
                <Alert className="border-green-200 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    {success}
                  </AlertDescription>
                </Alert>
              )}

              {/* Formulaire */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                    Adresse email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="votre.email@exemple.com"
                    className="mt-2 h-12"
                    disabled={loading}
                  />
                </div>

                <Button 
                  onClick={handleResendEmail}
                  disabled={loading || !email.trim()}
                  className="w-full h-12"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Envoi en cours...
                    </>
                  ) : (
                    <>
                      <Mail className="w-4 h-4 mr-2" />
                      Renvoyer l'email de vérification
                    </>
                  )}
                </Button>
              </div>

              {/* Instructions */}
              <div className="bg-blue-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-900 mb-2">
                  💡 Conseils
                </h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Vérifiez votre dossier spam/indésirables</li>
                  <li>• L'email peut prendre quelques minutes à arriver</li>
                  <li>• Le lien de vérification est valable 24 heures</li>
                </ul>
              </div>

              {/* Lien retour */}
              <div className="text-center pt-4">
                <Link 
                  to="/login" 
                  className="inline-flex items-center text-sm text-gray-600 hover:text-primary transition-colors"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Retour à la connexion
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default EmailVerification;
