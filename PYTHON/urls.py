"""
URL configuration for projekt project.

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
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from app import views as boa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ledanschalten/', boa.ledanschalten),
    path('lcddisplay', boa.lcddisplay),
    path('brautest', boa.brautest),
    path('', boa.index),
    path('rezept', boa.rezept, name="rezept"),
    path('nutzer', boa.nutzer, name="nutzer"),
    path('nutzerdatenaendern', boa.nutzerdatenaendern, name="nutzerdatenaendern"),
    path('rezeptanlegen', boa.rezeptanlegen, name="rezeptanlegen"),
    path('status', boa.status, name="status"),
]

urlpatterns += staticfiles_urlpatterns()
