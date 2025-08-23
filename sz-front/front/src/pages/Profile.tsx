import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  User, 
  Mail, 
  Calendar, 
  Clock,
  CreditCard,
  CheckCircle,
  AlertTriangle,
  Save,
  Shield
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';

const Profile = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // États pour le formulaire d'édition
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: ''
  });

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProfile();
      setProfileData(data);
      setFormData({
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        username: data.username || ''
      });
    } catch (err: any) {
      setError('Impossible de charger les informations du profil');
      console.error('Erreur lors du chargement du profil:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      await api.updateProfile(formData);
      
      // Recharger les données
      await loadProfile();
      setIsEditing(false);
      setSuccess('Profil mis à jour avec succès');
      
      // Effacer le message de succès après 3 secondes
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      first_name: profileData?.first_name || '',
      last_name: profileData?.last_name || '',
      username: profileData?.username || ''
    });
    setIsEditing(false);
    setError(null);
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-1/3 mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="h-64 bg-gray-300 rounded"></div>
              <div className="h-64 bg-gray-300 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 pt-20 pb-12">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          {/* En-tête */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 rounded-full bg-gradient-primary flex items-center justify-center mx-auto mb-4">
              <User className="w-10 h-10 text-primary-foreground" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Mon Profil
            </h1>
            <p className="text-gray-600 text-lg">
              Gérez vos informations personnelles et paramètres de compte
            </p>
          </div>

        {/* Messages d'alerte */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {success}
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Informations personnelles */}
          <Card className="lg:col-span-2 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-6">
              <div>
                <CardTitle className="text-xl font-semibold flex items-center">
                  <User className="w-5 h-5 mr-2 text-primary" />
                  Informations personnelles
                </CardTitle>
                <CardDescription className="text-base mt-1">
                  Vos données personnelles et d'identification
                </CardDescription>
              </div>
              {!isEditing ? (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setIsEditing(true)}
                >
                  Modifier
                </Button>
              ) : (
                <div className="flex space-x-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleCancel}
                    disabled={saving}
                  >
                    Annuler
                  </Button>
                  <Button 
                    size="sm" 
                    onClick={handleSave}
                    disabled={saving}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Sauvegarde...' : 'Sauvegarder'}
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <Label htmlFor="username" className="text-sm font-medium text-gray-700">Nom d'utilisateur</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    disabled={!isEditing}
                    className="mt-2 h-12"
                  />
                </div>
                
                <div>
                  <Label htmlFor="first_name" className="text-sm font-medium text-gray-700">Prénom</Label>
                  <Input
                    id="first_name"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    disabled={!isEditing}
                    placeholder="Votre prénom"
                    className="mt-2 h-12"
                  />
                </div>
                
                <div>
                  <Label htmlFor="last_name" className="text-sm font-medium text-gray-700">Nom de famille</Label>
                  <Input
                    id="last_name"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    disabled={!isEditing}
                    placeholder="Votre nom de famille"
                    className="mt-2 h-12"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Paramètres du compte */}
          <Card className="shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-6">
              <CardTitle className="text-xl font-semibold flex items-center">
                <Shield className="w-5 h-5 mr-2 text-primary" />
                Paramètres du compte
              </CardTitle>
              <CardDescription className="text-base mt-1">
                Sécurité et paramètres de votre compte
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <Label className="text-sm font-medium text-gray-700">Adresse email</Label>
                <div className="flex items-center justify-between mt-3">
                  <div className="flex items-center space-x-3">
                    <Mail className="w-5 h-5 text-gray-400" />
                    <span className="text-sm text-gray-900 font-medium">{profileData?.email}</span>
                  </div>
                  <Badge variant={profileData?.is_email_verified ? "default" : "secondary"} className="ml-2">
                    {profileData?.is_email_verified ? (
                      <><CheckCircle className="w-3 h-3 mr-1" /> Vérifié</>
                    ) : (
                      <><AlertTriangle className="w-3 h-3 mr-1" /> Non vérifié</>
                    )}
                  </Badge>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4">
                <Label className="text-sm font-medium text-gray-700">Crédits disponibles</Label>
                <div className="flex items-center space-x-3 mt-3">
                  <CreditCard className="w-6 h-6 text-primary" />
                  <span className="text-2xl font-bold text-primary">
                    {profileData?.credits || 0}
                  </span>
                  <span className="text-sm text-gray-600">crédits</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Statistiques du compte */}
          <Card className="lg:col-span-3 shadow-lg border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="pb-6">
              <CardTitle className="text-xl font-semibold">Activité du compte</CardTitle>
              <CardDescription className="text-base mt-1">
                Informations sur votre activité et historique
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                      <Calendar className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Membre depuis</p>
                      <p className="text-base font-semibold text-gray-900 mt-1">
                        {formatDate(profileData?.date_joined)}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                      <Clock className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700">Dernière connexion</p>
                      <p className="text-base font-semibold text-gray-900 mt-1">
                        {formatDate(profileData?.last_login)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
