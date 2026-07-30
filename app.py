import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client, Client

st.set_page_config(page_title="Gerenciador de Estudos", page_icon="📚", layout="wide")

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Erro ao conectar com o Supabase. Verifique se configurou o Secrets no Streamlit Cloud.")

st.title("📚 Meu Painel de Estudos Personalizado")

opcao = st.sidebar.radio("Navegação", ["Registrar Estudo", "Histórico & Desempenho", "Assistente de IA"])

if opcao == "Registrar Estudo":
    st.header("📝 Registrar Sessão de Estudo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        materia = st.text_input("Disciplina / Matéria", placeholder="Ex: Legislação de Trânsito, Português, Direito...")
        assunto = st.text_input("Assunto / Tópico Estudado", placeholder="Ex: Sinalização de Trânsito, Crase, Atos Administrativos...")
        
        tempo = st.number_input("Tempo estudado (minutos)", min_value=5, max_value=600, step=5, value=60)
        questoes_total = st.number_input("Total de questões feitas", min_value=0, step=1, value=10)
        questoes_acertos = st.number_input("Questões acertadas", min_value=0, step=1, value=8)
        
        if st.button("Salvar Sessão"):
            if not materia.strip():
                st.warning("Por favor, preencha o nome da disciplina antes de salvar.")
            elif questoes_acertos > questoes_total:
                st.error("O número de acertos não pode ser maior que o total de questões!")
            else:
                taxa = (questoes_acertos / questoes_total * 100) if questoes_total > 0 else 0
                
                dados_nova_sessao = {
                    "disciplina": materia.strip(),
                    "assunto": assunto.strip() if assunto.strip() else "Geral",
                    "tempo_min": tempo,
                    "questoes": questoes_total,
                    "acertos": questoes_acertos,
                    "aproveitamento": round(taxa, 1)
                }
                
                try:
                    supabase.table("historico_estudos").insert(dados_nova_sessao).execute()
                    st.success(f"Sessão de '{materia}' ({assunto}) salva no banco de dados! Taxa de acerto: {taxa:.1f}%")
                except Exception as e:
                    st.error(f"Erro ao salvar no banco de dados: {e}")

    with col2:
        st.subheader("💡 Resumo da Sessão Atual")
        if questoes_total > 0:
            taxa_atual = (questoes_acertos / questoes_total) * 100
            st.metric(label="Aproveitamento Nesta Sessão", value=f"{taxa_atual:.1f}%")
        st.metric(label="Tempo Dedicado", value=f"{tempo} min")

elif opcao == "Histórico & Desempenho":
    st.header("📊 Histórico e Estatísticas de Estudo")
    
    try:
        resposta = supabase.table("historico_estudos").select("*").order("created_at", desc=True).execute()
        historico_dados = resposta.data
        
        if not historico_dados:
            st.info("Nenhuma sessão registrada ainda no banco de dados. Vá na aba 'Registrar Estudo' para começar!")
        else:
            df = pd.DataFrame(historico_dados)
            df['created_at_dt'] = pd.to_datetime(df['created_at'], utc=True)
            
            hoje = pd.Timestamp.now(tz='UTC')
            inicio_hoje = hoje.floor('D')
            uma_semana_atras = hoje - pd.Timedelta(days=7)
            um_mes_atras = hoje - pd.Timedelta(days=30)
            
            df_dia = df[df['created_at_dt'] >= inicio_hoje]
            df_semana = df[df['created_at_dt'] >= uma_semana_atras]
            df_mes = df[df['created_at_dt'] >= um_mes_atras]
            
            q_dia = df_dia["questoes"].sum()
            a_dia = df_dia["acertos"].sum()
            t_dia = df_dia["tempo_min"].sum()
            taxa_dia = (a_dia / q_dia * 100) if q_dia > 0 else 0
            
            q_sem = df_semana["questoes"].sum()
            a_sem = df_semana["acertos"].sum()
            t_sem = df_semana["tempo_min"].sum()
            taxa_semana = (a_sem / q_sem * 100) if q_sem > 0 else 0
            
            q_mes = df_mes["questoes"].sum()
            a_mes = df_mes["acertos"].sum()
            t_mes = df_mes["tempo_min"].sum()
            taxa_mes = (a_mes / q_mes * 100) if q_mes > 0 else 0
            
            q_geral = df["questoes"].sum()
            a_geral = df["acertos"].sum()
            t_geral = df["tempo_min"].sum()
            taxa_geral = (a_geral / q_geral * 100) if q_geral > 0 else 0
            
            st.subheader("📅 Desempenho por Período")
            c1, c2, c3, c4 = st.columns(4)
            
            c1.metric("Hoje", f"{taxa_dia:.1f}%", f"{q_dia} quest. | {t_dia} min")
            c2.metric("Últimos 7 dias", f"{taxa_semana:.1f}%", f"{q_sem} quest. | {t_sem} min")
            c3.metric("Últimos 30 dias", f"{taxa_mes:.1f}%", f"{q_mes} quest. | {t_mes} min")
            c4.metric("Total Acumulado", f"{taxa_geral:.1f}%", f"{q_geral} quest. | {t_geral} min")
            
            st.write("---")
            
            df_exibicao = df.rename(columns={
                "created_at": "Data/Hora",
                "disciplina": "Disciplina",
                "assunto": "Assunto",
                "tempo_min": "Tempo (min)",
                "questoes": "Questões",
                "acertos": "Acertos",
                "aproveitamento": "Aproveitamento (%)"
            })
            
            st.subheader("📋 Tabela Completa de Sessões")
            colunas_visiveis = ["Data/Hora", "Disciplina", "Assunto", "Tempo (min)", "Questões", "Acertos", "Aproveitamento (%)"]
            st.dataframe(df_exibicao[colunas_visiveis], use_container_width=True)
            
    except Exception as e:
        st.error(f"Erro ao carregar o histórico: {e}")

elif opcao == "Assistente de IA":
    st.header("🤖 Tirar Dúvidas com IA")
    st.write("Digite o assunto ou questão que deseja entender melhor:")
    
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
                resposta = model.generate_content(f"Explique de forma didática e objetiva para um estudante: {pergunta}")
                st.write("---")
                st.markdown(resposta.text)
            except Exception as e:
                st.error(f"Erro ao consultar a IA: {e}")
