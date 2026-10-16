"""
Generador de Gráficos Analíticos en Formato Vectorial SVG (Normas APA 7.ª ed.)
Proyecto Interdisciplinario UNVES 2026 - Sesiones 10 y 12
Exporta las 5 figuras analíticas a r-analysis/output/*.svg en alta fidelidad.
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Rutas
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "r-analysis" / "data"
OUTPUT_DIR = BASE_DIR / "r-analysis" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuración Estilo APA 7
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "axes.labelweight": "bold",
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "figure.titlesize": 12,
    "figure.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#111827",
    "axes.linewidth": 0.8,
    "svg.fonttype": "none"  # Preserve text in SVG
})

# Cargar datos
df_trab = pd.read_csv(DATA_DIR / "vw_trabajadores_consolidado.csv")
df_mype = pd.read_csv(DATA_DIR / "vw_unidades_productivas_consolidado.csv")
df_mkt_res = pd.read_csv(DATA_DIR / "vw_marketing_resumen_canales.csv")

with open(OUTPUT_DIR / "resultados_econometricos.json", "r", encoding="utf-8") as f:
    stats = json.load(f)

SALARIO_MINIMO = 3044000

# -----------------------------------------------------------------------------
# FIGURA 1: Correlación Escolaridad vs Ingreso
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
x = df_trab["anios_estudio"].values
y = df_trab["ingreso_mensual_pyg"].values / 1e6

ax.scatter(x, y, alpha=0.5, color="#1E3A8A", edgecolors="none", s=30, label="Trabajadores (N=420)")
# Recta MCO
slope, intercept = np.polyfit(x, y, 1)
x_vals = np.linspace(x.min(), x.max(), 100)
ax.plot(x_vals, slope * x_vals + intercept, color="#B91C1C", linewidth=1.8, label="Ajuste lineal MCO")
ax.axhline(SALARIO_MINIMO / 1e6, color="#047857", linestyle="--", linewidth=1.2, label=f"Salario Mínimo Legal (Gs. {SALARIO_MINIMO:,.0f})".replace(",", "."))

r_val = stats["correlacion_escolaridad_ingreso"]["pearson"]["r"]
p_val = stats["correlacion_escolaridad_ingreso"]["pearson"]["p_value"]
rho_val = stats["correlacion_escolaridad_ingreso"]["spearman"]["rho"]
rho_p = stats["correlacion_escolaridad_ingreso"]["spearman"]["p_value"]

ax.text(0.04, 0.90, f"Pearson r = {r_val:.3f} (p = {p_val:.3f})\nSpearman ρ = {rho_val:.3f} (p = {rho_p:.3f})", 
        transform=ax.transAxes, bbox=dict(boxstyle="round,pad=0.4", facecolor="#F3F4F6", edgecolor="#D1D5DB"),
        fontsize=9, verticalalignment="top")

ax.set_title("Figura 1. Correlación entre Años de Escolaridad e Ingreso Mensual", loc="left", pad=12)
ax.set_xlabel("Años de Educación Formal Acumulada")
ax.set_ylabel("Ingreso Mensual Percibido (Millones de Gs.)")
ax.set_ylim(1.0, 4.8)
ax.yaxis.grid(True, linestyle=":", alpha=0.5, color="#9CA3AF")
ax.legend(loc="upper right", frameon=False, fontsize=8.5)
fig.text(0.12, -0.02, "Nota. N = 420 trabajadores informales. Elaboración propia según relevamiento KoboCollect UNVES (2026).", fontsize=8, style="italic")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "figura1_correlacion_escolaridad_ingreso.svg", format="svg", bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# FIGURA 2: Vulnerabilidad Social por Barrio
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
barrios = sorted(df_trab["barrio"].unique(), key=lambda b: df_trab[df_trab["barrio"] == b]["indice_vulnerabilidad_social"].median(), reverse=True)
box_data = [df_trab[df_trab["barrio"] == b]["indice_vulnerabilidad_social"].values for b in barrios]

bp = ax.boxplot(box_data, tick_labels=barrios, patch_artist=True,
                boxprops=dict(facecolor="#E0E7FF", color="#1E3A8A"),
                medianprops=dict(color="#B91C1C", linewidth=1.8),
                whiskerprops=dict(color="#1E3A8A"),
                capprops=dict(color="#1E3A8A"),
                flierprops=dict(marker="o", markerfacecolor="#DC2626", markeredgecolor="none", markersize=4, alpha=0.6))

f_stat = stats["vulnerabilidad_por_barrio"]["anova"]["f_stat"]
p_anova = stats["vulnerabilidad_por_barrio"]["anova"]["p_value"]
h_kw = stats["vulnerabilidad_por_barrio"]["kruskal_wallis"]["chi_squared"]
p_kw = stats["vulnerabilidad_por_barrio"]["kruskal_wallis"]["p_value"]

ax.text(0.5, 0.92, f"ANOVA: F(6, 413) = {f_stat:.3f}, p = {p_anova:.3f} | Kruskal-Wallis: H(6) = {h_kw:.3f}, p = {p_kw:.3f}",
        transform=ax.transAxes, ha="center", bbox=dict(boxstyle="round,pad=0.4", facecolor="#F3F4F6", edgecolor="#D1D5DB"),
        fontsize=9)

ax.set_title("Figura 2. Índice Sintético de Vulnerabilidad Social en los 7 Barrios de Villarrica", loc="left", pad=12)
ax.set_xlabel("Barrio de Relevamiento Censal")
ax.set_ylabel("Índice de Vulnerabilidad Social (Escala 0 a 100)")
ax.yaxis.grid(True, linestyle=":", alpha=0.5, color="#9CA3AF")
plt.xticks(rotation=15, ha="right")
fig.text(0.12, -0.04, "Nota. N = 420. Diferencias inter-barriales no significativas (p > .05). Cátedra Realidad Social - UNVES (2026).", fontsize=8, style="italic")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "figura2_vulnerabilidad_social_barrios.svg", format="svg", bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# FIGURA 3: Densidad de Ingresos por Género y Brecha con Salario Mínimo
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
fem_inc = df_trab[df_trab["genero"] == "femenino"]["ingreso_mensual_pyg"] / 1e6
masc_inc = df_trab[df_trab["genero"] == "masculino"]["ingreso_mensual_pyg"] / 1e6

# Kernel Density
from scipy.stats import gaussian_kde
kde_fem = gaussian_kde(fem_inc)
kde_masc = gaussian_kde(masc_inc)
x_eval = np.linspace(1.2, 4.5, 200)

ax.plot(x_eval, kde_fem(x_eval), color="#DB2777", linewidth=2, label=f"Femenino (Media: Gs. {fem_inc.mean()*1e6:,.0f})".replace(",", "."))
ax.fill_between(x_eval, 0, kde_fem(x_eval), color="#F472B6", alpha=0.3)

ax.plot(x_eval, kde_masc(x_eval), color="#2563EB", linewidth=2, label=f"Masculino (Media: Gs. {masc_inc.mean()*1e6:,.0f})".replace(",", "."))
ax.fill_between(x_eval, 0, kde_masc(x_eval), color="#60A5FA", alpha=0.3)

ax.axvline(SALARIO_MINIMO / 1e6, color="#047857", linestyle="--", linewidth=1.4, label="Salario Mínimo Legal (Gs. 3.044.000)")

brecha = stats["brecha_genero"]["brecha_porcentaje"]
p_t = stats["brecha_genero"]["t_test"]["p_value"]
p_w = stats["brecha_genero"]["wilcox_test"]["p_value"]

ax.text(0.96, 0.70, f"Brecha salarial de género: {brecha:.1f}%\nt de Welch: p = {p_t:.3f}\nMann-Whitney: p = {p_w:.3f}",
        transform=ax.transAxes, ha="right", bbox=dict(boxstyle="round,pad=0.4", facecolor="#F3F4F6", edgecolor="#D1D5DB"),
        fontsize=8.5)

ax.set_title("Figura 3. Curva de Densidad de Ingresos por Género frente al Salario Mínimo Legal", loc="left", pad=12)
ax.set_xlabel("Ingreso Mensual Percibido (Millones de Guaraníes)")
ax.set_ylabel("Densidad de Probabilidad Kernel")
ax.yaxis.grid(True, linestyle=":", alpha=0.5, color="#9CA3AF")
ax.legend(loc="upper left", frameon=False, fontsize=8.5)
fig.text(0.12, -0.02, "Nota. N = 420 (Femenino n = 198, Masculino n = 222). Datos Proyecto Interdisciplinario UNVES (2026).", fontsize=8, style="italic")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "figura3_brecha_ingreso_genero_minimo.svg", format="svg", bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# FIGURA 4: Tasa de Informalidad en MYPEs por Rubro
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
rubro_stats = df_mype.groupby("rubro_actividad").agg(
    tasa_media=("tasa_informalidad_laboral_pct", "mean"),
    n=("id_unidad", "count")
).sort_values(by="tasa_media", ascending=True)

y_pos = np.arange(len(rubro_stats))
bars = ax.barh(y_pos, rubro_stats["tasa_media"], color="#3B82F6", edgecolor="#1E3A8A", height=0.65)

for i, bar in enumerate(bars):
    val = rubro_stats["tasa_media"].iloc[i]
    count = rubro_stats["n"].iloc[i]
    ax.text(val + 1.2, bar.get_y() + bar.get_height() / 2, f"{val:.1f}% (n={count})", 
            va="center", fontsize=8.5, fontweight="bold", color="#1F2937")

ax.set_yticks(y_pos)
ax.set_yticklabels(rubro_stats.index)
ax.set_xlim(0, 115)
ax.set_title("Figura 4. Tasa Media de Informalidad Laboral Patronal por Rubro de MYPEs", loc="left", pad=12)
ax.set_xlabel("Tasa de Informalidad Laboral Media (%)")
ax.xaxis.grid(True, linestyle=":", alpha=0.5, color="#9CA3AF")
fig.text(0.12, -0.03, "Nota. N = 135 unidades productivas relevadas en Villarrica. Cátedra SIG - UNVES (2026).", fontsize=8, style="italic")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "figura4_informalidad_mypes_rubro.svg", format="svg", bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# FIGURA 5: Embudo Multicanal de Marketing Social
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
canales = df_mkt_res["canal_nombre"].tolist()
etapas = ["Alcance (/100)", "Consultas", "Derivaciones"]

x = np.arange(len(etapas))
width = 0.20
colors = ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"]

for i, canal in enumerate(canales):
    row = df_mkt_res[df_mkt_res["canal_nombre"] == canal].iloc[0]
    vals = [row["total_alcance"] / 100, row["total_consultas"], row["total_derivaciones"]]
    offset = (i - 1.5) * width
    ax.bar(x + offset, vals, width, label=canal, color=colors[i % len(colors)], edgecolor="#111827", linewidth=0.5)

ax.set_xticks(x)
ax.set_xticklabels(["1. Impresiones / Alcance (÷100)", "2. Consultas Iniciadas", "3. Derivaciones Efectivas"])
ax.set_title("Figura 5. Rendimiento y Conversión del Embudo Multicanal de Marketing Social", loc="left", pad=12)
ax.set_ylabel("Volumen Registrado")
ax.yaxis.grid(True, linestyle=":", alpha=0.5, color="#9CA3AF")
ax.legend(title="Canal Estratégico", loc="upper right", frameon=False, fontsize=8.5)
fig.text(0.12, -0.03, "Nota. 42 días continuos de activación 'Trabajo Formal, Futuro Seguro'. Cátedra Marketing Social - UNVES (2026).", fontsize=8, style="italic")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "figura5_embudo_marketing_multicanal.svg", format="svg", bbox_inches="tight")
plt.close()

print(f"Figuras vectoriales SVG generadas exitosamente en {OUTPUT_DIR}")
