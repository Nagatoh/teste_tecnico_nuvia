# --- Estágio 1: Builder ---
# Usamos uma imagem base que contém as ferramentas de build necessárias.
FROM python:3.11-slim-bookworm AS builder

# Define variáveis de ambiente para consistência
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
# Cria o ambiente virtual antes de instalar pacotes para manter o sistema limpo
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala o PyTorch para CPU primeiro para garantir que outras bibliotecas o utilizem.
# O uso do cache de build do Docker (--mount) acelera builds repetidos.
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch --index-url https://download.pytorch.org/whl/cpu

# Copia e instala as dependências Python.
# Este passo é separado da cópia do código-fonte para aproveitar o cache do Docker.
# As dependências só serão reinstaladas se o requirements.txt mudar.
COPY . .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt && \
    pip install --no-cache-dir -e .

# ------------------------------------------- Estágio 2: Final ---------------------------------------
# Começa com uma imagem 'slim' para um tamanho final menor.
FROM python:3.11-slim-bookworm AS final

# Cria um usuário e grupo não-root para rodar a aplicação com mais segurança.
RUN groupadd --system --gid 1001 appgroup && \
    useradd --system --uid 1001 --gid 1001 -m appuser

WORKDIR /app
ENV NLTK_DATA=/opt/nltk_data

# Instala apenas as dependências de sistema para execução
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia os artefatos do builder, definindo a propriedade durante a cópia.
# Isso é muito mais rápido do que usar 'chown -R'.
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv
COPY --from=builder --chown=appuser:appgroup /app/src ./src
#COPY --from=builder --chown=appuser:appgroup /app/nltk_data ${NLTK_DATA}
COPY nltk_data ${NLTK_DATA}
# Muda para o usuário não-root antes de executar a aplicação
USER appuser

# Ativa o ambiente virtual
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8501

CMD ["streamlit", "run", "src/nuvia/interface/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]