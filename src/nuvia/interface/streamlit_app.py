# interface/streamlit_app.py
import os
import subprocess
import sys
import streamlit as st
import re
from weasyprint import HTML  # Importa a biblioteca para gerar PDF

# --- Dependências do seu projeto ---
from nuvia.domain.entities.article import Article
# Importa a classe de resultado junto com o caso de uso
from nuvia.application.use_cases.analyze_article_use_case import AnalyzeArticleUseCase, AnalysisResult
from nuvia.adapters.nlp.hybrid_bias_detector import HybridBiasDetector
from nuvia.adapters.wikipedia.wikipedia_scraper import WikipediaScraper

# ==============================================================================
# FUNÇÕES AUXILIARES DE GERAÇÃO E EXIBIÇÃO
# ==============================================================================

def create_pdf_report(result: AnalysisResult, article_text: str, content_url: str = None):
    """
    Gera um relatório em PDF a partir dos resultados da análise.
    """
    # --- Monta o conteúdo HTML do relatório ---
    sorted_segments = sorted(result.segments, key=lambda s: article_text.find(s.text))
    display_text = article_text

    for seg in reversed(sorted_segments):
        if seg.text in display_text:
            score = seg.score
            if score > 0.4:
                bg_color = "rgba(255, 76, 76, 0.3)"
            elif score > 0.3:
                bg_color = "rgba(255, 165, 0, 0.3)"
            else:
                bg_color = "rgba(255, 255, 0, 0.4)"

            text_html = seg.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            replacement = f'<span style="background-color: {bg_color}; padding: 1px 3px; border-radius: 3px;">{text_html}</span>'
            display_text = display_text.replace(seg.text, replacement, 1)

    link_html = f'<p><strong>Source:</strong> <a href="{content_url}">{content_url}</a></p>' if content_url else ""

    html_content = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; color: #333; }}
                h1, h2, h3 {{ color: #000; }}
                hr {{ border: 0; border-top: 1px solid #ccc; }}
                .summary-box {{ border: 1px solid #ddd; padding: 15px; margin: 20px 0; border-radius: 5px; background-color: #f9f9f9; }}
                .score-label {{ font-weight: bold; }}
                .article-text {{ white-space: pre-wrap; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <h1>Bias Analysis Report</h1>
            <h2>{result.article_title}</h2>
            {link_html}
            <hr>
            
            <div class="summary-box">
                <h3>Analysis Summary</h3>
                <p><span class="score-label">Overall Bias Score:</span> {result.overall_score:.2f} (Score per 1000 words)</p>
                <p><span class="score-label">Biased Segments Found:</span> {len(result.segments)}</p>
            </div>

            <h3>Article Text with Highlights</h3>
            <div class="article-text">{display_text.replace(chr(10), '<br>')}</div>
        </body>
    </html>
    """
    # --- Converte o HTML para PDF em memória ---
    return HTML(string=html_content).write_pdf()

def display_highlighted_text(full_text: str, biased_segments: list):
    """
    Exibe o texto completo no Streamlit, destacando os segmentos tendenciosos.
    """
    sorted_segments = sorted(biased_segments, key=lambda s: full_text.find(s.text))
    
    st.markdown("""
    <style>
    .tooltip { position: relative; display: inline-block; cursor: pointer; border-bottom: 1px dotted black; }
    .tooltip .tooltiptext { visibility: hidden; width: 250px; background-color: #555; color: #fff; text-align: center; border-radius: 6px; padding: 8px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -125px; opacity: 0; transition: opacity 0.3s; }
    .tooltip .tooltiptext::after { content: ""; position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #555 transparent transparent transparent; }
    .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
    </style>
    """, unsafe_allow_html=True)

    display_text = full_text
    for seg in reversed(sorted_segments):
        if seg.text in display_text:
            score = seg.score
            bg_color = "rgba(255, 255, 0, 0.4)" # Amarelo claro
            if score > 0.4: bg_color = "rgba(255, 76, 76, 0.4)" # Vermelho claro
            elif score > 0.3: bg_color = "rgba(255, 165, 0, 0.4)" # Laranja claro
            
            reason_html = seg.reason.replace('"', '&quot;')
            text_html = seg.text.replace('"', '&quot;')
            replacement = (f'<span class="tooltip" style="background-color: {bg_color}; padding: 2px 0; border-radius: 3px;">'
                           f'{text_html}'
                           f'<span class="tooltiptext"><b>Reason:</b> {reason_html}<br><b>Score:</b> {score:.2f}</span>'
                           f'</span>')
            display_text = display_text.replace(seg.text, replacement, 1)

    st.markdown(f'<div style="line-height: 1.8;">{display_text}</div>', unsafe_allow_html=True)

def display_analysis_results(result: AnalysisResult, original_text: str, detector: HybridBiasDetector, content_url: str = None):
    """Função reutilizável para exibir todos os resultados da análise."""
    st.subheader("Bias Analysis Dashboard")
    col1, col2 = st.columns(2)
    col1.metric("Overall Bias Score", f"{result.overall_score:.2f}", delta="Score per 1000 words", delta_color="off")
    col2.metric("Biased Segments Found", str(len(result.segments)))
    
    summary = detector.summarize_bias(result.segments)
    if "strong" in summary.lower(): color = "rgba(255, 76, 76, 0.6)"
    elif "considerable" in summary.lower() or "moderate" in summary.lower(): color = "rgba(255, 165, 0, 0.6)"
    else: color = "rgba(144, 238, 144, 0.6)"
    
    st.markdown(f'<div style="background-color: {color}; padding: 10px; border-radius: 5px; margin-bottom: 20px;"><strong>📊 Bias Summary:</strong> {summary}</div>', unsafe_allow_html=True)

    st.subheader("Article Text with Bias Highlights")
    st.info("Hover over a highlighted segment to see the reason for the flag.")
    display_highlighted_text(original_text, result.segments)

    st.divider()
    st.subheader("📄 Download Report")
    pdf_bytes = create_pdf_report(result, original_text, content_url)
    safe_title = "".join(c for c in result.article_title if c.isalnum() or c in (' ', '_')).rstrip()
    st.download_button(label="📥 Download PDF Report", data=pdf_bytes, file_name=f"Bias_Report_{safe_title}.pdf", mime="application/pdf")

# ==============================================================================
# FUNÇÃO PRINCIPAL DA APLICAÇÃO
# ==============================================================================

def launch_app():
    st.set_page_config(page_title="Wikipedia Bias Analyzer", layout="wide")
    st.title("🧠 Wikipedia Bias Analyzer")
    st.markdown("This app detects biased segments in English Wikipedia articles or custom text.")
    with st.spinner("Loading Models"):
        # --- Inicialização dos componentes ---
        if 'detector' not in st.session_state:
            st.session_state.detector = HybridBiasDetector()
        if 'use_case' not in st.session_state:
            st.session_state.use_case = AnalyzeArticleUseCase(st.session_state.detector)
    
    detector = st.session_state.detector
    use_case = st.session_state.use_case

    mode = st.radio("Input mode", ["Search on Wikipedia", "Insert Text Manually"])

    if mode == "Search on Wikipedia":
        wiki_scrap = WikipediaScraper()
        title = st.text_input("🔍 Search for a topic (e.g., Artificial Intelligence):")
        
        if st.button("Search"):
            if 'results' in st.session_state: del st.session_state.results
            with st.spinner("Searching for articles..."):
                search_results = wiki_scrap.search_articles(title)
            if search_results: st.session_state.results = search_results
            else: st.warning("No articles found.")

        if 'results' in st.session_state and st.session_state.results:
            selected_title = st.selectbox("Choose an article:", st.session_state.results)
            if selected_title:
                with st.spinner("Fetching and analyzing article... Please wait."):
                    content = wiki_scrap.fetch_article(selected_title)
                    if content:
                        article = Article(title=content['title'], content=content['text'])
                        result: AnalysisResult = use_case.execute(article)
                    else: result = None
                
                if content and result:
                    display_analysis_results(result, content['text'], detector, content['url'])
                    st.subheader(f"📄 {result.article_title}")
                    st.markdown(f"[Read on Wikipedia]({content['url']})")
                else:
                    st.error("❌ Could not load or analyze the article.")

    elif mode == "Insert Text Manually":
        st.subheader("Analyze Custom Text")
        text_area = st.text_area("Paste the text you want to analyze here:", height=250)
        if st.button("Analyze Text"):
            if text_area:
                with st.spinner("Analyzing text..."):
                    article = Article(title="Custom Text Analysis", content=text_area)
                    result: AnalysisResult = use_case.execute(article)
                st.success("Analysis complete!")
                display_analysis_results(result, text_area, detector)
            else:
                st.warning("Please paste some text to analyze.")

def main():
    file_path = os.path.abspath(__file__)
    subprocess.run(["streamlit", "run", file_path] + sys.argv[1:])

if __name__ == "__main__":
    launch_app()