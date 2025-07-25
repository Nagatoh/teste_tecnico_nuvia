import streamlit as st
from wikipedia_fetcher import search_articles, get_article
from bias_detection import analyze_bias

st.title("🧠 Detector de Viés em Artigos da Wikipedia")

query = st.text_input("🔍 Buscar por tema (ex: Artificial Intelligence):")

if st.button("Buscar"):
    results = search_articles(query)
    if results:
        selected_article = st.selectbox("Escolha um artigo:", results)
        if selected_article:
            article_data = get_article(selected_article)
            if article_data:
                st.subheader(f"📄 {article_data['title']}")
                st.markdown(f"[Abrir no navegador]({article_data['url']})")
                st.write(article_data['summary'])
                st.session_state["article_text"] = article_data['text']
            else:
                st.error("❌ Não foi possível carregar o artigo.")
    else:
        st.warning("Nenhum artigo encontrado.")

if "article_text" in st.session_state and st.button("Analisar viés"):
    biased = analyze_bias(st.session_state["article_text"])
    if biased:
        st.write("⚠️ Sentenças com viés detectado:")
        for b in biased[:10]:
            st.markdown(f"- **{b['sentence']}**\n  (Score: {b['bias_score']})")
    else:
        st.success("✅ Nenhum viés detectado.")
