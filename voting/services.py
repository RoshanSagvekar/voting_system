from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from .models import *
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.urls import reverse
import datetime


class UserService:
    @staticmethod
    def register_user(data, request):
        """Handles user registration logic."""
        username = data.get("username", "").strip()
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        dob = data.get("date_of_birth")
        phone = data.get("phone_number", "").strip()
        aadhar = data.get("aadhar_number", "").strip()
        profile_picture = request.FILES.get("profile_picture")

        # Validate required fields
        if not first_name:
            raise ValidationError("First name is required.")
        if not last_name:
            raise ValidationError("Last name is required.")

        # Age Validation
        birth_date = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        age = (datetime.date.today() - birth_date).days // 365
        if age < 18:
            raise ValidationError("You must be 18+ to register.")

        # Check for duplicate email and Aadhar
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered.")
        if User.objects.filter(aadhar_number=aadhar).exists():
            raise ValidationError("Aadhar number already registered.")

        # Create user
        user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
            date_of_birth=dob,
            phone_number=phone,
            aadhar_number=aadhar,
            profile_picture=profile_picture,
            is_verified=False  # Pending email verification
        )
        user.save()

        # Generate Email Verification Token
        token = EmailVerificationToken.objects.create(user=user)

        # Send Verification Email
        verification_link = request.build_absolute_uri(reverse('verify-email', args=[token.token]))
        send_mail(
            "Verify Your Email - Online Voting System",
            f"Click the link to verify your email: {verification_link}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return user


class VotingService:
    @staticmethod
    def get_ongoing_elections():
        return Election.objects.filter(start_date__lte=now(), end_date__gte=now(), is_active=True).order_by('end_date')
    
    @staticmethod
    def get_completed_elections():
        return Election.objects.filter(end_date__lt=now(), is_active=True).order_by('end_date')

    @staticmethod
    def get_upcoming_elections():
        return Election.objects.filter(start_date__gte=now(),is_active=True).order_by('end_date')

    @staticmethod
    def get_candidates_for_election(election_id):
        election = get_object_or_404(Election, id=election_id)
        return Candidate.objects.filter(election=election)

    @staticmethod
    def cast_vote(user, election_id, candidate_id):
        election = get_object_or_404(Election, id=election_id)

        if Vote.objects.filter(voter=user, election=election).exists():
            raise ValidationError("You have already voted in this election.")

        candidate = get_object_or_404(Candidate, id=candidate_id, election=election)

        Vote.objects.create(voter=user, election=election, candidate=candidate)

        candidate.votes += 1
        candidate.save()

        return candidate


class ElectionResultService:
    @staticmethod
    def get_results(election_id):
        election = get_object_or_404(Election, id=election_id)

        candidates = Candidate.objects.filter(election=election).order_by('-votes')
        total_votes = sum(candidate.votes for candidate in candidates)

        candidate_results = [
            {
                "id": candidate.id,
                "name": candidate.name,
                "party": candidate.party,
                "votes": candidate.votes,
                "vote_percentage": round((candidate.votes / total_votes) * 100, 2) if total_votes > 0 else 0,
                "profile_picture": candidate.profile_picture.url if candidate.profile_picture else None
            }
            for candidate in candidates
        ]

        # Only declare a winner if the election has ended
        winner = election.get_winner() if election.is_completed() else None

        return {
            "election": election.name,
            "total_votes": total_votes,
            "candidates": candidate_results,
            "winner": {
                "id": winner.id,
                "name": winner.name,
                "party": winner.party,
                "votes": winner.votes,
                "vote_percentage": round((winner.votes / total_votes) * 100, 2) if total_votes > 0 else 0,
                "profile_picture": winner.profile_picture.url if winner.profile_picture else None
            } if winner else None
        }