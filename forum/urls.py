"""forum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

urlpatterns = [
    path('', admin.site.urls),
]

# Customize the admin site
admin.site.site_header = admin.site_title = "Forum of Ethics"
admin.site.site_url = None
admin.site.index_title = "Welcome to the conversation!"
# Allow everyone to access the site even if they aren't logged in
admin.site.has_permission = lambda request: True if "login" not in request.path or request.user.is_superuser else False
