import unittest
from django.test import TestCase
from ..pii.recognizers import nir_valid, NIR_RE_COMPILED
from ..pii.masking import token_hex, mask_keep_edges
from ..pii.pipeline import detect_pii, pseudonymize


class TestPIIDetection(TestCase):
    """Tests pour la détection et pseudonymisation des PII."""
    
    def test_nir_validation(self):
        """Test de validation des NIR avec clé de contrôle."""
        # NIR valides
        valid_nirs = [
            "1 85 03 75 118 075 23",  # Femme née en 1985
            "2 95 12 2A 001 234 56",  # Homme né en Corse du Sud
            "1 88 07 2B 002 123 09",  # Femme née en Corse du Nord
        ]
        
        for nir in valid_nirs:
            with self.subTest(nir=nir):
                self.assertTrue(nir_valid(nir), f"NIR {nir} devrait être valide")
    
    def test_nir_regex(self):
        """Test de détection par regex des NIR."""
        text = "Mon NIR est 1 85 03 75 118 075 23 et mon IBAN FR14 2004 1010 0505 0001 3M02 606"
        
        matches = list(NIR_RE_COMPILED.finditer(text))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group(), "1 85 03 75 118 075 23")
    
    def test_masking_functions(self):
        """Test des fonctions de masquage."""
        # Test token déterministe
        secret = b"test-secret"
        salt = b"doc123"
        
        token1 = token_hex("Jean Dupont", secret, salt)
        token2 = token_hex("Jean Dupont", secret, salt)
        self.assertEqual(token1, token2, "Le token doit être déterministe")
        
        token3 = token_hex("Marie Martin", secret, salt)
        self.assertNotEqual(token1, token3, "Différentes valeurs doivent donner différents tokens")
        
        # Test masquage avec edges
        masked = mask_keep_edges("1234567890", 2, 2)
        self.assertEqual(masked, "12******90")
        
        masked_iban = mask_keep_edges("FR1420041010050500013M02606", 4, 4)
        self.assertEqual(masked_iban, "FR14*******************2606")
    
    def test_pii_detection_integration(self):
        """Test d'intégration de la détection PII."""
        text = """
        Nom: Jean MARTIN
        NIR: 1 85 03 75 118 075 23
        IBAN: FR14 2004 1010 0505 0001 3M02 606
        Email: jean.martin@example.com
        Téléphone: 06 12 34 56 78
        """
        
        # Note: Ce test nécessite spaCy et Presidio installés
        try:
            results = detect_pii(text)
            
            # Vérifier qu'on détecte au moins quelques types
            detected_types = {r.entity_type for r in results}
            
            # On s'attend à détecter au moins certains types
            # (Note: les résultats exacts dépendent du modèle spaCy)
            self.assertGreater(len(results), 0, "Au moins une entité PII devrait être détectée")
            
        except ImportError:
            self.skipTest("spaCy ou Presidio non installé")
    
    def test_pseudonymization(self):
        """Test de pseudonymisation."""
        from unittest.mock import Mock
        
        # Mock des résultats de détection
        mock_results = [
            Mock(entity_type="PERSON", start=5, end=16, score=0.9),  # "Jean MARTIN"
            Mock(entity_type="NIR_FR", start=22, end=45, score=0.95),  # NIR
        ]
        
        text = "Nom: Jean MARTIN\nNIR: 1 85 03 75 118 075 23"
        doc_digest = "abc123"
        
        pseudonymized = pseudonymize(text, mock_results, doc_digest)
        
        # Vérifier que les PII ont été remplacées
        self.assertNotIn("Jean MARTIN", pseudonymized)
        self.assertIn("[PERSON_", pseudonymized)
        self.assertIn("[NIR_FR:", pseudonymized)


class TestPIIUtils(TestCase):
    """Tests pour les utilitaires PII."""
    
    def test_whitelist_preservation(self):
        """Test que la whitelist est respectée."""
        from ..pii.pipeline import WHITELIST
        from unittest.mock import Mock
        
        # Mock un résultat qui correspond à la whitelist
        mock_results = [
            Mock(entity_type="PERSON", start=0, end=15, score=0.9),
        ]
        
        text = "Salaire de base: 2500€"
        doc_digest = "test"
        
        pseudonymized = pseudonymize(text, mock_results, doc_digest)
        
        # "Salaire de base" ne doit pas être masqué car dans la whitelist
        self.assertEqual(pseudonymized, text)
    
    def test_score_thresholds(self):
        """Test que les seuils de score sont respectés."""
        from unittest.mock import Mock
        
        # Mock avec score trop faible
        mock_results = [
            Mock(entity_type="PERSON", start=0, end=4, score=0.3),  # Score trop faible
        ]
        
        text = "Test"
        doc_digest = "test"
        
        pseudonymized = pseudonymize(text, mock_results, doc_digest)
        
        # Aucun changement car score trop faible
        self.assertEqual(pseudonymized, text)
