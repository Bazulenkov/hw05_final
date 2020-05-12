"""yatube URL Configuration

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
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path, re_path
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('auth/', include('users.urls')),  # регистрация и авторизация

    #  если нужного шаблона для /auth не нашлось в файле users.urls -
    #  ищем совпадения в файле django.contrib.auth.urls
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),  # импорт правил из приложения admin
]

urlpatterns += [
    path('about/', include('django.contrib.flatpages.urls')),  # flatpages

    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about-us'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path('about-author/', views.flatpage,
         {'url': '/about-author/'}, name='about-author'),
    path('about-spec/', views.flatpage,
         {'url': '/about-spec/'}, name='about-spec'),

    path('rasskaz-o-tom-kakie-my-horoshie/', views.flatpage,
         {'url': '/about-us/'}, name='about'),
]

urlpatterns += [
    # не трогать, порядок важен'
    path('', include('posts.urls')),  # импорт правил из приложения posts
]

handler404 = 'posts.views.page_not_found'  # noqa
handler500 = 'posts.views.server_error'  # noqa

if settings.DEBUG is False:  # if DEBUG is True it will be served automatically
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve,
                {'document_root': settings.STATIC_ROOT}),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
