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

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False  # désactiver jusqu'à confirmation de l'email
        user.save()
        signer = TimestampSigner()
        token = signer.sign(user.pk)
        verification_url = f"http://localhost:8000/api/verify-email/?token={token}"
        send_mail(
            'Vérifiez votre adresse email',
            f'Cliquez sur ce lien pour valider votre adresse email : {verification_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


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
#           frontend_url = "http://localhost:3000/verification-success"
#           return redirect(frontend_url)   
            return Response({"message": "Email vérifié avec succès"}, status=status.HTTP_200_OK)
        except SignatureExpired:
            return Response({"error": "Le token a expiré"}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"error": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "L'utilisateur n'existe pas"}, status=status.HTTP_400_BAD_REQUEST)
        
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