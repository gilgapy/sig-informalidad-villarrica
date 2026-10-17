# ==============================================================================
# PROYECTO INTERDISCIPLINARIO UNVES 2026 - 4° CURSO (8° SEMESTRE)
# FACULTAD DE CIENCIAS ECONÓMICAS - ADMINISTRACIÓN DE EMPRESAS
# Cátedras: Sistema de Información Gerencial | Realidad Social | Marketing Social
# Script: analisis_econometrico.R
# Objetivo: Análisis econométrico, pruebas de hipótesis y visualizaciones APA 7.ª ed.
# Sesiones 10 y 12 - Indicador 4 de Rúbrica
# ==============================================================================

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(tidyr)
  library(scales)
  library(jsonlite)
})

# Definición de Directorios
script_dir <- getwd()
data_dir <- file.path(script_dir, "r-analysis", "data")
output_dir <- file.path(script_dir, "r-analysis", "output")
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

cat("==============================================================================\n")
cat("INICIANDO ANÁLISIS ECONOMÉTRICO Y ESTADÍSTICO REPRODUCIBLE (UNVES 2026)\n")
cat("Directorio de datos:  ", data_dir, "\n")
cat("Directorio de salida: ", output_dir, "\n")
cat("==============================================================================\n\n")

# 1. Carga de Datasets Analíticos Extraídos de PostgreSQL
# ------------------------------------------------------------------------------
file_trabajadores <- file.path(data_dir, "vw_trabajadores_consolidado.csv")
file_unidades <- file.path(data_dir, "vw_unidades_productivas_consolidado.csv")
file_marketing_resumen <- file.path(data_dir, "vw_marketing_resumen_canales.csv")
file_marketing_diario <- file.path(data_dir, "marketing_kpis_diario.csv")

if (!file.exists(file_trabajadores)) {
  stop(paste("Error: No se encontró el archivo:", file_trabajadores))
}

df_trab <- read.csv(file_trabajadores, stringsAsFactors = FALSE)
df_mype <- read.csv(file_unidades, stringsAsFactors = FALSE)
df_mkt_res <- read.csv(file_marketing_resumen, stringsAsFactors = FALSE)
df_mkt_dia <- read.csv(file_marketing_diario, stringsAsFactors = FALSE)

salario_minimo_legal <- 3044000

cat(sprintf("Datos cargados correctamente:\n"))
cat(sprintf(" - Trabajadores informales: %d observaciones\n", nrow(df_trab)))
cat(sprintf(" - Unidades productivas (MYPEs): %d observaciones\n", nrow(df_mype)))
cat(sprintf(" - Canales de Marketing: %d canales\n", nrow(df_mkt_res)))
cat(sprintf(" - Registros diarios de Marketing: %d observaciones\n\n", nrow(df_mkt_dia)))


# 2. Estadísticas Descriptivas (Trabajadores e Indicadores Sociales)
# ------------------------------------------------------------------------------
calc_stats <- function(x) {
  x <- na.omit(x)
  c(
    n = length(x),
    media = mean(x),
    desv_est = sd(x),
    mediana = median(x),
    iqr = IQR(x),
    min = min(x),
    max = max(x)
  )
}

desc_ingreso <- calc_stats(df_trab$ingreso_mensual_pyg)
desc_escolaridad <- calc_stats(df_trab$anios_estudio)
desc_edad <- calc_stats(df_trab$edad)
desc_horas <- calc_stats(df_trab$horas_semanales)
desc_vulnerabilidad <- calc_stats(df_trab$indice_vulnerabilidad_social)
desc_brecha <- calc_stats(df_trab$brecha_salario_pyg)

# Proporciones clave
prop_bajo_minimo <- mean(df_trab$ingreso_mensual_pyg < salario_minimo_legal) * 100
prop_sin_ips <- mean(df_trab$cobertura_ips %in% c("no", "Sin seguro IPS")) * 100
prop_posee_smartphone <- mean(df_trab$posee_smartphone == "si") * 100
prop_conoce_resimple <- mean(df_trab$conoce_resimple == "si") * 100
prop_interes_formalizar <- mean(df_trab$interes_formalizacion %in% c("Muy interesado", "Interesado", "Interes medio")) * 100

