from flask import Flask, request, render_template_string
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.io as pio
import random

# Configura o Plotly para abrir os gráficos no navegador
pio.renderers.default = "browser"

# Carrega os dados do CSV
# (Certifique-se de que o arquivo drinks.csv esteja no mesmo diretório do script)
df = pd.read_csv("drinks.csv")

# Cria e popula o banco de dados SQLite com os dados do CSV
conn = sqlite3.connect("consumo_alcool.db")
df.to_sql("drinks", conn, if_exists="replace", index=False)
conn.commit()
conn.close()

# Inicializa a aplicação Flask
app = Flask(__name__)

# Template HTML com links para cada gráfico
html_template = """
<h1>Dashboard - Consumo de Álcool</h1>
<ul>
  <li><a href="/grafico1">Top 10 países com maior consumo de álcool</a></li>
  <li><a href="/grafico2">Média de consumo de cada tipo de bebida</a></li>
  <li><a href="/grafico3">Consumo total por região do mundo</a></li>
  <li><a href="/grafico4">Comparativo entre tipos de bebida</a></li>
  <li><a href="/pais?nome=Brazil">Insight por país (ex: Brazil)</a></li>

<li><a href="/comparar">Comparar Tipos</a></li>
<li><a href="/upload_avengers">Upload Vingadores</a></li>
<li><a href="/apagar_avengers">Apagar Avengers</a></li>
<li><a href="/atribuir_paises_avengers">Atribuir Paises</a></li>
<li><a href="/avengers_vs_drinks">VAA (Vingadores Alcolicos Anonimos)</a></li>
</ul>
"""

# Rota inicial com os links para os gráficos
@app.route("/")
def index():
    return render_template_string(html_template)

# Rota: Top 10 países com maior consumo de álcool puro
@app.route("/grafico1")
def grafico1():
    conn = sqlite3.connect("consumo_alcool.db")
    df = pd.read_sql_query("""
        SELECT country, total_litres_of_pure_alcohol
        FROM drinks
        ORDER BY total_litres_of_pure_alcohol DESC
        LIMIT 10
    """, conn)
    conn.close()
    fig = px.bar(df, x="country", y="total_litres_of_pure_alcohol", title="Top 10 países com maior consumo de álcool")
    return fig.to_html() + '<br><a href="/">Voltar ao início</a>'

# Rota: Média global de consumo por tipo de bebida
@app.route("/grafico2")
def grafico2():
    conn = sqlite3.connect("consumo_alcool.db")
    df = pd.read_sql_query("SELECT AVG(beer_servings) AS cerveja, AVG(spirit_servings) AS destilados, AVG(wine_servings) AS vinho FROM drinks", conn)
    conn.close()
    df_melted = df.melt(var_name="Bebida", value_name="Média de Porções")
    fig = px.bar(df_melted, x="Bebida", y="Média de Porções", title="Média de consumo global por tipo de bebida")
    return fig.to_html() + '<br><a href="/">Voltar ao início</a>'

# Rota: Consumo total de álcool por regiões simuladas do mundo
@app.route("/grafico3")
def grafico3():
    # Define grupos de países por região (simulação)
    regioes = {
        "Europe": ["France", "Germany", "Italy", "Spain", "Portugal", "UK", "Andorra"],
        "Asia": ["China", "Japan", "India", "Thailand", "Afghanistan"],
        "Africa": ["Angola", "Nigeria", "South Africa", "Egypt", "Algeria"],
        "Americas": ["USA", "Canada", "Brazil", "Argentina", "Mexico"]
    }
    dados = []
    conn = sqlite3.connect("consumo_alcool.db")
    # Consulta o total de álcool por região
    for regiao, paises in regioes.items():
        placeholders = ",".join([f"'{p}'" for p in paises])
        query = f"""
            SELECT SUM(total_litres_of_pure_alcohol) as total FROM drinks WHERE country IN ({placeholders})
        """
        total = pd.read_sql_query(query, conn)["total"][0] or 0
        dados.append({"Região": regiao, "Consumo Total": total})
    conn.close()
    df_regioes = pd.DataFrame(dados)
    fig = px.pie(df_regioes, names="Região", values="Consumo Total", title="Consumo total por região do mundo")
    return fig.to_html() + '<br><a href="/">Voltar ao início</a>'

# Rota: Proporção média global entre tipos de bebidas
@app.route("/grafico4")
def grafico4():
    conn = sqlite3.connect("consumo_alcool.db")
    df = pd.read_sql_query("SELECT beer_servings, spirit_servings, wine_servings FROM drinks", conn)
    conn.close()
    medias = df.mean().reset_index()
    medias.columns = ["Tipo", "Média"]
    fig = px.pie(medias, names="Tipo", values="Média", title="Proporção média entre tipos de bebidas")
    return fig.to_html() + '<br><a href="/">Voltar ao início</a>'

