import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  ArrowLeft, 
  Download, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Info,
  Euro,
  Calendar,
  FileText,
  TrendingUp,
  Shield
} from 'lucide-react';

const AnalysisDetails = () => {
	const { id } = useParams();
	const [analysis, setAnalysis] = useState<any | null>(null);
	const [loading, setLoading] = useState<boolean>(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const fetchData = async () => {
			try {
				if (!id) return;
				const { api } = await import('@/lib/api');
				const data = await api.getPayslipAnalysis(Number(id));
				setAnalysis(data);
			} catch (e: any) {
				setError(e?.error?.message || 'Impossible de récupérer les résultats');
			} finally {
				setLoading(false);
			}
		};
		fetchData();
	}, [id]);

	const getErrorIcon = (type: string) => {
		switch (type) {
			case "error":
				return <XCircle className="w-5 h-5 text-red-500" />;
			case "warning":
				return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
			case "info":
				return <Info className="w-5 h-5 text-blue-500" />;
			default:
				return <CheckCircle className="w-5 h-5 text-green-500" />;
		}
	};

	const getErrorBadge = (type: string) => {
		switch (type) {
			case "error":
				return <Badge className="bg-red-500/20 text-red-700 border-red-500/30">Erreur</Badge>;
			case "warning":
				return <Badge className="bg-yellow-500/20 text-yellow-700 border-yellow-500/30">Alerte</Badge>;
			case "info":
				return <Badge className="bg-blue-500/20 text-blue-700 border-blue-500/30">Info</Badge>;
			default:
				return <Badge className="bg-green-500/20 text-green-700 border-green-500/30">OK</Badge>;
		}
	};

	if (loading) {
		return (
			<div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">
				<div className="max-w-6xl mx-auto">Chargement...</div>
			</div>
		);
	}

	if (error || !analysis) {
		return (
			<div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">
				<div className="max-w-6xl mx-auto">{error || 'Aucune analyse trouvée'}</div>
			</div>
		);
	}

	const derived = {
		period: analysis?.details?.period || '—',
		date: analysis?.date || '—',
		fileName: analysis?.details?.file || '—',
		status: analysis?.status || 'success',
		conformityScore: analysis?.details?.conformity || 0,
		globalScore: analysis?.details?.globalScore || 0,
		errors: analysis?.details?.errors || [],
		recommendations: analysis?.details?.recommendations || [],
		details: {
			salaireBrut: analysis?.details?.salaireBrut || 0,
			salaireNet: analysis?.details?.salaireNet || 0,
			cotisationsSociales: analysis?.details?.cotisationsSociales || 0,
			convention: analysis?.details?.convention || '—',
		},
	};

	return (
		<div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">
			<div className="max-w-6xl mx-auto">
				{/* Header */}
				<div className="flex items-center space-x-4 mb-8">
					<Link to="/dashboard">
						<Button variant="outline" size="sm" className="btn-glass">
							<ArrowLeft className="w-4 h-4 mr-2" />
							Retour au dashboard
						</Button>
					</Link>
					<div className="flex-1 animate-fade-in-up">
						<h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
							Analyse détaillée
						</h1>
						<p className="text-muted-foreground">
							Fiche de paie - {derived.period}
						</p>
					</div>
					<Button className="bg-gradient-primary hover:opacity-90 border-0">
						<Download className="w-4 h-4 mr-2" />
						Télécharger le rapport
					</Button>
				</div>

				<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
					{/* Left Column - Summary */}
					<div className="lg:col-span-1 space-y-6">
						{/* Analysis Summary */}
						<Card className="glass-card border-0">
							<CardHeader>
								<CardTitle className="flex items-center space-x-2">
									<TrendingUp className="w-5 h-5 text-primary" />
									<span>Résumé de l'analyse</span>
								</CardTitle>
							</CardHeader>
							<CardContent className="space-y-4">
								<div className="text-center">
									<div className="text-4xl font-bold text-primary mb-2">
										{derived.globalScore}/10
									</div>
									<p className="text-sm text-muted-foreground">Score global</p>
								</div>

								<div className="space-y-3">
									<div>
										<div className="flex justify-between text-sm mb-1">
											<span>Conformité</span>
											<span>{derived.conformityScore}%</span>
										</div>
										<Progress value={derived.conformityScore} className="h-2" />
									</div>
								</div>

								<div className="pt-4 border-t border-glass-border/20 space-y-2 text-sm">
									<div className="flex items-center justify-between">
										<span className="text-muted-foreground">Analysé le</span>
										<span>{derived.date}</span>
									</div>
									<div className="flex items-center justify-between">
										<span className="text-muted-foreground">Fichier</span>
										<span className="truncate max-w-[150px]">{derived.fileName}</span>
									</div>
									<div className="flex items-center justify-between">
										<span className="text-muted-foreground">Erreurs trouvées</span>
										<span className="text-red-500 font-medium">
											{derived.errors.filter((e: any) => e.type === 'error').length}
										</span>
									</div>
								</div>
							</CardContent>
						</Card>

						{/* Financial Details */}
						<Card className="glass-card border-0">
							<CardHeader>
								<CardTitle className="flex items-center space-x-2">
									<Euro className="w-5 h-5 text-primary" />
									<span>Détails financiers</span>
								</CardTitle>
							</CardHeader>
							<CardContent className="space-y-3 text-sm">
								<div className="flex justify-between">
									<span className="text-muted-foreground">Salaire brut</span>
									<span className="font-medium">{derived.details.salaireBrut.toFixed(2)}€</span>
								</div>
								<div className="flex justify-between">
									<span className="text-muted-foreground">Cotisations sociales</span>
									<span className="font-medium">-{derived.details.cotisationsSociales.toFixed(2)}€</span>
								</div>
								<div className="flex justify-between border-t border-glass-border/20 pt-3">
									<span className="text-muted-foreground">Salaire net</span>
									<span className="font-bold text-lg">{derived.details.salaireNet.toFixed(2)}€</span>
								</div>
							</CardContent>
						</Card>

						{/* Convention */}
						<Card className="glass-card border-0">
							<CardHeader>
								<CardTitle className="flex items-center space-x-2">
									<Shield className="w-5 h-5 text-primary" />
									<span>Convention collective</span>
								</CardTitle>
							</CardHeader>
							<CardContent>
								<p className="text-sm">{derived.details.convention}</p>
							</CardContent>
						</Card>
					</div>

					{/* Right Column - Errors and Recommendations */}
					<div className="lg:col-span-2 space-y-6">
						{/* Errors List */}
						<Card className="glass-card border-0">
							<CardHeader>
								<CardTitle className="flex items-center space-x-2">
									<AlertTriangle className="w-5 h-5 text-primary" />
									<span>Erreurs et alertes détectées</span>
								</CardTitle>
								<CardDescription>
									{derived.errors.length} point(s) d'attention identifié(s)
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="space-y-4">
									{derived.errors.map((error: any, index: number) => (
										<div key={index} className="glass-card p-4 rounded-lg">
											<div className="flex items-start space-x-3">
												{getErrorIcon(error.type)}
												<div className="flex-1">
													<div className="flex items-center justify-between mb-2">
														<h4 className="font-semibold text-foreground">{error.title}</h4>
														{getErrorBadge(error.type)}
													</div>
													<p className="text-sm text-muted-foreground mb-2">
														{error.description}
													</p>
													{error.impact && (
														<p className="text-sm font-medium text-primary mb-2">
															Impact : {error.impact}
														</p>
													)}
													<div className="bg-muted/30 p-3 rounded-lg">
														<p className="text-sm">
															<span className="font-medium">Recommandation :</span> {error.recommendation}
														</p>
													</div>
												</div>
											</div>
										</div>
									))}
								</div>
							</CardContent>
						</Card>

						{/* Recommendations */}
						<Card className="glass-card border-0">
							<CardHeader>
								<CardTitle className="flex items-center space-x-2">
									<CheckCircle className="w-5 h-5 text-primary" />
									<span>Recommandations générales</span>
								</CardTitle>
								<CardDescription>
									Actions recommandées pour corriger les erreurs identifiées
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="space-y-3">
									{derived.recommendations.map((recommendation: string, index: number) => (
										<div key={index} className="flex items-start space-x-3">
											<div className="w-6 h-6 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
												<span className="text-xs font-bold text-primary">{index + 1}</span>
											</div>
											<p className="text-sm text-foreground">{recommendation}</p>
										</div>
									))}
								</div>
							</CardContent>
						</Card>

						{/* Actions */}
						<div className="flex flex-col sm:flex-row gap-4">
							<Button size="lg" className="bg-gradient-primary hover:opacity-90 border-0 flex-1">
								<Download className="w-4 h-4 mr-2" />
								Télécharger le rapport complet
							</Button>
							<Link to="/upload" className="flex-1">
								<Button variant="outline" size="lg" className="btn-glass w-full">
									<FileText className="w-4 h-4 mr-2" />
									Nouvelle analyse
								</Button>
							</Link>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};

export default AnalysisDetails;