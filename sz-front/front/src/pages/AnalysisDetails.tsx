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

	// Seuil d'affichage pour l'évaluation déterministe
	const epsilon = 0.01;
	const diffValue = Number(evaluation?.difference ?? 0);
	const showDeterministic = Math.abs(diffValue) >= epsilon;

	// Générer des recommandations intelligentes basées sur les anomalies
	const generateSmartRecommendations = () => {
		const recs: string[] = [];
		
		// Recommandation pour écart SMIC: utiliser le montant dû réel (avec seuil)
		const montantDu = Number(evaluation?.montant_potentiel_du_salarie || 0);
		if (montantDu >= 0.01) {
			recs.push(`Régulariser le salaire : Un montant de ${montantDu.toFixed(2)}€ est dû au salarié selon le calcul SMIC/quotité. Contacter la paie pour effectuer un rappel de salaire.`);
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
		
		// Recommandations générales uniquement si erreurs/alertes (pas pour les infos)
		const significantAnomalies = anomalies.filter((a: any) => {
			const lvl = normalizeLevel(a?.level || a?.gravite);
			return lvl === 'error' || lvl === 'warning';
		}).length;
		if (significantAnomalies > 0) {
			recs.push('Documentation : Conserver tous les justificatifs de paie et contrats pour d\'éventuels contrôles administratifs.');
			recs.push('Suivi mensuel : Mettre en place une vérification systématique des bulletins de paie pour éviter la répétition d\'erreurs.');
		}
		
		// Enlever les doublons
		return [...new Set(recs)];
	};

	const smartRecommendations = generateSmartRecommendations();

	// Génération d'un rapport PDF moderne et professionnel
	const downloadReport = () => {
		try {
			const significantAnomalies = anomalies.filter((a: any) => normalizeLevel(a?.level || a?.gravite) !== 'ok');
			
			// Création du contenu du rapport minimaliste et professionnel
			const reportContent = `
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Analyse - ${derived.period}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #ffffff;
            font-size: 14px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }
        
        .header {
            text-align: center;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }
        
        .header .period {
            font-size: 16px;
            color: #6b7280;
            font-weight: 500;
        }
        
        .header .date {
            font-size: 12px;
            color: #9ca3af;
            margin-top: 16px;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .summary-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        
        .summary-card .value {
            font-size: 24px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 4px;
        }
        
        .summary-card .label {
            font-size: 12px;
            color: #6b7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .section {
            margin-bottom: 32px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #111827;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .financial-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1px;
            background: #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .financial-item {
            background: white;
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .financial-item .label {
            color: #6b7280;
            font-weight: 500;
        }
        
        .financial-item .value {
            font-weight: 600;
            color: #111827;
        }
        
        .financial-item.total {
            background: #f3f4f6;
            font-weight: 700;
            border-top: 2px solid #d1d5db;
        }
        
        .anomaly {
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .anomaly.error {
            background: #fee2e2;
            border-color: #ef4444;
        }
        
        .anomaly .anomaly-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .anomaly .anomaly-title {
            font-weight: 600;
            color: #111827;
            flex: 1;
        }
        
        .anomaly .anomaly-badge {
            background: #f59e0b;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .anomaly.error .anomaly-badge {
            background: #ef4444;
        }
        
        .anomaly .anomaly-description {
            color: #4b5563;
            font-size: 13px;
        }
        
        .recommendations .recommendation {
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 8px;
            position: relative;
            padding-left: 32px;
        }
        
        .recommendations .recommendation::before {
            content: counter(rec-counter);
            counter-increment: rec-counter;
            position: absolute;
            left: 12px;
            top: 12px;
            background: #0ea5e9;
            color: white;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 600;
        }
        
        .recommendations {
            counter-reset: rec-counter;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 12px;
        }
        
        .no-data {
            text-align: center;
            color: #6b7280;
            font-style: italic;
            padding: 20px;
        }
        
        @media print {
            body { font-size: 12px; }
            .container { padding: 20px; }
            .summary-grid { grid-template-columns: repeat(4, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Rapport d'Analyse de Paie</h1>
            <div class="period">${derived.period}</div>
            <div class="date">Généré le ${new Date().toLocaleDateString('fr-FR', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })}</div>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="value">${derived.globalScore}/10</div>
                <div class="label">Score Global</div>
            </div>
            <div class="summary-card">
                <div class="value">${derived.conformityPercent}%</div>
                <div class="label">Conformité</div>
            </div>
            <div class="summary-card">
                <div class="value">${significantAnomalies.length}</div>
                <div class="label">Anomalies</div>
            </div>
            <div class="summary-card">
                <div class="value">${derived.details.salaireNet.toFixed(0)}€</div>
                <div class="label">Salaire Net</div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Détails Financiers</h2>
            <div class="financial-grid">
                <div class="financial-item">
                    <span class="label">Salaire brut</span>
                    <span class="value">${derived.details.salaireBrut.toFixed(2)}€</span>
                </div>
                <div class="financial-item">
                    <span class="label">Cotisations sociales</span>
                    <span class="value">-${derived.details.cotisationsSociales.toFixed(2)}€</span>
                </div>
                <div class="financial-item total">
                    <span class="label">Salaire net</span>
                    <span class="value">${derived.details.salaireNet.toFixed(2)}€</span>
                </div>
                <div class="financial-item">
                    <span class="label">Convention</span>
                    <span class="value">${derived.details.convention}</span>
                </div>
            </div>
        </div>

        ${evaluation && (evaluation.attendu_mensuel || evaluation.recu_mensuel) ? `
        <div class="section">
            <h2 class="section-title">Évaluation Déterministe</h2>
            <div class="financial-grid">
                <div class="financial-item">
                    <span class="label">Salaire attendu</span>
                    <span class="value">${Number(evaluation.attendu_mensuel || 0).toFixed(2)}€</span>
                </div>
                <div class="financial-item">
                    <span class="label">Salaire reçu</span>
                    <span class="value">${Number(evaluation.recu_mensuel || 0).toFixed(2)}€</span>
                </div>
                <div class="financial-item total">
                    <span class="label">Différence</span>
                    <span class="value" style="color: ${Number(evaluation.difference || 0) > 0 ? '#ef4444' : '#10b981'}">
                        ${Number(evaluation.difference || 0) > 0 ? '+' : ''}${Number(evaluation.difference || 0).toFixed(2)}€
                    </span>
                </div>
                <div class="financial-item">
                    <span class="label">Statut</span>
                    <span class="value">${Number(evaluation.difference || 0) > 0 ? 'Non conforme' : 'Conforme'}</span>
                </div>
            </div>
        </div>
        ` : ''}

        <div class="section">
            <h2 class="section-title">Anomalies Détectées</h2>
            ${significantAnomalies.length > 0 ? significantAnomalies.map((anomalie: any) => {
                const severity = normalizeLevel(anomalie.level || anomalie.gravite);
                const severityText = severity === 'error' ? 'ERREUR' : 'ALERTE';
                return `
                <div class="anomaly ${severity}">
                    <div class="anomaly-header">
                        <div class="anomaly-title">${formatAnomalyTitle(anomalie.type)}</div>
                        <div class="anomaly-badge">${severityText}</div>
                    </div>
                    <div class="anomaly-description">${anomalie.description || 'Aucune description disponible'}</div>
                </div>
                `;
            }).join('') : '<div class="no-data">Aucune anomalie significative détectée</div>'}
        </div>

        <div class="section">
            <h2 class="section-title">Recommandations</h2>
            <div class="recommendations">
                ${derived.recommendations.length > 0 ? derived.recommendations.map((rec: string) => `
                    <div class="recommendation">${rec}</div>
                `).join('') : '<div class="no-data">Aucune recommandation spécifique</div>'}
            </div>
        </div>

        <div class="footer">
            <div><strong>SalariZ</strong> - Analyse automatisée de fiche de paie</div>
            <div>Ce rapport est généré automatiquement et doit être vérifié par un professionnel</div>
        </div>
    </div>
</body>
</html>`;

			// Créer et télécharger le fichier
			const blob = new Blob([reportContent], { type: 'text/html;charset=utf-8' });
			const url = URL.createObjectURL(blob);
			const link = document.createElement('a');
			link.href = url;
			link.download = `rapport-analyse-paie-${derived.period.replace(/[^a-zA-Z0-9]/g, '-')}.html`;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			URL.revokeObjectURL(url);

			// Animation de succès discrète
			const buttons = document.querySelectorAll('.download-btn');
			buttons.forEach(button => {
				const btnElement = button as HTMLElement;
				btnElement.style.transform = 'scale(0.98)';
				setTimeout(() => {
					btnElement.style.transform = 'scale(1)';
				}, 150);
			});

		} catch (error) {
			console.error('Erreur lors de la génération du rapport:', error);
			// Notification d'erreur plus discrète
			const errorDiv = document.createElement('div');
			errorDiv.textContent = 'Erreur lors de la génération du rapport';
			errorDiv.style.cssText = `
				position: fixed; top: 20px; right: 20px; 
				background: #fee2e2; color: #dc2626; 
				padding: 12px 16px; border-radius: 8px; 
				border: 1px solid #fecaca; 
				font-size: 14px; z-index: 1000;
				box-shadow: 0 4px 12px rgba(0,0,0,0.1);
			`;
			document.body.appendChild(errorDiv);
			setTimeout(() => document.body.removeChild(errorDiv), 3000);
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
		fileName: analysis?.filename || analysis?.original_filename || '—',
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

	// Normalisation des montants financiers pour l'affichage
	const financeBrut = Number(derived.details.salaireBrut) || 0;
	const financeCotis = Math.abs(Number(derived.details.cotisationsSociales) || 0);
	let financeNet = Number(derived.details.salaireNet) || 0;
	if (!(financeNet > 0)) {
		financeNet = Math.max(0, financeBrut - financeCotis);
	}
	if (financeCotis === 0 && Math.abs(financeNet - financeBrut) > 0.01) {
		financeNet = financeBrut;
	}
	const cotisDisplay = financeCotis === 0 ? '0.00€' : `-${financeCotis.toFixed(2)}€`;

	return (
		<div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">
			<div className="max-w-6xl mx-auto">
				{/* Header */}
				<div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0 mb-8">
					<div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-4">
						<Link to="/dashboard">
							<Button variant="outline" size="sm" className="btn-glass">
								<ArrowLeft className="w-4 h-4 mr-2" />
								Retour au dashboard
							</Button>
						</Link>
						<div className="animate-fade-in-up">
							<h1 className="text-2xl md:text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
								Analyse détaillée
							</h1>
							<p className="text-muted-foreground">
								Fiche de paie - {derived.period}
							</p>
						</div>
					</div>
					<div className="text-left md:text-right">
						<div className="text-sm text-muted-foreground">Analysé le</div>
						<div className="font-medium">{derived.date}</div>
					</div>
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
										<span className="truncate max-w-[150px]" title={derived.fileName}>
											{derived.fileName}
										</span>
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
									<span className="font-medium">{financeBrut.toFixed(2)}€</span>
								</div>
								<div className="flex justify-between">
									<span className="text-muted-foreground">Cotisations sociales</span>
									<span className="font-medium">{cotisDisplay}</span>
								</div>
								<div className="flex justify-between border-t border-glass-border/20 pt-3">
									<span className="text-muted-foreground">Salaire net</span>
									<span className="font-bold text-lg">{financeNet.toFixed(2)}€</span>
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
						{showDeterministic && evaluation && (evaluation.attendu_mensuel || evaluation.recu_mensuel) && (
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

						{/* État conforme quand aucun écart */}
						{!showDeterministic && evaluation && (evaluation.attendu_mensuel || evaluation.recu_mensuel) && (
							<Card className="glass-card border-0 border-l-4 border-l-emerald-500">
								<CardHeader>
									<CardTitle className="flex items-center space-x-2">
										<CheckCircle className="w-5 h-5 text-emerald-500" />
										<span>Salaire conforme au minimum attendu</span>
									</CardTitle>
									<CardDescription>
										Aucun écart détecté entre le salaire attendu et le salaire perçu
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
										<span className="text-muted-foreground">Écart</span>
										<span className="font-bold text-lg text-emerald-600">Aucun écart</span>
									</div>
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
						<Card className="glass-card border-0 bg-gradient-to-r from-primary/5 to-accent/5">
							<CardContent className="p-6">
								<h3 className="text-lg font-semibold mb-4 text-center">Actions disponibles</h3>
								<div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
									<Button 
										size="lg" 
										className="bg-gradient-primary hover:opacity-90 border-0 download-btn transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
										onClick={downloadReport}
									>
										<Download className="w-4 h-4 mr-2" />
										Exporter le rapport
									</Button>
									
									<Button 
										variant="outline" 
										size="lg" 
										className="btn-glass"
										onClick={() => window.print()}
									>
										<Info className="w-4 h-4 mr-2" />
										Imprimer la page
									</Button>
									
									<Link to="/upload" className="w-full">
										<Button variant="outline" size="lg" className="btn-glass w-full">
											<FileText className="w-4 h-4 mr-2" />
											Nouvelle analyse
										</Button>
									</Link>
								</div>
								
								<div className="mt-4 text-center">
									<p className="text-sm text-muted-foreground">
										💡 Tip: Sauvegardez ce rapport pour vos archives RH
									</p>
								</div>
							</CardContent>
						</Card>
					</div>
				</div>
			</div>
		</div>
	);
};

export default AnalysisDetails;