from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import RegisterView, UserProfileView, EmailVerificationView, ResendVerificationView, CustomTokenObtainPairView, LogoutView, CookieTokenRefreshView, RequestPasswordResetView, ResetPasswordView
from django.http import HttpResponse

# Vue simple pour le health check
def health_check(request):
    return HttpResponse("OK", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Auth endpoints
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('api/verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('api/resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path('api/request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    # Documents endpoints
    path('api/payslips/', include('documents.urls')),
    # Analysis endpoints
    path('api/analysis/', include('analysis.urls')),
    # Billing endpoints
    path('api/billing/', include('billing.urls')),
    # Nouvel endpoint de health check
    path('health/', health_check, name='health_check'),


]

# Ajouter cette configuration pour servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)