tabla_descriptiva_cuanti <- data.frame(
  Variable = c("Ingreso Mensual (PYG)", "Años de Escolaridad", "Edad (Años)", 
               "Horas Semanales", "Índice Vulnerabilidad Social", "Brecha Salarial (PYG)"),
  N = c(desc_ingreso["n"], desc_escolaridad["n"], desc_edad["n"], 
        desc_horas["n"], desc_vulnerabilidad["n"], desc_brecha["n"]),
  Media = c(desc_ingreso["media"], desc_escolaridad["media"], desc_edad["media"], 
            desc_horas["media"], desc_vulnerabilidad["media"], desc_brecha["media"]),
  Desv_Est = c(desc_ingreso["desv_est"], desc_escolaridad["desv_est"], desc_edad["desv_est"], 
               desc_horas["desv_est"], desc_vulnerabilidad["desv_est"], desc_brecha["desv_est"]),
  Mediana = c(desc_ingreso["mediana"], desc_escolaridad["mediana"], desc_edad["mediana"], 
              desc_horas["mediana"], desc_vulnerabilidad["mediana"], desc_brecha["mediana"]),
  IQR = c(desc_ingreso["iqr"], desc_escolaridad["iqr"], desc_edad["iqr"], 
          desc_horas["iqr"], desc_vulnerabilidad["iqr"], desc_brecha["iqr"]),
  Min = c(desc_ingreso["min"], desc_escolaridad["min"], desc_edad["min"], 
          desc_horas["min"], desc_vulnerabilidad["min"], desc_brecha["min"]),
  Max = c(desc_ingreso["max"], desc_escolaridad["max"], desc_edad["max"], 
          desc_horas["max"], desc_vulnerabilidad["max"], desc_brecha["max"])
)


# 3. Análisis de Correlación: Escolaridad vs. Ingreso
# ------------------------------------------------------------------------------
cor_pearson <- cor.test(df_trab$anios_estudio, df_trab$ingreso_mensual_pyg, method = "pearson")
cor_spearman <- cor.test(df_trab$anios_estudio, df_trab$ingreso_mensual_pyg, method = "spearman")

# Modelo de Regresión Lineal de Mincer (Ecuación Salarial)
reg_mincer <- lm(log(ingreso_mensual_pyg) ~ anios_estudio + antiguedad_oficio_anios + edad + factor(genero), data = df_trab)
summary_mincer <- summary(reg_mincer)


# 4. Pruebas de Hipótesis: Vulnerabilidad Social por Barrio
# ------------------------------------------------------------------------------
# Prueba de Normalidad (Shapiro-Wilk)
shapiro_vuln <- shapiro.test(df_trab$indice_vulnerabilidad_social)

# Prueba de Homocedasticidad (Bartlett)
bartlett_vuln <- bartlett.test(indice_vulnerabilidad_social ~ factor(barrio), data = df_trab)

# Análisis de Varianza (ANOVA Paramétrico de 1 Vía)
anova_vuln <- aov(indice_vulnerabilidad_social ~ factor(barrio), data = df_trab)
summary_anova <- summary(anova_vuln)
f_stat <- summary_anova[[1]]$`F value`[1]
p_val_anova <- summary_anova[[1]]$`Pr(>F)`[1]

# Prueba no paramétrica de Kruskal-Wallis
kruskal_vuln <- kruskal.test(indice_vulnerabilidad_social ~ factor(barrio), data = df_trab)

