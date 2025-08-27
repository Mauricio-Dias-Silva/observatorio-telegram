# observatorio_telegram/urls.py
from django.contrib import admin
from django.urls import path, include # Importe 'include'
from analise_telegram import views # Importe as views do seu app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'), # Página inicial
    path('canais/', views.lista_canais, name='lista_canais'),
    path('mensagens/', views.lista_mensagens, name='lista_mensagens'),
    # Se você quiser um arquivo urls.py separado para seu app:
    # path('analise/', include('analise_telegram.urls')),
]