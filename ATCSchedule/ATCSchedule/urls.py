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

from schedule.views import estimated_hours, daily_machine_hours, accuracy, total_load_on_sys_output, daily_report_hours_output, accuracy_output, overall_effiency_output, usage_efficiency_output, base

admin.site.site_header = "ATC Portal"
admin.site.site_title = "ATC Admin Portal"
admin.site.index_title = "Welcome to Amritha Tool Craft portal"

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', base,name = 'base'),
    path(r'estimated_hours/',estimated_hours,name='estimated hours'),
    path(r'daily_machine_hours/',daily_machine_hours,name='Daily Machine Hours'),
    path(r'accuracy/',accuracy,name='Accuracy'),
    path(r'total_load_on_systems/',total_load_on_sys_output,name='Total Load On System Report'),
    path(r'quality_report/',accuracy_output,name='Quality Report'),
    path(r'overall_efficiency_report/',overall_effiency_output,name='Overall Efficiency Report'),
    path(r'usage_efficiency_report/',usage_efficiency_output,name='Usage Efficiency Report'),
    path(r'daily_report/',daily_report_hours_output,name='Daily Report'),
]
