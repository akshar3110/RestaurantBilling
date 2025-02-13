from django.shortcuts import render, redirect,get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from Store_Admin.models import CustomUser, Category, Product, Cafe  # Import your custom user model
from django.conf import settings
import random
from datetime import datetime, timedelta

# Login View
def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=username)  # ✅ Get user from DB

            if user.role is None:  # ✅ Role doesn't exist
                raise Http404("User role not assigned!")

            if check_password(password, user.password):  # ✅ Validate password manually
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['role'] = user.role.role_name  # ✅ Ensure role is stored correctly
                request.session['cafe'] = user.cafe.cafe_name if user.cafe else None

                print("Logged in user role:", user.role.role_name)  # ✅ Debugging line

                # ✅ Redirect to the correct dashboard
                if user.role.role_name == "Shop_Owner":
                    return redirect('dashboard_shop_owner', username=user.username)
                elif user.role.role_name == "Shop_Manager":
                    return redirect('dashboard_shop_manager', username=user.username)
                elif user.role.role_name == "Chef":
                    return redirect('dashboard_chef', username=user.username)
                

                messages.error(request, 'Role not recognized.')
                return redirect('loginPage')  # If no valid role, go back to login
                
            else:
                messages.error(request, 'Invalid username or password.')
        
        except CustomUser.DoesNotExist:
            messages.error(request, 'User does not exist.')

    return render(request, 'login.html')  # Reload login page on failure
# Dashboard for Shop Owner




def dashboard_shop_owner(request, username):
    # ✅ Check if user session exists
    if 'user_id' not in request.session or 'role' not in request.session:
        messages.error(request, "Please log in again.")
        return redirect('loginPage')  

    # ✅ Ensure the user is a Shop Owner
    if request.session['role'] != "Shop_Owner":
        messages.error(request, "Access denied! You are not a Shop Owner.")
        return redirect('loginPage')

    # ✅ Get username from session or fallback to URL username
    session_username = request.session.get('username', username)

    # ✅ Display success message if category was added (optional: you can manage this via session)
    success_message = request.GET.get('success', None)

    return render(request, 'others/dashboard_shop_owner.html', {
        'username': session_username,
        'role': 'Shop Owner',
        'success_message': success_message,
        'cafe' : request.session.get('cafe'),
    })


def add_category(request, username):
    # ✅ Check if user is logged in
    if 'user_id' not in request.session or 'role' not in request.session:
        messages.error(request, "Please log in again.")
        return redirect('loginPage')

    # ✅ Check if the logged-in user is a shop owner
    if request.session['role'] != "Shop_Owner":
        messages.error(request, "Access denied! You are not a Shop Owner.")
        return redirect('loginPage')

    # ✅ Fetch the logged-in user's cafe from session
    try:
        user = CustomUser.objects.get(username=username)
        if not user.cafe:
            messages.error(request, "You are not assigned to any café.")
            return redirect('dashboard_shop_owner', username=username)

        cafe = user.cafe.cafe_name  # Get cafe name linked to shop owner
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('dashboard_shop_owner', username=username)

    if request.method == 'POST':
        category_name = request.POST.get('category_name')

        if not category_name:
            messages.error(request, "Category name is required.")
        else:
            # ✅ Check if category already exists for this café
            if Category.objects.filter(name=category_name, cafe=user.cafe).exists():
                messages.error(request, f'Category "{category_name}" already exists for your café.')
                return redirect('viewCategories', username=username)
            else:
                # ✅ Automatically assign the category to the shop owner's café
                Category.objects.create(name=category_name, cafe=user.cafe)
                messages.success(request, f'Category "{category_name}" added successfully!')
                return redirect('viewCategories', username=username)

    return render(request, 'shop_owner/add_category.html', {'username': username, 'cafe': cafe})
    



