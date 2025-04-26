from django.urls import path
from . import views

urlpatterns = [
    path('', views.receptionist_view, name='receptionist'),
    path('patient-panel/', views.patient_panel, name='patient_panel'),
    path('doctor-panel/', views.doctor_panel_view, name='doctor_panel'),
    path('treated/<int:patient_id>/', views.mark_patient_treated, name='mark_treated'),
]
