import streamlit as st

index = st.Page(
    "paginas/index.py",
    title="Página Inicial.",
    icon=":material/home:"
)

calculadora_honorarios = st.Page(
    "paginas/honorarios.py",
    title="Calculadora de Honorários!",
    icon=":material/help:"
)

prazos = st.Page(
    "paginas/prazos.py", 
    title="Calculadora de Prazos!", 
    icon=":material/bug_report:"
)

st.set_page_config(
    page_title="Advogando!",
    page_icon="👋",
)


pg = st.navigation([index, calculadora_honorarios, prazos])

pg.run()