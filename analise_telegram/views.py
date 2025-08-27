# analise_telegram/views.py
from django.shortcuts import render
from django.db.models import Count
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from collections import Counter # Importar para contar palavras

from .models import CanalTelegram, MensagemTelegram

def dashboard(request):
    """
    Renderiza o dashboard com estatísticas gerais.
    """
    total_canais = CanalTelegram.objects.count()
    total_mensagens = MensagemTelegram.objects.count()

    # Mensagens nos últimos 7 dias
    data_7dias_atras = datetime.now() - timedelta(days=7)
    
    mensagens_risco_7dias = MensagemTelegram.objects.filter(
        eh_risco=True,
        data_publicacao__gte=data_7dias_atras
    ).count()

    mensagens_neutras_7dias = MensagemTelegram.objects.filter(
        sentimento='neutro', # Filtrando por 'neutro'
        data_publicacao__gte=data_7dias_atras
    ).count()

    ultimas_mensagens_risco = MensagemTelegram.objects.filter(eh_risco=True).order_by('-data_publicacao')[:5] # Limitar a 5 para o card

    # Simulação de Termos Mais Frequentes (em um projeto real, isso viria da análise de IA)
    # Para demonstração, vamos pegar os termos mais frequentes de todas as mensagens (ou de um período recente)
    # Em um cenário real, você faria uma agregação no DB ou via um processo de PLN
    recent_messages_texts = MensagemTelegram.objects.filter(data_publicacao__gte=data_7dias_atras).values_list('texto', flat=True)
    all_words = []
    for text in recent_messages_texts:
        if text: # Garante que o texto não é None
            # Simplificação: tokeniza e remove pontuação. Use sua função preprocess_text real do script de IA
            words = text.lower().replace('.', '').replace(',', '').split() 
            all_words.extend(words)
    
    word_counts = Counter(all_words)
    # Remove stopwords básicas ou palavras genéricas
    common_stopwords = set(['e', 'de', 'o', 'a', 'do', 'da', 'em', 'um', 'uma', 'para', 'com', 'no', 'na', 'os', 'as', 'por', 'é', 'que', 'se', 'mas', 'não', 'mais', 'ou', 'como', 'pra', 'dos', 'das', 'ele', 'ela', 'eles', 'elas', 'um', 'uma', 'nos', 'nas', 'me', 'você', 'eu', 'nós', 'isso', 'esse', 'essa'])
    # Filtra palavras comuns e palavras muito curtas
    termos_frequentes_filtrados = [(word, count) for word, count in word_counts.most_common(20) if word not in common_stopwords and len(word) > 3]


    context = {
        'total_canais': total_canais,
        'total_mensagens': total_mensagens,
        'mensagens_risco_7dias': mensagens_risco_7dias,
        'mensagens_neutras_7dias': mensagens_neutras_7dias, # Adicionado
        'ultimas_mensagens_risco': ultimas_mensagens_risco,
        'termos_frequentes': termos_frequentes_filtrados, # Adicionado
    }
    return render(request, 'analise_telegram/dashboard.html', context)

def lista_canais(request):
    """
    Renderiza a lista de todos os canais monitorados.
    """
    canais = CanalTelegram.objects.all()
    context = {
        'canais': canais
    }
    return render(request, 'analise_telegram/lista_canais.html', context)

def lista_mensagens(request):
    """
    Renderiza a lista de mensagens coletadas com filtros e paginação.
    """
    mensagens_list = MensagemTelegram.objects.all().order_by('-data_publicacao')

    # Aplicar filtros
    canal_id = request.GET.get('canal_id')
    eh_risco = request.GET.get('eh_risco')
    sentimento = request.GET.get('sentimento')
    # Novo filtro de período (ex: para usar no link do dashboard)
    periodo = request.GET.get('periodo') 

    if canal_id:
        mensagens_list = mensagens_list.filter(canal_id=canal_id)
    if eh_risco in ['True', 'False']: 
        mensagens_list = mensagens_list.filter(eh_risco=(eh_risco == 'True'))
    if sentimento in ['positivo', 'neutro', 'negativo']:
        mensagens_list = mensagens_list.filter(sentimento=sentimento)
    
    # Adicionar filtro por período (se o período for especificado)
    if periodo == '7dias':
        data_inicio_periodo = datetime.now() - timedelta(days=7)
        mensagens_list = mensagens_list.filter(data_publicacao__gte=data_inicio_periodo)
    elif periodo == '30dias':
        data_inicio_periodo = datetime.now() - timedelta(days=30)
        mensagens_list = mensagens_list.filter(data_publicacao__gte=data_inicio_periodo)


    # Paginação
    paginator = Paginator(mensagens_list, 20) # 20 mensagens por página
    page_number = request.GET.get('page')
    mensagens = paginator.get_page(page_number)

    todos_canais = CanalTelegram.objects.all().order_by('nome')

    context = {
        'mensagens': mensagens,
        'todos_canais': todos_canais, # Para o dropdown de filtro
    }
    return render(request, 'analise_telegram/lista_mensagens.html', context)