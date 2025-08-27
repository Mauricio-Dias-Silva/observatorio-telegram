import os
import django
import re
from datetime import datetime
from collections import Counter

# Para PLN e Machine Learning
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB # Um modelo simples para começar
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Baixe recursos NLTK (execute isso uma vez no seu ambiente virtual)
# nltk.download('punkt')
# nltk.download('stopwords')

# Configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'observatorio_telegram.settings')
django.setup()

from analise_telegram.models import MensagemTelegram

# --- Configurações e Modelos ---

# Stopwords para o português
stop_words_pt = set(stopwords.words('portuguese'))

# Exemplo de lista de palavras-chave de risco (apenas para demonstração)
# Na vida real, esta lista seria muito maior e refinada, e talvez complementada por um modelo de IA treinado
PALAVRAS_CHAVE_RISCO = [
    'ataque', 'odio', 'violencia', 'armas', 'ameaça', 'terror', 'morte',
    'extremista', 'nazismo', 'fascismo', 'racismo', 'genocidio', 'propaganda'
]

# --- Funções de Pré-processamento e Análise ---

def preprocess_text(text):
    """
    Limpa e tokeniza o texto para análise.
    """
    if not text:
        return []
    # Converte para minúsculas
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove menções e hashtags
    text = re.sub(r'@\w+|#\w+', '', text)
    # Remove caracteres não alfanuméricos e números
    text = re.sub(r'[^a-záàâãéêíóôõúüç\s]', '', text) # Mantém apenas letras e espaços
    # Tokeniza o texto
    tokens = word_tokenize(text, language='portuguese')
    # Remove stopwords e tokens curtos
    tokens = [word for word in tokens if word not in stop_words_pt and len(word) > 2]
    return tokens

def identify_risk_keywords(text):
    """
    Identifica palavras-chave de risco em um texto (abordagem simples baseada em lista).
    Em um sistema real, seria um modelo de IA.
    """
    tokens = preprocess_text(text)
    found_keywords = [kw for kw in PALAVRAS_CHAVE_RISCO if kw in tokens]
    return list(set(found_keywords)) # Retorna palavras únicas

def classify_sentiment(text):
    """
    Simulação de classificação de sentimento (em um projeto real, usaria um modelo de IA treinado).
    """
    # Para demonstração, uma regra muito simplificada
    tokens = preprocess_text(text)
    
    # Exemplo: Se contém "bom", "ótimo", é positivo. Se contém "ruim", "péssimo", é negativo.
    positive_words = ['bom', 'ótimo', 'excelente', 'parabéns', 'feliz']
    negative_words = ['ruim', 'péssimo', 'lixo', 'odeio', 'triste']

    pos_score = sum(1 for word in tokens if word in positive_words)
    neg_score = sum(1 for word in tokens if word in negative_words)

    if pos_score > neg_score:
        return 'positivo'
    elif neg_score > pos_score:
        return 'negativo'
    else:
        return 'neutro' # Ou 'não definido' se não houver palavras claras

def train_and_predict_risk_model(texts, labels):
    """
    Treina um modelo simples de ML para classificar risco.
    Em um PI, você precisaria de um dataset de treinamento rotulado.
    """
    if not texts or len(set(labels)) < 2:
        print("Dados insuficientes ou apenas uma classe para treinamento do modelo de risco.")
        # Retorna um modelo dummy que sempre prediz 'False' se não puder treinar
        class DummyModel:
            def predict(self, X): return [False] * len(X)
        return DummyModel(), None

    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1,2))
    X = vectorizer.fit_transform(texts)
    y = [True if label == 'risco' else False for label in labels] # Converte para booleano

    # Garante que temos pelo menos duas classes (risco e não-risco) para o split
    if len(set(y)) < 2:
        print("Apenas uma classe presente nos dados rotulados para o modelo de risco. Treinamento não é possível.")
        # Retorna um modelo dummy se não puder treinar
        class DummyModel:
            def predict(self, X): return [False] * len(X)
        return DummyModel(), vectorizer

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = MultinomialNB()
    model.fit(X_train, y_train)

    # Avaliação (apenas para fins de demonstração)
    y_pred = model.predict(X_test)
    print("\n--- Relatório de Classificação de Risco (Amostra de Teste) ---")
    print(classification_report(y_test, y_pred, zero_division=0)) # zero_division=0 para evitar avisos em classes sem preditos

    return model, vectorizer

