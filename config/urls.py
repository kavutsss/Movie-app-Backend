from django.urls import path, include
urlpatterns = [
    path('api/auth/', include('accounts.urls_auth')),
    path('api/users/', include('accounts.urls_users')),
    path('api/', include('posts.urls')),
    path('api/', include('clubs.urls')),
    path('api/', include('watchlist.urls')),
]