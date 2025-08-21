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
// Pas besoin de jsPDF, on va faire du pure HTML/CSS qui pète ! 🚀

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

	const normalizeLevel = (raw: any): 'error' | 'warning' | 'info' | 'ok' => {
		const l = String(raw || '').toLowerCase();
		if (["haute", "grave", "critical", "erreur", "error"].includes(l)) return 'error';
		if (["moyenne", "warning", "alerte"].includes(l)) return 'warning';
		if (["info", "information"].includes(l)) return 'info';
		if (["positive_check", "ok", "bon", "conforme"].includes(l)) return 'ok';
		return 'info';
	};

	const formatAnomalyTitle = (rawType?: string) => {
		if (!rawType) return 'Anomalie détectée';
		// Si déjà une phrase lisible (contient un espace ou accent), garder
		if (/\s/.test(rawType) || /[À-ÿ]/.test(rawType)) return rawType;
		const map: Record<string, string> = {
			apprenti_cotisations_salariales_nulles: 'Cotisations apprenti nulles',
			taux_horaire_inferieur_SMIC: 'Taux horaire inférieur au SMIC',
			heures_base_vs_duree_mensuelle: 'Incohérence base d’heures / durée mensuelle',
			prime_vacances_syntec: 'Prime de vacances Syntec',
			coherence_heures: 'Cohérence des heures',
			coherence_nets: 'Cohérence des nets (net social vs net à payer)',
			SMIC_apprenti_verification: 'Vérification SMIC apprenti',
		};
		if (map[rawType]) return map[rawType];
		// Fallback: snake_case -> Titre
		const words = rawType.replace(/_/g, ' ').toLowerCase().split(' ');
		const titled = words.map(w => {
			if (w === 'smic') return 'SMIC';
			if (w === 'rtt') return 'RTT';
			if (w.length === 0) return w;
			return w[0].toUpperCase() + w.slice(1);
		}).join(' ');
		return titled;
	};

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
	let anomalies = Array.isArray(gptData?.anomalies_potentielles_observees) ? gptData.anomalies_potentielles_observees : [];
	const evaluation = gptData?.evaluation_financiere_salarie || {};
	const remuneration = gptData?.remuneration || {};
	const periode = gptData?.periode || {};
	const recommendations = Array.isArray(gptData?.recommandations_amelioration) ? gptData.recommandations_amelioration : [];
	const infoGenerales = gptData?.informations_generales || {};
	const userContext = {
		employment_status: gptData?.employment_status || analysis?.details?.employment_status || undefined,
		expected_smic_percent: gptData?.expected_smic_percent || analysis?.details?.expected_smic_percent || undefined,
	};

	// Générer des recommandations intelligentes basées sur les anomalies
	const generateSmartRecommendations = () => {
		const recs: string[] = [];
		
		// Recommandation pour écart SMIC
		if (evaluation?.difference && Number(evaluation.difference) > 0) {
			recs.push(`Régulariser le salaire : Un montant de ${Number(evaluation.difference).toFixed(2)}€ est dû au salarié selon le calcul SMIC/quotité. Contacter la paie pour effectuer un rappel de salaire.`);
		}
		
		// Recommandations basées sur les anomalies
		anomalies.forEach((anomalie: any) => {
			const type = anomalie.type?.toLowerCase() || '';
			const level = normalizeLevel(anomalie.level || anomalie.gravite);
			
			if (level === 'error' || level === 'warning') {
				if (type.includes('smic') || type.includes('horaire')) {
					recs.push('Vérifier le respect du SMIC : Contrôler le taux horaire appliqué et s\'assurer qu\'il respecte les minima légaux pour le statut du salarié.');
				}
				if (type.includes('syntec') || type.includes('rémunération')) {
					recs.push('Contrôle convention collective : Vérifier que la rémunération respecte les grilles salariales Syntec pour la classification ETAM.');
				}
				if (type.includes('prime') && type.includes('vacances')) {
					recs.push('Prime de vacances Syntec : Vérifier le versement de la prime de vacances obligatoire (période mai-octobre, minimum 10% des congés payés).');
				}
			}
		});
		
		// Recommandations générales si des anomalies significatives
		const significantAnomalies = anomalies.filter((a: any) => normalizeLevel(a?.level || a?.gravite) !== 'ok').length;
		if (significantAnomalies > 0) {
			recs.push('Documentation : Conserver tous les justificatifs de paie et contrats pour d\'éventuels contrôles administratifs.');
			recs.push('Suivi mensuel : Mettre en place une vérification systématique des bulletins de paie pour éviter la répétition d\'erreurs.');
		}
		
		// Enlever les doublons
		return [...new Set(recs)];
	};

	const smartRecommendations = generateSmartRecommendations();

	// Fonction de téléchargement de rapport qui PÈTE 🚀💥
	const downloadReport = () => {
		try {
			const significantAnomalies = anomalies.filter((a: any) => normalizeLevel(a?.level || a?.gravite) !== 'ok');
			
			// Création du HTML du rapport stylé
			const reportHTML = `
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Analyse de Paie - ${derived.period}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            line-height: 1.6; 
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #6366f1, #8b5cf6); 
            color: white; 
            padding: 30px; 
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 3s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(0.9); opacity: 0.7; }
            50% { transform: scale(1.1); opacity: 1; }
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }
        .header .subtitle { 
            font-size: 1.2em; 
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        .content { padding: 30px; }
        .section { 
            margin-bottom: 30px; 
            padding: 20px; 
            border-radius: 15px; 
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            border-left: 5px solid #6366f1;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .section h2 { 
            color: #6366f1; 
            margin-bottom: 15px; 
            font-size: 1.8em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 10px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .metric strong { color: #1f2937; }
        .anomaly { 
            margin: 15px 0; 
            padding: 15px; 
            border-radius: 10px; 
            border-left: 4px solid #f59e0b;
            background: linear-gradient(135deg, #fef3c7, #fde68a);
        }
        .anomaly.error { 
            border-left-color: #ef4444; 
            background: linear-gradient(135deg, #fee2e2, #fecaca);
        }
        .anomaly.warning { 
            border-left-color: #f59e0b; 
            background: linear-gradient(135deg, #fef3c7, #fde68a);
        }
        .anomaly.info { 
            border-left-color: #3b82f6; 
            background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        }
        .anomaly h4 { 
            font-size: 1.1em; 
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .badge { 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 0.8em; 
            font-weight: bold;
            text-transform: uppercase;
        }
        .badge.error { background: #ef4444; color: white; }
        .badge.warning { background: #f59e0b; color: white; }
        .badge.info { background: #3b82f6; color: white; }
        .recommendation { 
            margin: 10px 0; 
            padding: 15px; 
            background: linear-gradient(135deg, #ecfdf5, #d1fae5);
            border-radius: 10px; 
            border-left: 4px solid #10b981;
        }
        .score-big { 
            font-size: 3em; 
            font-weight: bold; 
            color: #6366f1; 
            text-align: center;
            margin: 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .footer { 
            background: #f8fafc; 
            padding: 20px; 
            text-align: center; 
            border-top: 2px solid #e5e7eb;
            color: #6b7280;
        }
        .highlight { 
            background: linear-gradient(135deg, #fbbf24, #f59e0b); 
            color: white; 
            padding: 15px; 
            border-radius: 10px; 
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
        }
        @media print {
            body { background: white; padding: 0; }
            .container { box-shadow: none; }
            .header::before { display: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 RAPPORT D'ANALYSE DE PAIE</h1>
            <div class="subtitle">${derived.period} • Généré le ${new Date().toLocaleString('fr-FR')}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>🔍 Résumé Exécutif</h2>
                <div class="score-big">${derived.globalScore}/10</div>
                <div class="metric">
                    <span>Conformité légale</span>
                    <strong>${derived.conformityPercent}%</strong>
                </div>
                <div class="metric">
                    <span>Date d'analyse</span>
                    <strong>${derived.date}</strong>
                </div>
            </div>

            <div class="section">
                <h2>💰 Détails Financiers</h2>
                <div class="metric">
                    <span>Salaire brut</span>
                    <strong>${derived.details.salaireBrut.toFixed(2)}€</strong>
                </div>
                <div class="metric">
                    <span>Cotisations sociales</span>
                    <strong>-${derived.details.cotisationsSociales.toFixed(2)}€</strong>
                </div>
                <div class="metric">
                    <span>Salaire net</span>
                    <strong style="color: #10b981; font-size: 1.2em;">${derived.details.salaireNet.toFixed(2)}€</strong>
                </div>
            </div>

            ${evaluation && (evaluation.attendu_mensuel || evaluation.recu_mensuel) ? `
            <div class="section">
                <h2>🎯 Évaluation Déterministe</h2>
                <div class="highlight">
                    <div style="font-size: 1.4em; margin-bottom: 10px;">
                        ${Number(evaluation.difference || 0) > 0 ? '⚠️ ÉCART DÉTECTÉ' : '✅ CONFORME'}
                    </div>
                    <div style="font-size: 1.8em; font-weight: bold;">
                        ${Number(evaluation.difference || 0) > 0 ? '+' : ''}${Number(evaluation.difference || 0).toFixed(2)}€
                    </div>
                </div>
                <div class="metric">
                    <span>Salaire mensuel attendu</span>
                    <strong>${Number(evaluation.attendu_mensuel || 0).toFixed(2)}€</strong>
                </div>
                <div class="metric">
                    <span>Salaire reçu</span>
                    <strong>${Number(evaluation.recu_mensuel || 0).toFixed(2)}€</strong>
                </div>
                ${evaluation.explication_montant_du ? `
                <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.7); border-radius: 8px; font-size: 0.9em;">
                    ${evaluation.explication_montant_du}
                </div>
                ` : ''}
            </div>
            ` : ''}

            <div class="section">
                <h2>⚠️ Anomalies Détectées (${significantAnomalies.length})</h2>
                ${significantAnomalies.map((anomalie: any) => {
                    const severity = normalizeLevel(anomalie.level || anomalie.gravite);
                    const severityEmoji = severity === 'error' ? '🔴' : severity === 'warning' ? '🟡' : '🔵';
                    const severityText = severity === 'error' ? 'ERREUR' : severity === 'warning' ? 'ALERTE' : 'INFO';
                    return `
                    <div class="anomaly ${severity}">
                        <h4>${severityEmoji} ${anomalie.type || 'Anomalie détectée'} <span class="badge ${severity}">${severityText}</span></h4>
                        <p>${anomalie.description || 'Aucune description disponible'}</p>
                    </div>
                    `;
                }).join('')}
                ${significantAnomalies.length === 0 ? '<div style="text-align: center; padding: 30px; color: #10b981;">✅ Aucune anomalie significative détectée</div>' : ''}
            </div>

            <div class="section">
                <h2>✅ Recommandations Prioritaires</h2>
                ${derived.recommendations.map((rec: string, index: number) => `
                    <div class="recommendation">
                        <strong>${index + 1}.</strong> ${rec}
                    </div>
                `).join('')}
                ${derived.recommendations.length === 0 ? '<div style="text-align: center; padding: 30px; color: #6b7280;">Aucune recommandation spécifique</div>' : ''}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>SalariZ Analytics</strong> • Rapport généré automatiquement</p>
            <p style="font-size: 0.9em; margin-top: 5px;">Pour toute question, contactez votre service RH</p>
        </div>
    </div>
</body>
</html>`;

			// Ouvrir le rapport dans un nouvel onglet
			const newWindow = window.open('', '_blank');
			if (newWindow) {
				newWindow.document.write(reportHTML);
				newWindow.document.close();
				
				// Focus sur la nouvelle fenêtre et déclencher l'impression
				setTimeout(() => {
					newWindow.focus();
					newWindow.print();
				}, 500);
			}

			// Animation de succès sur le bouton
			const buttons = document.querySelectorAll('.download-btn');
			buttons.forEach(button => {
				const btnElement = button as HTMLElement;
				btnElement.style.transform = 'scale(0.95)';
				btnElement.style.background = 'linear-gradient(135deg, #10b981, #059669)';
				setTimeout(() => {
					btnElement.style.transform = 'scale(1)';
					btnElement.style.background = '';
				}, 200);
			});

		} catch (error) {
			console.error('Erreur lors de la génération du rapport:', error);
			alert('🚨 Oups ! Erreur lors de la génération du rapport. Réessayez !');
		}
	};

	// Tri des anomalies: error > warning > info > ok
	anomalies = anomalies.slice().sort((a: any, b: any) => {
		const order: any = { error: 0, warning: 1, info: 2, ok: 3 };
		const la = normalizeLevel(a?.level || a?.gravite);
		const lb = normalizeLevel(b?.level || b?.gravite);
		return (order[la] ?? 99) - (order[lb] ?? 99);
	});

	const conformityScore10 = typeof gptData?.note_conformite_legale === 'number' ? gptData.note_conformite_legale : 0;
	const conformityPercent = Math.round(Math.max(0, Math.min(100, (conformityScore10 / 10) * 100)));

	const derived = {
		period: (periode?.periode_du && periode?.periode_au) ? `Du ${periode.periode_du} au ${periode.periode_au}` : '—',
		date: analysis?.date ? new Date(analysis.date).toLocaleString('fr-FR') : '—',
		fileName: '—',
		status: analysis?.status || 'success',
		conformityPercent,
		globalScore: typeof gptData?.note_globale === 'number' ? gptData.note_globale : 0,
		errors: anomalies || [],
		recommendations: smartRecommendations.length > 0 ? smartRecommendations : recommendations,
		details: {
			salaireBrut: parseFloat(remuneration?.salaire_brut_total) || 0,
			salaireNet: parseFloat(remuneration?.net_a_payer) || 0,
			netSocial: typeof remuneration?.net_social === 'number' ? remuneration.net_social : (remuneration?.net_social ? parseFloat(remuneration.net_social) : undefined),
			cotisationsSociales: parseFloat(remuneration?.total_cotisations_salariales) || 0,
			convention: gptData?.informations_generales?.convention_collective_applicable || '—',
			employmentStatus: userContext.employment_status,
			expectedSmicPercent: userContext.expected_smic_percent,
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
					<Button 
						className="bg-gradient-primary hover:opacity-90 border-0 download-btn transition-transform"
						onClick={downloadReport}
					>
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
									{(derived.details.employmentStatus || derived.details.expectedSmicPercent) && (
										<div className="flex items-center justify-between">
											<span className="text-muted-foreground">Statut / SMIC</span>
											<span className="font-medium">
												{derived.details.employmentStatus || '—'}{derived.details.expectedSmicPercent ? ` • ${Number(derived.details.expectedSmicPercent).toFixed(0)}%` : ''}
											</span>
										</div>
									)}
									<div className="flex items-center justify-between">
										<span className="text-muted-foreground">Anomalies détectées</span>
										<span className="text-amber-500 font-medium">
											{anomalies.filter((e: any) => normalizeLevel(e?.level || e?.gravite) !== 'ok').length}
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
								{derived.details.netSocial !== undefined && (
									<div className="flex justify-between">
										<span className="text-muted-foreground">Montant net social</span>
										<span className="font-medium">{Number(derived.details.netSocial).toFixed(2)}€</span>
									</div>
								)}
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
						{/* Évaluation financière déterministe */}
						{evaluation && (evaluation.attendu_mensuel || evaluation.recu_mensuel) && (
							<Card className="glass-card border-0 border-l-4 border-l-amber-500">
								<CardHeader>
									<CardTitle className="flex items-center space-x-2">
										<Euro className="w-5 h-5 text-amber-500" />
										<span>Évaluation déterministe</span>
									</CardTitle>
									<CardDescription>
										Calcul précis basé sur le SMIC et les informations contractuelles
									</CardDescription>
								</CardHeader>
								<CardContent className="space-y-3 text-sm">
									<div className="flex justify-between">
										<span className="text-muted-foreground">Salaire mensuel attendu</span>
										<span className="font-medium">{Number(evaluation.attendu_mensuel || 0).toFixed(2)}€</span>
									</div>
									<div className="flex justify-between">
										<span className="text-muted-foreground">Salaire de base brut reçu</span>
										<span className="font-medium">{Number(evaluation.recu_mensuel || 0).toFixed(2)}€</span>
									</div>
									<div className="flex justify-between border-t border-glass-border/20 pt-3">
										<span className="text-muted-foreground">Différence</span>
										<span className={`font-bold text-lg ${Number(evaluation.difference || 0) > 0 ? 'text-red-500' : 'text-green-500'}`}>
											{Number(evaluation.difference || 0) > 0 ? '+' : ''}{Number(evaluation.difference || 0).toFixed(2)}€
										</span>
									</div>
									{evaluation.explication_montant_du && (
										<div className="mt-3 p-3 bg-muted/30 rounded-lg">
											<p className="text-xs text-muted-foreground">
												{evaluation.explication_montant_du}
											</p>
										</div>
									)}
								</CardContent>
							</Card>
						)}

						{/* Errors List */}
						<Card className="glass-card border-0">
							<CardHeader>
								<CardTitle className="flex items-center space-x-2">
									<AlertTriangle className="w-5 h-5 text-primary" />
									<span>Anomalies et observations</span>
								</CardTitle>
								<CardDescription>
									{anomalies.filter((e: any) => normalizeLevel(e?.level || e?.gravite) !== 'ok').length} anomalie(s) identifiée(s)
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="space-y-4">
									{anomalies.map((anomalie: any, index: number) => {
										const severity = normalizeLevel(anomalie.level || anomalie.gravite);
										return (
											<div key={index} className="glass-card p-4 rounded-lg">
												<div className="flex items-start space-x-3">
													{getErrorIcon(severity)}
													<div className="flex-1">
														<div className="flex items-center justify-between mb-2">
															<h4 className="font-semibold text-foreground">{formatAnomalyTitle(anomalie.type) || 'Anomalie détectée'}</h4>
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
							<Button 
								size="lg" 
								className="bg-gradient-primary hover:opacity-90 border-0 flex-1 download-btn transition-transform"
								onClick={downloadReport}
							>
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