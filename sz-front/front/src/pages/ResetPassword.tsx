import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Lock, ArrowLeft, KeyRound, CheckCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/api/apiClient';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const [formData, setFormData] = useState({
    new_password: '',
    confirm_password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      toast({
        title: "Lien invalide",
        description: "Le lien de réinitialisation est invalide ou manquant.",
        variant: "destructive"
      });
      navigate('/forgot-password');
    }
  }, [token, navigate, toast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.new_password !== formData.confirm_password) {
      toast({
        title: "Erreur",
        description: "Les mots de passe ne correspondent pas.",
        variant: "destructive"
      });
      return;
    }

    if (!token) return;

    setIsLoading(true);

    try {
      const response = await apiClient.resetPassword({
        token,
        new_password: formData.new_password,
        confirm_password: formData.confirm_password
      });
      
      setIsSuccess(true);
      toast({
        title: "Mot de passe réinitialisé",
        description: response.message || "Votre mot de passe a été modifié avec succès.",
      });

    } catch (err: any) {
      let errorMsg = 'Une erreur est survenue';
      
      if (err?.response?.data) {
        const errorData = err.response.data;
        if (errorData.error) {
          errorMsg = errorData.error;
        } else if (errorData.new_password) {
          errorMsg = `Mot de passe: ${errorData.new_password.join(', ')}`;
        } else if (errorData.confirm_password) {
          errorMsg = `Confirmation: ${errorData.confirm_password.join(', ')}`;
        }
      } else if (err?.error) {
        errorMsg = err.error;
      }
      
      toast({
        title: "Erreur",
        description: errorMsg,
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen relative">
        <div className="absolute inset-0 bg-gradient-hero opacity-10"></div>

        <div className="min-h-screen flex items-center justify-center px-4 pt-24 pb-16">
          <div className="relative w-full max-w-md">
            <Card className="glass-card border-0 animate-fade-in-up">
              <CardHeader className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  </div>
                </div>
                <CardTitle className="text-2xl text-foreground">
                  Mot de passe réinitialisé !
                </CardTitle>
                <CardDescription>
                  Vous pouvez maintenant vous connecter
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="text-center space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Votre mot de passe a été modifié avec succès. Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.
                  </p>
                  
                  <div className="glass-card border-glass-border/30 p-4 rounded-lg">
                    <div className="text-sm font-medium text-foreground mb-2">
                      🔐 Conseils de sécurité :
                    </div>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• Utilisez un gestionnaire de mots de passe</li>
                      <li>• Ne partagez jamais votre mot de passe</li>
                      <li>• Activez l'authentification à deux facteurs si disponible</li>
                    </ul>
                  </div>
                </div>

                <div className="space-y-3">
                  <Button 
                    onClick={() => navigate('/login')} 
                    className="w-full bg-gradient-primary hover:opacity-90 border-0"
                  >
                    Se connecter maintenant
                  </Button>
                  
                  <Button 
                    onClick={() => navigate('/')} 
                    variant="outline" 
                    className="w-full glass-card border-glass-border/30"
                  >
                    Retour à l'accueil
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
          to="/forgot-password" 
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border-glass-border/30 text-foreground hover:text-primary hover:bg-primary/5 transition-all duration-200 group backdrop-blur-sm shadow-lg"
        >
          <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          <span className="font-medium">Retour</span>
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
                Nouveau mot de passe
              </CardTitle>
              <CardDescription>
                Choisissez un mot de passe sécurisé pour votre compte
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="new_password">Nouveau mot de passe</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      id="new_password"
                      type="password"
                      placeholder="••••••••"
                      className="pl-10 glass-card border-glass-border/30"
                      value={formData.new_password}
                      onChange={(e) => setFormData({ ...formData, new_password: e.target.value })}
                      required
                      autoComplete="new-password"
                      autoFocus
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirmer le mot de passe</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      id="confirm_password"
                      type="password"
                      placeholder="••••••••"
                      className="pl-10 glass-card border-glass-border/30"
                      value={formData.confirm_password}
                      onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                      required
                      autoComplete="new-password"
                    />
                  </div>
                </div>

                <div className="glass-card border-glass-border/30 p-4 rounded-lg">
                  <div className="text-sm text-muted-foreground space-y-2">
                    <div className="font-medium text-foreground mb-2">🔒 Critères de sécurité :</div>
                    <ul className="text-xs space-y-1">
                      <li>• Au moins 8 caractères</li>
                      <li>• Mélange de majuscules et minuscules</li>
                      <li>• Au moins un chiffre</li>
                      <li>• Au moins un caractère spécial</li>
                    </ul>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-gradient-primary hover:opacity-90 border-0"
                  disabled={isLoading || !formData.new_password || !formData.confirm_password}
                >
                  {isLoading ? "Modification en cours..." : "Changer le mot de passe"}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <div className="text-sm text-muted-foreground">
                  <Link to="/login" className="text-primary hover:underline font-medium">
                    Retour à la connexion
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

export default ResetPassword;