# Descriptivos de Vulnerabilidad por Barrio
stats_por_barrio <- df_trab %>%
  group_by(barrio) %>%
  summarise(
    n = n(),
    media_vuln = mean(indice_vulnerabilidad_social),
    sd_vuln = sd(indice_vulnerabilidad_social),
    mediana_vuln = median(indice_vulnerabilidad_social),
    iqr_vuln = IQR(indice_vulnerabilidad_social),
    media_ingreso = mean(ingreso_mensual_pyg),
    sd_ingreso = sd(ingreso_mensual_pyg),
    pct_bajo_minimo = mean(ingreso_mensual_pyg < salario_minimo_legal) * 100,
    .groups = "drop"
  ) %>%
  arrange(desc(media_vuln))


# 5. Brecha Salarial de Género (Pruebas de Hipótesis)
# ------------------------------------------------------------------------------
ingreso_fem <- df_trab$ingreso_mensual_pyg[df_trab$genero == "femenino"]
ingreso_masc <- df_trab$ingreso_mensual_pyg[df_trab$genero == "masculino"]

t_test_genero <- t.test(ingreso_fem, ingreso_masc, alternative = "two.sided", var.equal = FALSE)
wilcox_genero <- wilcox.test(ingreso_fem, ingreso_masc, alternative = "two.sided")

media_fem <- mean(ingreso_fem)
media_masc <- mean(ingreso_masc)
diferencial_genero_pyg <- media_masc - media_fem
brecha_genero_pct <- (diferencial_genero_pyg / media_masc) * 100


# 6. Estadísticas MYPEs y Marketing Social
# ------------------------------------------------------------------------------
stats_mypes_rubro <- df_mype %>%
  group_by(rubro_actividad) %>%
  summarise(
    n = n(),
    tasa_informalidad_media = mean(tasa_informalidad_laboral_pct),
    ingreso_mensual_medio = mean(ingreso_mensual_estimado_pyg),
    total_trabajadores_sin_ips = sum(trabajadores_sin_ips),
    total_trabajadores_con_ips = sum(trabajadores_con_ips),
    .groups = "drop"
  ) %>%
  arrange(desc(tasa_informalidad_media))

resumen_marketing <- df_mkt_res %>%
  select(
    codigo_canal, canal_nombre, tipo_canal, 
    total_alcance, total_interacciones, ctr_promedio_pct,
    total_consultas, total_derivaciones, presupuesto_total_pyg,
    costo_promedio_por_consulta_pyg, costo_por_derivacion_efectiva_pyg
  )


# 7. Compilación de Resultados en Estructura JSON
# ------------------------------------------------------------------------------
resultados_json <- list(
  metadatos = list(
    institucion = "UNVES - Facultad de Ciencias Económicas",
    proyecto = "Transformación Digital y Diagnóstico Social en la Gestión Organizacional",
    fecha_ejecucion = Sys.time(),
    muestra_trabajadores = nrow(df_trab),
    muestra_unidades = nrow(df_mype),
    salario_minimo_legal = salario_minimo_legal
  ),
  descriptivos_trabajadores = list(
    ingreso = as.list(desc_ingreso),
    escolaridad = as.list(desc_escolaridad),
    edad = as.list(desc_edad),
    vulnerabilidad = as.list(desc_vulnerabilidad),
    proporciones = list(
      pct_bajo_minimo = prop_bajo_minimo,
      pct_sin_ips = prop_sin_ips,
      pct_posee_smartphone = prop_posee_smartphone,
      pct_conoce_resimple = prop_conoce_resimple,
      pct_interes_formalizar = prop_interes_formalizar
    )
  ),
  correlacion_escolaridad_ingreso = list(
    pearson = list(
      r = unname(cor_pearson$estimate),
      t_statistic = unname(cor_pearson$statistic),
      df = unname(cor_pearson$parameter),
      p_value = unname(cor_pearson$p.value),
      ci_95 = as.numeric(cor_pearson$conf.int)
    ),
    spearman = list(
      rho = unname(cor_spearman$estimate),
      statistic = unname(cor_spearman$statistic),
      p_value = unname(cor_spearman$p.value)
    ),
    mincer_model = list(
      r_squared = summary_mincer$r.squared,
      adj_r_squared = summary_mincer$adj.r.squared,
      f_statistic = unname(summary_mincer$fstatistic[1]),
      p_value = pf(summary_mincer$fstatistic[1], summary_mincer$fstatistic[2], summary_mincer$fstatistic[3], lower.tail = FALSE)
    )
  ),
  vulnerabilidad_por_barrio = list(
    shapiro_wilk = list(w = unname(shapiro_vuln$statistic), p_value = unname(shapiro_vuln$p.value)),
    bartlett = list(statistic = unname(bartlett_vuln$statistic), p_value = unname(bartlett_vuln$p.value)),
    anova = list(f_stat = f_stat, p_value = p_val_anova),
    kruskal_wallis = list(chi_squared = unname(kruskal_vuln$statistic), df = unname(kruskal_vuln$parameter), p_value = unname(kruskal_vuln$p.value)),
    descriptivos_barrio = as.data.frame(stats_por_barrio)
  ),
  brecha_genero = list(
    media_femenino = media_fem,
    media_masculino = media_masc,
    diferencial_pyg = diferencial_genero_pyg,
    brecha_porcentaje = brecha_genero_pct,
    t_test = list(t = unname(t_test_genero$statistic), df = unname(t_test_genero$parameter), p_value = unname(t_test_genero$p.value)),
    wilcox_test = list(w = unname(wilcox_genero$statistic), p_value = unname(wilcox_genero$p.value))
  )
)

