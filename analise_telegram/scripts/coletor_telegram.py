# analise_telegram/scripts/coletor_telegram.py

import os
import django
import asyncio
from pyrogram import Client
from datetime import datetime, timedelta

# Configurações do Django
# Ajuste o caminho para o seu projeto Django
# Se você estiver executando este script da raiz do projeto, ele deve encontrar o settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'observatorio_telegram.settings')
django.setup()

from analise_telegram.models import CanalTelegram, MensagemTelegram

# Suas credenciais da API do Telegram (preencha com as suas!)
API_ID = 1234567 # Substitua pelo seu api_id
API_HASH = "sua_api_hash_aqui" # Substitua pelo seu api_hash

# Nome da sessão do Pyrogram (pode ser qualquer nome, é para armazenar a sessão)
SESSION_NAME = "observatorio_session"

# ----- Funções Auxiliares -----

async def get_messages_from_channel(client, canal_db):
    """
    Busca mensagens de um canal e as salva no banco de dados Django.
    """
    print(f"Buscando mensagens do canal: {canal_db.nome} ({canal_db.username or canal_db.telegram_id})")
    
    # Define o offset para buscar mensagens apenas a partir da última processada
    # Se nunca foi processado, pega as mais recentes ou de um período inicial
    offset_date = canal_db.ultimo_processamento
    if not offset_date:
        # Pega mensagens dos últimos 30 dias se for o primeiro processamento
        offset_date = datetime.now() - timedelta(days=30) 
        
    messages_count = 0
    try:
        # Pyrogram itera sobre as mensagens. Limitamos para não sobrecarregar
        # Você pode ajustar 'limit' conforme a necessidade e os limites do Telegram
        async for message in client.get_chat_history(chat_id=canal_db.telegram_id, limit=200): 
            # Verifica se a mensagem é mais recente que o último processamento
            # A TDLib pode retornar mensagens mais antigas no início, então precisamos filtrar
            if message.date and message.date.replace(tzinfo=None) <= offset_date.replace(tzinfo=None):
                break # Já processamos até aqui, para a iteração
            
            # Garante que a mensagem tem texto e que não é uma mensagem de serviço
            if message.text:
                # print(f"  > Nova mensagem de {canal_db.nome} em {message.date}: {message.text[:50]}...")
                
                # Obtém o tipo de mídia
                media_type = None
                if message.media:
                    media_type = str(message.media).split('.')[-1].lower() # e.g., MessageMediaType.PHOTO -> 'photo'

                try:
                    # Cria ou atualiza a mensagem no banco de dados
                    # Usamos update_or_create para evitar duplicatas se o script rodar novamente com mensagens recentes
                    MensagemTelegram.objects.update_or_create(
                        canal=canal_db,
                        mensagem_id=message.id,
                        defaults={
                            'texto': message.text,
                            'data_publicacao': message.date,
                            'tipo_midia': media_type,
                            # eh_risco, sentimento, palavras_chave_encontradas serão preenchidos pela análise de IA
                        }
                    )
                    messages_count += 1
                except Exception as e:
                    print(f"Erro ao salvar mensagem {message.id} do canal {canal_db.nome}: {e}")
            
            # O Pyrogram faz um controle de flood implícito, mas é bom ter cuidado com o volume
            await asyncio.sleep(0.1) # Pequeno delay entre as requisições para ser educado com a API

        # Atualiza o timestamp do último processamento
        canal_db.ultimo_processamento = datetime.now()
        canal_db.save()
        print(f"Coletadas {messages_count} novas mensagens do canal {canal_db.nome}.")

    except Exception as e:
        print(f"Erro ao coletar do canal {canal_db.nome}: {e}")

async def main():
    """
    Função principal que gerencia a conexão e a coleta dos canais.
    """
    # Inicializa o cliente Pyrogram
    app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
    
    async with app:
        # Garante que estamos autenticados
        me = await app.get_me()
        print(f"Conectado ao Telegram como: {me.first_name} (@{me.username or 'Sem username'})")

        # Busca todos os canais ativos no seu banco de dados Django
        canais_ativos = CanalTelegram.objects.filter(ativo=True)

        if not canais_ativos.exists():
            print("Nenhum canal ativo encontrado no banco de dados. Adicione canais via Admin do Django.")
            print("Exemplo: python manage.py shell")
            print("from analise_telegram.models import CanalTelegram")
            print("CanalTelegram.objects.create(nome='SeuCanalPublico', username='SeuCanalPublico', telegram_id=1234567890)")
            return

        for canal_db in canais_ativos:
            await get_messages_from_channel(app, canal_db)
            await asyncio.sleep(5) # Delay entre a coleta de cada canal para evitar sobrecarga

if __name__ == "__main__":
    asyncio.run(main())