def add_product(request, username):
    if 'username' not in request.session or request.session.get('role') != "Shop_Owner":
        messages.error(request, "Access denied! You are not a Shop Owner.")
        return redirect('loginPage')

    # 🔹 Get the Cafe based on session username
    cafe = get_object_or_404(Cafe, cafe_name=request.session['cafe'])

    # 🔹 Fetch all categories related to this Cafe
    categories = Category.objects.filter(cafe=cafe)

    if request.method == "POST":
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')  # Get category from dropdown
        price = request.POST.get('price')

        # 🔹 Get selected category
        category = get_object_or_404(Category, id=category_id)

        # 🔹 Create the Product
        Product.objects.create(name=product_name, category=category, price=price)

        messages.success(request, "Product added successfully!")
        return redirect('viewProducts', username=username)

    return render(request, 'shop_owner/add_product.html', {'username': username,'cafe':cafe ,'categories': categories})


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
def changePasswordView(request,username):
    if 'user_id' not in request.session:
        messages.error(request, "You must be logged in to change your password.")
        return redirect('loginPage')
    user = CustomUser.objects.get(id=request.session['user_id'])

    if user.username != username:
        messages.error(request, "Access Denied! You can only change your own password.")
        return redirect('dashboard_shop_owner', username=user.username) 

    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')


        if not check_password(current_password, user.password):  
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:  
            messages.error(request, "New passwords do not match.")
        else:
            try:
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully!")
                return redirect('dashboard_shop_owner', username=user.username)
            except Exception as e:
                messages.error(request, str(e))

    return render(request, 'change_password.html', {'username': username})

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

# def error_404(request, exception):
#     return render(request, 'common_files/404.html', status=404)
    

from django.shortcuts import render, redirect
from .models import Category
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Category, Cafe, CustomUser

def viewCategories(request, username):
    if 'user_id' not in request.session or 'role' not in request.session:
        messages.error(request, "Please log in again.")
        return redirect('loginPage')

    if request.session['role'] != "Shop_Owner":
        messages.error(request, "Access denied! You are not a Shop Owner.")
        return redirect('loginPage')

    try:
        user = CustomUser.objects.get(username=username)
        if not user.cafe:
            messages.error(request, "You are not assigned to any café.")
            return redirect('dashboard_shop_owner', username=username)

        cafe = user.cafe
        categories = Category.objects.filter(cafe=cafe)  # ✅ Show only this shop owner's café categories

    except CustomUser.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('dashboard_shop_owner', username=username)

    return render(request, 'shop_owner/view_categories.html', {'categories': categories, 'username': username, 'cafe': cafe})
def editCategory(request, username, category_id):  # Accept 'username' as an argument
    category = get_object_or_404(Category, id=category_id)
    cafe = request.session.get('cafe')

    if request.method == 'POST':
        category.name = request.POST.get('category_name')
        category.description = request.POST.get('description')
        category.save()
        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('viewCategories', username=username)

    return render(request, 'shop_owner/edit_category.html', {
        'category': category,
        'username': username,
        'cafe': cafe
    })



def deleteCategory(request, username, category_id):
    if 'username' not in request.session or request.session.get('role') != "Shop_Owner":
        messages.error(request, "Access denied! You are not a Shop Owner.")
        return redirect('loginPage')

    category = get_object_or_404(Category, id=category_id)

    # ✅ Check if there are any products under this category
    if Product.objects.filter(category=category).exists():
        messages.error(request, "Cannot delete category! There are products under this category.")
        return redirect('viewCategories', username=username)

    # ✅ If no products exist, delete the category
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect('viewCategories', username=username)

def view_products(request, username):
    if 'username' not in request.session or request.session.get('role') != "Shop_Owner":
        messages.error(request, "Access denied! You are not a Shop Owner.")
        return redirect('loginPage')

    # 🔹 Get Cafe using session data
    cafe = get_object_or_404(Cafe, cafe_name=request.session['cafe'])

    # 🔹 Fetch all products related to this Cafe
    products = Product.objects.filter(category__cafe=cafe)

    return render(request, 'shop_owner/view_products.html', {
        'username': username,
        'products': products,
        'cafe': cafe.cafe_name,
    })

def deleteProduct(request, username, product_id):
    product = get_object_or_404(Product, id=product_id)

    product.delete()
    messages.success(request, f'Product "{product.name}" deleted successfully!')

    return redirect('viewProducts', username=username)