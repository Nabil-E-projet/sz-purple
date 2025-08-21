import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Eye, 
  TrendingUp,
  Calendar,
  BarChart3,
  Clock,
  Shield,
  Trash2
} from 'lucide-react';

const Dashboard = () => {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [pageInfo, setPageInfo] = useState<{ count: number; next?: string | null; previous?: string | null; limit: number; offset: number }>({ count: 0, next: null, previous: null, limit: 10, offset: 0 });
  const [globalStats, setGlobalStats] = useState<{ totalAnalyses: number; avgScore: string; avgConformityScore: string; totalErrors: number; lastAnalysis: string | null }>({ totalAnalyses: 0, avgScore: '0.0', avgConformityScore: '0.0', totalErrors: 0, lastAnalysis: null });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        const { api } = await import('@/lib/api');
        const page = await api.listPayslips({ limit: 10, offset: 0 });
        const mapped = (page.results as any[]).map((p) => ({
          id: p.id,
          period: p.period || '—',
          date: new Date(p.upload_date).toLocaleDateString('fr-FR'),
          status: p.processing_status === 'completed' ? 'success' : (p.processing_status === 'error' ? 'errors' : 'warning'),
          score: p.analysis_score || 0,
          conformityScore: p.conformity_score || 0,
          errorsCount: p.anomalies_count || 0,
          fileName: (p.uploaded_file || '').split('/').pop() || '—',
        }));
        setAnalyses(mapped);
        setPageInfo({ count: page.count || 0, next: page.next, previous: page.previous, limit: 10, offset: 0 });

        // Charger les stats globales indépendamment de la pagination
        const stats = await api.getPayslipsStats();
        setGlobalStats({
          totalAnalyses: stats.totalAnalyses || 0,
          avgScore: (stats.avgScore ?? 0).toFixed ? (stats.avgScore as any).toFixed(1) : Number(stats.avgScore || 0).toFixed(1),
          avgConformityScore: (stats.avgConformityScore ?? 0).toFixed ? (stats.avgConformityScore as any).toFixed(1) : Number(stats.avgConformityScore || 0).toFixed(1),
          totalErrors: stats.totalErrors || 0,
          lastAnalysis: stats.lastAnalysis ? new Date(stats.lastAnalysis).toLocaleDateString('fr-FR') : null,
        });
      } catch (e: any) {
        setError(e?.error?.message || 'Impossible de charger vos analyses');
      } finally {
        setLoading(false);
      }
    };
    run();
  }, []);

  const stats = {
    totalAnalyses: globalStats.totalAnalyses,
    avgScore: globalStats.avgScore,
    avgConformityScore: globalStats.avgConformityScore,
    totalErrors: globalStats.totalErrors,
    lastAnalysis: globalStats.lastAnalysis || '—',
  };

  const getStatusBadge = (status: string, errorsCount: number) => {
    // Statut visuel basé d'abord sur le nombre d'anomalies
    if (status === 'errors') {
      return <Badge className="bg-red-500/20 text-red-700 border-red-500/30">Erreurs</Badge>;
    }
    if (errorsCount > 0) {
      return <Badge className="bg-yellow-500/20 text-yellow-700 border-yellow-500/30">{errorsCount} anomalie(s)</Badge>;
    }
    if (status === 'success') {
      return <Badge className="bg-green-500/20 text-green-700 border-green-500/30">Conforme</Badge>;
    }
    return <Badge variant="outline">En cours</Badge>;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case "errors":
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-muted-foreground" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">Chargement...</div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">{error}</div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8">
          <div className="animate-fade-in-up">
            <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent mb-2">
              Dashboard
            </h1>
            <p className="text-muted-foreground">
              Vue d'ensemble de vos analyses de fiches de paie
            </p>
          </div>
          
          <Link to="/upload" className="mt-4 sm:mt-0">
            <Button className="bg-gradient-primary hover:opacity-90 border-0">
              <Plus className="w-4 h-4 mr-2" />
              Nouvelle analyse
            </Button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="glass-card border-0 hover:scale-105 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total analyses</p>
                  <p className="text-2xl font-bold text-foreground">{stats.totalAnalyses}</p>
                </div>
                <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center">
                  <FileText className="w-6 h-6 text-primary-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card border-0 hover:scale-105 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Score moyen</p>
                  <p className="text-2xl font-bold text-foreground">{stats.avgScore}/10</p>
                </div>
                <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-primary-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card border-0 hover:scale-105 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Erreurs détectées</p>
                  <p className="text-2xl font-bold text-foreground">{stats.totalErrors}</p>
                </div>
                <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-primary-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card border-0 hover:scale-105 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Conformité moyenne</p>
                  <p className="text-2xl font-bold text-foreground">{stats.avgConformityScore}/10</p>
                </div>
                <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center">
                  <Shield className="w-6 h-6 text-primary-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Analyses List */}
        <Card className="glass-card border-0">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              <span>Historique des analyses</span>
            </CardTitle>
            <CardDescription>
              Retrouvez toutes vos analyses de fiches de paie
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analyses.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Aucune analyse</h3>
                <p className="text-muted-foreground mb-6">
                  Vous n'avez pas encore effectué d'analyse de fiche de paie
                </p>
                <Link to="/upload">
                  <Button className="bg-gradient-primary hover:opacity-90 border-0">
                    <Plus className="w-4 h-4 mr-2" />
                    Commencer une analyse
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {analyses.map((analysis) => (
                  <div 
                    key={analysis.id}
                    className="glass-card p-6 rounded-xl hover:scale-[1.02] transition-all duration-300"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between space-y-4 sm:space-y-0">
                      <div className="flex items-center space-x-4">
                        {getStatusIcon(analysis.status)}
                        <div className="flex-1">
                          <h3 className="font-semibold text-foreground mb-1">
                            Fiche de paie - {analysis.period}
                          </h3>
                          <p className="text-sm text-muted-foreground mb-2">
                            {analysis.fileName}
                          </p>
                          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                            <span>Analysé le {analysis.date}</span>
                            <span>Score: {analysis.score}/10</span>
                            <span>Conformité: {analysis.conformityScore}/10</span>
                            {analysis.errorsCount > 0 ? (
                              <span className="text-amber-600 font-medium">{analysis.errorsCount} anomalie(s)</span>
                            ) : (
                              <span className="text-green-600">0 anomalie</span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4">
                        {getStatusBadge(analysis.status, analysis.errorsCount)}
                        <Link to={`/analysis/${analysis.id}`}>
                          <Button variant="outline" size="sm" className="btn-glass">
                            <Eye className="w-4 h-4 mr-2" />
                            Voir le détail
                          </Button>
                        </Link>
                        <Button
                          variant="destructive"
                          size="sm"
                          className="border-0"
                          onClick={async () => {
                            const yes = window.confirm('Supprimer définitivement cette fiche de paie et son analyse ?');
                            if (!yes) return;
                            try {
                              const { api } = await import('@/lib/api');
                              await api.deletePayslip(analysis.id);
                              setAnalyses(prev => prev.filter(a => a.id !== analysis.id));
                              setPageInfo(p => ({ ...p, count: Math.max(0, (p.count || 1) - 1) }));
                            } catch (e: any) {
                              alert(e?.error?.message || 'Suppression impossible');
                            }
                          }}
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Supprimer
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {/* Pagination simple */}
            {analyses.length > 0 && (
              <div className="flex justify-between items-center mt-6">
                <Button
                  variant="outline"
                  disabled={!pageInfo.previous}
                  onClick={async () => {
                    const { api } = await import('@/lib/api');
                    const newOffset = Math.max(0, pageInfo.offset - pageInfo.limit);
                    const page = await api.listPayslips({ limit: pageInfo.limit, offset: newOffset });
                    const mapped = (page.results as any[]).map((p) => ({
                      id: p.id,
                      period: p.period || '—',
                      date: new Date(p.upload_date).toLocaleDateString('fr-FR'),
                      status: p.processing_status === 'completed' ? 'success' : (p.processing_status === 'error' ? 'errors' : 'warning'),
                      score: p.analysis_score || 0,
                      conformityScore: p.conformity_score || 0,
                      errorsCount: p.anomalies_count || 0,
                      fileName: (p.uploaded_file || '').split('/').pop() || '—',
                    }));
                    setAnalyses(mapped);
                    setPageInfo({ count: page.count || 0, next: page.next, previous: page.previous, limit: pageInfo.limit, offset: newOffset });
                  }}
                >
                  Précédent
                </Button>
                <div className="text-sm text-muted-foreground">
                  {Math.min(pageInfo.offset + 1, pageInfo.count)}–{Math.min(pageInfo.offset + pageInfo.limit, pageInfo.count)} sur {pageInfo.count}
                </div>
                <Button
                  variant="outline"
                  disabled={!pageInfo.next}
                  onClick={async () => {
                    const { api } = await import('@/lib/api');
                    const newOffset = pageInfo.offset + pageInfo.limit;
                    const page = await api.listPayslips({ limit: pageInfo.limit, offset: newOffset });
                    const mapped = (page.results as any[]).map((p) => ({
                      id: p.id,
                      period: p.period || '—',
                      date: new Date(p.upload_date).toLocaleDateString('fr-FR'),
                      status: p.processing_status === 'completed' ? 'success' : (p.processing_status === 'error' ? 'errors' : 'warning'),
                      score: p.analysis_score || 0,
                      conformityScore: p.conformity_score || 0,
                      errorsCount: p.anomalies_count || 0,
                      fileName: (p.uploaded_file || '').split('/').pop() || '—',
                    }));
                    setAnalyses(mapped);
                    setPageInfo({ count: page.count || 0, next: page.next, previous: page.previous, limit: pageInfo.limit, offset: newOffset });
                  }}
                >
                  Suivant
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="mt-8 text-center">
          <Link to="/upload">
            <Button 
              size="lg" 
              className="bg-gradient-primary hover:opacity-90 border-0 px-8 py-6 text-lg font-semibold animate-float"
            >
              <Plus className="w-5 h-5 mr-2" />
              Analyser une nouvelle fiche de paie
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;