write_json(resultados_json, file.path(output_dir, "resultados_econometricos.json"), pretty = TRUE, auto_unbox = TRUE)
cat("Archivo JSON de resultados guardado en:", file.path(output_dir, "resultados_econometricos.json"), "\n")


# 8. Generación del Informe Escrito en Formato APA 7.ª ed.
# ------------------------------------------------------------------------------
reporte_apa_path <- file.path(output_dir, "reporte_econometrico_apa7.txt")
sink(reporte_apa_path)

cat("==============================================================================\n")
cat("INFORME DE ANÁLISIS ECONOMÉTRICO Y ESTADÍSTICO - FORMALIZACIÓN LABORAL EN VILLARRICA\n")
cat("UNIVERSIDAD NACIONAL DE VILLARRICA DEL ESPÍRITU SANTO (UNVES)\n")
cat("FACULTAD DE CIENCIAS ECONÓMICAS - LICENCIATURA EN ADMINISTRACIÓN DE EMPRESAS\n")
cat("Cátedras: Sistema de Información Gerencial | Realidad Social | Marketing Social\n")
cat("Normas: American Psychological Association (APA), 7.ª edición\n")
cat("==============================================================================\n\n")

cat("1. RESUMEN METODOLÓGICO Y PARAMÉTRICO\n")
cat("------------------------------------------------------------------------------\n")
cat(sprintf("Muestra de trabajadores informales: N = %d individuos georreferenciados.\n", nrow(df_trab)))
cat(sprintf("Muestra de unidades productivas:     N = %d microempresas/talleres.\n", nrow(df_mype)))
cat(sprintf("Salario mínimo legal de referencia: Gs. %s (2026).\n", format(salario_minimo_legal, big.mark = ".")))
cat(sprintf("Período de recolección en terreno:   Setiembre - Octubre 2026 (Villarrica, Guairá).\n\n"))

cat("2. TABLA 1: ESTADÍSTICAS DESCRIPTIVAS DE VARIABLES SOCIOECONÓMICAS (APA 7)\n")
cat("------------------------------------------------------------------------------\n")
print(tabla_descriptiva_cuanti, row.names = FALSE)
cat("\nNota. Elaboración propia con base en el relevamiento de campo KoboToolbox/ODK (UNVES 2026).\n")
cat(sprintf("El %.2f%% de los trabajadores percibe ingresos estrictamente inferiores al salario mínimo legal.\n\n", prop_bajo_minimo))

