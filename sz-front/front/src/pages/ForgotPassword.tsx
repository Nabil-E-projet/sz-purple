import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Mail, ArrowLeft, KeyRound } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/api/apiClient';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isEmailSent, setIsEmailSent] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await apiClient.requestPasswordReset({ email });
      
      setIsEmailSent(true);
      toast({
        title: "Email envoyé",
        description: response.message || "Si cette adresse email est associée à un compte, vous recevrez un lien de réinitialisation.",
      });

    } catch (err: any) {
      const errorMsg = err?.error || err?.response?.data?.error || 'Une erreur est survenue';
      toast({
        title: "Erreur",
        description: errorMsg,
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isEmailSent) {
    return (
      <div className="min-h-screen relative">
        <div className="absolute inset-0 bg-gradient-hero opacity-10"></div>
        
        {/* Back button */}
        <div className="absolute top-20 left-6 z-50">
          <Link 
            to="/login" 
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border-glass-border/30 text-foreground hover:text-primary hover:bg-primary/5 transition-all duration-200 group backdrop-blur-sm shadow-lg"
          >
            <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
            <span className="font-medium">Connexion</span>
          </Link>
        </div>

        <div className="min-h-screen flex items-center justify-center px-4 pt-24 pb-16">
          <div className="relative w-full max-w-md">
            <Card className="glass-card border-0 animate-fade-in-up">
              <CardHeader className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center">
                    <Mail className="w-6 h-6 text-green-500" />
                  </div>
                </div>
                <CardTitle className="text-2xl text-foreground">
                  Email envoyé !
                </CardTitle>
                <CardDescription>
                  Vérifiez votre boîte de réception
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="text-center space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Si cette adresse email est associée à un compte Salariz, vous devriez recevoir un lien de réinitialisation dans les prochaines minutes.
                  </p>
                  
                  <div className="glass-card border-glass-border/30 p-4 rounded-lg">
                    <div className="text-sm font-medium text-foreground mb-2">
                      🕒 N'oubliez pas de vérifier :
                    </div>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• Votre dossier spam/courrier indésirable</li>
                      <li>• L'onglet Promotions (Gmail)</li>
                      <li>• Le lien expire dans <strong>1 heure</strong></li>
                    </ul>
                  </div>
                </div>

                <div className="space-y-3">
                  <Button 
                    onClick={() => setIsEmailSent(false)} 
                    variant="outline" 
                    className="w-full glass-card border-glass-border/30"
                  >
                    Essayer une autre adresse
                  </Button>
                  
                  <Button 
                    onClick={() => navigate('/login')} 
                    className="w-full bg-gradient-primary hover:opacity-90 border-0"
                  >
                    Retour à la connexion
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <div className="absolute inset-0 bg-gradient-hero opacity-10"></div>
      
      {/* Back button */}
      <div className="absolute top-20 left-6 z-50">
        <Link 
          to="/login" 
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border-glass-border/30 text-foreground hover:text-primary hover:bg-primary/5 transition-all duration-200 group backdrop-blur-sm shadow-lg"
        >
          <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          <span className="font-medium">Connexion</span>
        </Link>
      </div>

      <div className="min-h-screen flex items-center justify-center px-4 pt-24 pb-16">
        <div className="relative w-full max-w-md">
          <Card className="glass-card border-0 animate-fade-in-up">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center">
                  <KeyRound className="w-6 h-6 text-primary-foreground" />
                </div>
              </div>
              <CardTitle className="text-2xl bg-gradient-primary bg-clip-text text-transparent">
                Mot de passe oublié
              </CardTitle>
              <CardDescription>
                Entrez votre adresse email pour recevoir un lien de réinitialisation
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Adresse email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="votre@email.com"
                      className="pl-10 glass-card border-glass-border/30"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      autoComplete="email"
                      autoFocus
                    />
                  </div>
                </div>

                <div className="glass-card border-glass-border/30 p-4 rounded-lg">
                  <div className="text-sm text-muted-foreground space-y-2">
                    <div className="font-medium text-foreground mb-2">📋 Conditions :</div>
                    <ul className="text-xs space-y-1">
                      <li>• Votre compte doit être actif et vérifié</li>
                      <li>• Le lien sera valable 1 heure seulement</li>
                      <li>• Vérifiez vos spams si vous ne recevez rien</li>
                    </ul>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-gradient-primary hover:opacity-90 border-0"
                  disabled={isLoading}
                >
                  {isLoading ? "Envoi en cours..." : "Envoyer le lien de réinitialisation"}
                </Button>
              </form>

              <div className="mt-6 text-center space-y-3">
                <div className="text-sm text-muted-foreground">
                  Vous vous souvenez de votre mot de passe ?{' '}
                  <Link to="/login" className="text-primary hover:underline font-medium">
                    Se connecter
                  </Link>
                </div>
                
                <div className="text-sm text-muted-foreground">
                  Pas encore de compte ?{' '}
                  <Link to="/login" className="text-primary hover:underline font-medium">
                    S'inscrire
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
