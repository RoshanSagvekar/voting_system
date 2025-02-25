from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound, ValidationError

from voting.serializers import *
from voting.services import ElectionResultService, UserService, VotingService
from .models import User, EmailVerificationToken
from django.contrib.auth.decorators import login_required



def home(request):
    return render(request, "home.html")

def register_page(request):
    return render(request, "register.html")

def login_page(request):
    return render(request, "login.html")

def dashboard(request):
    return render(request, "dashboard.html")

def vote_page(request):
    return render(request, "vote.html")

def result_page(request):
    return render(request, "results.html")

def forgot_password_page(request):
    return render(request, "forgot_password.html")

def reset_password_page(request,uid,token):
    return render(request, "reset_password.html")

class RegisterAPIView(APIView):
    """Handles User Registration API"""

    def post(self, request):
        try:
            # Validate request data
            serializer = UserSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            # Register the user using service layer
            UserService.register_user(request.data, request)

            return Response({"message": "User registered successfully! Check your email for verification."}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({ "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      

class VerifyEmailAPIView(APIView):
    def get(self, request, token):
        try:
            token_obj = get_object_or_404(EmailVerificationToken, token=token)
            user = token_obj.user
            user.is_verified = True
            user.save()
            token_obj.delete()  # Remove token after verification

            # Redirect user to email verification success page
            return redirect('email-verified')

        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Login API

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({
            "access_token": response.data["access"],
            "refresh_token": response.data["refresh"],
            "message": "Login successful!",
        }, status=status.HTTP_200_OK)
    

# Profile
class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # For handling file uploads

    def get(self, request):
        """Fetch user profile details"""
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "date_of_birth": user.date_of_birth,
            "aadhar_number": user.aadhar_number,
            "profile_picture": request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update user profile details"""
        user = request.user
        data = request.data

        user.phone_number = data.get("phone_number", user.phone_number)
        user.date_of_birth = data.get("date_of_birth", user.date_of_birth)
        if "profile_picture" in request.FILES:
            user.profile_picture = request.FILES["profile_picture"]
        
        user.save()
        return Response({"message": "Profile updated successfully!"}, status=status.HTTP_200_OK)
    


class ElectionsAPIView(APIView):
    """Fetch all ongoing elections with candidates"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            ongoing_elections = ElectionSerializer(VotingService.get_ongoing_elections(), many=True, context={'request': request}).data
            upcoming_elections = ElectionSerializer(VotingService.get_upcoming_elections(), many=True, context={'request': request}).data
            completed_elections = ElectionSerializer(VotingService.get_completed_elections(), many=True, context={'request': request}).data
            return Response({"ongoing_elections": ongoing_elections,"completed_elections":completed_elections,"upcoming_elections":upcoming_elections}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ElectionCandidatesAPIView(APIView):
    """Fetch all candidates for a given election."""
    permission_classes = [IsAuthenticated]

    def get(self, request, election_id):
        try:
            election = get_object_or_404(Election, id=election_id)
            candidates = VotingService.get_candidates_for_election(election_id)
            serializer = CandidateSerializer(candidates, many=True)

            return Response({
                "election_name": election.name,
                "candidates": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubmitVoteAPIView(APIView):
    """API for users to cast their vote (Only once per election)"""
    permission_classes = [IsAuthenticated]

    def post(self, request,election_id):
        try:
            user = request.user
            candidate_id = request.data.get("candidate_id")

            candidate = VotingService.cast_vote(user, election_id, candidate_id)
            return Response({"message": "Vote submitted successfully!!", "candidate": candidate.name}, status=status.HTTP_201_CREATED)
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ElectionResultsAPIView(APIView):
    """Fetch results for completed elections"""
    permission_classes = [IsAuthenticated]

    def get(self, request, election_id):
        try:
            results = ElectionResultService.get_results(election_id)
            return Response(results, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e.detail[0]) if isinstance(e.detail, list) else str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from django.utils.encoding import force_bytes, force_str     
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link  = request.build_absolute_uri(reverse('reset-password', args=[uid,token]))
            # reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            return Response({"message": "Password reset link sent!"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                password = request.data.get("password")
                confirm_password = request.data.get("confirm_password")

                # Validate password and confirm_password
                if not password or not confirm_password:
                    return Response({"message": "Both password fields are required."}, status=status.HTTP_400_BAD_REQUEST)

                if password != confirm_password:
                    return Response({"message": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

                if len(password) < 6:
                    return Response({"message": "Password must be at least 6 characters."}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(password)
                user.save()
                return Response({"message": "Password reset successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

