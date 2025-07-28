# interface/streamlit_app.py
import os
import subprocess
import sys
import streamlit as st
import re # Importando a biblioteca de expressões regulares

# --- Dependências do seu projeto (assumindo que estão configuradas para inglês) ---
from nuvia.domain.entities.article import Article
from nuvia.application.use_cases.analyze_article_use_case import AnalyzeArticleUseCase
from nuvia.adapters.nlp.hybrid_bias_detector import HybridBiasDetector # Verifique se este detector usa modelos em inglês
from nuvia.adapters.wikipedia.wikipedia_scraper import WikipediaScraper # Verifique se o scraper busca na Wikipedia em inglês

def display_highlighted_text(full_text, biased_segments):
    """
    Exibe o texto completo do artigo, destacando os segmentos tendenciosos.
    Ao passar o mouse, uma dica de ferramenta mostra o motivo e o score.
    """
    # Ordena os segmentos para processamento correto, evitando sobreposições
    sorted_segments = sorted(biased_segments, key=lambda s: full_text.find(s.text))
    
    # Injeta CSS para as dicas de ferramenta (tooltips)
    st.markdown("""
    <style>
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 250px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -125px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #555 transparent transparent transparent;
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    display_text = full_text
    # Substitui os trechos tendenciosos por HTML com destaque e tooltip
    for seg in reversed(sorted_segments): # Processa de trás para frente para não bagunçar os índices
        if seg.text in display_text:
            score = seg.score
            if score > 0.4:
                bg_color = "rgba(255, 76, 76, 0.4)" # Vermelho claro
            elif score > 0.3:
                bg_color = "rgba(255, 165, 0, 0.4)" # Laranja claro
            else:
                bg_color = "rgba(255, 255, 0, 0.4)" # Amarelo claro
            
            # Escapa aspas para não quebrar o HTML
            reason_html = seg.reason.replace('"', '&quot;')
            text_html = seg.text.replace('"', '&quot;')

            replacement = (
                f'<span class="tooltip" style="background-color: {bg_color}; padding: 2px 0; border-radius: 3px;">'
                f'{text_html}'
                f'<span class="tooltiptext"><b>Reason:</b> {reason_html}<br><b>Score:</b> {score:.2f}</span>'
                f'</span>'
            )
            # Usa re.escape para tratar caracteres especiais no texto do segmento
            display_text = display_text.replace(seg.text, replacement, 1)

    st.markdown(f'<div style="line-height: 1.8;">{display_text}</div>', unsafe_allow_html=True)


def launch_app():
    # Page configuration
    st.set_page_config(page_title="Wikipedia Bias Analyzer", layout="wide")

    st.title("🧠 Wikipedia Bias Analyzer")
    st.markdown("This app detects biased segments in English Wikipedia articles about Artificial Intelligence.")

    mode = st.radio("Input mode", ["Search on Wikipedia", "Insert Text Manually"])

    # --- Inicialização ---
    # Certifique-se de que o HybridBiasDetector está configurado para o inglês (modelos, stopwords, etc.)
    detector = HybridBiasDetector() 
    use_case = AnalyzeArticleUseCase(detector)

    if mode == "Search on Wikipedia":
        # Certifique-se de que o scraper usa a Wikipedia em inglês (ex: wikipedia.set_lang("en"))
        wiki_scrap = WikipediaScraper()
        title = st.text_input("🔍 Search for a topic (e.g., Artificial Intelligence):")
        
        if st.button("Search"):
            results = wiki_scrap.search_articles(title)
            if results:
                st.session_state.results = results
            else:
                st.warning("No articles found.")

        if 'results' in st.session_state and st.session_state.results:
            selected_title = st.selectbox("Choose an article:", st.session_state.results)
            
            if selected_title:
                with st.spinner("Fetching article content..."):
                    content = wiki_scrap.fetch_article(selected_title)
                with st.spinner("Analyzing article and detecting bias..."):
                    if content:
                        article = Article(content['title'], content['text'])
                        result = use_case.execute(article)

                        st.subheader(f"📄 {content['title']}")
                        st.markdown(f"[Read on Wikipedia]({content['url']})")
                        
                        # --- Painel de Análise de Viés ---
                        st.subheader("Bias Analysis Dashboard")
                        col1, col2, col3 = st.columns(3)
                        
                        overall_score = result.overall_score if hasattr(result, 'overall_score') else 0.0 # Supondo que o 'result' tenha um score geral
                        total_segments = len(result.bias_segments)
                        
                        col1.metric("Overall Bias Score", f"{overall_score:.2f}", delta="Higher is more biased", delta_color="inverse")
                        col2.metric("Biased Segments Found", str(total_segments))
                        
                        # Gera o resumo em inglês
                        summary = detector.summarize_bias(result.bias_segments)
                        if "strong subjective language" in summary.lower():
                            color = "#FF4C4C"  # Red
                        elif "considerable presence" in summary.lower():
                            color = "#FFA500"  # Orange
                        else:
                            color = "#90EE90"  # Green
                        
                        st.markdown(
                            f"""
                            <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                                <strong>📊 Bias Summary:</strong> {summary}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # --- Visualização do Texto Completo com Destaques ---
                        st.subheader("Article Text with Bias Highlights")
                        st.info("Hover over a highlighted segment to see the reason for the flag.")
                        display_highlighted_text(content['text'], result.bias_segments)

        else:
            st.error("❌ Could not load the article.")

    # O modo de inserção manual pode ser implementado de forma similar
    elif mode == "Insert Text Manually":
        st.info("Manual text insertion feature coming soon.")

def main():
    """
    This function serves as the entry point for use via [project.scripts] in pyproject.toml,
    starting Streamlit correctly instead of just running the function locally.
    """
    file_path = os.path.abspath(__file__)
    subprocess.run(["streamlit", "run", file_path] + sys.argv[1:])

# Direct execution via: `python streamlit_app.py`
if __name__ == "__main__":
    launch_app()