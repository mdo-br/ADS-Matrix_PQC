# Análise Estatística do Experimento Matrix

## Visão Geral

Este documento apresenta o pipeline estatístico utilizado no experimento de avaliação de impacto da criptografia pós-quântica (Matrix-Like), detalhando as etapas de análise durante a coleta dos dados e os testes estatísticos realizados posteriormente.

---

## 1. Análise Estatística Durante o Experimento

- **Detecção de Outliers:**  
  Utilização do método IQR (Intervalo Interquartil) para identificar outliers moderados e extremos. Outliers extremos são removidos da amostra para garantir robustez dos resultados.

- **Verificação de Normalidade:**  
  Cálculo de assimetria (skewness) e curtose (kurtosis) para cada métrica. Dados com |skewness| < 2.0 e |kurtosis| < 7.0 são considerados normalmente distribuídos.

- **Estatísticas Adaptativas:**  
  - Dados normais: média, desvio padrão, IC95 (intervalo de confiança de 95% via z-score).
  - Dados não-normais: mediana, MAD (Median Absolute Deviation) escalado, IC95 via percentis.

- **Logging Detalhado:**  
  Todas as decisões sobre tratamento de outliers, normalidade e escolha de estatísticas são registradas para garantir transparência e reprodutibilidade.

- **Resultados:**  
  Os resultados são salvos em arquivos CSV, incluindo métricas de desempenho, estatísticas descritivas, flags de normalidade, contadores de outliers e informações de amostra.

---

## 2. Testes Estatísticos Realizados Após o Experimento

Após a coleta dos dados, são realizados diversos testes estatísticos utilizando Python (`pandas`, `scipy`, `statsmodels`):

- **Teste t para Diferença entre Protocolos:**  
  Comparação entre Olm-Clássico e Olm-Híbrido para tempo de acordo de chaves (KEM), incluindo teste bilateral, unilateral e cálculo do tamanho do efeito (Cohen's d).

- **ANOVA (One-Way):**  
  - Diferenças entre cenários de uso (SmallChat, MediumGroup, etc.).
  - Diferenças entre padrões de tráfego (Constant, Burst, etc.).
  - Diferenças entre algoritmos de cifra (AES-GCM, ChaCha20, Megolm-Like).

- **Testes Pareados:**  
  Testes t entre pares de algoritmos de cifra para identificar diferenças específicas.

- **Teste de Equivalência:**  
  Avaliação se algoritmos de cifra apresentam desempenho estatisticamente equivalente.

- **Testes de Correlação:**  
  - Correlação entre número de mensagens e latência KEM.
  - Correlação entre número de rotações e largura de banda.

- **Interpretação dos Resultados:**  
  Para cada teste, são reportados valores de estatística, p-valor, decisão sobre hipótese nula e conclusões práticas.

---

## 3. Importância da Abordagem

A aplicação rigorosa de métodos estatísticos garante que as conclusões do experimento sejam confiáveis, reprodutíveis e relevantes para decisões técnicas e científicas. O pipeline estatístico permite identificar diferenças significativas, quantificar o impacto de algoritmos pós-quânticos e orientar futuras implementações em sistemas de comunicação