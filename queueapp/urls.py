from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontpage_view, name='frontpage'),
    path('receptionist/', views.receptionist_view, name='receptionist'),
    path('doctor/', views.doctor_panel_view, name='doctor_panel'),
    path('patient/', views.patient_panel, name='patient_panel'),
    path('mark_treated/<int:patient_id>/', views.mark_patient_treated, name='mark_treated'),
    path('chatbot/', views.chatbot_api, name='chatbot_api'),
    path('knowmore/', views.know_more_view, name='knowmore'),
    path('specialities/', views.specialities_view, name='specialities'),
    path('academics/', views.academics_view, name='academics'),
    path('doctors/', views.doctors_view, name='doctors'),
    path('doctor_find/', views.doctor_find_view, name='doctor_find'),
]