# Rota: Insight individual por país (recebe o nome do país por GET)
@app.route("/pais")
def grafico_pais():
    nome = request.args.get("nome", "Brazil")  # País padrão é Brazil
    conn = sqlite3.connect("consumo_alcool.db")
    df = pd.read_sql_query(f"""
        SELECT beer_servings, spirit_servings, wine_servings, total_litres_of_pure_alcohol 
        FROM drinks WHERE country = ?
    """, conn, params=(nome,))
    conn.close()
    if df.empty:
        return f"<h3>País '{nome}' não encontrado.</h3>"
    dados = df.T.reset_index()
    dados.columns = ["Tipo", "Valor"]
    fig = px.bar(dados, x="Tipo", y="Valor", title=f"Consumo de bebidas em {nome}")
    return fig.to_html() + '<br><a href="/">Voltar ao início</a>'

# Rota: Formulário para comparação personalizada
@app.route("/comparar", methods=["GET", "POST"])
def comparar():
    opcoes = ["beer_servings", "spirit_servings", "wine_servings", "total_litres_of_pure_alcohol"]
    
    if request.method == "POST":
        eixo_x = request.form.get("eixo_x")
        eixo_y = request.form.get("eixo_y")

        if eixo_x == eixo_y:
            return "<h3>Selecione variáveis diferentes para comparar.</h3>"

        conn = sqlite3.connect("consumo_alcool.db")
        df = pd.read_sql_query("SELECT country, {}, {} FROM drinks".format(eixo_x, eixo_y), conn)
        conn.close()

        fig = px.scatter(df, x=eixo_x, y=eixo_y, text="country",
                         title=f"Comparação entre {eixo_x} e {eixo_y}")
        fig.update_traces(textposition='top center')
        return fig.to_html() + '<br><a href="/">Voltar ao início</a>'

    # Formulário HTML simples
    return render_template_string('''
        <h2>Comparar variáveis</h2>
        <form method="POST">
            <label for="eixo_x">Eixo X:</label>
            <select name="eixo_x">
                {% for col in opcoes %}
                    <option value="{{ col }}">{{ col }}</option>
                {% endfor %}
            </select><br><br>

            <label for="eixo_y">Eixo Y:</label>
            <select name="eixo_y">
                {% for col in opcoes %}
                    <option value="{{ col }}">{{ col }}</option>
                {% endfor %}
            </select><br><br>

            <input type="submit" value="Comparar">
        </form>
    ''', opcoes=opcoes)

@app.route("/upload_avengers", methods=["GET", "POST"])
def upload_avengers():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return "Nenhum arquivo enviado."

        df_avengers = pd.read_csv(file, encoding="latin1")
        conn = sqlite3.connect("consumo_alcool.db")
        df_avengers.to_sql("avengers", conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        return "<h3>Arquivo Avengers inserido no banco com sucesso!</h3><a href='/'>Voltar</a>"

    return '''
    <h2>Upload do arquivo avengers.csv</h2>
    <form method="POST" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv"><br><br>
        <input type="submit" value="Enviar">
    </form>
    '''

@app.route("/apagar_avengers")
def apagar_avengers():
    conn = sqlite3.connect("consumo_alcool.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("DROP TABLE IF EXISTS avengers")
        conn.commit()
        mensagem = "<h3>Tabela 'avengers' apagada com sucesso!</h3>"
    except Exception as e:
        mensagem = f"<h3>Erro ao apagar a tabela: {str(e)}</h3>"
    
    conn.close()
    return mensagem + '<br><a href="/">Voltar ao início</a>'


@app.route("/atribuir_paises_avengers")
def atribuir_paises_avengers():
    conn = sqlite3.connect("consumo_alcool.db")

    df_avengers = pd.read_sql_query("SELECT * FROM avengers", conn)
    df_drinks = pd.read_sql_query("SELECT country FROM drinks", conn)
    
    # Sorteio dos países
    random.seed(42)
    paises_possiveis = df_drinks["country"].unique()
    df_avengers["country"] = [random.choice(paises_possiveis) for _ in range(len(df_avengers))]

    # Salva de volta no banco
    df_avengers.to_sql("avengers", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    
    return "<h3>Países atribuídos aos Avengers com sucesso!</h3><a href='/'>Voltar</a>"


@app.route("/avengers_vs_drinks")
def avengers_vs_drinks():
    conn = sqlite3.connect("consumo_alcool.db")
    
    df_drinks = pd.read_sql_query("SELECT * FROM drinks", conn)
    df_avengers = pd.read_sql_query("SELECT * FROM avengers", conn)
    
    # Corrige o tipo da coluna 'Death1' se for string
    if df_avengers['Death1'].dtype != bool:
        df_avengers['Death1'] = df_avengers['Death1'].astype(str).str.strip().str.lower() == 'false'

    vivos = df_avengers[df_avengers['Death1'] == True]

    if vivos.empty:
        conn.close()
        return "<h3>Não há avengers vivos no dataset.</h3>"

    avengers_por_pais = vivos["country"].value_counts().reset_index()
    avengers_por_pais.columns = ["country", "avengers_vivos"]

    merged = pd.merge(df_drinks, avengers_por_pais, on="country", how="inner")

    fig = px.scatter(merged, x="avengers_vivos", y="total_litres_of_pure_alcohol",
                     text="country", title="Avengers vivos vs Consumo de álcool por país")
    fig.update_traces(textposition='top center')

    conn.close()
    return fig.to_html() + '<br><a href="/">Voltar ao início</a>'





if __name__ == "__main__":
    app.run(debug=True)
