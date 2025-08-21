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
				
				// Log simplifié pour vérifier la réception des données
				if (process.env.NODE_ENV === 'development') {
					console.log('Analyse reçue - Score:', data?.details?.gpt_analysis?.note_globale, 'Conformité:', data?.details?.gpt_analysis?.note_conformite_legale);
				}
				
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

	// Extraire les données réelles de l'analyse GPT (compatibilité avec anciens schémas)
	const gptData = analysis?.details?.gpt_analysis || analysis?.details?.gpt_analysis?.result || {};
	const anomalies = Array.isArray(gptData?.anomalies_potentielles_observees) ? gptData.anomalies_potentielles_observees : [];
	const evaluation = gptData?.evaluation_financiere_salarie || {};
	const remuneration = gptData?.remuneration || {};
	const periode = gptData?.periode || {};
	const recommendations = Array.isArray(gptData?.recommandations_amelioration) ? gptData.recommandations_amelioration : [];

	const conformityScore10 = typeof gptData?.note_conformite_legale === 'number' ? gptData.note_conformite_legale : 0;
	const conformityPercent = Math.round(Math.max(0, Math.min(100, (conformityScore10 / 10) * 100)));

	const derived = {
		period: (periode?.periode_du && periode?.periode_au) ? `Du ${periode.periode_du} au ${periode.periode_au}` : '—',
		date: analysis?.date ? new Date(analysis.date).toLocaleString('fr-FR') : '—',
		fileName: '—',
		status: analysis?.status || 'success',
		conformityPercent,
		globalScore: typeof gptData?.note_globale === 'number' ? gptData.note_globale : 0,
		errors: anomalies || [], // Ajouté pour éviter l'erreur filter
		recommendations,
		details: {
			salaireBrut: parseFloat(remuneration?.salaire_brut_total) || 0,
			salaireNet: parseFloat(remuneration?.net_a_payer) || 0,
			cotisationsSociales: parseFloat(remuneration?.total_cotisations_salariales) || 0,
			convention: gptData?.informations_generales?.convention_collective_applicable || '—',
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
									<p className="text-sm text-muted-foreground">Score d'analyse</p>
									<p className="text-xs text-muted-foreground mt-1">
										Inclut conformité légale, complétude et clarté
									</p>
								</div>

								<div className="space-y-3">
									<div>
										<div className="flex justify-between text-sm mb-1">
											<span>Conformité légale</span>
											<span>{derived.conformityPercent}%</span>
										</div>
										<Progress value={derived.conformityPercent} className="h-2" />
										<p className="text-xs text-muted-foreground mt-1">
											Respect des obligations légales et conventionnelles
										</p>
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
										<span className="text-muted-foreground">Anomalies détectées</span>
										<span className="text-amber-500 font-medium">
											{anomalies.filter((e: any) => (e.level || e.gravite) !== 'positive_check').length}
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
									<span>Anomalies et observations</span>
								</CardTitle>
								<CardDescription>
									{anomalies.length} anomalie(s) identifiée(s)
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="space-y-4">
									{anomalies.map((anomalie: any, index: number) => {
										const severity = anomalie.level || (anomalie.gravite === 'haute' ? 'error' : anomalie.gravite === 'moyenne' ? 'warning' : 'info');
										return (
											<div key={index} className="glass-card p-4 rounded-lg">
												<div className="flex items-start space-x-3">
													{getErrorIcon(severity)}
													<div className="flex-1">
														<div className="flex items-center justify-between mb-2">
															<h4 className="font-semibold text-foreground">{anomalie.type || 'Anomalie détectée'}</h4>
															{getErrorBadge(severity)}
														</div>
														<p className="text-sm text-muted-foreground mb-2">
															{anomalie.description || 'Aucune description disponible'}
														</p>
														{anomalie.impact_financier && (
															<p className="text-sm font-medium text-primary mb-2">
																Impact financier : {anomalie.impact_financier}
															</p>
														)}
														{anomalie.recommandation_correctif && (
															<div className="bg-muted/30 p-3 rounded-lg">
																<p className="text-sm">
																	<span className="font-medium">Recommandation :</span> {anomalie.recommandation_correctif}
																</p>
															</div>
														)}
													</div>
												</div>
											</div>
										);
									})}
									{anomalies.length === 0 && (
										<div className="text-center py-8">
											<CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
											<p className="text-muted-foreground">Aucune anomalie détectée</p>
										</div>
									)}
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
									{derived.recommendations.length === 0 && (
										<div className="text-center py-8">
											<CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
											<p className="text-muted-foreground">Aucune recommandation spécifique</p>
										</div>
									)}
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