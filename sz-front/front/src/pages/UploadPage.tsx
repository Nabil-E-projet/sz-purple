import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Upload, FileText, Calendar as CalendarIcon, Euro, MessageSquare, Sparkles, ArrowRight, ArrowLeft, Check } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';

const UploadPage = () => {
	// États existants
	const [selectedDate, setSelectedDate] = useState<Date>();
	const [calendarDate, setCalendarDate] = useState<Date>(new Date());
	const [showYearMonthPicker, setShowYearMonthPicker] = useState(false);
	const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
	const [dragActive, setDragActive] = useState(false);
	const [isAnalyzing, setIsAnalyzing] = useState(false);
	const navigate = useNavigate();
	const { toast } = useToast();
	const [convention, setConvention] = useState<string | undefined>();
	const [conventions, setConventions] = useState<{ value: string; label: string }[]>([]);
	const [loadingConventions, setLoadingConventions] = useState<boolean>(false);
	const [salary, setSalary] = useState<string>('');
	const [details, setDetails] = useState<string>('');
	const [employmentStatus, setEmploymentStatus] = useState<string>('');
	const [expectedSmicPercent, setExpectedSmicPercent] = useState<string>('');
	const [workingTimeRatio, setWorkingTimeRatio] = useState<string>('');

	// Nouveaux états pour Typeform-like
	const [currentStep, setCurrentStep] = useState(0);
	const [direction, setDirection] = useState(1); // 1 pour suivant, -1 pour précédent

	const steps = [
		{ 
			id: 'upload', 
			title: 'Téléchargez votre fiche de paie', 
			subtitle: 'Formats acceptés : PDF uniquement',
			required: true 
		},
		{ 
			id: 'convention', 
			title: 'Quelle est votre convention collective ?', 
			subtitle: 'Cette information est obligatoire pour une analyse précise',
			required: true 
		},
		{ 
			id: 'period', 
			title: 'Pour quelle période souhaitez-vous analyser ?', 
			subtitle: 'Optionnel - nous pouvons extraire cette information du document',
			required: false 
		},
		{ 
			id: 'salary', 
			title: 'Quel est votre salaire contractuel brut ?', 
			subtitle: 'Optionnel - cela nous aide à détecter les écarts',
			required: false 
		},
		{ 
			id: 'status', 
			title: "Quel est votre statut d'emploi et votre quotité?", 
			subtitle: "Ex: Apprenti 80% du SMIC, temps partiel 0.8, etc.",
			required: false 
		},
		{ 
			id: 'details', 
			title: 'Avez-vous des détails supplémentaires à partager ?', 
			subtitle: 'Optionnel - toute information qui pourrait nous aider',
			required: false 
		},
		{ 
			id: 'confirm', 
			title: 'Tout est prêt !', 
			subtitle: 'Vérifiez vos informations avant de lancer l\'analyse',
			required: false 
		}
	];

	// Charger les conventions depuis le backend pour garantir des valeurs valides
	useEffect(() => {
		const run = async () => {
			setLoadingConventions(true);
			try {
				const data = await api.getConventions<{ value: string; label: string }[]>();
				setConventions(data || []);
			} catch (e: any) {
				toast({ title: 'Erreur', description: 'Impossible de charger les conventions collectives' });
			} finally {
				setLoadingConventions(false);
			}
		};
		run();
	}, [toast]);

	// Fonctions de navigation
	const nextStep = () => {
		if (currentStep < steps.length - 1) {
			setDirection(1);
			setCurrentStep(currentStep + 1);
		}
	};

	const prevStep = () => {
		if (currentStep > 0) {
			setDirection(-1);
			setCurrentStep(currentStep - 1);
		}
	};

	// Validation des étapes
	const canProceed = () => {
		const step = steps[currentStep];
		if (!step.required) return true;
		
		switch (step.id) {
			case 'upload':
				return selectedFiles.length > 0;
			case 'convention':
				return !!convention;
			default:
				return true;
		}
	};

	// Animation variants
	const slideVariants = {
		enter: (direction: number) => ({
			x: direction > 0 ? 1000 : -1000,
			opacity: 0
		}),
		center: {
			zIndex: 1,
			x: 0,
			opacity: 1
		},
		exit: (direction: number) => ({
			zIndex: 0,
			x: direction < 0 ? 1000 : -1000,
			opacity: 0
		})
	};

	const handleDrag = (e: React.DragEvent) => {
		e.preventDefault();
		e.stopPropagation();
		if (e.type === "dragenter" || e.type === "dragover") {
			setDragActive(true);
		} else if (e.type === "dragleave") {
			setDragActive(false);
		}
	};

	const handleDrop = (e: React.DragEvent) => {
		e.preventDefault();
		e.stopPropagation();
		setDragActive(false);
		
		if (e.dataTransfer.files && e.dataTransfer.files[0]) {
			const files = Array.from(e.dataTransfer.files);
			setSelectedFiles(prev => [...prev, ...files]);
		}
	};

	const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		if (e.target.files && e.target.files[0]) {
			const files = Array.from(e.target.files);
			setSelectedFiles(prev => [...prev, ...files]);
		}
	};

	const removeFile = (index: number) => {
		setSelectedFiles(prev => prev.filter((_, i) => i !== index));
	};

	const handleSubmit = async () => {
		setIsAnalyzing(true);

		try {
			if (selectedFiles.length === 0) return;
			
			const uploadData = {
				file: selectedFiles[0],
				convention_collective: convention,
				contractual_salary: salary,
				additional_details: details,
				period: selectedDate ? format(selectedDate, 'MMMM yyyy', { locale: fr }) : undefined,
				date_paiement: selectedDate ? format(selectedDate, 'yyyy-MM-dd') : undefined,
				employment_status: employmentStatus || undefined,
				expected_smic_percent: expectedSmicPercent ? Number(expectedSmicPercent) : undefined,
				working_time_ratio: workingTimeRatio ? Number(workingTimeRatio) : undefined,
			};
			
			// DEBUG: Log des données envoyées
			console.log('=== DEBUG UPLOAD FRONTEND ===');
			console.log('Fichier:', selectedFiles[0]?.name, '- Taille:', selectedFiles[0]?.size, 'bytes');
			console.log('Convention collective:', convention);
			console.log('Salaire contractuel:', salary);
			console.log('Détails additionnels:', details);
			console.log('Période:', uploadData.period, 'date_paiement:', uploadData.date_paiement);
			console.log('=== FIN DEBUG UPLOAD ===');
			
			const uploadRes = await api.uploadPayslip(uploadData);
			const payslipId = (uploadRes as any)?.id;
			if (!payslipId) throw new Error('Upload échoué');
			// L'analyse est désormais déclenchée automatiquement par le backend (signal post_save)
			toast({ title: 'Upload terminé', description: 'Analyse lancée automatiquement' });
			navigate('/dashboard');
		} catch (err: any) {
			const msg = err?.error || err?.message || 'Erreur lors de l\'analyse';
			toast({ title: 'Erreur', description: typeof msg === 'string' ? msg : JSON.stringify(msg) });
		} finally {
			setIsAnalyzing(false);
		}
	};

	// Fonctions de rendu pour chaque étape
	const renderStepContent = () => {
		const step = steps[currentStep];
		
		switch (step.id) {
			case 'upload':
				return (
					<div className="space-y-8">
						<div
							className={cn(
								"upload-zone rounded-xl p-12 text-center cursor-pointer transition-all duration-300 border-2 border-dashed",
								dragActive && "border-primary bg-primary/5",
								selectedFiles.length > 0 ? "border-green-500 bg-green-50/50" : "border-muted-foreground/30"
							)}
							onDragEnter={handleDrag}
							onDragLeave={handleDrag}
							onDragOver={handleDrag}
							onDrop={handleDrop}
							onClick={() => document.getElementById('file-upload')?.click()}
						>
							<div className="space-y-6">
								<div className="w-20 h-20 bg-gradient-primary rounded-3xl flex items-center justify-center mx-auto">
									{selectedFiles.length > 0 ? <Check className="w-10 h-10 text-white" /> : <Upload className="w-10 h-10 text-white" />}
								</div>
								<div>
									<p className="text-2xl font-medium mb-2">
										{selectedFiles.length > 0 ? 'Fichier sélectionné !' : 'Glissez-déposez votre fiche de paie ici'}
									</p>
									<p className="text-muted-foreground mb-6">
										ou cliquez pour parcourir vos fichiers
									</p>
									<Button size="lg" variant="outline" className="btn-glass">
										{selectedFiles.length > 0 ? 'Changer de fichier' : 'Parcourir les fichiers'}
									</Button>
								</div>
							</div>
						</div>

						<input
							id="file-upload"
							type="file"
							accept=".pdf"
							onChange={handleFileChange}
							className="hidden"
						/>

						{selectedFiles.length > 0 && (
							<motion.div 
								initial={{ opacity: 0, y: 20 }}
								animate={{ opacity: 1, y: 0 }}
								className="glass-card p-4 rounded-lg"
							>
								<div className="flex items-center justify-between">
									<div className="flex items-center space-x-3">
										<FileText className="w-6 h-6 text-primary" />
										<div>
											<p className="font-medium">{selectedFiles[0].name}</p>
											<p className="text-sm text-muted-foreground">
												{(selectedFiles[0].size / 1024 / 1024).toFixed(2)} MB
											</p>
										</div>
									</div>
									<Button
										variant="ghost"
										size="sm"
										onClick={() => setSelectedFiles([])}
										className="text-destructive hover:text-destructive"
									>
										Supprimer
									</Button>
								</div>
							</motion.div>
						)}
					</div>
				);

			case 'convention':
				return (
					<div className="space-y-8">
						<Select disabled={loadingConventions} onValueChange={(v) => setConvention(v)} value={convention}>
							<SelectTrigger className="glass-card border-glass-border/30 h-14 text-lg">
								<SelectValue placeholder="Sélectionnez votre convention collective" />
							</SelectTrigger>
							<SelectContent className="glass-card border-glass-border/30 backdrop-blur-md">
								{conventions.map((c, index) => (
									<SelectItem key={index} value={c.value} className="py-3">
										{c.label}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
						
						{convention && (
							<motion.div 
								initial={{ opacity: 0, scale: 0.95 }}
								animate={{ opacity: 1, scale: 1 }}
								className="text-center"
							>
								<div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
									<Check className="w-6 h-6 text-white" />
								</div>
								<p className="text-muted-foreground">Convention sélectionnée !</p>
							</motion.div>
						)}
					</div>
				);

			case 'period':
				return (
					<div className="space-y-8">
						<Popover>
							<PopoverTrigger asChild>
								<Button
									variant="outline"
									className={cn(
										"w-full h-14 text-lg justify-start text-left font-normal glass-card border-glass-border/30",
										!selectedDate && "text-muted-foreground"
									)}
								>
									<CalendarIcon className="mr-3 h-5 w-5" />
									{selectedDate ? 
										format(selectedDate, "MMMM yyyy", { locale: fr }) : 
										"Cliquez pour sélectionner la période"
									}
								</Button>
							</PopoverTrigger>
							<PopoverContent className="w-auto p-0 glass-card border-glass-border/30 backdrop-blur-md" align="center">
								{showYearMonthPicker ? (
									<div className="p-4 space-y-4">
										<div className="text-center">
											<h3 className="font-semibold text-primary mb-4">Sélectionnez une période</h3>
										</div>
										<div className="grid grid-cols-2 gap-4">
											<div>
												<label className="block text-sm text-muted-foreground mb-2">Année</label>
												<Select
													value={calendarDate.getFullYear().toString()}
													onValueChange={(year) => {
														const newDate = new Date(calendarDate);
														newDate.setFullYear(parseInt(year));
														setCalendarDate(newDate);
													}}
												>
													<SelectTrigger className="h-10">
														<SelectValue />
													</SelectTrigger>
													<SelectContent>
														{Array.from({ length: 10 }, (_, i) => {
															const year = new Date().getFullYear() - 5 + i;
															return (
																<SelectItem key={year} value={year.toString()}>
																	{year}
																</SelectItem>
															);
														})}
													</SelectContent>
												</Select>
											</div>
											<div>
												<label className="block text-sm text-muted-foreground mb-2">Mois</label>
												<Select
													value={calendarDate.getMonth().toString()}
													onValueChange={(month) => {
														const newDate = new Date(calendarDate);
														newDate.setMonth(parseInt(month));
														setCalendarDate(newDate);
													}}
												>
													<SelectTrigger className="h-10">
														<SelectValue />
													</SelectTrigger>
													<SelectContent>
														{Array.from({ length: 12 }, (_, i) => (
															<SelectItem key={i} value={i.toString()}>
																{format(new Date(2024, i, 1), "MMMM", { locale: fr })}
															</SelectItem>
														))}
													</SelectContent>
												</Select>
											</div>
										</div>
										<div className="flex gap-2 pt-2">
											<Button
												variant="outline"
												size="sm"
												onClick={() => setShowYearMonthPicker(false)}
												className="flex-1"
											>
												Retour
											</Button>
											<Button
												size="sm"
												onClick={() => {
													setShowYearMonthPicker(false);
												}}
												className="flex-1 bg-gradient-primary"
											>
												Confirmer
											</Button>
										</div>
									</div>
								) : (
									<Calendar
										mode="single"
										selected={selectedDate}
										onSelect={setSelectedDate}
										month={calendarDate}
										onMonthChange={setCalendarDate}
										initialFocus
										locale={fr}
										className="p-4 rounded-xl"
										classNames={{
											months: "flex flex-col sm:flex-row space-y-4 sm:space-x-4 sm:space-y-0",
											month: "space-y-4",
											caption: "flex justify-center pt-1 relative items-center",
											caption_label: "text-lg font-semibold text-primary cursor-pointer hover:bg-primary/10 px-3 py-1 rounded-lg transition-colors",
											nav: "space-x-1 flex items-center",
											nav_button: "h-8 w-8 bg-transparent p-0 opacity-50 hover:opacity-100 rounded-lg hover:bg-primary/10 transition-colors",
											nav_button_previous: "absolute left-1",
											nav_button_next: "absolute right-1",
											table: "w-full border-collapse space-y-1",
											head_row: "flex",
											head_cell: "text-muted-foreground rounded-md w-8 font-medium text-[0.8rem] text-center",
											row: "flex w-full mt-2",
											cell: "text-center text-sm p-0 relative [&:has([aria-selected])]:bg-accent first:[&:has([aria-selected])]:rounded-l-md last:[&:has([aria-selected])]:rounded-r-md focus-within:relative focus-within:z-20",
											day: "h-8 w-8 p-0 font-medium aria-selected:opacity-100 rounded-lg hover:bg-primary/10 transition-colors",
											day_selected: "bg-gradient-primary text-white hover:bg-gradient-primary hover:text-white focus:bg-gradient-primary focus:text-white",
											day_today: "bg-accent text-accent-foreground font-bold",
											day_outside: "text-muted-foreground opacity-50",
											day_disabled: "text-muted-foreground opacity-50",
											day_range_middle: "aria-selected:bg-accent aria-selected:text-accent-foreground",
											day_hidden: "invisible",
										}}
										components={{
											Caption: ({ displayMonth }: any) => (
												<div className="flex justify-center pt-1 relative items-center">
													<button
														onClick={() => setShowYearMonthPicker(true)}
														className="text-lg font-semibold text-primary cursor-pointer hover:bg-primary/10 px-3 py-1 rounded-lg transition-colors"
													>
														{format(displayMonth, "MMMM yyyy", { locale: fr })}
													</button>
												</div>
											)
										}}
									/>
								)}
							</PopoverContent>
						</Popover>
						
						{selectedDate && (
							<motion.div 
								initial={{ opacity: 0, scale: 0.95 }}
								animate={{ opacity: 1, scale: 1 }}
								className="text-center"
							>
								<div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
									<Check className="w-6 h-6 text-white" />
								</div>
								<p className="text-muted-foreground">Période sélectionnée !</p>
							</motion.div>
						)}
					</div>
				);

			case 'salary':
				return (
					<div className="space-y-8">
						<div className="relative">
							<Euro className="absolute left-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-muted-foreground" />
							<Input
								type="number"
								placeholder="3500"
								className="pl-14 glass-card border-glass-border/30 h-14 text-lg"
								step="0.01"
								value={salary}
								onChange={(e) => setSalary(e.target.value)}
							/>
						</div>
						
						{salary && (
							<motion.div 
								initial={{ opacity: 0, scale: 0.95 }}
								animate={{ opacity: 1, scale: 1 }}
								className="text-center"
							>
								<div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
									<Check className="w-6 h-6 text-white" />
								</div>
								<p className="text-muted-foreground">Salaire enregistré : {salary}€</p>
							</motion.div>
						)}

					</div>
				);

			case 'details':
				return (
					<div className="space-y-8">
						<Textarea
							placeholder="Décrivez ici toute demande spécifique ou point particulier à analyser..."
							className="glass-card border-glass-border/30 min-h-[120px] text-lg"
							value={details}
							onChange={(e) => setDetails(e.target.value)}
						/>
						
						{details && (
							<motion.div 
								initial={{ opacity: 0, scale: 0.95 }}
								animate={{ opacity: 1, scale: 1 }}
								className="text-center"
							>
								<div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
									<Check className="w-6 h-6 text-white" />
								</div>
								<p className="text-muted-foreground">Détails enregistrés !</p>
							</motion.div>
						)}

					</div>
				);

			case 'status':
				return (
					<div className="space-y-8">
						<div className="grid grid-cols-1 gap-6">
							<div>
								<label className="block text-sm text-muted-foreground mb-2">Statut d'emploi</label>
								<Select onValueChange={(v) => setEmploymentStatus(v)} value={employmentStatus}>
									<SelectTrigger className="glass-card border-glass-border/30 h-14 text-lg">
										<SelectValue placeholder="Sélectionnez votre statut" />
									</SelectTrigger>
									<SelectContent className="glass-card border-glass-border/30 backdrop-blur-md">
										<SelectItem value="APPRENTI">Apprenti</SelectItem>
										<SelectItem value="CDI">CDI</SelectItem>
										<SelectItem value="CDD">CDD</SelectItem>
										<SelectItem value="STAGIAIRE">Stagiaire</SelectItem>
										<SelectItem value="TEMPS_PARTIEL">Temps partiel</SelectItem>
										<SelectItem value="AUTRE">Autre</SelectItem>
									</SelectContent>
								</Select>
							</div>
							<div>
								<label className="block text-sm text-muted-foreground mb-2">Pourcentage SMIC attendu (ex: 75 pour 75%)</label>
								<Input
									type="number"
									placeholder="75"
									className="glass-card border-glass-border/30 h-14 text-lg"
									step="0.01"
									value={expectedSmicPercent}
									onChange={(e) => setExpectedSmicPercent(e.target.value)}
								/>
							</div>
							<div>
								<label className="block text-sm text-muted-foreground mb-2">Quotité (ratio temps de travail, ex: 1.0 temps plein, 0.8 pour 80%)</label>
								<Input
									type="number"
									placeholder="1.0"
									className="glass-card border-glass-border/30 h-14 text-lg"
									step="0.01"
									value={workingTimeRatio}
									onChange={(e) => setWorkingTimeRatio(e.target.value)}
								/>
							</div>
						</div>
						{(employmentStatus || expectedSmicPercent || workingTimeRatio) && (
							<motion.div 
								initial={{ opacity: 0, scale: 0.95 }}
								animate={{ opacity: 1, scale: 1 }}
								className="text-center"
							>
								<div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
									<Check className="w-6 h-6 text-white" />
								</div>
								<p className="text-muted-foreground">Contexte enregistré !</p>
							</motion.div>
						)}
					</div>
				);

			case 'confirm':
				return (
					<div className="space-y-8">
						<div className="glass-card p-6 rounded-xl space-y-4">
							<div className="flex items-center justify-between">
								<span className="text-muted-foreground">Fichier :</span>
								<span className="font-medium">{selectedFiles[0]?.name || 'Aucun'}</span>
							</div>
							<div className="flex items-center justify-between">
								<span className="text-muted-foreground">Convention :</span>
								<span className="font-medium">
									{conventions.find(c => c.value === convention)?.label || 'Non sélectionnée'}
								</span>
							</div>
							{selectedDate && (
								<div className="flex items-center justify-between">
									<span className="text-muted-foreground">Période :</span>
									<span className="font-medium">{format(selectedDate, "MMMM yyyy", { locale: fr })}</span>
								</div>
							)}
							{salary && (
								<div className="flex items-center justify-between">
									<span className="text-muted-foreground">Salaire contractuel :</span>
									<span className="font-medium">{salary}€</span>
								</div>
							)}
							{details && (
								<div className="space-y-2">
									<span className="text-muted-foreground block">Détails supplémentaires :</span>
									<p className="text-sm bg-muted/30 p-3 rounded-lg">{details}</p>
								</div>
							)}
						</div>
						
						<Button
							onClick={handleSubmit}
							size="lg"
							className="w-full bg-gradient-primary hover:opacity-90 border-0 h-14 text-lg font-semibold"
							disabled={isAnalyzing}
						>
							{isAnalyzing ? (
								<>
									<Sparkles className="mr-2 w-5 h-5 animate-spin" />
									Analyse en cours...
								</>
							) : (
								<>
									<Sparkles className="mr-2 w-5 h-5" />
									Lancer l'analyse IA
								</>
							)}
						</Button>
						
						{isAnalyzing && (
							<motion.div 
								initial={{ opacity: 0, y: 20 }}
								animate={{ opacity: 1, y: 0 }}
								className="glass-card p-4 rounded-lg"
							>
								<div className="flex items-center space-x-3">
									<div className="flex space-x-1">
										<div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
										<div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-75"></div>
										<div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-150"></div>
									</div>
									<span className="text-sm text-muted-foreground">
										Notre IA analyse votre fiche de paie...
									</span>
								</div>
							</motion.div>
						)}
					</div>
				);

			default:
				return null;
		}
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
			{/* Progress Bar */}
			<div className="fixed top-0 left-0 w-full h-1 bg-muted z-50">
				<motion.div 
					className="h-full bg-gradient-primary"
					initial={{ width: "0%" }}
					animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
					transition={{ duration: 0.3 }}
				/>
			</div>

			<div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
				<div className="max-w-2xl mx-auto">
					{/* Header */}
					<div className="text-center mb-12">
						<motion.div
							key={currentStep}
							initial={{ opacity: 0, y: 20 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ duration: 0.3 }}
						>
							<div className="flex items-center justify-center space-x-2 mb-4">
								<span className="text-sm font-medium text-primary">
									{currentStep + 1} sur {steps.length}
								</span>
							</div>
							<h1 className="text-3xl md:text-4xl font-bold mb-4">
								{steps[currentStep].title}
							</h1>
							<p className="text-xl text-muted-foreground">
								{steps[currentStep].subtitle}
							</p>
							{steps[currentStep].required && (
								<div className="inline-flex items-center mt-4 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm">
									Obligatoire
								</div>
							)}
						</motion.div>
					</div>

					{/* Step Content */}
					<div className="relative">
						<AnimatePresence mode="wait" custom={direction}>
							<motion.div
								key={currentStep}
								custom={direction}
								variants={slideVariants}
								initial="enter"
								animate="center"
								exit="exit"
								transition={{
									x: { type: "spring", stiffness: 300, damping: 30 },
									opacity: { duration: 0.2 }
								}}
								className="w-full"
							>
								{renderStepContent()}
							</motion.div>
						</AnimatePresence>
					</div>

					{/* Navigation */}
					<div className="flex items-center justify-between mt-12">
						<Button
							variant="ghost"
							onClick={prevStep}
							disabled={currentStep === 0}
							className="flex items-center space-x-2"
						>
							<ArrowLeft className="w-4 h-4" />
							<span>Précédent</span>
						</Button>

						{currentStep < steps.length - 1 && (
							<Button
								onClick={nextStep}
								disabled={!canProceed()}
								className="flex items-center space-x-2 bg-gradient-primary hover:opacity-90 border-0"
							>
								<span>Suivant</span>
								<ArrowRight className="w-4 h-4" />
							</Button>
						)}
					</div>
				</div>
			</div>
		</div>
	);
};

export default UploadPage;