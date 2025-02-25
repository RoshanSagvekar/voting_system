import os
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from datetime import date

# Function to upload profile pictures
def upload_profile_pic(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"profile_pics/{uuid.uuid4()}.{ext}"  # Unique filename
    return os.path.join('uploads/', filename)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('voter', 'Voter'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='voter')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)  # For age verification
    profile_picture = models.ImageField(upload_to=upload_profile_pic, null=True, blank=True)
    aadhar_number = models.CharField(max_length=12, unique=True, null=True, blank=True)  # Unique ID
    is_verified = models.BooleanField(default=False)  # Email verification status
    
    # Enforce mandatory first_name and last_name
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    # Fix related_name conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",  # Avoids clash with default User model
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",  # Avoids clash
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


    def __str__(self):
        return self.username

    # Age verification function
    def is_eligible(self):
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age >= 18
        return False
    

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


# Election model to store election details
class Election(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)  # Controls if voting is open

    def __str__(self):
        return self.name
    
    def is_ongoing(self):
        return self.start_date <= now() <= self.end_date

    def is_completed(self):
        return now() > self.end_date
    
    def get_winner(self):
        """Returns the candidate with the highest votes"""
        if not self.is_completed():
            return None
        return self.candidate_set.order_by('-votes').first()


# Candidate model to store candidates running in elections
class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    party = models.CharField(max_length=255)
    description = models.TextField()
    votes = models.IntegerField(default=0)  # To store vote count
    profile_picture = models.ImageField(upload_to=upload_profile_pic, null=True, blank=True)  # Candidate picture

    def __str__(self):
        return f"{self.name} ({self.party})"


# Vote model to store each user's vote
class Vote(models.Model):
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voter', 'election')  # Prevents duplicate votes

    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.name}"


# Result model to store election outcomes
class Result(models.Model):
    election = models.OneToOneField(Election, on_delete=models.CASCADE)
    winner = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    def __str__(self):
        return f"Winner: {self.winner.name} ({self.election.name})"
