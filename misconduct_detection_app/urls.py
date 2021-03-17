"""misconduct_detection_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('guestLogin/', views.guest_index, name='guest_index'),
    path('upload/', views.upload_index, name='upload_index'),
    path('select/', views.select_index, name='select_index'),
    path('results/', views.results_index, name='results'),
    path('upload/runningWaitingPage/', views.run_detection, name='rwp'),
    path('upload/uploadFile/', views.upload_file, name='upload_file'),
    path('upload/uploadFolder/', views.upload_folder, name='upload_folder'),
    path('upload/checkIncluded/', views.upload_check_included, name='upload_check_included'),
    path('upload/updateContext/', views.upload_update_context, name="upload_update_context"),
    path('upload/uploadedFolder/', views.uploaded_folder_index, name="uploaded_folder_index"),
    path('examine/singlefiles/<str:name>', views.examine_file, name='examine_file'),
    path('examine/folders/<path:name>', views.examine_folder, name='examine_folder'),
    path('select/selectCode/', views.select_code, name='select_code'),
    path('select/checkBoxStatus/', views.select_check_box, name='select_check_box'),
    path('select/runningWaitingPage/', views.run_detection, name='run_detection'),
    path('select/running/', views.run_detection_core, name='run_detection'),
    path('select/autoDetect/', views.auto_detect, name='auto_detect'),
    path('select/saveHtml/', views.select_save_html, name='select_save_html'),
    path('select/loadHtml/', views.select_load_html, name='select_load_html'),
    path('results/details/<path:name>', views.examine_file_in_result_page, name='examine_file_in_result'),

    path('clean/', views.clean, name='clean'),
    path('clean/session/', views.clean_session, name='clean_session'),
    path('configs/savingConfigs/', views.saving_configs, name='saving_configs'),

    path('errors/errorNoResults/', views.error_no_results_error, name='error_no_results_error'),
    path('errors/errorUnsupportedFile/', views.error_uploaded_unsupported_file, name='error_uploaded_unsupported_file'),
    path('errors/errorResultsKeysNotExists/', views.error_results_keys_not_exists, name='error_results_keys_not_exists'),
    # path('save/<str:name>', views.save_workspace, name='save'),
    path('upload/save/<str:name>', views.save_workspace, name='save'),
    path('select/save/<str:name>', views.save_workspace, name='save'),
    path('results/save/<str:name>', views.save_workspace, name='save'),

    path('list/', views.list_workspaces, name='list'),
    path('listt/load/<str:name>', views.load_workspace, name='load'),
    path('listt/delete/<str:name>', views.delete_workspace, name='load'),
    path('listt/', views.list_workspace, name='listt'),
    path('upload/selectcodemoss/', views.select_code_moss, name='selectt'),

    path('test/', views.test, name='test')
]