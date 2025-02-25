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