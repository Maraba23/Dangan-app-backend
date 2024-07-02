from usuarios.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from api.views import *

urlpatterns = [

    path('login/', login),
    path('register/', register),
    path('check-token/', token_checker),

    path('cases/', list_all_cases),
    path('cases/<int:case_id>/', get_case),
    path('cases/<int:case_id>/delete/', delete_case),
    path('cases/<int:case_id>/edit/', edit_case),
    path('cases/create/', create_case),
    path('cases/<int:case_id>/truth-bullets/', list_all_truth_bullets_by_case),
    path('cases/<int:case_id>/user-truth-bullets/', get_truth_bullets_founded_by_user),

    path('truth-bullets/', list_all_truth_bullets),
    path('truth-bullets/<int:bullet_id>/', get_truth_bullet),
    path('truth-bullets/<int:bullet_id>/delete/', delete_truth_bullet),
    path('truth-bullets/<int:bullet_id>/edit/', edit_truth_bullet),
    path('truth-bullets/create/', create_truth_bullet),

    path('add-truth-bullet-to-profile/', add_truth_bullet_to_profile),
]