import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const WelcomeAnimation = () => {
	const [showWelcome, setShowWelcome] = useState(false);
	const [closing, setClosing] = useState(false);

	// Timings (ms)
	const DISPLAY_MS = 5000; // durée totale d'affichage
	const FADE_MS = 900;     // durée du fondu de sortie

	const greeting = new Date().getHours() >= 18 ? 'Bonsoir' : 'Bonjour';

	useEffect(() => {
		// Vérifier si c'est la première visite du jour
		const checkFirstVisitToday = () => {
			const today = new Date().toDateString();
			const lastVisit = localStorage.getItem('lastWelcomeShown');
			
			if (lastVisit !== today) {
				localStorage.setItem('lastWelcomeShown', today);
				setShowWelcome(true);
				
				// Déclencher un fondu de sortie doux juste avant la fin
				const t1 = window.setTimeout(() => setClosing(true), Math.max(0, DISPLAY_MS - FADE_MS));
				const t2 = window.setTimeout(() => setShowWelcome(false), DISPLAY_MS);
				return () => { window.clearTimeout(t1); window.clearTimeout(t2); };
			}
		};

		// Délai court pour laisser l'app se charger
		const id = window.setTimeout(checkFirstVisitToday, 500);
		return () => window.clearTimeout(id);
	}, []);

	if (!showWelcome) return null;

	return (
		<AnimatePresence>
			<motion.div
				initial={{ opacity: 0 }}
				animate={{ opacity: closing ? 0 : 1 }}
				exit={{ opacity: 0 }}
				transition={{ duration: closing ? FADE_MS / 1000 : 0.5 }}
				className="fixed inset-0 z-[9999] flex items-center justify-center bg-gradient-to-br from-violet-900/95 via-purple-800/95 to-indigo-900/95 backdrop-blur-sm"
				style={{ pointerEvents: showWelcome ? 'auto' : 'none' }}
			>
				{/* Particules flottantes */}
				<div className="absolute inset-0 overflow-hidden">
					{Array.from({ length: 20 }).map((_, i) => (
						<motion.div
							key={i}
							className="absolute w-1 h-1 bg-yellow-200/60 rounded-full"
							initial={{ 
								x: Math.random() * window.innerWidth,
								y: window.innerHeight + 20,
								scale: 0 
							}}
							animate={{ 
								y: -20,
								scale: [0, 1, 0],
								opacity: closing ? 0 : 1,
							}}
							transition={{
								duration: 3 + Math.random() * 2,
								delay: Math.random() * 2,
								repeat: closing ? 0 : Infinity,
								ease: 'easeOut'
							}}
						/>
					))}
				</div>

				<div className="text-center space-y-8 z-10">
					{/* Soleil violet animé */}
					<motion.div 
						className="relative mx-auto w-32 h-32"
						initial={{ scale: 0, rotate: -180 }}
						animate={{ scale: closing ? 0.95 : 1, rotate: closing ? 10 : 0, opacity: closing ? 0 : 1 }}
						transition={{ duration: 0.8, ease: 'easeOut' }}
					>
						{/* Rayons du soleil */}
						{Array.from({ length: 12 }).map((_, i) => (
							<motion.div
								key={i}
								className="absolute w-1 bg-gradient-to-t from-yellow-400 to-yellow-200 rounded-full"
								style={{ height: '2rem', left: '50%', top: '50%', transformOrigin: '50% 4rem', transform: `translate(-50%, -50%) rotate(${i * 30}deg)` }}
								initial={{ scaleY: 0, opacity: 0 }}
								animate={{ scaleY: [0, 1, 0.8, 1], opacity: closing ? 0 : [0, 1, 0.7, 1] }}
								transition={{ duration: 2, delay: 0.8 + (i * 0.1), repeat: closing ? 0 : Infinity, repeatType: 'reverse', ease: 'easeInOut' }}
							/>
						))}
						
						{/* Corps du soleil */}
						<motion.div 
							className="absolute inset-4 bg-gradient-to-br from-yellow-300 via-orange-400 to-yellow-500 rounded-full shadow-2xl"
							initial={{ scale: 0 }}
							animate={{ scale: closing ? 0.98 : 1, opacity: closing ? 0.85 : 1 }}
							transition={{ duration: 0.6 }}
						>
							{/* Gradient intérieur chaleureux */}
							<div className="absolute inset-2 bg-gradient-to-br from-yellow-200/50 to-transparent rounded-full" />
							
							{/* Petites étincelles intérieures */}
							{Array.from({ length: 6 }).map((_, i) => (
								<motion.div
									key={i}
									className="absolute w-1 h-1 bg-white rounded-full"
									style={{ left: `${30 + Math.random() * 40}%`, top: `${30 + Math.random() * 40}%` }}
									animate={{ opacity: closing ? 0 : [0, 1, 0], scale: closing ? 0.5 : [0.5, 1, 0.5] }}
									transition={{ duration: 1.5, delay: 1 + (i * 0.2), repeat: closing ? 0 : Infinity, repeatType: 'reverse' }}
								/>
							))}
						</motion.div>

						{/* Halo lumineux */}
						<motion.div 
							className="absolute -inset-8 bg-gradient-radial from-yellow-400/30 via-orange-300/20 to-transparent rounded-full"
							animate={{ scale: closing ? 0.95 : [1, 1.2, 1], opacity: closing ? 0 : [0.3, 0.6, 0.3] }}
							transition={{ duration: 0.8, repeat: closing ? 0 : Infinity, ease: 'easeInOut' }}
						/>
					</motion.div>

					{/* Message de bienvenue */}
					<motion.div
						initial={{ opacity: 0, y: 30 }}
						animate={{ opacity: closing ? 0 : 1, y: closing ? 10 : 0 }}
						transition={{ duration: 0.6, delay: 1.0 }}
						className="space-y-4"
					>
						<motion.h1 
							className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-yellow-200 via-orange-200 to-yellow-300 bg-clip-text text-transparent"
							animate={{ scale: closing ? 1 : [1, 1.04, 1] }}
							transition={{ duration: 1.6, repeat: closing ? 0 : Infinity, ease: 'easeInOut' }}
						>
							{greeting}
						</motion.h1>
						
						<motion.p 
							className="text-xl text-white/90 max-w-md mx-auto"
							initial={{ opacity: 0 }}
							animate={{ opacity: closing ? 0 : 1 }}
							transition={{ delay: 1.4 }}
						>
							Nous préparons votre espace d'analyse.
						</motion.p>

						<motion.div
							className="flex items-center justify-center space-x-2 text-orange-200"
							initial={{ opacity: 0 }}
							animate={{ opacity: closing ? 0 : 1 }}
							transition={{ delay: 1.8 }}
						>
							<span className="text-sm">SalariZ Analytics</span>
							<motion.div animate={{ scale: closing ? 1 : [1, 1.15, 1] }} transition={{ duration: 1.5, repeat: closing ? 0 : Infinity }}>
								💜
							</motion.div>
						</motion.div>
					</motion.div>

					{/* Indicateur de progression */}
					<motion.div 
						className="w-48 h-1 bg-white/20 rounded-full mx-auto overflow-hidden"
						initial={{ opacity: 0 }}
						animate={{ opacity: closing ? 0 : 1 }}
						transition={{ delay: 2.2 }}
					>
						<motion.div 
							className="h-full bg-gradient-to-r from-yellow-400 to-orange-400 rounded-full"
							initial={{ width: '0%' }}
							animate={{ width: closing ? '100%' : '100%' }}
							transition={{ duration: 1.6, delay: 2.2 }}
						/>
					</motion.div>
				</div>

				{/* Effet de chaleur en arrière-plan */}
				<motion.div
					className="absolute inset-0 bg-gradient-radial from-orange-500/10 via-transparent to-transparent"
					animate={{ scale: closing ? 0.98 : [1, 1.5, 1], opacity: closing ? 0 : [0.1, 0.3, 0.1] }}
					transition={{ duration: 0.8, repeat: closing ? 0 : Infinity, ease: 'easeInOut' }}
				/>
			</motion.div>
		</AnimatePresence>
	);
};

export default WelcomeAnimation;
