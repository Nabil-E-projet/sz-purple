import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Upload, FileText, Calendar as CalendarIcon, Euro, MessageSquare, Sparkles } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

const UploadPage = () => {
	const [selectedDate, setSelectedDate] = useState<Date>();
	const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
	const [dragActive, setDragActive] = useState(false);
	const [isAnalyzing, setIsAnalyzing] = useState(false);
	const navigate = useNavigate();
	const { toast } = useToast();
	const [convention, setConvention] = useState<string | undefined>();
	const [salary, setSalary] = useState<string>('');
	const [details, setDetails] = useState<string>('');

	const conventions = [
		"Convention collective nationale du commerce de détail et de gros à prédominance alimentaire",
		"Convention collective nationale de la métallurgie",
		"Convention collective nationale du bâtiment et des travaux publics",
		"Convention collective nationale des employés, techniciens et agents de maîtrise du bâtiment",
		"Convention collective nationale des services de l'automobile",
		"Convention collective nationale de l'hôtellerie de plein air",
		"Convention collective nationale du transport routier et activités auxiliaires du transport",
		"Convention collective nationale de la coiffure et des soins esthétiques",
		"Convention collective nationale de la restauration rapide",
		"Convention collective nationale des organismes de formation"
	];

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

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setIsAnalyzing(true);

		try {
			if (selectedFiles.length === 0) return;
			const uploadRes = await api.uploadPayslip({
				file: selectedFiles[0],
				convention_collective: convention,
				contractual_salary: salary,
				additional_details: details,
				period: selectedDate ? format(selectedDate, 'MMMM yyyy', { locale: fr }) : undefined,
			});
			const payslipId = (uploadRes as any)?.id;
			if (!payslipId) throw new Error('Upload échoué');
			await api.analyzePayslip(payslipId);
			toast({ title: 'Upload terminé', description: 'Analyse lancée' });
			navigate(`/analysis/${payslipId}`);
		} catch (err: any) {
			const msg = err?.error || err?.message || 'Erreur lors de l\'analyse';
			toast({ title: 'Erreur', description: typeof msg === 'string' ? msg : JSON.stringify(msg) });
		} finally {
			setIsAnalyzing(false);
		}
	};

	return (
		<div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">
			<div className="max-w-4xl mx-auto">
				<div className="text-center mb-12 animate-fade-in-up">
					<h1 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-primary bg-clip-text text-transparent">
						Analyser une fiche de paie
					</h1>
					<p className="text-xl text-muted-foreground max-w-2xl mx-auto">
						Téléchargez votre fiche de paie et obtenez une analyse détaillée avec détection d'erreurs
					</p>
				</div>

				<form onSubmit={handleSubmit} className="space-y-8">
					<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
						{/* Left Column - Form Fields */}
						<div className="space-y-6">
							<Card className="glass-card border-0">
								<CardHeader>
									<CardTitle className="flex items-center space-x-2">
										<FileText className="w-5 h-5 text-primary" />
										<span>Informations requises</span>
									</CardTitle>
									<CardDescription>
										Ces informations nous aident à mieux analyser votre fiche de paie
									</CardDescription>
								</CardHeader>
								<CardContent className="space-y-4">
									<div className="space-y-2">
										<Label htmlFor="convention">Convention collective *</Label>
										<Select required onValueChange={(v) => setConvention(v)}>
											<SelectTrigger className="glass-card border-glass-border/30">
												<SelectValue placeholder="Sélectionnez votre convention collective" />
											</SelectTrigger>
											<SelectContent className="glass-card border-glass-border/30 backdrop-blur-md">
												{conventions.map((convention, index) => (
													<SelectItem key={index} value={convention}>
														{convention}
													</SelectItem>
												))}
											</SelectContent>
										</Select>
									</div>

									<div className="space-y-2">
										<Label>Période d'analyse *</Label>
										<Popover>
											<PopoverTrigger asChild>
												<Button
													variant="outline"
													className={cn(
														"w-full justify-start text-left font-normal glass-card border-glass-border/30",
														!selectedDate && "text-muted-foreground"
													)}
												>
													<CalendarIcon className="mr-2 h-4 w-4" />
													{selectedDate ? 
														format(selectedDate, "MMMM yyyy", { locale: fr }) : 
														"Sélectionnez la période"
													}
												</Button>
											</PopoverTrigger>
											<PopoverContent className="w-auto p-0 glass-card border-glass-border/30" align="start">
												<Calendar
														mode="single"
														selected={selectedDate}
														onSelect={setSelectedDate}
														initialFocus
														className="p-3 pointer-events-auto"
												/>
											</PopoverContent>
										</Popover>
									</div>

									<div className="space-y-2">
										<Label htmlFor="salaire">Salaire contractuel brut (optionnel)</Label>
										<div className="relative">
											<Euro className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
											<Input
												id="salaire"
												type="number"
												placeholder="3500"
												className="pl-10 glass-card border-glass-border/30"
												step="0.01"
												value={salary}
												onChange={(e) => setSalary(e.target.value)}
											/>
										</div>
									</div>
								</CardContent>
							</Card>

							<Card className="glass-card border-0">
								<CardHeader>
									<CardTitle className="flex items-center space-x-2">
										<MessageSquare className="w-5 h-5 text-primary" />
										<span>Commentaires supplémentaires</span>
									</CardTitle>
								</CardHeader>
								<CardContent>
									<Textarea
										placeholder="Décrivez ici toute demande spécifique ou point particulier à analyser..."
										className="glass-card border-glass-border/30 min-h-[120px]"
										value={details}
										onChange={(e) => setDetails(e.target.value)}
									/>
								</CardContent>
							</Card>
						</div>

						{/* Right Column - File Upload */}
						<div className="space-y-6">
							<Card className="glass-card border-0">
								<CardHeader>
									<CardTitle className="flex items-center space-x-2">
										<Upload className="w-5 h-5 text-primary" />
										<span>Téléchargement de fichier</span>
									</CardTitle>
									<CardDescription>
										Formats acceptés : PDF, JPG, PNG (max 10 MB)
									</CardDescription>
								</CardHeader>
								<CardContent>
									<div
										className={cn(
											"upload-zone rounded-xl p-8 text-center cursor-pointer transition-all duration-300",
											dragActive && "drag-active"
										)}
										onDragEnter={handleDrag}
										onDragLeave={handleDrag}
										onDragOver={handleDrag}
										onDrop={handleDrop}
										onClick={() => document.getElementById('file-upload')?.click()}
									>
										<div className="space-y-4">
											<div className="w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto">
												<Upload className="w-8 h-8 text-primary-foreground" />
											</div>
											<div>
												<p className="text-lg font-medium mb-2">
													Glissez-déposez vos fichiers ici
												</p>
												<p className="text-muted-foreground mb-4">
													ou cliquez pour parcourir
												</p>
												<Button variant="outline" className="btn-glass">
													Parcourir les fichiers
												</Button>
											</div>
										</div>
									</div>

									<input
										id="file-upload"
										type="file"
										multiple
										accept=".pdf,.jpg,.jpeg,.png"
										onChange={handleFileChange}
										className="hidden"
									/>

									{selectedFiles.length > 0 && (
										<div className="mt-6 space-y-3">
											<h4 className="font-medium">Fichiers sélectionnés :</h4>
											{selectedFiles.map((file, index) => (
												<div key={index} className="flex items-center justify-between glass-card p-3 rounded-lg">
													<div className="flex items-center space-x-3">
														<FileText className="w-5 h-5 text-primary" />
														<span className="text-sm font-medium">{file.name}</span>
														<span className="text-xs text-muted-foreground">
															{(file.size / 1024 / 1024).toFixed(2)} MB
														</span>
													</div>
													<Button
														type="button"
														variant="ghost"
														size="sm"
														onClick={() => removeFile(index)}
														className="text-destructive hover:text-destructive"
													>
														Supprimer
													</Button>
												</div>
											))}
										</div>
									)}
								</CardContent>
							</Card>
						</div>
					</div>

					{/* Submit Button */}
					<div className="text-center">
						<Button
							type="submit"
							size="lg"
							className="bg-gradient-primary hover:opacity-90 border-0 px-12 py-6 text-lg font-semibold"
							disabled={isAnalyzing || selectedFiles.length === 0}
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
							<div className="mt-6 glass-card p-4 rounded-lg max-w-md mx-auto">
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
							</div>
						)}
					</div>
				</form>
			</div>
		</div>
	);
};

export default UploadPage;