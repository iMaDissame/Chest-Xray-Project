from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)