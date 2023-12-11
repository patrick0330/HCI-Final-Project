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
import copy

load_dotenv()

# Create your views here.
openai.api_key = os.getenv("API_KEY")

default_history = [
    {
        "role": "system", 
        "content": 
'''
只使用繁體中文進行提問及回答
你是一個HCI大學的教授 正在面試準備進入研究所的大學生。
以學生的回答，在內心給出一個介於 0~100 的整數x 代表你對這名學生的評分，以 70 作為初始數值，並以 60 做為錄取標準，若學生的分數距離此標準過低，你也可以選擇提前結束這場面試。在任何回覆的最後面印出獨立的一行 "分數: x"。
先請學生自我介紹
以學生的科系、報考動機、進入研究所後的規劃等方面，制定問題以"嚴格的口吻"進行提問
不要講太多無關問題的回答 一次以一個問題為主
參考的問題方向如下 但盡量讓每個問題都問過 且不要問得太深入 
1. 你好 我是HCI大學的教授 可以請你簡單介紹一下你自己嗎?
2. 想請問你為什麼選擇報考我們學校的研究所呢?
3. 可以分享一下你在學的學習經歷和相關的專長嗎?
4. 如果沒有考上你要怎麼辦? 是不是有打算出國念或工作
5. 在研究所二年內，想得到些什麼?
6. 對本所了解多少？你覺得本校的優點在哪？簡述系上老師的特色      
'''
    },
]

history = {}

@login_required(login_url='signin')
def index(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    seven_days_ago = date.today() - timedelta(days=7)
    print(request.user)
    questions = QuestionAnswer.objects.filter(user=request.user)
    t_questions = questions.filter(created=today)
    y_questions = questions.filter(created=yesterday)
    s_questions = questions.filter(created__gte=seven_days_ago, created__lte=today)
    
    context = {"t_questions":t_questions, "y_questions": y_questions, "s_questions": s_questions}

    return render(request, "chatapp/index.html", context)


def signup(request):
    if request.user.is_authenticated:
        return redirect("index")
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST["username"]
            password = request.POST["password1"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
    context = {"form": form}
    return render(request, "chatapp/signup.html", context)


def signin(request):
    err = None
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == 'POST':
        
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        
        else:
            err = "Invalid Credentials"
        
        
    context = {"error": err}
    return render(request, "chatapp/signin.html", context)


def signout(request):
    logout(request)
    return redirect("signin")


def ask_openai(message, user=None):

    if user not in history:
        history[user] = copy.deepcopy(default_history)
    print(str(user))
    print(history[user])
    
    # Add message to history
    history[user].append(
        {"role": "user", "content":message}
    )

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=history[user],   
    )
    
    response_message = response.choices[0].message
    
    history[user].append({
        "role": response_message.role,
        "content":response_message.content
    })
    print(history[user])
    return response_message.content


def getValue(request):
    data = json.loads(request.body)
    message = data["msg"]
    response = ask_openai(message, user=request.user)
    QuestionAnswer.objects.create(user = request.user, question=message, answer=response)
    return JsonResponse({"msg": message, "res": response})