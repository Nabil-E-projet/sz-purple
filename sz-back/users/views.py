from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.signing import TimestampSigner
from django.core.mail import send_mail
from django.conf import settings
from .serializers import UserCreateSerializer, UserSerializer, RequestPasswordResetSerializer, ResetPasswordSerializer
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
        verification_url = f"{settings.FRONTEND_URL}/verify-email?redirect_token={token}"
        
        # Nom à afficher dans l'email
        display_name = (user.get_full_name() or user.username or user.email)
        
        # Email HTML moderne avec glassmorphism - cohérent avec la DA du site
        html_message = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="format-detection" content="telephone=no">
            <title>Vérification de votre compte Salariz</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: hsl(260, 15%, 15%);
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, hsl(250, 60%, 88%) 0%, hsl(260, 50%, 85%) 100%);
                    min-height: 100vh;
                }}
                .email-wrapper {{
                    max-width: 640px;
                    margin: 0 auto;
                    padding: 20px 0;
                }}
                .container {{
                    background: linear-gradient(135deg, hsla(250, 100%, 100%, 0.7) 0%, hsla(260, 100%, 95%, 0.8) 100%);
                    backdrop-filter: blur(20px);
                    border: 1px solid hsla(250, 100%, 100%, 0.2);
                    box-shadow: 0 8px 32px hsla(270, 50%, 50%, 0.1);
                    border-radius: 20px;
                    overflow: hidden;
                    margin: 0 auto;
                }}
                .header {{
                    background: linear-gradient(135deg, hsl(270, 91%, 65%) 0%, hsl(280, 100%, 75%) 100%);
                    padding: 50px 40px;
                    text-align: center;
                    color: white;
                    position: relative;
                    overflow: hidden;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: radial-gradient(circle at 30% 20%, hsla(290, 85%, 70%, 0.3) 0%, transparent 50%),
                                radial-gradient(circle at 70% 80%, hsla(270, 91%, 75%, 0.2) 0%, transparent 50%);
                    pointer-events: none;
                }}
                .logo {{
                    font-size: 42px;
                    font-weight: 800;
                    margin-bottom: 8px;
                    text-shadow: 0 2px 12px rgba(0,0,0,0.2);
                    position: relative;
                    z-index: 1;
                    letter-spacing: -1px;
                }}
                .subtitle {{
                    font-size: 18px;
                    opacity: 0.95;
                    margin: 0;
                    font-weight: 500;
                    position: relative;
                    z-index: 1;
                    letter-spacing: 0.5px;
                }}
                .content {{
                    padding: 50px 40px;
                    background: hsla(250, 100%, 100%, 0.4);
                }}
                .greeting {{
                    font-size: 28px;
                    font-weight: 700;
                    color: hsl(260, 15%, 15%);
                    margin-bottom: 24px;
                    text-align: center;
                }}
                .message {{
                    font-size: 17px;
                    color: hsl(260, 25%, 25%);
                    margin-bottom: 36px;
                    line-height: 1.7;
                    text-align: center;
                }}
                .message p {{
                    margin: 0 0 16px 0;
                }}
                .cta-container {{
                    text-align: center;
                    margin: 40px 0;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, hsl(270, 91%, 65%) 0%, hsl(280, 100%, 75%) 100%);
                    color: white;
                    text-decoration: none;
                    padding: 20px 40px;
                    border-radius: 16px;
                    font-weight: 700;
                    font-size: 18px;
                    box-shadow: 0 8px 25px hsla(270, 91%, 65%, 0.4);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    border: none;
                    cursor: pointer;
                    letter-spacing: 0.5px;
                    position: relative;
                    overflow: hidden;
                }}
                .cta-button::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, hsla(0, 0%, 100%, 0.3), transparent);
                    transition: left 0.5s;
                }}
                .cta-button:hover {{
                    transform: translateY(-4px);
                    box-shadow: 0 12px 35px hsla(270, 91%, 65%, 0.6);
                    background: linear-gradient(135deg, hsl(270, 91%, 60%) 0%, hsl(280, 100%, 70%) 100%);
                }}
                .cta-button:hover::before {{
                    left: 100%;
                }}
                .glass-card {{
                    background: hsla(250, 100%, 100%, 0.6);
                    backdrop-filter: blur(15px);
                    border: 1px solid hsla(250, 100%, 100%, 0.3);
                    border-left: 4px solid hsl(270, 91%, 65%);
                    padding: 28px;
                    margin: 32px 0;
                    border-radius: 16px;
                    box-shadow: 0 4px 16px hsla(270, 50%, 50%, 0.08);
                }}
                .info-title {{
                    font-weight: 700;
                    color: hsl(260, 15%, 15%);
                    margin-bottom: 12px;
                    font-size: 18px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}
                .info-text {{
                    color: hsl(260, 25%, 25%);
                    margin: 0;
                    line-height: 1.7;
                    font-size: 15px;
                }}
                .url-box {{
                    background: hsla(250, 100%, 100%, 0.8);
                    border: 1px solid hsla(270, 91%, 65%, 0.2);
                    padding: 16px;
                    border-radius: 12px;
                    margin-top: 16px;
                    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                    font-size: 13px;
                    word-break: break-all;
                    color: hsl(270, 91%, 65%);
                    font-weight: 500;
                }}
                .footer {{
                    background: hsla(250, 100%, 100%, 0.3);
                    backdrop-filter: blur(10px);
                    padding: 40px;
                    text-align: center;
                    border-top: 1px solid hsla(250, 100%, 100%, 0.2);
                }}
                .footer-text {{
                    color: hsl(260, 8%, 45%);
                    font-size: 14px;
                    margin: 0;
                    line-height: 1.6;
                }}
                .footer-text p {{
                    margin: 0 0 8px 0;
                }}
                .sparkles {{
                    display: inline-block;
                    margin: 0 4px;
                    animation: sparkle 2s ease-in-out infinite;
                }}
                @keyframes sparkle {{
                    0%, 100% {{ transform: scale(1) rotate(0deg); opacity: 1; }}
                    50% {{ transform: scale(1.1) rotate(180deg); opacity: 0.8; }}
                }}
                @media (max-width: 680px) {{
                    body {{
                        padding: 10px;
                    }}
                    .email-wrapper {{
                        padding: 10px 0;
                    }}
                    .container {{
                        border-radius: 16px;
                        margin: 0 10px;
                    }}
                    .header, .content, .footer {{
                        padding: 30px 24px;
                    }}
                    .logo {{
                        font-size: 36px;
                    }}
                    .subtitle {{
                        font-size: 16px;
                    }}
                    .greeting {{
                        font-size: 24px;
                    }}
                    .message {{
                        font-size: 16px;
                    }}
                    .cta-button {{
                        padding: 18px 32px;
                        font-size: 16px;
                    }}
                    .glass-card {{
                        padding: 20px;
                        margin: 24px 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-wrapper">
                <div class="container">
                    <div class="header">
                        <div class="logo">🎯 Salariz</div>
                        <div class="subtitle">Analyse intelligente de fiches de paie</div>
                    </div>
                    
                    <div class="content">
                        <div class="greeting">Bonjour {display_name} ! <span class="sparkles">✨</span></div>
                        
                        <div class="message">
                            <p>Nous sommes <strong>ravis</strong> de vous accueillir sur Salariz !</p>
                            <p>Votre compte a été créé avec succès. Pour commencer à analyser vos fiches de paie et détecter automatiquement les anomalies, vous devez d'abord vérifier votre adresse email.</p>
                        </div>
                        
                        <div class="cta-container">
                            <a href="{verification_url}" class="cta-button">
                                ✅ Vérifier mon email
                            </a>
                        </div>
                        
                        <div class="glass-card">
                            <div class="info-title">🎯 Analyse intelligente</div>
                            <div class="info-text">
                                Salariz analyse vos fiches de paie avec une IA avancée pour détecter automatiquement 
                                les anomalies et assurer la conformité avec les conventions collectives.
                            </div>
                        </div>
                        
                        <div class="glass-card">
                            <div class="info-title">⏰ Lien de vérification</div>
                            <div class="info-text">
                                Ce lien est valable <strong>24 heures</strong>. 
                                Si vous ne pouvez pas cliquer sur le bouton, copiez cette URL dans votre navigateur :
                            </div>
                            <div class="url-box">
                                {verification_url}
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <div class="footer-text">
                            <p>Merci de faire confiance à Salariz pour l'analyse de vos fiches de paie.</p>
                            <p> 2025 Salariz - Tous droits réservés</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Version texte brut pour compatibilité
        text_message = f"""Bonjour {display_name},

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
                from_email='verify@salariz.com',
                to=[user.email],
                headers={
                    'Reply-To': 'support@salariz.com',
                    'X-Mailer': 'Salariz Platform',
                    'X-Priority': '1',
                    'Importance': 'high',
                    'List-Unsubscribe': '<mailto:unsubscribe@salariz.com>'
                }
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
                    'verify@salariz.com',
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
            verification_url = f"{settings.FRONTEND_URL}/verify-email?redirect_token={token}"
            
            # Nom à afficher dans l'email
            display_name = (user.get_full_name() or user.username or user.email)
            
            # Email HTML pour le renvoi
            html_message = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <title>Nouveau lien de vérification Salariz</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: hsl(260, 15%, 15%);
                        margin: 0;
                        padding: 20px;
                        background: linear-gradient(135deg, hsl(250, 60%, 88%) 0%, hsl(260, 50%, 85%) 100%);
                        min-height: 100vh;
                    }}
                    .email-wrapper {{
                        max-width: 640px;
                        margin: 0 auto;
                        padding: 20px 0;
                    }}
                    .container {{
                        background: linear-gradient(135deg, hsla(250, 100%, 100%, 0.7) 0%, hsla(260, 100%, 95%, 0.8) 100%);
                        backdrop-filter: blur(20px);
                        border: 1px solid hsla(250, 100%, 100%, 0.2);
                        box-shadow: 0 8px 32px hsla(270, 50%, 50%, 0.1);
                        border-radius: 20px;
                        overflow: hidden;
                        margin: 0 auto;
                    }}
                    .header {{
                        background: linear-gradient(135deg, hsl(270, 91%, 65%) 0%, hsl(280, 100%, 75%) 100%);
                        padding: 50px 40px;
                        text-align: center;
                        color: white;
                        position: relative;
                        overflow: hidden;
                    }}
                    .header::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: radial-gradient(circle at 30% 20%, hsla(290, 85%, 70%, 0.3) 0%, transparent 50%),
                                    radial-gradient(circle at 70% 80%, hsla(270, 91%, 75%, 0.2) 0%, transparent 50%);
                        pointer-events: none;
                    }}
                    .logo {{
                        font-size: 42px;
                        font-weight: 800;
                        margin-bottom: 8px;
                        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
                        position: relative;
                        z-index: 1;
                        letter-spacing: -1px;
                    }}
                    .subtitle {{
                        font-size: 18px;
                        opacity: 0.95;
                        margin: 0;
                        font-weight: 500;
                        position: relative;
                        z-index: 1;
                        letter-spacing: 0.5px;
                    }}
                    .content {{
                        padding: 50px 40px;
                        background: hsla(250, 100%, 100%, 0.4);
                    }}
                    .greeting {{
                        font-size: 28px;
                        font-weight: 700;
                        color: hsl(260, 15%, 15%);
                        margin-bottom: 24px;
                        text-align: center;
                    }}
                    .message {{
                        font-size: 17px;
                        color: hsl(260, 25%, 25%);
                        margin-bottom: 36px;
                        line-height: 1.7;
                        text-align: center;
                    }}
                    .message p {{
                        margin: 0 0 16px 0;
                    }}
                    .cta-container {{
                        text-align: center;
                        margin: 40px 0;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, hsl(270, 91%, 65%) 0%, hsl(280, 100%, 75%) 100%);
                        color: white;
                        text-decoration: none;
                        padding: 20px 40px;
                        border-radius: 16px;
                        font-weight: 700;
                        font-size: 18px;
                        box-shadow: 0 8px 25px hsla(270, 91%, 65%, 0.4);
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        border: none;
                        cursor: pointer;
                        letter-spacing: 0.5px;
                        position: relative;
                        overflow: hidden;
                    }}
                    .cta-button::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, hsla(0, 0%, 100%, 0.3), transparent);
                        transition: left 0.5s;
                    }}
                    .cta-button:hover {{
                        transform: translateY(-4px);
                        box-shadow: 0 12px 35px hsla(270, 91%, 65%, 0.6);
                        background: linear-gradient(135deg, hsl(270, 91%, 60%) 0%, hsl(280, 100%, 70%) 100%);
                    }}
                    .cta-button:hover::before {{
                        left: 100%;
                    }}
                    .glass-card {{
                        background: hsla(250, 100%, 100%, 0.6);
                        backdrop-filter: blur(15px);
                        border: 1px solid hsla(250, 100%, 100%, 0.3);
                        border-left: 4px solid hsl(270, 91%, 65%);
                        padding: 28px;
                        margin: 32px 0;
                        border-radius: 16px;
                        box-shadow: 0 4px 16px hsla(270, 50%, 50%, 0.08);
                    }}
                    .info-title {{
                        font-weight: 700;
                        color: hsl(260, 15%, 15%);
                        margin-bottom: 12px;
                        font-size: 18px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}
                    .info-text {{
                        color: hsl(260, 25%, 25%);
                        margin: 0;
                        line-height: 1.7;
                        font-size: 15px;
                    }}
                    .url-box {{
                        background: hsla(250, 100%, 100%, 0.8);
                        border: 1px solid hsla(270, 91%, 65%, 0.2);
                        padding: 16px;
                        border-radius: 12px;
                        margin-top: 16px;
                        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                        font-size: 13px;
                        word-break: break-all;
                        color: hsl(270, 91%, 65%);
                        font-weight: 500;
                    }}
                    .footer {{
                        background: hsla(250, 100%, 100%, 0.3);
                        backdrop-filter: blur(10px);
                        padding: 40px;
                        text-align: center;
                        border-top: 1px solid hsla(250, 100%, 100%, 0.2);
                    }}
                    .footer-text {{
                        color: hsl(260, 8%, 45%);
                        font-size: 14px;
                        margin: 0;
                        line-height: 1.6;
                    }}
                    .footer-text p {{
                        margin: 0 0 8px 0;
                    }}
                    .sparkles {{
                        display: inline-block;
                        margin: 0 4px;
                        animation: sparkle 2s ease-in-out infinite;
                    }}
                    @keyframes sparkle {{
                        0%, 100% {{ transform: scale(1) rotate(0deg); opacity: 1; }}
                        50% {{ transform: scale(1.1) rotate(180deg); opacity: 0.8; }}
                    }}
                    @media (max-width: 680px) {{
                        body {{
                            padding: 10px;
                        }}
                        .email-wrapper {{
                            padding: 10px 0;
                        }}
                        .container {{
                            border-radius: 16px;
                            margin: 0 10px;
                        }}
                        .header, .content, .footer {{
                            padding: 30px 24px;
                        }}
                        .logo {{
                            font-size: 36px;
                        }}
                        .subtitle {{
                            font-size: 16px;
                        }}
                        .greeting {{
                            font-size: 24px;
                        }}
                        .message {{
                            font-size: 16px;
                        }}
                        .cta-button {{
                            padding: 18px 32px;
                            font-size: 16px;
                        }}
                        .glass-card {{
                            padding: 20px;
                            margin: 24px 0;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-wrapper">
                    <div class="container">
                        <div class="header">
                            <div class="logo">🎯 Salariz</div>
                            <div class="subtitle">Analyse intelligente de fiches de paie</div>
                        </div>
                        
                        <div class="content">
                            <div class="greeting">Bonjour {display_name} ! <span class="sparkles">🔄</span></div>
                            
                            <div class="message">
                                <p>Vous avez demandé un nouveau lien de vérification pour votre compte <strong>Salariz</strong>.</p>
                                <p>Cliquez sur le bouton ci-dessous pour activer votre compte et commencer à analyser vos fiches de paie :</p>
                            </div>
                            
                            <div class="cta-container">
                                <a href="{verification_url}" class="cta-button">
                                    ✅ Activer mon compte
                                </a>
                            </div>
                            
                            <div class="glass-card">
                                <div class="info-title">⏰ Lien de vérification</div>
                                <div class="info-text">
                                    Ce lien est valable <strong>24 heures</strong>. 
                                    Si vous ne pouvez pas cliquer sur le bouton, copiez cette URL dans votre navigateur :
                                </div>
                                <div class="url-box">
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
                </div>
            </body>
            </html>
            """
            
            # Version texte brut pour compatibilité
            text_message = f"""Bonjour {display_name},

Voici un nouveau lien de vérification pour activer votre compte Salariz :
{verification_url}

Ce lien est valable 24 heures.

À bientôt sur Salariz !
            """
            
            try:
                send_mail(
                    'Nouveau lien de vérification Salariz',
                    f'Bonjour {display_name},\n\nVoici votre nouveau lien de vérification : {verification_url}\n\nCe lien est valable 24 heures.\n\nCordialement,\nL\'équipe Salariz',
                    'verify@salariz.com',
                    [user.email],
                    fail_silently=False,
                    html_message=html_message
                )
                
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
                "message": "Un nouvel email de vérification a été envoyé."
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
                    path='/',
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
                path='/',
                max_age=24 * 60 * 60
            )
            # On ne renvoie pas le refresh token dans la réponse JSON
            del response.data['refresh']
            
        return response
    

class LogoutView(APIView):
    permission_classes = (AllowAny,)
    
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
            response.delete_cookie('refresh_token', path='/', samesite='Lax', secure=False)
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # Ne pas lever d'erreur si l'utilisateur n'existe pas pour éviter toute fuite d'information
            user = User.objects.filter(email=email, is_active=True).first()
            if not user:
                return Response({
                    "message": "Si cette adresse email est associée à un compte, vous recevrez un lien de réinitialisation."
                }, status=status.HTTP_200_OK)
            
            # Générer le token de reset
            signer = TimestampSigner()
            token = signer.sign(user.pk)
            
            # URL qui pointe vers le frontend
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            
            # Nom à afficher dans l'email
            display_name = (user.get_full_name() or user.username or user.email)
            
            # Email HTML pour le reset de mot de passe
            html_message = f"""
            <!DOCTYPE html>
            <html lang="fr">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Réinitialisation de votre mot de passe Salariz</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: hsl(260, 15%, 15%);
                        margin: 0;
                        padding: 20px;
                        background: linear-gradient(135deg, hsl(250, 60%, 88%) 0%, hsl(260, 50%, 85%) 100%);
                        min-height: 100vh;
                    }}
                    .email-wrapper {{
                        max-width: 640px;
                        margin: 0 auto;
                        padding: 20px 0;
                    }}
                    .container {{
                        background: linear-gradient(135deg, hsla(250, 100%, 100%, 0.7) 0%, hsla(260, 100%, 95%, 0.8) 100%);
                        backdrop-filter: blur(20px);
                        border: 1px solid hsla(250, 100%, 100%, 0.2);
                        box-shadow: 0 8px 32px hsla(270, 50%, 50%, 0.1);
                        border-radius: 20px;
                        overflow: hidden;
                        margin: 0 auto;
                    }}
                    .header {{
                        background: linear-gradient(135deg, hsl(270, 91%, 65%) 0%, hsl(280, 100%, 75%) 100%);
                        padding: 50px 40px;
                        text-align: center;
                        color: white;
                        position: relative;
                        overflow: hidden;
                    }}
                    .header::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: radial-gradient(circle at 30% 20%, hsla(290, 85%, 70%, 0.3) 0%, transparent 50%),
                                    radial-gradient(circle at 70% 80%, hsla(270, 91%, 75%, 0.2) 0%, transparent 50%);
                        pointer-events: none;
                    }}
                    .logo {{
                        font-size: 42px;
                        font-weight: 800;
                        margin-bottom: 8px;
                        text-shadow: 0 2px 12px rgba(0,0,0,0.2);
                        position: relative;
                        z-index: 1;
                        letter-spacing: -1px;
                    }}
                    .subtitle {{
                        font-size: 18px;
                        opacity: 0.95;
                        margin: 0;
                        font-weight: 500;
                        position: relative;
                        z-index: 1;
                        letter-spacing: 0.5px;
                    }}
                    .content {{
                        padding: 50px 40px;
                        background: hsla(250, 100%, 100%, 0.4);
                    }}
                    .greeting {{
                        font-size: 28px;
                        font-weight: 700;
                        color: hsl(260, 15%, 15%);
                        margin-bottom: 24px;
                        text-align: center;
                    }}
                    .message {{
                        font-size: 17px;
                        color: hsl(260, 25%, 25%);
                        margin-bottom: 36px;
                        line-height: 1.7;
                        text-align: center;
                    }}
                    .message p {{
                        margin: 0 0 16px 0;
                    }}
                    .cta-container {{
                        text-align: center;
                        margin: 40px 0;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, hsl(270, 91%, 65%) 0%, hsl(280, 100%, 75%) 100%);
                        color: white;
                        text-decoration: none;
                        padding: 20px 40px;
                        border-radius: 16px;
                        font-weight: 700;
                        font-size: 18px;
                        box-shadow: 0 8px 25px hsla(270, 91%, 65%, 0.4);
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        border: none;
                        cursor: pointer;
                        letter-spacing: 0.5px;
                        position: relative;
                        overflow: hidden;
                    }}
                    .cta-button::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, hsla(0, 0%, 100%, 0.3), transparent);
                        transition: left 0.5s;
                    }}
                    .cta-button:hover {{
                        transform: translateY(-4px);
                        box-shadow: 0 12px 35px hsla(270, 91%, 65%, 0.6);
                        background: linear-gradient(135deg, hsl(270, 91%, 60%) 0%, hsl(280, 100%, 70%) 100%);
                    }}
                    .cta-button:hover::before {{
                        left: 100%;
                    }}
                    .glass-card {{
                        background: hsla(250, 100%, 100%, 0.6);
                        backdrop-filter: blur(15px);
                        border: 1px solid hsla(250, 100%, 100%, 0.3);
                        border-left: 4px solid hsl(270, 91%, 65%);
                        padding: 28px;
                        margin: 32px 0;
                        border-radius: 16px;
                        box-shadow: 0 4px 16px hsla(270, 50%, 50%, 0.08);
                    }}
                    .info-title {{
                        font-weight: 700;
                        color: hsl(260, 15%, 15%);
                        margin-bottom: 12px;
                        font-size: 18px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}
                    .info-text {{
                        color: hsl(260, 25%, 25%);
                        margin: 0;
                        line-height: 1.7;
                        font-size: 15px;
                    }}
                    .url-box {{
                        background: hsla(250, 100%, 100%, 0.8);
                        border: 1px solid hsla(270, 91%, 65%, 0.2);
                        padding: 16px;
                        border-radius: 12px;
                        margin-top: 16px;
                        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                        font-size: 13px;
                        word-break: break-all;
                        color: hsl(270, 91%, 65%);
                        font-weight: 500;
                    }}
                    .footer {{
                        background: hsla(250, 100%, 100%, 0.3);
                        backdrop-filter: blur(10px);
                        padding: 40px;
                        text-align: center;
                        border-top: 1px solid hsla(250, 100%, 100%, 0.2);
                    }}
                    .footer-text {{
                        color: hsl(260, 8%, 45%);
                        font-size: 14px;
                        margin: 0;
                        line-height: 1.6;
                    }}
                    .footer-text p {{
                        margin: 0 0 8px 0;
                    }}
                    .sparkles {{
                        display: inline-block;
                        margin: 0 4px;
                        animation: sparkle 2s ease-in-out infinite;
                    }}
                    @keyframes sparkle {{
                        0%, 100% {{ transform: scale(1) rotate(0deg); opacity: 1; }}
                        50% {{ transform: scale(1.1) rotate(180deg); opacity: 0.8; }}
                    }}
                    .warning-card {{
                        background: hsla(45, 100%, 50%, 0.1);
                        border: 1px solid hsla(45, 100%, 50%, 0.2);
                        border-left: 4px solid hsl(45, 100%, 50%);
                        padding: 20px;
                        margin: 24px 0;
                        border-radius: 12px;
                        box-shadow: 0 2px 8px hsla(45, 100%, 50%, 0.05);
                    }}
                    .warning-title {{
                        font-weight: 700;
                        color: hsl(45, 100%, 35%);
                        margin-bottom: 8px;
                        font-size: 16px;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    }}
                    .warning-text {{
                        color: hsl(45, 100%, 25%);
                        margin: 0;
                        line-height: 1.6;
                        font-size: 14px;
                    }}
                    @media (max-width: 680px) {{
                        body {{
                            padding: 10px;
                        }}
                        .email-wrapper {{
                            padding: 10px 0;
                        }}
                        .container {{
                            border-radius: 16px;
                            margin: 0 10px;
                        }}
                        .header, .content, .footer {{
                            padding: 30px 24px;
                        }}
                        .logo {{
                            font-size: 36px;
                        }}
                        .subtitle {{
                            font-size: 16px;
                        }}
                        .greeting {{
                            font-size: 24px;
                        }}
                        .message {{
                            font-size: 16px;
                        }}
                        .cta-button {{
                            padding: 18px 32px;
                            font-size: 16px;
                        }}
                        .glass-card {{
                            padding: 20px;
                            margin: 24px 0;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-wrapper">
                    <div class="container">
                        <div class="header">
                            <div class="logo">🔐 Salariz</div>
                            <div class="subtitle">Réinitialisation de mot de passe</div>
                        </div>
                        
                        <div class="content">
                            <div class="greeting">Bonjour {display_name} ! <span class="sparkles">🔑</span></div>
                            
                            <div class="message">
                                <p>Vous avez demandé à réinitialiser votre mot de passe pour votre compte <strong>Salariz</strong>.</p>
                                <p>Cliquez sur le bouton ci-dessous pour choisir un nouveau mot de passe :</p>
                            </div>
                            
                            <div class="cta-container">
                                <a href="{reset_url}" class="cta-button">
                                    🔐 Changer mon mot de passe
                                </a>
                            </div>
                            
                            <div class="warning-card">
                                <div class="warning-title">⚠️ Sécurité</div>
                                <div class="warning-text">
                                    Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email. 
                                    Votre mot de passe actuel restera inchangé.
                                </div>
                            </div>
                            
                            <div class="glass-card">
                                <div class="info-title">⏰ Lien de réinitialisation</div>
                                <div class="info-text">
                                    Ce lien est valable <strong>1 heure</strong> pour des raisons de sécurité. 
                                    Si vous ne pouvez pas cliquer sur le bouton, copiez cette URL dans votre navigateur :
                                </div>
                                <div class="url-box">
                                    {reset_url}
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
                </div>
            </body>
            </html>
            """
            
            # Version texte brut pour compatibilité
            text_message = f"""Bonjour {display_name},

Vous avez demandé à réinitialiser votre mot de passe pour votre compte Salariz.

Cliquez sur ce lien pour choisir un nouveau mot de passe :
{reset_url}

Ce lien est valable 1 heure pour des raisons de sécurité.

Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.

À bientôt sur Salariz !
            """
            
            try:
                from django.core.mail import EmailMultiAlternatives
                
                # Créer l'email avec HTML et texte brut
                email = EmailMultiAlternatives(
                    subject='🔐 Réinitialisation de votre mot de passe Salariz',
                    body=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
                
                print(f"Email de reset de mot de passe envoyé à {user.email}")
                
                return Response({
                    "message": "Si cette adresse email est associée à un compte, vous recevrez un lien de réinitialisation."
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email de reset: {e}")
                return Response({
                    "error": "Erreur lors de l'envoi de l'email de réinitialisation."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Même en cas d'erreur de validation, on renvoie le même message pour la sécurité
        return Response({
            "message": "Si cette adresse email est associée à un compte, vous recevrez un lien de réinitialisation."
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            signer = TimestampSigner()
            try:
                # Token valable 1 heure (3600 secondes)
                user_pk = signer.unsign(token, max_age=3600)
                user = User.objects.get(pk=user_pk, is_active=True)
                
                # Réinitialiser le mot de passe
                user.set_password(new_password)
                user.save()
                
                return Response({
                    "message": "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter."
                }, status=status.HTTP_200_OK)
                
            except SignatureExpired:
                return Response({
                    "error": "Le lien de réinitialisation a expiré. Veuillez en demander un nouveau."
                }, status=status.HTTP_400_BAD_REQUEST)
            except BadSignature:
                return Response({
                    "error": "Le lien de réinitialisation est invalide."
                }, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({
                    "error": "L'utilisateur n'existe pas."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)