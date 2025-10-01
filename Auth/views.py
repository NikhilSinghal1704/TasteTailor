from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from TasteTailor import settings
from .tokens import generate_token
import re


def is_valid_string(input_string):
    # Define the regular expression pattern for the given conditions
    pattern = r"^[A-Za-z0-9@/./+/-/_]{1,150}$"

    # Use re.match to check if the input string matches the pattern
    if re.match(pattern, input_string):
        return True
    else:
        return False


def is_valid_password(password):
    # Check if the password has at least 8 characters
    if len(password) < 8:
        return False

    # Check if the password contains at least one special character, one numeric digit, and one alphabetic character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False  # No special character
    if not re.search(r"\d", password):
        return False  # No numeric digit

    # If all checks pass, the password is valid
    return True


# Create your views here.
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]

        if User.objects.filter(username=username):
            return render(
                request, "signup.html", {"umessage": "Username already exist"}
            )

        elif is_valid_string(username) == False:
            return render(
                request,
                "signup.html",
                {
                    "umessage": "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only"
                },
            )

        elif User.objects.filter(email=email):
            messages.error(request, "Email already exist try Logging In")
            return redirect("/authentication/signup")

        elif is_valid_password(pass1) == False:
            messages.error(
                request,
                "Password should contain 8 characters, at least one alphabetic character, at least one special character, and at least one number.",
            )
            return render(request, "signup.html", {"pmessage": "Invalid Password"})

        elif pass1 != pass2:
            return render(
                request, "signup.html", {"pmessage": "Password doesn't match"}
            )

        myuser = User.objects.create_user(username, email, pass1)
        myuser.is_active = False

        myuser.save()

        messages.success(request, "Account Created")

        # Email Address Confirmation Email

        current_site = get_current_site(request)
        email_subject = "Confirmation Email"
        email_message = render_to_string(
            "email_confirmation.html",
            {
                "name": myuser.username,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
                "token": generate_token.make_token(myuser),
            },
        )
        email = EmailMessage(
            email_subject, email_message, settings.EMAIL_HOST_USER, [myuser.email]
        )
        email.fail_silently = False
        email.send()

        return render(request, "message.html")

    return render(request, "signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["pass1"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect("/")

        else:
            return render(request, "signin.html", {"message": "Wrong Credentials"})

    return render(request, "signin.html")


def signout(request):
    logout(request)
    messages.success(request, "logged Out Successfully")
    return redirect("/")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        messages.success(request, "Account Activated")
        return redirect("/authentication/signin")

    else:
        messages.error(request, "Invalid Email")
        return redirect("/authentication/signup")
