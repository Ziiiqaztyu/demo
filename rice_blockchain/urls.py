"""
URL configuration for rice_blockchain project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from blockchain import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('producer/', views.producer_view, name='producer'),
    path('verification/', views.verification_view, name='verification'),
    path('verify-block/', views.verify_block_view, name='verify_block'),
    path('blocks/', views.block_list_view, name='block_list'),
    path('signin/', views.signin, name='signin'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.home, name='home')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
