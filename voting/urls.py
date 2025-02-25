from django.urls import path
from .views import *
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Frontend Endpoints
    path('', home, name="home"),
    path('register/', register_page, name="register"),
    path('login/', login_page, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("vote/", vote_page, name="vote"),
    path("results/", result_page, name="results"),
    path('email-verified/', TemplateView.as_view(template_name="email_verified.html"), name="email-verified"),
    path('forgot-password/',forgot_password_page,name="forgot_password"),
    path('reset-password/<str:uid>/<str:token>',reset_password_page,name="reset-password"),
    # API Endpoints
    path('api/register/', RegisterAPIView.as_view(), name="api-register"),
    path('api/verify-email/<uuid:token>/', VerifyEmailAPIView.as_view(), name="verify-email"),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('api/elections/', ElectionsAPIView.as_view(), name='ongoing-elections'),
    path('api/elections/<int:election_id>/vote/', SubmitVoteAPIView.as_view(), name='submit-vote'),
    path('api/elections/<int:election_id>/results/', ElectionResultsAPIView.as_view(), name='election-results'),
    path("api/elections/<int:election_id>/candidates/", ElectionCandidatesAPIView.as_view(), name="election-candidates"),

    path('api/password-reset/', ForgotPasswordView.as_view(), name='password-reset'),
    path('api/password-reset-confirm/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='password-reset-confirm'),

]