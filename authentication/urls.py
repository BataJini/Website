from django.urls import path, re_path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('', views.home, name='home'),  # Now points to the jobs view
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('job/<slug:job_slug>/', views.job_detail, name='job_detail'),
    path('post-job/', views.post_job_view, name='post_job'),
    path('job/<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('manage/users/', views.user_list, name='user_list'),
    path('ajax/search-jobs/', views.search_jobs_ajax, name='search_jobs_ajax'),  # New AJAX endpoint
    path('search-jobs/', views.search_jobs_ajax, name='search_jobs_ajax'),
    path('search-cities/', views.search_cities, name='search_cities'),
    # Catch-all pattern for unmatched URLs
    re_path(r'^.*$', views.handle_404),
]
