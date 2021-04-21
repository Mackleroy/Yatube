"""Yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import path, include

import debug_toolbar

from Yatube import settings
from posts.views import server_error, page_not_found


urlpatterns = [
    path("auth/", include("django.contrib.auth.urls")),
    path("auth/", include("Users.urls")),
    path('about/', include('django.contrib.flatpages.urls')),
    path('admin/', admin.site.urls),
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path('404/', page_not_found),
    path('500/', server_error),
    path("__debug__/", include(debug_toolbar.urls)),

    path('follow/', include('follows.urls')),
    path('', include('posts.urls')),

]

handler404 = "posts.views.page_not_found"
handler500 = "posts.views.server_error"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)


