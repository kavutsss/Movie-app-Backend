from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


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
    path('admin/', admin.site.urls),
    path('', api_root, name='api-health'),
    path('api/', api_root, name='api-root'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/auth/', include('accounts.url_auth')),
    path('api/users/', include('accounts.url_users')),
    path('api/admin/', include('administration.urls')),
    path('api/', include('posts.urls')),
    path('api/', include('clubs.urls')),
    path('api/', include('watchlist.urls')),
]
