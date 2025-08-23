import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Mail, Lock, User, ArrowLeft } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/context/AuthContext';

const LoginPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  const { login, register } = useAuth();
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ username: '', email: '', password: '', password_confirm: '' });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await login({ username: loginForm.username, password: loginForm.password });
      toast({ title: "Connexion réussie", description: "Bienvenue sur Salariz" });
      navigate('/dashboard');
    } catch (err: any) {
      const msg = err?.error?.detail || err?.error?.message || 'Identifiants invalides';
      toast({ title: 'Erreur de connexion', description: String(msg) });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await register(registerForm);
      toast({
        title: 'Compte créé',
        description: "Vérifiez votre email pour activer votre compte",
      });
    } catch (err: any) {
      // Gestion spéciale pour les comptes non vérifiés
      if (err?.response?.status === 200 && err?.response?.data?.message) {
        toast({
          title: 'Email de vérification envoyé',
          description: err.response.data.message,
        });
        // Rediriger vers la page de vérification d'email
        navigate('/email-verification');
        return;
      }
      
      // Gestion des erreurs de validation
      const errorData = err?.response?.data;
      if (errorData && typeof errorData === 'object') {
        const errors = [];
        if (errorData.username) errors.push(`Nom d'utilisateur: ${errorData.username.join(', ')}`);
        if (errorData.email) errors.push(`Email: ${errorData.email.join(', ')}`);
        if (errorData.password) errors.push(`Mot de passe: ${errorData.password.join(', ')}`);
        
        if (errors.length > 0) {
          toast({
            title: 'Erreur de validation',
            description: errors.join(' | '),
            variant: 'destructive'
          });
          return;
        }
      }
      
      const msg = err?.error || 'Erreur lors de la création du compte';
      toast({ 
        title: 'Erreur', 
        description: typeof msg === 'string' ? msg : JSON.stringify(msg),
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative">
      <div className="absolute inset-0 bg-gradient-hero opacity-10"></div>
      
      {/* Enhanced back button - positioned below navbar */}
      <div className="absolute top-20 left-6 z-50">
        <Link 
          to="/" 
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card border-glass-border/30 text-foreground hover:text-primary hover:bg-primary/5 transition-all duration-200 group backdrop-blur-sm shadow-lg"
        >
          <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          <span className="font-medium">Accueil</span>
        </Link>
      </div>
      
      <div className="min-h-screen flex items-center justify-center px-4 pt-24 pb-16">
        <div className="relative w-full max-w-md">

          <Card className="glass-card border-0 animate-fade-in-up">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center">
                  <FileText className="w-6 h-6 text-primary-foreground" />
                </div>
              </div>
              <CardTitle className="text-2xl bg-gradient-primary bg-clip-text text-transparent">
                Salariz
              </CardTitle>
              <CardDescription>
                Connectez-vous pour accéder à vos analyses
              </CardDescription>
            </CardHeader>

          <CardContent>
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2 glass-card">
                <TabsTrigger value="login">Connexion</TabsTrigger>
                <TabsTrigger value="register">Inscription</TabsTrigger>
              </TabsList>

              <TabsContent value="login" className="mt-6">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Nom d'utilisateur</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="username"
                        type="text"
                        placeholder="votre identifiant"
                        className="pl-10 glass-card border-glass-border/30"
                        value={loginForm.username}
                        onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Mot de passe</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="password"
                        type="password"
                        placeholder="••••••••"
                        className="pl-10 glass-card border-glass-border/30"
                        value={loginForm.password}
                        onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full bg-gradient-primary hover:opacity-90 border-0"
                    disabled={isLoading}
                  >
                    {isLoading ? "Connexion..." : "Se connecter"}
                  </Button>

                  <div className="text-center">
                    <Link to="/forgot-password" className="text-sm text-primary hover:underline font-medium">
                      Mot de passe oublié ?
                    </Link>
                  </div>
                </form>
              </TabsContent>

              <TabsContent value="register" className="mt-6">
                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="usernameReg">Nom d'utilisateur</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="usernameReg"
                        type="text"
                        placeholder="votre identifiant"
                        className="pl-10 glass-card border-glass-border/30"
                        value={registerForm.username}
                        onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="registerEmail">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="registerEmail"
                        type="email"
                        placeholder="votre@email.com"
                        className="pl-10 glass-card border-glass-border/30"
                        value={registerForm.email}
                        onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="registerPassword">Mot de passe</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="registerPassword"
                        type="password"
                        placeholder="••••••••"
                        className="pl-10 glass-card border-glass-border/30"
                        value={registerForm.password}
                        onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirmer le mot de passe</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="confirmPassword"
                        type="password"
                        placeholder="••••••••"
                        className="pl-10 glass-card border-glass-border/30"
                        value={registerForm.password_confirm}
                        onChange={(e) => setRegisterForm({ ...registerForm, password_confirm: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full bg-gradient-primary hover:opacity-90 border-0"
                    disabled={isLoading}
                  >
                    {isLoading ? "Création..." : "Créer un compte"}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            <div className="mt-6 text-center space-y-3">
              <div className="text-sm text-muted-foreground">
                <Link to="/email-verification" className="text-primary hover:underline font-medium">
                  📧 Problème avec la vérification d'email ?
                </Link>
              </div>
              
              <div className="text-sm text-muted-foreground">
                En continuant, vous acceptez nos{' '}
                <Link to="/terms" className="text-primary hover:underline">
                  conditions d'utilisation
                </Link>{' '}
                et notre{' '}
                <Link to="/privacy" className="text-primary hover:underline">
                  politique de confidentialité
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

export default LoginPage;