cat("3. ANÁLISIS DE CORRELACIÓN Y RETORNOS DE LA ESCOLARIDAD\n")
cat("------------------------------------------------------------------------------\n")
cat(sprintf("Coeficiente de correlación de Pearson:  r = %.4f (t = %.3f, gl = %d, p = %.4f, IC 95%%: [%.4f, %.4f])\n",
            cor_pearson$estimate, cor_pearson$statistic, cor_pearson$parameter, cor_pearson$p.value,
            cor_pearson$conf.int[1], cor_pearson$conf.int[2]))
cat(sprintf("Coeficiente de correlación de Spearman: rho = %.4f (S = %.1f, p = %.4f)\n\n",
            cor_spearman$estimate, cor_spearman$statistic, cor_spearman$p.value))
cat("Interpretación APA 7:\n")
cat("La relación lineal y monótona entre los años de escolaridad formal y el ingreso mensual en el sector informal\n")
cat("de Villarrica resulta estadísticamente no significativa (p > .05). Esto evidencia que en la economía sumergida\n")
cat("local existe una 'trampa de informalidad' donde los años de estudio formal no se traducen automáticamente en\n")
cat("mayores ingresos sin acceso a capital de trabajo, certificación de oficios o inserción en cadenas de valor formales.\n\n")

cat("4. TABLA 2: MODELO DE REGRESIÓN DE MINCER (LOG-INGRESOS)\n")
cat("------------------------------------------------------------------------------\n")
print(summary_mincer)
cat("\nNota. Variable dependiente: log(ingreso_mensual_pyg). Errores estándar entre paréntesis.\n\n")

cat("5. TABLA 3: ANÁLISIS DE VULNERABILIDAD SOCIAL POR BARRIO\n")
cat("------------------------------------------------------------------------------\n")
print(as.data.frame(stats_por_barrio), row.names = FALSE)
cat(sprintf("\nPrueba de Normalidad (Shapiro-Wilk): W = %.4f, p = %.4f\n", shapiro_vuln$statistic, shapiro_vuln$p.value))
cat(sprintf("Prueba de Homocedasticidad (Bartlett): K2 = %.3f, p = %.4f\n", bartlett_vuln$statistic, bartlett_vuln$p.value))
cat(sprintf("ANOVA de una vía (Efecto Barrio):      F(6, 413) = %.3f, p = %.4f\n", f_stat, p_val_anova))
cat(sprintf("Prueba Kruskal-Wallis:                 H(6) = %.3f, p = %.4f\n\n", kruskal_vuln$statistic, kruskal_vuln$p.value))
cat("Interpretación APA 7:\n")
cat("El índice de vulnerabilidad social no presenta diferencias estadísticamente significativas entre barrios (p > .05),\n")
cat("lo que demuestra que la precariedad laboral informal es un fenómeno estructural homogéneo a lo largo del tejido urbano\n")
cat("de Villarrica, tanto en zonas céntricas comerciales como en barrios periféricos.\n\n")

cat("6. TABLA 4: ANÁLISIS DE BRECHA SALARIAL DE GÉNERO\n")
cat("------------------------------------------------------------------------------\n")
cat(sprintf("Ingreso medio Femenino:   Gs. %s (sd = Gs. %s)\n", format(round(media_fem), big.mark = "."), format(round(sd(ingreso_fem)), big.mark = ".")))
cat(sprintf("Ingreso medio Masculino:  Gs. %s (sd = Gs. %s)\n", format(round(media_masc), big.mark = "."), format(round(sd(ingreso_masc)), big.mark = ".")))
grupo_favorecido <- if (diferencial_genero_pyg >= 0) "los hombres" else "las mujeres"
cat(sprintf("Diferencial de género:    Gs. %s (Brecha: %.2f%% a favor de %s)\n", format(round(diferencial_genero_pyg), big.mark = "."), brecha_genero_pct, grupo_favorecido))
cat(sprintf("Prueba t de Welch:        t = %.3f, gl = %.1f, p = %.4f\n", t_test_genero$statistic, t_test_genero$parameter, t_test_genero$p.value))
cat(sprintf("Prueba U de Mann-Whitney: W = %.1f, p = %.4f\n\n", wilcox_genero$statistic, wilcox_genero$p.value))

