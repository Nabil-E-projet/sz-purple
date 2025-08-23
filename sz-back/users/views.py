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
        try:
            send_mail(
                'Vérifiez votre adresse email - Salariz',
                f'Bonjour,\n\nMerci de vous être inscrit sur Salariz !\n\nPour activer votre compte, cliquez sur ce lien :\n{verification_url}\n\nCe lien est valable 24 heures.\n\nÀ bientôt sur Salariz !',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            print(f"Email de vérification envoyé à {user.email}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            # Ne pas faire échouer l'inscription à cause de l'email
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
            
            send_mail(
                'Vérifiez votre adresse email - Salariz',
                f'Bonjour,\n\nVoici un nouveau lien de vérification pour activer votre compte Salariz :\n{verification_url}\n\nCe lien est valable 24 heures.\n\nÀ bientôt sur Salariz !',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
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