from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from Store_Admin.models import CustomUser  # Import your custom user model
from django.conf import settings
import random
from datetime import datetime, timedelta

# Login View
def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=username)  # Fetch user from DB
            
            if check_password(password, user.password):  # ✅ Check password manually
                # Manually set session data
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['role'] = user.role.role_name if user.role else 'No role assigned'
                request.session['cafe'] = user.cafe.cafe_name if user.cafe else 'No cafe assigned'
                
                # Redirect based on role
                if user.role and user.role.role_name == "Shop_Owner":
                    return redirect('dashboard_shop_owner', username=user.username)  # Dashboard 1
                elif user.role and user.role.role_name == "Shop_Manager":
                    return redirect('dashboard_shop_manager', username=user.username)  # Dashboard 2
                elif user.role and user.role.role_name == "Chef":
                    return redirect('dashboard_chef', username=user.username)
                else:
                    messages.error(request, "Role not recognized.")
                    return redirect('loginPage')  # If no valid role, go back to login
                
            else:
                messages.error(request, 'Invalid username or password.')
        
        except CustomUser.DoesNotExist:
            messages.error(request, 'User does not exist.')

    return render(request, 'login.html')  # Reload login page on failure

# Dashboard for Shop Owner
def dashboard_shop_owner(request, username):
    return render(request, 'others/dashboard_shop_owner.html', {'username': username})

# Dashboard for Shop Manager
def dashboard_shop_manager(request, username):
    return render(request, 'others/dashboard_shop_manager.html', {'username': username})

# Dashboard for Chef
def dashboard_chef(request, username):
    return render(request, 'others/dashboard_chef.html', {'username': username})

# Logout View
def logoutView(request):
    request.session.flush()  # ✅ Clears all session data
    return redirect('loginPage')

# Change Password View
def changePasswordView(request):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in to change your password.")
        return redirect('loginPage')

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = CustomUser.objects.get(id=request.session['user_id'])

        if not check_password(current_password, user.password):  # ✅ Check current password
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:  # ✅ Ensure passwords match
            messages.error(request, "New passwords do not match.")
        else:
            try:
                # ✅ Validate password strength before saving
                CustomUser.objects.validate_password_strength(new_password)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully!")
                return redirect('dashboard_shop_owner', username=user.username)  # Change as per role
            except ValidationError as e:
                messages.error(request, e.messages[0])  # Show password error message

    return render(request, 'change_password.html')  # Load change password page

# Forgot Password View
def forgotPasswordView(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)  # ✅ Check if user exists
            otp = random.randint(100000, 999999)  # Generate OTP
            otp_expiry = datetime.now() + timedelta(minutes=10)  # OTP valid for 10 minutes

            # ✅ Store OTP in session
            request.session['reset_otp'] = otp
            request.session['reset_user'] = user.id
            request.session['otp_expiry'] = otp_expiry.strftime('%Y-%m-%d %H:%M:%S')

            # ✅ Send OTP via Email
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}. It will expire in 10 minutes.",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "OTP sent to your email.")
            return redirect('verifyOtp')

        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with this email.")

    return render(request, 'forgot_password.html')

# OTP Verification View (Assumed implementation for verifying OTP)
def verifyOtp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_expiry = datetime.strptime(request.session.get('otp_expiry'), '%Y-%m-%d %H:%M:%S')

        if int(otp_entered) == request.session.get('reset_otp') and datetime.now() < otp_expiry:
            user_id = request.session.get('reset_user')
            user = CustomUser.objects.get(id=user_id)
            return redirect('resetPassword', user_id=user.id)  # Assuming you have a reset password page
            
        else:
            messages.error(request, "Invalid OTP or OTP has expired.")
            return redirect('forgotPassword')

    return render(request, 'verify_otp.html')