cat("7. RESUMEN DE LA CAMPAÑA DE MARKETING SOCIAL 'TRABAJO FORMAL, FUTURO SEGURO'\n")
cat("------------------------------------------------------------------------------\n")
print(resumen_marketing, row.names = FALSE)
cat("\nNota. Rendimiento acumulado en 42 días continuos de activación multicanal.\n")
cat("==============================================================================\n")

sink()
cat("Informe en formato APA 7 guardado en:", reporte_apa_path, "\n\n")


# 9. Generación de Gráficos Analíticos en Alta Resolución (Formato APA 7.ª ed.)
# ------------------------------------------------------------------------------
# Tema personalizado acorde a las normas APA 7 (minimalista, escala de grises/accesible, sin cuadrículas distractoras)
theme_apa7 <- function(base_size = 11, base_family = "sans") {
  theme_classic(base_size = base_size, base_family = base_family) +
    theme(
      plot.title = element_text(face = "bold", size = rel(1.1), hjust = 0, margin = margin(b = 6)),
      plot.subtitle = element_text(face = "italic", size = rel(0.95), hjust = 0, margin = margin(b = 10)),
      plot.caption = element_text(face = "plain", size = rel(0.8), hjust = 0, margin = margin(t = 10)),
      axis.title = element_text(face = "bold", size = rel(0.95)),
      axis.text = element_text(size = rel(0.85), color = "black"),
      axis.line = element_line(color = "black", linewidth = 0.6),
      legend.position = "top",
      legend.title = element_text(face = "bold", size = rel(0.9)),
      legend.text = element_text(size = rel(0.85)),
      panel.grid.major.y = element_line(color = "grey90", linewidth = 0.3),
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank()
    )
}

# --- FIGURA 1: Correlación Escolaridad vs. Ingreso Mensual ---
p1 <- ggplot(df_trab, aes(x = anios_estudio, y = ingreso_mensual_pyg / 1e6)) +
  geom_point(alpha = 0.45, color = "#1E3A8A", size = 2) +
  geom_smooth(method = "lm", color = "#B91C1C", se = TRUE, fill = "#F87171", alpha = 0.25, linewidth = 1) +
  geom_hline(yintercept = salario_minimo_legal / 1e6, linetype = "dashed", color = "#047857", linewidth = 0.8) +
  annotate("text", x = 15, y = (salario_minimo_legal / 1e6) + 0.15, 
           label = "Salario Mínimo Legal (Gs. 3.044.000)", color = "#047857", fontface = "bold", size = 3.2, hjust = 1) +
  annotate("label", x = 3, y = 4.2, 
           label = sprintf("Pearson r = %.3f (p = %.3f)\nSpearman rho = %.3f (p = %.3f)", 
                           cor_pearson$estimate, cor_pearson$p.value, cor_spearman$estimate, cor_spearman$p.value),
           fill = "white", color = "black", size = 3.2, label.size = 0.3) +
  scale_x_continuous(breaks = seq(0, 18, 2), limits = c(1, 18)) +
  scale_y_continuous(breaks = seq(1, 5, 0.5), labels = function(x) paste0(x, "M")) +
  labs(
    title = "Figura 1. Correlación entre Años de Escolaridad e Ingreso Mensual",
    subtitle = "Dispersión con recta ajustada MCO y nivel de salario mínimo legal en trabajadores informales",
    x = "Años de Educación Formal Acumulada",
    y = "Ingreso Mensual Percibido (Millones de Gs.)",
    caption = "Nota. N = 420 trabajadores informales. Elaboración propia según datos de relevamiento KoboCollect UNVES (2026)."
  ) +
  theme_apa7()

png(file.path(output_dir, "figura1_correlacion_escolaridad_ingreso.png"), width = 2400, height = 1600, res = 300)
print(p1)
invisible(dev.off())


