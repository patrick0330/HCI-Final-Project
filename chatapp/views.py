from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date, timedelta
from .models import QuestionAnswer
import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Create your views here.
openai.api_key = os.getenv("API_KEY")

app_name = "HCI Project"


def index(request):
    context = {"app_name": app_name}
    return render(request, "index.html", context)


@login_required(login_url="signin")
def mockgpt(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    seven_days_ago = date.today() - timedelta(days=7)

    questions = QuestionAnswer.objects.filter(user=request.user)
    t_questions = questions.filter(created=today)
    y_questions = questions.filter(created=yesterday)
    s_questions = questions.filter(created__gte=seven_days_ago, created__lte=today)

    context = {
        "t_questions": t_questions,
        "y_questions": y_questions,
        "s_questions": s_questions,
    }

    return render(request, "chatapp/mockgpt.html", context)


def info(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "info.html", context)


def NTU(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTU/NTU.html", context)


def NYCU(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NYCU/NYCU.html", context)


def NTHU(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "NTHU/NTHU.html", context)


def mock(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "mock.html", context)


def identity(request):
    username = request.user.username
    context = {"username": username, "app_name": app_name}
    return render(request, "identity.html", context)


def signup(request):
    if request.user.is_authenticated:
        return redirect("info")
    form = UserForm()
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST["username"]
            password = request.POST["password1"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("info")
    context = {"form": form, "app_name": app_name}
    return render(request, "chatapp/signup.html", context)


def signin(request):
    err = None
    if request.user.is_authenticated:
        return redirect("info")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("info")

        else:
            err = "Invalid Credentials"

    context = {"error": err, "app_name": app_name}
    return render(request, "chatapp/signin.html", context)


def signout(request):
    logout(request)
    return redirect("signin")


def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message},
        ],
    )

    answer = response["choices"][0]["message"]["content"]
    return answer


def getValue(request):
    data = json.loads(request.body)
    message = data["msg"]
    response = ask_openai(message)
    QuestionAnswer.objects.create(user=request.user, question=message, answer=response)
    return JsonResponse({"msg": message, "res": response})
