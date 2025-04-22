
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Ventas por Cliente", layout="wide")

# === CARGA DE DATOS ===
archivo_default = os.path.join(os.path.dirname(__file__), "ventas_clientes.xlsx")
uploaded_file = st.sidebar.file_uploader("📤 Sube el archivo Excel de ventas:", type=["xlsx"])
archivo_excel = uploaded_file if uploaded_file else archivo_default

df = pd.read_excel(archivo_excel)

# === LIMPIEZA Y FORMATO ===
df.fillna(0, inplace=True)
columnas_meses = ['Enero', 'Febrero', 'Marzo', 'Abril']
df[columnas_meses] = df[columnas_meses].astype(float)
df['Total'] = df[columnas_meses].sum(axis=1)
df[columnas_meses + ['Total']] = df[columnas_meses + ['Total']].round(0)

# === INTERFAZ: SELECCIÓN DE CLIENTES ===
clientes = df['Cliente'].unique()
clientes_seleccionados = st.sidebar.multiselect("🧲 Selecciona uno o varios clientes:", clientes)
df_seleccionado = df[df['Cliente'].isin(clientes_seleccionados)]

if df_seleccionado.empty:
    st.warning("Selecciona al menos un cliente para visualizar los datos.")
    st.stop()

# === GRÁFICO DE LÍNEAS ===
st.markdown("### 📈 Gráfico de líneas de ventas")
fig, ax = plt.subplots(figsize=(10, 5))
for _, fila in df_seleccionado.iterrows():
    y = fila[columnas_meses].values
    ax.plot(columnas_meses, y, marker='o', label=fila['Cliente'])
    for i, valor in enumerate(y):
        ax.annotate(f"{int(valor):,} €", (i, y[i]), textcoords="offset points", xytext=(0, -10),
                    ha='center', fontsize=8)

ax.set_xlabel("Mes")
ax.set_ylabel("Ventas (€)")
ax.set_title("Ventas por cliente de Enero a Abril", fontsize=14, fontweight="bold")
ax.legend(loc="best", fontsize=8)
plt.tight_layout()
st.pyplot(fig)

# === GRÁFICO DE BARRAS ===
st.markdown("### 📊 Total de ventas por cliente (ene-abril)")
fig2, ax2 = plt.subplots(figsize=(10, 5))
totales = df_seleccionado[['Cliente', 'Total']].sort_values(by="Total", ascending=False)
ax2.bar(totales['Cliente'], totales['Total'], color=sns.color_palette("pastel", len(totales)))
ax2.set_xticks(range(len(totales)))
ax2.set_xticklabels(totales['Cliente'], rotation=0, fontsize=8)
for i, valor in enumerate(totales['Total']):
    ax2.text(i, valor, f"{int(valor):,} €", ha='center', va='bottom', fontsize=8)
ax2.set_ylabel("Total Ventas (€)")
ax2.set_title("Total de ventas por cliente (ene-abril)", fontsize=14, fontweight="bold")
plt.tight_layout()
st.pyplot(fig2)

# === MAPA DE CALOR ===
st.markdown("### 🔥 Mapa de calor de ventas por cliente y mes")
def mapa_color(fila):
    max_val = fila.max()
    min_val = fila[fila > 0].min() if any(fila > 0) else 0
    colores = []
    for valor in fila:
        if valor == 0:
            colores.append("background-color: red; color: white")
        elif valor == max_val:
            colores.append("background-color: #003f5c; color: white")
        elif valor == min_val:
            colores.append("background-color: #f9c74f; color: black")
        else:
            colores.append("")
    return colores

df_mapa = df_seleccionado[['Cliente'] + columnas_meses].copy()
df_mapa[columnas_meses] = df_mapa[columnas_meses].round(0)
styled_mapa = df_mapa.set_index('Cliente').style.format("{:,.0f} €").apply(mapa_color, axis=1)
st.dataframe(styled_mapa, use_container_width=True)

# === ALERTAS Y SEMÁFORO ===
st.markdown("### 🚦 Semáforo de tendencias y alertas")
for _, row in df_seleccionado.iterrows():
    cliente = row['Cliente']
    ventas = row[columnas_meses].values
    texto = f"**{cliente}** — Total acumulado: **{int(row['Total']):,} €**\n"
    alertas = []
    for i in range(1, len(ventas)):
        anterior, actual = ventas[i-1], ventas[i]
        if anterior == 0:
            continue
        cambio = (actual - anterior) / anterior * 100
        if cambio >= 25:
            alertas.append(f"🟢 Subida del {cambio:.1f}% de {columnas_meses[i-1]} a {columnas_meses[i]}")
        elif cambio <= -40:
            alertas.append(f"🔴 Bajón fuerte del {abs(cambio):.1f}% de {columnas_meses[i-1]} a {columnas_meses[i]}")
        elif cambio <= -25:
            alertas.append(f"🟡 Bajada del {abs(cambio):.1f}% de {columnas_meses[i-1]} a {columnas_meses[i]}")

    if alertas:
        st.markdown(texto + '\n' + '\n'.join(alertas))
    else:
        st.markdown(texto + "✅ Sin variaciones significativas.")
