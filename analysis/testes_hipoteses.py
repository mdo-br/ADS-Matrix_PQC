#!/usr/bin/env python3
"""
Testes de Hipóteses Estatísticas para Experimento Matrix
Análise dos resultados do experimento criptográfico
Atualizado para resultados_normality_check_20250716_202824.csv
"""

import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import ttest_ind, f_oneway, shapiro, levene, mannwhitneyu
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
class DualWriter:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log = open(file_path, "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()


def load_data():
    """Carregar dados do experimento"""
    results_dir = Path("../results")
    pattern = "resultados_normality_check_*.csv"
    
    arquivos = list(results_dir.glob(pattern))
    if not arquivos:
        print("Nenhum arquivo de resultados de normalidade encontrado!")
        return None, None
    
    # Pega o arquivo mais recente
    arquivo_mais_recente = max(arquivos, key=lambda x: x.stat().st_mtime)
    print(f"Carregando dados de: {arquivo_mais_recente}")
    
    # Extrai timestamp do nome do arquivo
    filename = arquivo_mais_recente.name
    timestamp_part = filename.replace('resultados_normality_check_', '').replace('.csv', '')
    
    df = pd.read_csv(arquivo_mais_recente)
    return df

def test_protocol_difference(df):
    """Teste t para diferença entre protocolos"""
    print("="*60)
    print("TESTE 1: DIFERENÇA ENTRE PROTOCOLOS")
    print("="*60)
    
    classico = df[df['acordo'] == 'Olm-Clássico']['kem_ms_mean']
    hibrido = df[df['acordo'] == 'Olm-Híbrido']['kem_ms_mean']
    
    print(f"Olm-Clássico: n={len(classico)}, μ={classico.mean():.4f}, σ={classico.std():.4f}")
    print(f"Olm-Híbrido:  n={len(hibrido)}, μ={hibrido.mean():.4f}, σ={hibrido.std():.4f}")
    
    # Teste t bilateral
    t_stat, p_value = ttest_ind(hibrido, classico, alternative='two-sided')
    print(f"\nTeste t bilateral:")
    print(f"  H₀: μ_híbrido = μ_clássico")
    print(f"  H₁: μ_híbrido ≠ μ_clássico")
    print(f"  t = {t_stat:.4f}, p = {p_value:.6f}")
    
    # Teste t unilateral
    t_stat_uni, p_value_uni = ttest_ind(hibrido, classico, alternative='greater')
    print(f"\nTeste t unilateral:")
    print(f"  H₀: μ_híbrido ≤ μ_clássico")
    print(f"  H₁: μ_híbrido > μ_clássico")
    print(f"  t = {t_stat_uni:.4f}, p = {p_value_uni:.6f}")
    
    alpha = 0.05
    if p_value_uni < alpha:
        print(f"  Resultado: Rejeitar H₀ (p < {alpha})")
        print(f"  Conclusão: Protocolo híbrido é significativamente mais lento")
    else:
        print(f"  Resultado: Não rejeitar H₀ (p ≥ {alpha})")
    
    # Tamanho do efeito (Cohen's d)
    pooled_std = np.sqrt(((len(classico)-1)*classico.var() + (len(hibrido)-1)*hibrido.var()) / (len(classico)+len(hibrido)-2))
    cohens_d = (hibrido.mean() - classico.mean()) / pooled_std
    print(f"  Cohen's d: {cohens_d:.4f}")
    
    # Teste de largura de banda
    print(f"\n--- Largura de Banda ---")
    bw_classico = df[df['acordo'] == 'Olm-Clássico']['kem_bw_mean']
    bw_hibrido = df[df['acordo'] == 'Olm-Híbrido']['kem_bw_mean']
    overhead_bw = ((bw_hibrido.mean() - bw_classico.mean()) / bw_classico.mean()) * 100
    print(f"  Overhead de largura de banda: {overhead_bw:.1f}%")
    
    return p_value_uni, cohens_d

def test_scenario_anova(df):
    """ANOVA para diferenças entre cenários"""
    print("\n" + "="*60)
    print("TESTE 2: ANOVA - DIFERENÇAS ENTRE CENÁRIOS")
    print("="*60)
    
    cenarios = df['cenario'].unique()
    grupos = [df[df['cenario'] == c]['kem_ms_mean'] for c in cenarios]
    
    print("Estatísticas por cenário:")
    for i, cenario in enumerate(cenarios):
        grupo = grupos[i]
        print(f"  {cenario}: n={len(grupo)}, μ={grupo.mean():.4f}, σ={grupo.std():.4f}")
    
    f_stat, p_value = f_oneway(*grupos)
    print(f"\nANOVA One-Way:")
    print(f"  H₀: Todas as médias são iguais")
    print(f"  H₁: Pelo menos uma média é diferente")
    print(f"  F = {f_stat:.4f}, p = {p_value:.6f}")
    
    alpha = 0.05
    if p_value < alpha:
        print(f"  Resultado: Rejeitar H₀ (p < {alpha})")
        print(f"  Conclusão: Há diferença significativa entre cenários")
    else:
        print(f"  Resultado: Não rejeitar H₀ (p ≥ {alpha})")
    
    return p_value

def test_traffic_pattern_anova(df):
    """ANOVA para padrões de tráfego"""
    print("\n" + "="*60)
    print("TESTE 3: ANOVA - PADRÕES DE TRÁFEGO")
    print("="*60)
    
    padroes = df['padrao_trafego'].unique()
    grupos = [df[df['padrao_trafego'] == p]['cipher_ms_mean'] for p in padroes]
    
    print("Estatísticas por padrão de tráfego:")
    for i, padrao in enumerate(padroes):
        grupo = grupos[i]
        print(f"  {padrao}: n={len(grupo)}, μ={grupo.mean():.2f}, σ={grupo.std():.2f}")
    
    f_stat, p_value = f_oneway(*grupos)
    print(f"\nANOVA One-Way:")
    print(f"  H₀: Todos os padrões têm a mesma média")
    print(f"  H₁: Pelo menos um padrão é diferente")
    print(f"  F = {f_stat:.4f}, p = {p_value:.6f}")
    
    alpha = 0.05
    if p_value < alpha:
        print(f"  Resultado: Rejeitar H₀ (p < {alpha})")
        print(f"  Conclusão: Padrões de tráfego têm impacto significativo")
    else:
        print(f"  Resultado: Não rejeitar H₀ (p ≥ {alpha})")
    
    return p_value

def test_cipher_equivalence(df):
    """Teste de equivalência para algoritmos de cifra"""
    print("\n" + "="*60)
    print("TESTE 4: EQUIVALÊNCIA DE ALGORITMOS DE CIFRA")
    print("="*60)
    
    cifras = df['cifra'].unique()
    grupos = [df[df['cifra'] == c]['cipher_ms_mean'] for c in cifras]
    
    print("Estatísticas por algoritmo de cifra:")
    for i, cifra in enumerate(cifras):
        grupo = grupos[i]
        print(f"  {cifra}: n={len(grupo)}, μ={grupo.mean():.2f}, σ={grupo.std():.2f}")
    
    f_stat, p_value = f_oneway(*grupos)
    print(f"\nANOVA One-Way:")
    print(f"  F = {f_stat:.4f}, p = {p_value:.6f}")
    
    print(f"\nComparações pareadas (Teste t):")
    for i in range(len(cifras)):
        for j in range(i+1, len(cifras)):
            t_stat, p_val = ttest_ind(grupos[i], grupos[j])
            diff_perc = abs((grupos[i].mean() - grupos[j].mean()) / grupos[i].mean()) * 100
            print(f"  {cifras[i]} vs {cifras[j]}: t={t_stat:.4f}, p={p_val:.4f}, diff={diff_perc:.2f}%")
    
    return p_value

def test_correlation(df):
    """Teste de correlação"""
    print("\n" + "="*60)
    print("TESTE 5: CORRELAÇÕES")
    print("="*60)
    
    # Correlação entre número de mensagens e latência KEM
    if 'num_msgs' in df.columns:
        corr, p_value = stats.pearsonr(df['num_msgs'], df['kem_ms_mean'])
        print(f"Correlação: num_msgs vs kem_ms_mean")
        print(f"  r = {corr:.4f}, p = {p_value:.6f}")
    else:
        print("Coluna 'num_msgs' não encontrada.")
    
    # Correlação entre rotações e largura de banda
    corr2, p_value2 = stats.pearsonr(df['rotacoes'], df['kem_bw_mean'])
    print(f"\nCorrelação: rotacoes vs kem_bw_mean")
    print(f"  r = {corr2:.4f}, p = {p_value2:.6f}")

def main():
    """Executar todos os testes"""
    # Redireciona sys.stdout para DualWriter
    report_path = Path(__file__).parent / "report_testes_hipoteses.txt"
    sys.stdout = DualWriter(report_path)

    print("ANÁLISE ESTATÍSTICA - EXPERIMENTO MATRIX")
    print("="*60)
    
    df = load_data()
    print(f"Dados carregados: {len(df)} observações")
    
    test_protocol_difference(df)
    test_scenario_anova(df)
    test_traffic_pattern_anova(df)
    test_cipher_equivalence(df)
    test_correlation(df)
    
    print("\n" + "="*60)
    print("ANÁLISE CONCLUÍDA")
    print("="*60)
    # Restaura sys.stdout
    sys.stdout.log.close()
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    main()