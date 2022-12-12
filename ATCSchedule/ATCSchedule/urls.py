"""ATCSchedule URL Configuration

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
#from django.config.urls.static import static
#from django.conf.settings import base,local

from schedule.views import estimated_hours,print_df,base

admin.site.site_header = "ATC Portal"
admin.site.site_title = "ATC Admin Portal"
admin.site.index_title = "Welcome to Amritha Tool Craft portal"

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', base,name = 'base'),
    path(r'estimated_hours/',estimated_hours,name='estimated hours'),
    path(r'print/',print_df,name='Total Load On System Report')
]