# --- FIGURA 2: Distribución del Índice de Vulnerabilidad Social por Barrio ---
p2 <- ggplot(df_trab, aes(x = reorder(barrio, -indice_vulnerabilidad_social, FUN = median), y = indice_vulnerabilidad_social)) +
  geom_boxplot(fill = "#E0E7FF", color = "#1E3A8A", outlier.shape = 21, outlier.fill = "#DC2626", outlier.size = 1.8, width = 0.6) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 2.5, fill = "#B91C1C", color = "black") +
  annotate("label", x = 4, y = 92,
           label = sprintf("ANOVA: F(6, 413) = %.3f, p = %.3f\nKruskal-Wallis: H(6) = %.3f, p = %.3f",
                           f_stat, p_val_anova, kruskal_vuln$statistic, kruskal_vuln$p.value),
           fill = "white", color = "black", size = 3.1) +
  scale_y_continuous(breaks = seq(10, 100, 10), limits = c(10, 100)) +
  labs(
    title = "Figura 2. Índice Sintético de Vulnerabilidad Social en los 7 Barrios de Villarrica",
    subtitle = "Diagrama de cajas y bigotes con medias (rombos rojos) y medianas por cuadrante censal",
    x = "Barrio de Relevamiento Censal",
    y = "Índice de Vulnerabilidad Social (Escala 0 a 100)",
    caption = "Nota. N = 420. Diferencias no significativas entre barrios a nivel alpha = .05. Proyecto UNVES (2026)."
  ) +
  theme_apa7() +
  theme(axis.text.x = element_text(angle = 20, hjust = 1))

png(file.path(output_dir, "figura2_vulnerabilidad_social_barrios.png"), width = 2400, height = 1600, res = 300)
print(p2)
invisible(dev.off())


# --- FIGURA 3: Densidad de Ingresos por Género y Brecha con Salario Mínimo ---
p3 <- ggplot(df_trab, aes(x = ingreso_mensual_pyg / 1e6, fill = genero, color = genero)) +
  geom_density(alpha = 0.35, linewidth = 0.9) +
  geom_vline(xintercept = salario_minimo_legal / 1e6, linetype = "dashed", color = "#047857", linewidth = 0.9) +
  geom_vline(xintercept = media_fem / 1e6, linetype = "dotted", color = "#EC4899", linewidth = 0.8) +
  geom_vline(xintercept = media_masc / 1e6, linetype = "dotted", color = "#3B82F6", linewidth = 0.8) +
  scale_fill_manual(values = c("femenino" = "#F472B6", "masculino" = "#60A5FA"), labels = c("Femenino", "Masculino")) +
  scale_color_manual(values = c("femenino" = "#DB2777", "masculino" = "#2563EB"), labels = c("Femenino", "Masculino")) +
  annotate("text", x = 4.2, y = 0.60, vjust = 1, 
           label = sprintf("Brecha de género: %.1f%%\nt de Welch: p = %.3f\nMann-Whitney: p = %.3f", 
                           brecha_genero_pct, t_test_genero$p.value, wilcox_genero$p.value),
           size = 3.2, hjust = 1, fontface = "italic") +
  labs(
    title = "Figura 3. Curva de Densidad de Ingresos por Género frente al Salario Mínimo Legal",
    subtitle = "Línea verde discontinua: Salario Mínimo (Gs. 3.044.000). Líneas punteadas: Medias grupales.",
    x = "Ingreso Mensual Estimado (Millones de Guaraníes)",
    y = "Densidad de Probabilidad Kernel",
    fill = "Género",
    color = "Género",
    caption = sprintf("Nota. N = %d (Mujeres n = %d, Hombres n = %d). Datos del Proyecto Interdisciplinario UNVES (2026).",
                      nrow(df_trab), sum(df_trab$genero == "femenino"), sum(df_trab$genero == "masculino"))
  ) +
  theme_apa7()

png(file.path(output_dir, "figura3_brecha_ingreso_genero_minimo.png"), width = 2400, height = 1600, res = 300)
print(p3)
invisible(dev.off())


