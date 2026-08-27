from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Movie app API is running.',
        'endpoints': {
            'auth': '/api/auth/',
            'users': '/api/users/',
            'posts': '/api/posts/',
            'clubs': '/api/clubs/',
            'watchlist': '/api/watchlist/',
        },
    })


urlpatterns = [
    path('', api_root, name='api-health'),
    path('api/', api_root, name='api-root'),
    path('api/auth/', include('accounts.urls_auth')),
    path('api/users/', include('accounts.urls_users')),
    path('api/', include('posts.urls')),
    path('api/', include('clubs.urls')),
    path('api/', include('watchlist.urls')),
]