# analise_telegram/models.py
from django.db import models

class CanalTelegram(models.Model):
    """
    Representa um canal público do Telegram sendo monitorado.
    """
    nome = models.CharField(max_length=255, unique=True, help_text="Nome do canal público no Telegram")
    username = models.CharField(max_length=255, unique=True, help_text="Username (@) do canal público", blank=True, null=True)
    telegram_id = models.BigIntegerField(unique=True, help_text="ID numérico do canal no Telegram (usado pela API)")
    link_convite = models.URLField(max_length=500, blank=True, null=True, help_text="Link público de convite do canal")
    data_adicao = models.DateTimeField(auto_now_add=True, help_text="Data em que o canal foi adicionado ao monitoramento")
    ativo = models.BooleanField(default=True, help_text="Indica se o monitoramento do canal está ativo")
    ultimo_processamento = models.DateTimeField(blank=True, null=True, help_text="Timestamp do último processamento de mensagens deste canal")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Canal do Telegram"
        verbose_name_plural = "Canais do Telegram"
        ordering = ['nome']


class MensagemTelegram(models.Model):
    """
    Representa uma mensagem coletada de um canal público do Telegram.
    """
    canal = models.ForeignKey(CanalTelegram, on_delete=models.CASCADE, related_name='mensagens', help_text="Canal de onde a mensagem foi coletada")
    mensagem_id = models.BigIntegerField(help_text="ID único da mensagem dentro do canal no Telegram")
    texto = models.TextField(blank=True, null=True, help_text="Conteúdo textual da mensagem")
    data_publicacao = models.DateTimeField(help_text="Data e hora da publicação da mensagem no Telegram")
    tipo_midia = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Tipo de mídia anexada à mensagem (e.g., photo, video, text, document)"
    )
    # Campos para análise de conteúdo (preenchidos por processamento posterior)
    eh_risco = models.BooleanField(default=False, help_text="Indica se a mensagem foi classificada como de risco")
    sentimento = models.CharField(
        max_length=20,
        choices=[('positivo', 'Positivo'), ('neutro', 'Neutro'), ('negativo', 'Negativo')],
        blank=True,
        null=True,
        help_text="Sentimento geral da mensagem (se aplicável)"
    )
    palavras_chave_encontradas = models.JSONField(blank=True, null=True, help_text="Lista de palavras-chave relevantes encontradas na mensagem")

    def __str__(self):
        return f"Mensagem {self.mensagem_id} de {self.canal.nome}"

    class Meta:
        verbose_name = "Mensagem do Telegram"
        verbose_name_plural = "Mensagens do Telegram"
        # Garante que não haverá duplicidade de mensagens pelo ID do Telegram dentro do mesmo canal
        unique_together = ('canal', 'mensagem_id')
        ordering = ['-data_publicacao']