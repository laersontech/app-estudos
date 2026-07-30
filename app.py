import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Gerenciador de Estudos", page_icon="📚", layout="wide")

st.title("📚 Meu Painel de Estudos - Concursos")

opcao = st.sidebar.radio("Navegação", ["Painel de Estudos", "Assistente de IA"])

if opcao == "Painel de Estudos":
    st.header("📊 Registro de Desempenho")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Registrar Sessão")
        materia = st.selectbox("Disciplina", ["Português", "Direito Constitucional", "Direito Administrativo", "Raciocínio Lógico", "Legislação Específica"])
        tempo = st.number_input("Tempo estudado (minutos)", min_value=10, max_value=480, step=10)
        questoes_total = st.number_input("Total de questões feitas", min_value=0, step=1)
        questoes_acertos = st.number_input("Questões acertadas", min_value=0, step=1)
        
        if st.button("Salvar Progresso"):
            if questoes_total > 0:
                taxa = (questoes_acertos / questoes_total) * 100
                st.success(f"Sessão de {materia} registrada! Sua taxa de acerto foi de {taxa:.1f}%.")
            else:
                st.success(f"Sessão de {materia} registrada!")

    with col2:
        st.subheader("Resumo do Dia")
        st.metric(label="Tempo Total Estudado", value="120 min")
        st.metric(label="Taxa de Acerto Geral", value="85%")

elif opcao == "Assistente de IA":
    st.header("🤖 Tirar Dúvidas com IA")
    st.write("Digite o conceito ou questão sobre o edital que deseja entender melhor:")
    
    api_key = st.text_input("Cole sua chave de API do Gemini:", type="password")
    pergunta = st.text_area("Sua dúvida:")
    
    if st.button("Perguntar"):
        if not api_key:
            st.warning("Por favor, insira a chave da API do Gemini.")
        elif not pergunta:
            st.warning("Escreva uma dúvida antes de enviar.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                resposta = model.generate_content(f"Explique de forma didática e resumida para um estudante de concurso público: {pergunta}")
                st.write("---")
                st.markdown(resposta.text)
            except Exception as e:
                st.error(f"Erro ao consultar a IA: {e}")
