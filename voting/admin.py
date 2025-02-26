import datetime
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.urls import path, reverse
from django.shortcuts import render
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.contrib.auth.models import Group
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from .models import *
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
import base64
from io import BytesIO

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'display_profile_pic', 'aadhar_number', 'is_verified')
    search_fields = ('username', 'email', 'aadhar_number')
    list_filter = ('is_verified',)

    # Specify only the required fields in the form
    fields = [
        "username", "first_name", "last_name", "email", "password",
        "date_of_birth", "phone_number", "aadhar_number", "profile_picture","is_verified"
    ]

    def display_profile_pic(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:50%;" />', obj.profile_picture.url)
        return "No Image"

    display_profile_pic.short_description = "Profile Picture"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().add_view(request, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """Override save_model to apply custom registration logic in Django Admin."""
        
        if change:  # If updating user
            # Check if password was changed in the form
            old_user = self.model.objects.get(pk=obj.pk)
            if obj.password != old_user.password:  # Only hash if changed
                obj.password = make_password(obj.password)
        else:  # If creating a new user
            obj.password = make_password(obj.password)
            obj.is_verified = False  # Pending email verification

        super().save_model(request, obj, form, change)

        # Generate Email Verification Token only for new users
        if not change:
            token, created = EmailVerificationToken.objects.get_or_create(user=obj)

            # Send Verification Email
            verification_link = request.build_absolute_uri(reverse('verify-email', args=[token.token]))
            send_mail(
                "Verify Your Email - Online Voting System",
                f"Click the link to verify your email: {verification_link}",
                settings.EMAIL_HOST_USER,
                [obj.email],
                fail_silently=False,
            )

class CandidateInline(admin.TabularInline):
    """Display candidates inside the election page"""
    model = Candidate
    extra = 0  # Do not show empty candidate slots

class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'display_winner', 'total_votes')
    search_fields = ('name',)
    list_filter = ('is_active', 'start_date', 'end_date')
    inlines = [CandidateInline]
    readonly_fields = ('results_chart',)

    @admin.display(description="Winner")
    def display_winner(self, obj):
        """Display the election winner dynamically"""
        if not obj.end_date or obj.end_date > now():
            return "Results Pending"

        winner = obj.get_winner()
        return f"{winner.name} ({winner.party})" if winner else "No winner"

    @admin.display(description="Total Votes")
    def total_votes(self, obj):
        """Calculate total votes in an election"""
        return Vote.objects.filter(election=obj).count()

    def results_chart(self, obj):
        """Generate a pie chart for vote distribution"""
        if not obj.end_date or obj.end_date > now():
            return "Results will be available after the election ends."

        candidates = Candidate.objects.filter(election=obj)
        labels = [candidate.name for candidate in candidates]
        votes = [candidate.votes for candidate in candidates]

        if not any(votes):  # If no votes are cast
            return "No votes cast yet."

        # Create the pie chart
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(votes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

        # Convert plot to a PNG image
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()

        return format_html('<img src="data:image/png;base64,{}" style="width:100%;"/>', image_base64)

    results_chart.short_description = "Election Results Chart"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().add_view(request, form_url, extra_context)


class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'election', 'votes', 'vote_percentage', 'profile_pic_preview')
    search_fields = ('name', 'party', 'election__name')
    list_filter = ('election',)

    def vote_percentage(self, obj):
        """Calculate vote percentage dynamically"""
        total_votes = sum(c.votes for c in Candidate.objects.filter(election=obj.election))
        return f"{(obj.votes / total_votes * 100):.2f}%" if total_votes > 0 else "0%"

    vote_percentage.short_description = "Vote %"

    def profile_pic_preview(self, obj):
        """Show profile picture thumbnail in admin panel"""
        if obj.profile_picture:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;" />', obj.profile_picture.url)
        return "No Image"

    profile_pic_preview.short_description = "Profile Picture"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        return super().add_view(request, form_url, extra_context)


class CustomAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        """Override admin index to pass data to template"""
        extra_context = extra_context or {}
        extra_context.update({
            'total_users': User.objects.count(),
            'total_elections': Election.objects.count(),
            'total_votes': Vote.objects.count(),
            'total_candidates': Candidate.objects.count(),
        })
        return super().index(request, extra_context=extra_context)


# Register custom admin site
admin.site = CustomAdminSite()
admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Vote)