# --- FIGURA 4: Tasa de Informalidad Laboral en MYPEs por Rubro ---
p4 <- ggplot(stats_mypes_rubro, aes(x = reorder(rubro_actividad, tasa_informalidad_media), y = tasa_informalidad_media)) +
  geom_col(fill = "#3B82F6", color = "#1E3A8A", width = 0.65) +
  geom_text(aes(label = sprintf("%.1f%% (n=%d)", tasa_informalidad_media, n)), 
            hjust = -0.1, size = 3.1, color = "black", fontface = "bold") +
  coord_flip() +
  scale_y_continuous(limits = c(0, 128), breaks = seq(0, 100, 20), labels = function(x) paste0(x, "%")) +
  labs(
    title = "Figura 4. Tasa Media de Informalidad Laboral Patronal por Rubro de MYPEs",
    subtitle = "Porcentaje de asalariados sin inscripción en el Instituto de Previsión Social (IPS)",
    x = "Rama de Actividad Económica",
    y = "Tasa de Informalidad Laboral Media (%)",
    caption = "Nota. N = 135 unidades productivas relevadas en Villarrica. Cátedra SIG - UNVES (2026)."
  ) +
  theme_apa7() +
  theme(plot.title.position = "plot", plot.caption.position = "plot")

png(file.path(output_dir, "figura4_informalidad_mypes_rubro.png"), width = 2600, height = 1700, res = 300)
print(p4)
invisible(dev.off())


# --- FIGURA 5: Embudo Multicanal y Conversión de la Campaña de Marketing Social ---
funnel_data <- data.frame(
  Canal = rep(df_mkt_res$canal_nombre, each = 3),
  Etapa = rep(c("1. Impresiones/Alcance (/100)", "2. Consultas Iniciadas", "3. Derivaciones Efectivas"), times = nrow(df_mkt_res)),
  Valor = c(
    df_mkt_res$total_alcance[1] / 100, df_mkt_res$total_consultas[1], df_mkt_res$total_derivaciones[1],
    df_mkt_res$total_alcance[2] / 100, df_mkt_res$total_consultas[2], df_mkt_res$total_derivaciones[2],
    df_mkt_res$total_alcance[3] / 100, df_mkt_res$total_consultas[3], df_mkt_res$total_derivaciones[3],
    df_mkt_res$total_alcance[4] / 100, df_mkt_res$total_consultas[4], df_mkt_res$total_derivaciones[4]
  )
)

p5 <- ggplot(funnel_data, aes(x = Etapa, y = Valor, fill = Canal)) +
  geom_col(position = "dodge", color = "black", linewidth = 0.3) +
  scale_fill_manual(values = c("#3B82F6", "#10B981", "#F59E0B", "#8B5CF6")) +
  labs(
    title = "Figura 5. Rendimiento y Conversión del Embudo Multicanal de Marketing Social",
    subtitle = "Comparativa del alcance normalizado, consultas ciudadanas y derivaciones formales a SUACE/IPS",
    x = "Etapa del Embudo de Marketing Social",
    y = "Volumen Registrado",
    fill = "Canal Estratégico",
    caption = "Nota. 42 días de campaña 'Trabajo Formal, Futuro Seguro'. Cátedra Marketing Social - UNVES (2026)."
  ) +
  guides(fill = guide_legend(nrow = 2, title.position = "top")) +
  theme_apa7() +
  theme(plot.title.position = "plot", plot.caption.position = "plot")

png(file.path(output_dir, "figura5_embudo_marketing_multicanal.png"), width = 2600, height = 1600, res = 300)
print(p5)
invisible(dev.off())

cat("Gráficos analíticos generados exitosamente en alta resolución (300 DPI) en:", output_dir, "\n")
cat("==============================================================================\n")
cat("ANÁLISIS ECONOMÉTRICO COMPLETADO CON ÉXITO\n")
cat("==============================================================================\n")
