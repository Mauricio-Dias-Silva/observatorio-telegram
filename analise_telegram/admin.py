# analise_telegram/admin.py
from django.contrib import admin
from .models import CanalTelegram, MensagemTelegram

@admin.register(CanalTelegram)
class CanalTelegramAdmin(admin.ModelAdmin):
    list_display = ('nome', 'username', 'telegram_id', 'ativo', 'data_adicao', 'ultimo_processamento')
    search_fields = ('nome', 'username')
    list_filter = ('ativo', 'data_adicao')

@admin.register(MensagemTelegram)
class MensagemTelegramAdmin(admin.ModelAdmin):
    list_display = ('canal', 'mensagem_id', 'data_publicacao', 'tipo_midia', 'eh_risco', 'sentimento')
    list_filter = ('canal', 'eh_risco', 'tipo_midia', 'sentimento', 'data_publicacao')
    search_fields = ('texto',)
    raw_id_fields = ('canal',) # Útil para selecionar canais em vez de dropdown grande