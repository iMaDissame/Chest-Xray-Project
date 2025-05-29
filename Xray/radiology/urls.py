from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import api

urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('',views.index,name='index'),
    path('login/',views.doctor_login,name='doctor_login'),
    path('logout/',views.LogoutPage,name='logout'),
    path('about/',views.about,name='about'),
    path('doctoriterface/',views.intdoc,name='doctoriterface'),
    path('blogresult/',views.blogresult,name='blogresult'),
    path('predict_pneumonia/', views.predict_pneumonia, name='predict_pneumonia'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('chatbot/', views.chatbot_view, name='chat'),
    path('documents/', views.list_documents, name='list_documents'),
    path('heartbeat-classification/', views.heartbeat_classification, name='heartbeat_classification'),
    path('guest/', views.dropdownsearch, name='guest'),
    #Api URLs
    path('api/register/', api.api_register, name='api_register'),
    path('api/login/', api.api_login, name='api_login'),
    path('api/predict-pneumonia/', api.api_predict_pneumonia, name='api_predict_pneumonia'),
    path('api/heartbeat-classification/', api.api_heartbeat_classification, name='api_heartbeat_classification'),
    path('api/documents/', api.api_list_documents, name='api_list_documents'),
    path('api/doctors/', api.api_search_doctors, name='api_search_doctors'),
    path('api/doctor-filters/', api.api_get_doctor_filters, name='api_doctor_filters'),
    path('api/logout/', api.api_logout, name='api_logout'),
    path('api/generate-report/', api.api_generate_report, name='api_generate_report'),
    path('api/chatbot/', api.api_chatbot, name='api_chatbot'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)