# --- Função Principal de Análise ---

async def run_analysis():
    print("Iniciando o processo de análise de IA para mensagens do Telegram...")

    # --- Passo 1: Carregar um modelo de IA (ou treinar um dummy) ---
    # Em um projeto real, você carregaria um modelo pré-treinado ou treinado em um dataset maior.
    # Para este exemplo, vamos simular um treinamento simples.

    # Dados de exemplo para "treinar" um modelo de risco (muito simplificado!)
    # NO SEU PROJETO REAL: VOCÊ PRECISA DE UM DATASET ROTULADO DE VERDADE!
    sample_texts = [
        "Ataque terrorista foi frustrado pela polícia", "Ótima notícia, vamos celebrar a paz!",
        "Esse grupo dissemina ódio e preconceito", "Reunião de comunidade pacífica",
        "Precisamos combater a violência nas ruas", "Hoje o dia está lindo para passear",
        "Propaganda nazista é um crime e deve ser denunciada", "Vou comprar pão agora."
    ]
    sample_labels = [
        "risco", "nao_risco", "risco", "nao_risco",
        "risco", "nao_risco", "risco", "nao_risco"
    ]

    risk_model, vectorizer_risk = train_and_predict_risk_model(sample_texts, sample_labels)
    # --- Fim do "treinamento" simulado ---


    # Busca mensagens que ainda não foram analisadas (eh_risco é default False, sentimento é null)
    # Você pode ajustar o filtro para incluir mensagens que precisam de reanálise, etc.
    mensagens_para_analisar = MensagemTelegram.objects.filter(sentimento__isnull=True)[:100] # Limita para teste

    if not mensagens_para_analisar.exists():
        print("Nenhuma mensagem nova para analisar no momento.")
        return

    print(f"Encontradas {mensagens_para_analisar.count()} mensagens para análise.")

    for mensagem in mensagens_para_analisar:
        try:
            # 1. Análise de Risco
            # Se o modelo foi treinado com sucesso, use-o
            if risk_model and vectorizer_risk:
                processed_text_for_risk = " ".join(preprocess_text(mensagem.texto))
                # Transforma o texto para o formato que o modelo espera
                vectorized_text = vectorizer_risk.transform([processed_text_for_risk])
                mensagem.eh_risco = bool(risk_model.predict(vectorized_text)[0])
            else:
                # Fallback simples para risco se o modelo não puder ser treinado
                if any(kw in preprocess_text(mensagem.texto) for kw in PALAVRAS_CHAVE_RISCO):
                    mensagem.eh_risco = True

            # 2. Análise de Sentimento (usando a função de simulação)
            mensagem.sentimento = classify_sentiment(mensagem.texto)

            # 3. Extração de Palavras-Chave (usando a função de lista simples)
            mensagem.palavras_chave_encontradas = identify_risk_keywords(mensagem.texto) or None # JSONField pode ser None

            mensagem.save()
            # print(f"Mensagem {mensagem.id} analisada: Risco={mensagem.eh_risco}, Sentimento={mensagem.sentimento}")

        except Exception as e:
            print(f"Erro ao analisar mensagem {mensagem.id}: {e}")

    print("Processo de análise de IA concluído.")

if __name__ == "__main__":
    # É preciso rodar o asyncio.run, mesmo que a função principal não seja assíncrona,
    # caso você introduza chamadas assíncronas no futuro (como um modelo de IA online)
    import asyncio
    asyncio.run(run_analysis())