from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.signing import TimestampSigner
from django.core.mail import send_mail
from django.conf import settings
from .serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.core.signing import SignatureExpired, BadSignature
from django.shortcuts import redirect 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils import timezone
from rest_framework_simplejwt.exceptions import InvalidToken

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        # Vérifier si un utilisateur non vérifié existe déjà
        email = request.data.get('email')
        username = request.data.get('username')
        
        if email:
            existing_user = User.objects.filter(email=email, is_active=False, is_email_verified=False).first()
            if existing_user:
                # Renvoyer l'email de vérification pour l'utilisateur existant
                self.send_verification_email(existing_user)
                return Response({
                    "message": "Un compte avec cette adresse email existe déjà mais n'est pas vérifié. Un nouvel email de vérification a été envoyé.",
                    "email": email
                }, status=status.HTTP_200_OK)
        
        if username:
            existing_user = User.objects.filter(username=username, is_active=False, is_email_verified=False).first()
            if existing_user:
                # Renvoyer l'email de vérification pour l'utilisateur existant
                self.send_verification_email(existing_user)
                return Response({
                    "message": "Un compte avec ce nom d'utilisateur existe déjà mais n'est pas vérifié. Un nouvel email de vérification a été envoyé.",
                    "email": existing_user.email
                }, status=status.HTTP_200_OK)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False  # désactiver jusqu'à confirmation de l'email
        user.save()
        self.send_verification_email(user)
    
    def send_verification_email(self, user):
        signer = TimestampSigner()
        token = signer.sign(user.pk)
        # URL qui pointe directement vers le frontend avec redirection automatique
        verification_url = f"http://localhost:8080/verify-email?redirect_token={token}"
        
        # Email HTML moderne et professionnel
        html_message = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vérification de votre compte Salariz</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f8fafc;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px 30px;
                    text-align: center;
                    color: white;
                    border-radius: 12px 12px 0 0;
                }}
                .logo {{
                    font-size: 36px;
                    font-weight: bold;
                    margin-bottom: 12px;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .subtitle {{
                    font-size: 16px;
                    opacity: 0.95;
                    margin: 0;
                    font-weight: 500;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 24px;
                    font-weight: 600;
                    color: #2d3748;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    color: #4a5568;
                    margin-bottom: 30px;
                    line-height: 1.7;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    padding: 18px 36px;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 16px;
                    margin: 25px 0;
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
                    transition: all 0.3s ease;
                    border: none;
                    cursor: pointer;
                }}
                .cta-button:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
                    background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
                }}
                .info-box {{
                    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    border-left: 4px solid #667eea;
                    padding: 24px;
                    margin: 30px 0;
                    border-radius: 0 12px 12px 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    border: 1px solid #e2e8f0;
                }}
                .info-title {{
                    font-weight: 700;
                    color: #1e293b;
                    margin-bottom: 12px;
                    font-size: 16px;
                }}
                .info-text {{
                    color: #475569;
                    margin: 0;
                    line-height: 1.6;
                    font-size: 14px;
                }}
                .footer {{
                    background-color: #f8fafc;
                    padding: 30px;
                    text-align: center;
                    border-top: 1px solid #e2e8f0;
                }}
                .footer-text {{
                    color: #718096;
                    font-size: 14px;
                    margin: 0;
                }}
                .social-links {{
                    margin-top: 20px;
                }}
                .social-link {{
                    display: inline-block;
                    margin: 0 10px;
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 500;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        margin: 20px;
                        border-radius: 8px;
                    }}
                    .header, .content, .footer {{
                        padding: 30px 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎯 Salariz</div>
                    <div class="subtitle">Analyse intelligente de fiches de paie</div>
                </div>
                
                <div class="content">
                    <div class="greeting">Bonjour ! 👋</div>
                    
                    <div class="message">
                        <p>Nous sommes ravis de vous accueillir sur <strong>Salariz</strong> !</p>
                        <p>Votre compte a été créé avec succès. Pour commencer à analyser vos fiches de paie et détecter automatiquement les anomalies, vous devez d'abord vérifier votre adresse email.</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="cta-button">
                            ✅ Vérifier mon email
                        </a>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-title">🎯 Analyse intelligente</div>
                        <div class="info-text">
                            Salariz analyse vos fiches de paie avec une IA avancée pour détecter automatiquement 
                            les anomalies et assurer la conformité avec les conventions collectives.
                        </div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-title">⏰ Lien de vérification</div>
                        <div class="info-text">
                            Ce lien est valable <strong>24 heures</strong>. 
                            Si vous ne pouvez pas cliquer sur le bouton, copiez cette URL dans votre navigateur :
                        </div>
                        <div style="background: #f1f5f9; padding: 12px; border-radius: 6px; margin-top: 10px; font-family: monospace; font-size: 14px; word-break: break-all; color: #475569;">
                            {verification_url}
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="footer-text">
                        <p>Merci de faire confiance à Salariz pour l'analyse de vos fiches de paie.</p>
                        <p>© 2025 Salariz - Tous droits réservés</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Version texte brut pour compatibilité
        text_message = f"""Bonjour !

Merci de vous être inscrit sur Salariz !

Pour activer votre compte, cliquez sur ce lien :
{verification_url}

Ce lien est valable 24 heures.

À bientôt sur Salariz !
        """
        
        try:
            from django.core.mail import EmailMultiAlternatives
            
            # Créer l'email avec HTML et texte brut
            email = EmailMultiAlternatives(
                subject='🎯 Bienvenue sur Salariz - Vérifiez votre email',
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            print(f"Email de vérification HTML envoyé à {user.email}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email HTML: {e}")
            # Fallback vers l'ancien système si problème
            try:
                send_mail(
                    'Vérifiez votre adresse email - Salariz',
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                print(f"Email de vérification texte envoyé à {user.email}")
            except Exception as e2:
                print(f"Erreur lors de l'envoi de l'email texte: {e2}")
                pass


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        token = request.GET.get("token")
        if not token:
            return Response({"error": "Aucun token fourni"}, status=status.HTTP_400_BAD_REQUEST)
        
        signer = TimestampSigner()
        try:
            user_pk = signer.unsign(token, max_age=86400)  # token valable 1 jour
            user = User.objects.get(pk=user_pk)
            user.is_active = True
            user.is_email_verified = True
            user.save()
            
            return Response({"message": "Email vérifié avec succès"}, status=status.HTTP_200_OK)
        except SignatureExpired:
            return Response({"error": "Le token a expiré"}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"error": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "L'utilisateur n'existe pas"}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "L'adresse email est requise"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email, is_active=False, is_email_verified=False)
            
            # Renvoyer l'email de vérification
            signer = TimestampSigner()
            token = signer.sign(user.pk)
            verification_url = f"http://localhost:8080/verify-email?redirect_token={token}"
            
            # Email HTML pour le renvoi
            html_message = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Nouveau lien de vérification Salariz</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                        background-color: #f8fafc;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 40px 30px;
                        text-align: center;
                        color: white;
                        border-radius: 12px 12px 0 0;
                    }}
                    .logo {{
                        font-size: 36px;
                        font-weight: bold;
                        margin-bottom: 12px;
                        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .subtitle {{
                        font-size: 16px;
                        opacity: 0.95;
                        margin: 0;
                        font-weight: 500;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .greeting {{
                        font-size: 24px;
                        font-weight: 600;
                        color: #2d3748;
                        margin-bottom: 20px;
                    }}
                    .message {{
                        font-size: 16px;
                        color: #4a5568;
                        margin-bottom: 30px;
                        line-height: 1.7;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        padding: 18px 36px;
                        border-radius: 10px;
                        font-weight: 700;
                        font-size: 16px;
                        margin: 25px 0;
                        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
                        transition: all 0.3s ease;
                        border: none;
                        cursor: pointer;
                    }}
                    .cta-button:hover {{
                        transform: translateY(-3px);
                        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
                        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
                    }}
                    .info-box {{
                        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                        border-left: 4px solid #667eea;
                        padding: 24px;
                        margin: 30px 0;
                        border-radius: 0 12px 12px 0;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                        border: 1px solid #e2e8f0;
                    }}
                    .info-title {{
                        font-weight: 700;
                        color: #1e293b;
                        margin-bottom: 12px;
                        font-size: 16px;
                    }}
                    .info-text {{
                        color: #475569;
                        margin: 0;
                        line-height: 1.6;
                        font-size: 14px;
                    }}
                    .footer {{
                        background-color: #f8fafc;
                        padding: 30px;
                        text-align: center;
                        border-top: 1px solid #e2e8f0;
                    }}
                    .footer-text {{
                        color: #718096;
                        font-size: 14px;
                        margin: 0;
                    }}
                    @media (max-width: 600px) {{
                        .container {{
                            margin: 20px;
                            border-radius: 8px;
                        }}
                        .header, .content, .footer {{
                            padding: 30px 20px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🎯 Salariz</div>
                        <div class="subtitle">Analyse intelligente de fiches de paie</div>
                    </div>
                    
                    <div class="content">
                        <div class="greeting">Nouveau lien de vérification 🔄</div>
                        
                        <div class="message">
                            <p>Vous avez demandé un nouveau lien de vérification pour votre compte <strong>Salariz</strong>.</p>
                            <p>Cliquez sur le bouton ci-dessous pour activer votre compte et commencer à analyser vos fiches de paie :</p>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="{verification_url}" class="cta-button">
                                ✅ Activer mon compte
                            </a>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-title">⏰ Lien de vérification</div>
                            <div class="info-text">
                                Ce lien est valable <strong>24 heures</strong>. 
                                Si vous ne pouvez pas cliquer sur le bouton, copiez cette URL dans votre navigateur :
                            </div>
                            <div style="background: #f1f5f9; padding: 12px; border-radius: 6px; margin-top: 10px; font-family: monospace; font-size: 14px; word-break: break-all; color: #475569;">
                                {verification_url}
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <div class="footer-text">
                            <p>Merci de faire confiance à Salariz pour l'analyse de vos fiches de paie.</p>
                            <p>© 2025 Salariz - Tous droits réservés</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Version texte brut pour compatibilité
            text_message = f"""Bonjour,

Voici un nouveau lien de vérification pour activer votre compte Salariz :
{verification_url}

Ce lien est valable 24 heures.

À bientôt sur Salariz !
            """
            
            try:
                from django.core.mail import EmailMultiAlternatives
                
                # Créer l'email avec HTML et texte brut
                email = EmailMultiAlternatives(
                    subject='🔄 Nouveau lien de vérification Salariz',
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
                
                print(f"Email de renvoi HTML envoyé à {user.email}")
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email HTML: {e}")
                # Fallback vers l'ancien système si problème
                send_mail(
                    'Vérifiez votre adresse email - Salariz',
                    text_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                print(f"Email de renvoi texte envoyé à {user.email}")
            
            return Response({
                "message": "Un nouvel email de vérification a été envoyé.",
                "email": email
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                "error": "Aucun compte non vérifié trouvé avec cette adresse email."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": "Erreur lors de l'envoi de l'email de vérification."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
    

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Mettre à jour last_login
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
            except User.DoesNotExist:
                pass
            
            # Stocker le refresh token dans un cookie httpOnly
            if response.data.get('refresh'):
                refresh_token = response.data['refresh']
                response.set_cookie(
                    'refresh_token',
                    refresh_token,
                    httponly=True,
                    samesite='Lax',
                    # En développement, on peut mettre secure=False
                    secure=False,  # Mettre à True en production (HTTPS)
                    max_age=24 * 60 * 60  # 1 jour
                )
                # Supprimer le refresh token de la réponse JSON
                del response.data['refresh']
                
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Récupérer le refresh token du cookie
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            request.data['refresh'] = refresh_token
        
        response = super().post(request, *args, **kwargs)
        
        # Avec ROTATE_REFRESH_TOKENS=True, on reçoit un nouveau refresh token
        if response.status_code == 200 and response.data.get('refresh'):
            new_refresh_token = response.data['refresh']
            response.set_cookie(
                'refresh_token',
                new_refresh_token,
                httponly=True,
                samesite='Lax',
                secure=False,  # Mettre à True en production
                max_age=24 * 60 * 60
            )
            # On ne renvoie pas le refresh token dans la réponse JSON
            del response.data['refresh']
            
        return response
    

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            # Récupérer le refresh token du cookie
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                # Blacklister le token
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Préparer la réponse
            response = Response({"message": "Déconnexion réussie"}, status=status.HTTP_205_RESET_CONTENT)
            # Supprimer le cookie
            response.delete_cookie('refresh_token')
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)