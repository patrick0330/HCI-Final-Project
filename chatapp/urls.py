from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("mockgpt", views.mockgpt, name="mockgpt"),
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("signout", views.signout, name="signout"),
    path("get-value", views.getValue),
    path("info/", views.info, name="info"),
    path("NTU/", views.NTU, name="NTU"),
    path("NYCU/", views.NYCU, name="NYCU"),
    path("NTHU/", views.NTHU, name="NTHU"),
    path("mock/", views.mock, name="mock"),
    path("identity/", views.identity, name="identity"),
]
