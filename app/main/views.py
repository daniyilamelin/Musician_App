from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib import auth
from pymongo import MongoClient

from google import genai
import os
import secrets
import string

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm
import json
from django_redis import get_redis_connection
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(
    os.getenv("MONGO_URI"),
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=5000,
    maxPoolSize=1,
)
db = client[os.getenv("MONGO_DATABASE")]
ai_client = genai.Client(api_key= os.getenv("GEMINI_AI_KEY"))

def index(request) -> HttpResponse:
    context = {
        "title" : 'Musician - Головна',
        "name": 'Музика під твій настрій',
        "text": 'Система, яка підбирає треки залежно від вибраного вами настрою.'
    }
    return render(request, 'main/index.html', context)

def playlist(request):
    collection = db[os.getenv("MONGO_COLLECTION")]

    if request.user.is_anonymous:
        documents = []
        context = {
            "collection": documents,
            "title": 'Musician - Плейлист',
            "name": 'Ваш неповторний плейлист',
            "text": 'Всі пісні , які ви добавили в телеграм боті відображаються тут.'
        }
    else:
        energy_stats = {}
        mood_stats = {}
        documents = list(collection.find({"user_id": request.user.telegram_id }))
        for song in documents:
            mood_stats[song["mood"]] = mood_stats.get(song["mood"], 0) + 1
            energy_stats[song["energy"]] = energy_stats.get(song["energy"], 0) + 1

    #for doc in documents:
    #    doc["_id"] = str(doc["_id"])
        context = {
            "collection": documents,
            "title": 'Musician - Плейлист',
            "name": 'Ваш неповторний плейлист',
            "text": 'Всі пісні , які ви добавили в телеграм боті відображаються тут.',
            "mood_stats": mood_stats,
            "energy_stats": energy_stats
        }
    return render(request, 'main/playlist.html', context)

def reccomendation(request):
    lists_songs = []
    if request.user.is_anonymous:
        lists_songs = []
        print("User is not good")
    else:
        collection = db[os.getenv("MONGO_COLLECTION")]
        mod = request.GET.get('mood')
        if not mod:
            lists_songs = []
        else:
            tid = request.user.telegram_id
            songs = collection.find({
                "user_id": {"$in": [tid, str(tid), int(tid)]},
                "mood": {"$regex": mod, "$options": "i"}})
            for song in songs:
                lists_songs.append(song)

    context = {
        "title": "Musician - Настрій",
        "name": "Чудовий вибір",
        "text": "Ваш настрій - ваші правила - ваша музика",
        "songs": lists_songs,
    }
    print(lists_songs)
    return render(request, 'main/mood.html', context)

class UserLoginView(LoginView):
    template_name = "main/login.html"
    form_class = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Musician - Вхід"
        context["name"] = "Увійдіть у свій аккаунт"
        return context

class UserRegistrationView(CreateView):
    template_name = "main/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Musician - Реєстрація"
        context["name"] = "Спочатку зареєструйте аккаунт"
        return context

    def form_valid(self, form):
        user = form.instance
        if user:
            form.save()
            auth.login(self.request, user)
            return HttpResponseRedirect(self.success_url)

class ProfileForm(LoginRequiredMixin, UpdateView):
    template_name = "main/profile.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("users:profile")


    def get_object(self, queryset = None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Musician - Профіль"
        context["name"] = "Ваш аккаунт"
        key = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        context["token"] = key
        redis_conn = get_redis_connection("default")
        redis_conn.set(f"verify:{key}", str(self.request.user.id), ex = 600)
        return context

@login_required
def logout(request):
    auth.logout(request)
    return redirect("index")











