#!/usr/bin/env python3
"""
=============================================================================================
GERADOR DE GRÁFICOS - EXPERIMENTO COM ANÁLISE DE NORMALIDADE E OUTLIERS
=============================================================================================

Este script gera gráficos específicos para análise dos resultados do experimento
com detecção de outliers, verificação de normalidade e análise estatística avançada.

Novos gráficos incluem:
- Análise de normalidade por métrica
- Distribuição de outliers
- Comparação de estatísticas paramétricas vs robustas
- Qualidade das amostras após limpeza
- Análise estatística avançada

Autor: Marcos Dantas Ortiz
Data: Julho de 2025
=============================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import sys
warnings.filterwarnings('ignore')

# Configuração de estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def carregar_dados():
    """Carrega os dados do experimento com análise de normalidade"""
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
    
    # Calcula métricas adicionais
    df['throughput'] = df['num_msgs'] / (df['cipher_ms_mean'] / 1000)
    df['latencia_total'] = df['kem_ms_mean'] + df['cipher_ms_mean']
    df['eficiencia'] = df['throughput'] / df['latencia_total']
    
    # Calcula porcentagem de outliers
    df['kem_outliers_pct'] = (df['kem_outliers'] / (df['kem_sample_size'] + df['kem_outliers'])) * 100
    df['cipher_outliers_pct'] = (df['cipher_outliers'] / (df['cipher_sample_size'] + df['cipher_outliers'])) * 100
    df['kem_bw_outliers_pct'] = (df['kem_bw_outliers'] / (df['kem_bw_sample_size'] + df['kem_bw_outliers'])) * 100
    df['msg_bw_outliers_pct'] = (df['msg_bw_outliers'] / (df['msg_bw_sample_size'] + df['msg_bw_outliers'])) * 100
    
    return df, timestamp_part

def grafico_analise_normalidade(df, plots_subdir):
    """Gráfico de análise de normalidade por métrica"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análise de Normalidade das Métricas', fontsize=16, fontweight='bold')
    
    # Contagem de normalidade por métrica
    metricas = ['kem_normal', 'cipher_normal', 'kem_bw_normal', 'msg_bw_normal']
    labels = ['KEM Times', 'Cipher Times', 'KEM Bandwidth', 'Msg Bandwidth']
    
    for i, (metrica, label) in enumerate(zip(metricas, labels)):
        ax = axes[i//2, i%2]
        
        # Contagem de normal vs não-normal
        counts = df[metrica].value_counts()
        
        # Verifica quantas categorias existem nos dados
        if len(counts) == 1:
            # Se há apenas uma categoria, mostra como gráfico de barras
            category = counts.index[0]
            category_label = 'Normal' if category else 'Não-Normal'
            color = '#2ecc71' if category else '#e74c3c'
            
            ax.bar([category_label], [counts.iloc[0]], color=color, alpha=0.7)
            ax.set_ylabel('Quantidade de Amostras')
            ax.set_title(f'{label}\n(Todas as {len(df)} amostras são {category_label})')
            ax.set_ylim(0, len(df) * 1.1)
            
            # Adiciona texto com porcentagem
            ax.text(0, counts.iloc[0] + len(df) * 0.02, f'{100:.1f}%', 
                   ha='center', va='bottom', fontweight='bold')
        else:
            # Se há múltiplas categorias, mostra como pizza
            colors = ['#2ecc71' if cat else '#e74c3c' for cat in counts.index]
            labels_pie = ['Normal' if cat else 'Não-Normal' for cat in counts.index]
            
            ax.pie(counts.values, labels=labels_pie, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax.set_title(f'{label}\n(Total: {len(df)} amostras)')
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'analise_normalidade.png', dpi=300, bbox_inches='tight')
    plt.show()

def grafico_distribuicao_outliers(df, plots_subdir):
    """Gráfico de distribuição de outliers por métrica"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Distribuição de Outliers por Métrica', fontsize=16, fontweight='bold')
    
    # Métricas de outliers
    metricas = ['kem_outliers_pct', 'cipher_outliers_pct', 'kem_bw_outliers_pct', 'msg_bw_outliers_pct']
    labels = ['KEM Times', 'Cipher Times', 'KEM Bandwidth', 'Msg Bandwidth']
    
    for i, (metrica, label) in enumerate(zip(metricas, labels)):
        ax = axes[i//2, i%2]
        
        # Histograma da porcentagem de outliers
        ax.hist(df[metrica], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_title(f'Distribuição de Outliers - {label}')
        ax.set_xlabel('Porcentagem de Outliers (%)')
        ax.set_ylabel('Frequência')
        
        # Linha vertical para a média
        media = df[metrica].mean()
        ax.axvline(media, color='red', linestyle='--', label=f'Média: {media:.1f}%')
        ax.legend()
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'distribuicao_outliers.png', dpi=300, bbox_inches='tight')
    plt.show()

def grafico_comparacao_estatisticas(df, plots_subdir):
    """Gráfico comparativo de estatísticas paramétricas vs robustas"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Comparação: Estatísticas Paramétricas vs Robustas', fontsize=16, fontweight='bold')
    
    # Métricas de tipo de estatística
    metricas = ['kem_stat_type', 'cipher_stat_type', 'kem_bw_stat_type', 'msg_bw_stat_type']
    labels = ['KEM Times', 'Cipher Times', 'KEM Bandwidth', 'Msg Bandwidth']
    
    for i, (metrica, label) in enumerate(zip(metricas, labels)):
        ax = axes[i//2, i%2]
        
        # Contagem de paramétrico vs robusto
        counts = df[metrica].value_counts()
        
        # Verifica quantas categorias existem nos dados
        if len(counts) == 1:
            # Se há apenas uma categoria, mostra como gráfico de barras
            category = counts.index[0]
            category_label = 'Paramétrico' if category == 'parametric' else 'Robusto'
            color = '#3498db' if category == 'parametric' else '#f39c12'
            
            ax.bar([category_label], [counts.iloc[0]], color=color, alpha=0.7)
            ax.set_ylabel('Quantidade de Amostras')
            ax.set_title(f'{label}\n(Todas as {len(df)} amostras usam {category_label})')
            ax.set_ylim(0, len(df) * 1.1)
            
            # Adiciona texto com porcentagem
            ax.text(0, counts.iloc[0] + len(df) * 0.02, f'{100:.1f}%', 
                   ha='center', va='bottom', fontweight='bold')
        else:
            # Se há múltiplas categorias, mostra como pizza
            colors = ['#3498db' if cat == 'parametric' else '#f39c12' for cat in counts.index]
            labels_pie = ['Paramétrico' if cat == 'parametric' else 'Robusto' for cat in counts.index]
            
            ax.pie(counts.values, labels=labels_pie, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax.set_title(f'{label}\n(Total: {len(df)} amostras)')
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'comparacao_estatisticas.png', dpi=300, bbox_inches='tight')
    plt.show()

def grafico_qualidade_amostras(df, plots_subdir):
    """Gráfico de qualidade das amostras após limpeza"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Qualidade das Amostras Após Limpeza', fontsize=16, fontweight='bold')
    
    # Tamanhos das amostras
    sample_sizes = ['kem_sample_size', 'cipher_sample_size', 'kem_bw_sample_size', 'msg_bw_sample_size']
    labels = ['KEM Times', 'Cipher Times', 'KEM Bandwidth', 'Msg Bandwidth']
    
    for i, (sample_size, label) in enumerate(zip(sample_sizes, labels)):
        ax = axes[i//2, i%2]
        
        # Histograma do tamanho das amostras
        ax.hist(df[sample_size], bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
        ax.set_title(f'Tamanho da Amostra - {label}')
        ax.set_xlabel('Tamanho da Amostra')
        ax.set_ylabel('Frequência')
        
        # Estatísticas
        media = df[sample_size].mean()
        mediana = df[sample_size].median()
        ax.axvline(media, color='red', linestyle='--', label=f'Média: {media:.1f}')
        ax.axvline(mediana, color='blue', linestyle='-', label=f'Mediana: {mediana:.1f}')
        ax.legend()
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'qualidade_amostras.png', dpi=300, bbox_inches='tight')
    plt.show()

def grafico_outliers_extremos(df, plots_subdir):
    """Gráfico de análise de outliers extremos"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análise de Outliers Extremos', fontsize=16, fontweight='bold')
    
    # Métricas de outliers extremos
    metricas = ['kem_extreme_outliers', 'cipher_extreme_outliers', 'kem_bw_extreme_outliers', 'msg_bw_extreme_outliers']
    labels = ['KEM Times', 'Cipher Times', 'KEM Bandwidth', 'Msg Bandwidth']
    
    for i, (metrica, label) in enumerate(zip(metricas, labels)):
        ax = axes[i//2, i%2]
        
        # Boxplot dos outliers extremos por cenário
        sns.boxplot(data=df, x='cenario', y=metrica, ax=ax)
        ax.set_title(f'Outliers Extremos - {label}')
        ax.set_ylabel('Número de Outliers Extremos')
        ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'outliers_extremos.png', dpi=300, bbox_inches='tight')
    plt.show()

def grafico_desempenho_com_normalidade(df, plots_subdir):
    """Gráfico de desempenho considerando normalidade"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Desempenho por Normalidade das Métricas', fontsize=16, fontweight='bold')
    
    # Tempo de KEM por normalidade
    sns.boxplot(data=df, x='kem_normal', y='kem_ms_mean', ax=axes[0,0])
    axes[0,0].set_title('Tempo de KEM por Normalidade')
    axes[0,0].set_ylabel('Tempo (ms)')
    axes[0,0].set_xlabel('Distribuição Normal')
    
    # Tempo de cifragem por normalidade
    sns.boxplot(data=df, x='cipher_normal', y='cipher_ms_mean', ax=axes[0,1])
    axes[0,1].set_title('Tempo de Cifragem por Normalidade')
    axes[0,1].set_ylabel('Tempo (ms)')
    axes[0,1].set_xlabel('Distribuição Normal')
    
    # Throughput por normalidade da cifragem
    sns.boxplot(data=df, x='cipher_normal', y='throughput', ax=axes[1,0])
    axes[1,0].set_title('Throughput por Normalidade da Cifragem')
    axes[1,0].set_ylabel('Throughput (msg/s)')
    axes[1,0].set_xlabel('Distribuição Normal')
    
    # Eficiência por normalidade
    sns.boxplot(data=df, x='cipher_normal', y='eficiencia', ax=axes[1,1])
    axes[1,1].set_title('Eficiência por Normalidade da Cifragem')
    axes[1,1].set_ylabel('Eficiência')
    axes[1,1].set_xlabel('Distribuição Normal')
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'desempenho_normalidade.png', dpi=300, bbox_inches='tight')
    plt.show()

def grafico_correlacao_metricas(df, plots_subdir):
    """Gráfico de correlação entre métricas estatísticas"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Correlação entre Métricas Estatísticas', fontsize=16, fontweight='bold')
    
    # Correlação entre outliers e normalidade
    df_corr = df[['kem_outliers_pct', 'cipher_outliers_pct', 'kem_bw_outliers_pct', 'msg_bw_outliers_pct']].corr()
    sns.heatmap(df_corr, annot=True, cmap='coolwarm', center=0, ax=axes[0,0])
    axes[0,0].set_title('Correlação entre % de Outliers')
    
    # Correlação entre tempos e outliers
    axes[0,1].scatter(df['kem_outliers_pct'], df['kem_ms_mean'], alpha=0.6, color='blue')
    axes[0,1].set_xlabel('% Outliers KEM')
    axes[0,1].set_ylabel('Tempo KEM (ms)')
    axes[0,1].set_title('Outliers vs Tempo KEM')
    
    # Correlação entre tamanho da amostra e normalidade
    # Como todas as amostras são normais no dataset, mostra distribuição dos tamanhos
    axes[1,0].hist(df['kem_sample_size'], bins=15, alpha=0.7, color='green', 
                   label=f'Normal (n={len(df)})')
    axes[1,0].set_xlabel('Tamanho da Amostra')
    axes[1,0].set_ylabel('Frequência')
    axes[1,0].set_title('Distribuição do Tamanho da Amostra KEM\n(Todas as amostras são normais)')
    axes[1,0].legend()
    
    # Distribuição de intervalos de confiança
    ic_data = [df['kem_ms_ci95'], df['cipher_ms_ci95'], df['kem_bw_ci95'], df['msg_bw_ci95']]
    ic_labels = ['KEM Time', 'Cipher Time', 'KEM BW', 'Msg BW']
    
    # Remove possíveis valores NaN ou infinitos
    ic_data_clean = []
    ic_labels_clean = []
    for i, data in enumerate(ic_data):
        clean_data = data.dropna()
        clean_data = clean_data[np.isfinite(clean_data)]
        if len(clean_data) > 0:
            ic_data_clean.append(clean_data)
            ic_labels_clean.append(ic_labels[i])
    
    if ic_data_clean:
        axes[1,1].boxplot(ic_data_clean, labels=ic_labels_clean)
        axes[1,1].set_title('Distribuição dos Intervalos de Confiança 95%')
        axes[1,1].set_ylabel('IC95')
        axes[1,1].tick_params(axis='x', rotation=45)
    else:
        axes[1,1].text(0.5, 0.5, 'Dados insuficientes\npara análise de IC95', 
                      ha='center', va='center', transform=axes[1,1].transAxes)
        axes[1,1].set_title('Intervalos de Confiança 95%')
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'correlacao_metricas.png', dpi=300, bbox_inches='tight')
    plt.show()

# Mantém os gráficos originais com pequenas adaptações
def grafico_desempenho_por_cenario(df, plots_subdir):
    """Gráfico de desempenho por cenário de uso"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Desempenho por Cenário de Uso', fontsize=16, fontweight='bold')
    
    # Tempo de KEM por cenário
    sns.boxplot(data=df, x='cenario', y='kem_ms_mean', ax=axes[0,0])
    axes[0,0].set_title('Tempo de KEM por Cenário')
    axes[0,0].set_ylabel('Tempo (ms)')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Tempo de cifragem por cenário
    sns.boxplot(data=df, x='cenario', y='cipher_ms_mean', ax=axes[0,1])
    axes[0,1].set_title('Tempo de Cifragem por Cenário')
    axes[0,1].set_ylabel('Tempo (ms)')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Largura de banda por cenário
    sns.boxplot(data=df, x='cenario', y='msg_bw_mean', ax=axes[1,0])
    axes[1,0].set_title('Largura de Banda por Cenário')
    axes[1,0].set_ylabel('Bytes')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Rotações por cenário
    sns.boxplot(data=df, x='cenario', y='rotacoes', ax=axes[1,1])
    axes[1,1].set_title('Rotações por Cenário')
    axes[1,1].set_ylabel('Número de Rotações')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'desempenho_por_cenario.png', dpi=300, bbox_inches='tight')
    plt.show()

def grafico_comparacao_algoritmos(df, plots_subdir):
    """Gráfico comparativo de algoritmos"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Comparação de Algoritmos', fontsize=16, fontweight='bold')
    
    # Tempo total por algoritmo
    sns.boxplot(data=df, x='cifra', y='latencia_total', ax=axes[0,0])
    axes[0,0].set_title('Latência Total por Algoritmo')
    axes[0,0].set_ylabel('Latência (ms)')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Throughput por algoritmo
    sns.boxplot(data=df, x='cifra', y='throughput', ax=axes[0,1])
    axes[0,1].set_title('Throughput por Algoritmo')
    axes[0,1].set_ylabel('Throughput (msg/s)')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Eficiência por algoritmo
    sns.boxplot(data=df, x='cifra', y='eficiencia', ax=axes[1,0])
    axes[1,0].set_title('Eficiência por Algoritmo')
    axes[1,0].set_ylabel('Eficiência')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    # Largura de banda KEM por algoritmo
    sns.boxplot(data=df, x='cifra', y='kem_bw_mean', ax=axes[1,1])
    axes[1,1].set_title('Largura de Banda KEM por Algoritmo')
    axes[1,1].set_ylabel('Largura de Banda (bytes)')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(plots_subdir / 'comparacao_algoritmos.png', dpi=300, bbox_inches='tight')
    plt.show()

def grafico_analise_acordos_chave(df, plots_subdir):
    acordo_types = df['acordo'].unique()
    colors = ['#1f77b4', '#ff7f0e']
    # Boxplots lado a lado para tempo de KEM e largura de banda de KEM por acordo de chave
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    sns.boxplot(data=df, x='acordo', y='kem_ms_mean', ax=axes[0], palette=colors[:len(acordo_types)])
    axes[0].set_title('Tempo de KEM por Tipo de Acordo (Boxplot)')
    axes[0].set_ylabel('Tempo de KEM (ms)')
    axes[0].set_xlabel('Tipo de Acordo')
    sns.boxplot(data=df, x='acordo', y='kem_bw_mean', ax=axes[1], palette=colors[:len(acordo_types)])
    axes[1].set_title('Largura de Banda KEM por Tipo de Acordo (Boxplot)')
    axes[1].set_ylabel('Largura de Banda KEM (bytes)')
    axes[1].set_xlabel('Tipo de Acordo')
    plt.tight_layout()
    plt.savefig(plots_subdir / 'acordos_kem_boxplots_lado_a_lado.png', dpi=300)
    plt.close()
    """Gráficos de barras para análise de acordos de chave, com intervalo de confiança visual, cada métrica em uma figura separada."""
    import numpy as np
    acordo_types = df['acordo'].unique()
    colors = ['#1f77b4', '#ff7f0e']

    # Função auxiliar para plotar barras com IC
    def plot_bar_ic(metric, ci_metric, ylabel, title, filename, scale=1.0):
        means = df.groupby('acordo')[metric].mean() * scale
        cis = df.groupby('acordo')[ci_metric].mean() * scale
        x = np.arange(len(acordo_types))
        fig, ax = plt.subplots(figsize=(8,6))
        bars = ax.bar(x, means, yerr=cis, capsize=10, color=colors[:len(acordo_types)], alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(acordo_types)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        # Adiciona valor numérico acima do topo da barra de erro e desenha manualmente o cap
        for i, bar in enumerate(bars):
            y = bar.get_height()
            ci = cis.iloc[i]
            center_x = bar.get_x() + bar.get_width()/2
            # Desenha manualmente o cap da barra de erro
            cap_width = bar.get_width() * 0.5
            ax.plot([center_x - cap_width/2, center_x + cap_width/2], [y + ci, y + ci], color='black', lw=2)
            # Adiciona valor numérico acima do cap
            ax.text(center_x, y + ci + (0.03 * y), f'{y:.2f}',
                    ha='center', va='bottom', fontweight='bold')
        plt.tight_layout()
        plt.savefig(plots_subdir / filename, dpi=300)
        plt.close()

    # Tempo de KEM por tipo de acordo
    plot_bar_ic('kem_ms_mean', 'kem_ms_ci95', 'Tempo de KEM (ms)',
                'Tempo de KEM por Tipo de Acordo (com IC95)', 'acordos_kem_ms.png')

    # Adiciona boxplot para tempo de KEM por tipo de acordo
    plt.figure(figsize=(8,6))
    sns.boxplot(data=df, x='acordo', y='kem_ms_mean', palette=colors[:len(acordo_types)])
    plt.title('Tempo de KEM por Tipo de Acordo (Boxplot)')
    plt.ylabel('Tempo de KEM (ms)')
    plt.xlabel('Tipo de Acordo')
    plt.tight_layout()
    plt.savefig(plots_subdir / 'acordos_kem_ms_boxplot.png', dpi=300)
    plt.close()

    # Largura de banda KEM por tipo de acordo
    plot_bar_ic('kem_bw_mean', 'kem_bw_ci95', 'Largura de Banda KEM (bytes)',
                'Largura de Banda KEM por Tipo de Acordo (com IC95)', 'acordos_kem_bw.png')

    # Latência total por tipo de acordo
    # Calcula o IC95 da latência total como a soma dos ICs de KEM e cifragem
    df['latencia_total_ci95'] = df['kem_ms_ci95'] + df['cipher_ms_ci95']
    plot_bar_ic('latencia_total', 'latencia_total_ci95', 'Latência Total (ms)',
                'Latência Total por Tipo de Acordo (com IC95)', 'acordos_latencia_total.png')

    # Throughput por tipo de acordo
    plot_bar_ic('throughput', 'kem_ms_ci95', 'Throughput (msg/s)',
                'Throughput por Tipo de Acordo (com IC95)', 'acordos_throughput.png')

def grafico_overhead_protocolos(df, plots_dir):
    """Gráfico de overhead dos protocolos de acordo"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    sns.boxplot(data=df, x='acordo', y='kem_ms_mean', ax=axes[0])
    axes[0].set_title('Tempo de Estabelecimento de Chaves (KEM) por Protocolo')
    axes[0].set_ylabel('Tempo (ms)')
    axes[0].set_xlabel('Protocolo de Acordo')
    sns.boxplot(data=df, x='acordo', y='kem_bw_mean', ax=axes[1])
    axes[1].set_title('Largura de Banda KEM por Protocolo')
    axes[1].set_ylabel('Bytes')
    axes[1].set_xlabel('Protocolo de Acordo')
    plt.tight_layout()
    plt.savefig(plots_dir / 'overhead_protocolos.png', dpi=300)
    plt.close()

def grafico_eficiencia_pcs_fs(df, plots_dir):
    """Gráfico de eficiência PCS e overhead temporal por cenário"""
    cenarios = df['cenario'].unique()
    pcs_eff, overhead = [], []
    for c in cenarios:
        sub = df[df['cenario'] == c]
        msgs_protegidas = sub['msgs_por_rotacao'].mean()
        overhead_temporal = sub['kem_ms_mean'].mean() * sub['rotacoes'].mean()
        pcs_eff.append(msgs_protegidas / overhead_temporal if overhead_temporal else 0)
        overhead.append(overhead_temporal)
    plt.figure(figsize=(10,6))
    plt.bar(cenarios, pcs_eff, color='royalblue', label='Eficiência PCS (msgs/ms)')
    plt.plot(cenarios, overhead, color='red', marker='o', label='Overhead Temporal (ms)')
    plt.ylabel('Eficiência PCS / Overhead')
    plt.title('Eficiência PCS e Overhead Temporal por Cenário')
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / 'eficiencia_pcs_fs.png', dpi=300)
    plt.close()

def grafico_throughput_eficiencia_cifra(df, plots_dir):
    """Gráfico de throughput e eficiência por algoritmo de cifra"""
    if 'throughput' in df.columns and 'eficiencia' in df.columns:
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        sns.boxplot(data=df, x='cifra', y='throughput', ax=axes[0])
        axes[0].set_title('Throughput por Algoritmo de Cifra')
        axes[0].set_ylabel('Mensagens por Segundo')
        axes[0].set_xlabel('Algoritmo de Cifra')
        sns.boxplot(data=df, x='cifra', y='eficiencia', ax=axes[1])
        axes[1].set_title('Eficiência por Algoritmo de Cifra')
        axes[1].set_ylabel('Eficiência (Throughput/Latência)')
        axes[1].set_xlabel('Algoritmo de Cifra')
        plt.tight_layout()
        plt.savefig(plots_dir / 'throughput_eficiencia_cifra.png', dpi=300)
        plt.close()

def grafico_rotacao_por_cenario(df, plots_dir):
    """Gráfico do número de rotações de chave por cenário"""
    plt.figure(figsize=(10,6))
    sns.boxplot(data=df, x='cenario', y='rotacoes')
    plt.title('Número de Rotações de Chave por Cenário')
    plt.ylabel('Rotações')
    plt.xlabel('Cenário de Uso')
    plt.tight_layout()
    plt.savefig(plots_dir / 'rotacao_por_cenario.png', dpi=300)
    plt.close()

def grafico_outliers_normalidade(df, plots_dir):
    """Gráfico de outliers e normalidade por cenário"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    sns.boxplot(data=df, x='cenario', y='kem_outliers', ax=axes[0])
    axes[0].set_title('Outliers KEM por Cenário')
    axes[0].set_ylabel('Outliers')
    axes[0].set_xlabel('Cenário')
    normalidade = df.groupby('cenario')['kem_normal'].mean()
    axes[1].bar(normalidade.index, normalidade.values, color='seagreen')
    axes[1].set_title('Proporção de Dados Normais por Cenário')
    axes[1].set_ylabel('Proporção')
    axes[1].set_xlabel('Cenário')
    plt.tight_layout()
    plt.savefig(plots_dir / 'outliers_normalidade.png', dpi=300)
    plt.close()

def grafico_tradeoff_pcs(df, plots_dir):
    """Gráfico do trade-off PCS vs eficiência computacional"""
    cenarios = df['cenario'].unique()
    pcs_eff = []
    for c in cenarios:
        sub = df[df['cenario'] == c]
        msgs_protegidas = sub['msgs_por_rotacao'].mean()
        overhead_temporal = sub['kem_ms_mean'].mean() * sub['rotacoes'].mean()
        pcs_eff.append(msgs_protegidas / overhead_temporal if overhead_temporal else 0)
    plt.figure(figsize=(10,6))
    plt.plot(cenarios, pcs_eff, marker='o', color='purple')
    plt.title('Trade-off PCS vs Eficiência Computacional')
    plt.ylabel('Eficiência PCS (msgs/ms)')
    plt.xlabel('Cenário')
    plt.tight_layout()
    plt.savefig(plots_dir / 'tradeoff_pcs.png', dpi=300)
    plt.close()

def grafico_distribuicao_cifragem(df, plots_dir):
    """Gráfico da distribuição dos tempos de cifragem por algoritmo"""
    plt.figure(figsize=(10,6))
    sns.violinplot(data=df, x='cifra', y='cipher_ms_mean', inner='quartile', palette='muted')
    plt.title('Distribuição dos Tempos de Cifragem por Algoritmo')
    plt.ylabel('Tempo de Cifragem (ms)')
    plt.xlabel('Algoritmo de Cifra')
    plt.tight_layout()
    plt.savefig(plots_dir / 'distribuicao_cifragem.png', dpi=300)
    plt.close()

def grafico_intervalos_confianca(df, plots_dir):
    """Gráfico dos intervalos de confiança das métricas"""
    fig, axes = plt.subplots(2, 2, figsize=(14,10))
    sns.boxplot(data=df, x='cenario', y='kem_ms_ci95', ax=axes[0,0])
    axes[0,0].set_title('IC95 KEM (ms)')
    sns.boxplot(data=df, x='cenario', y='cipher_ms_ci95', ax=axes[0,1])
    axes[0,1].set_title('IC95 Cipher (ms)')
    sns.boxplot(data=df, x='cenario', y='kem_bw_ci95', ax=axes[1,0])
    axes[1,0].set_title('IC95 KEM BW (bytes)')
    sns.boxplot(data=df, x='cenario', y='msg_bw_ci95', ax=axes[1,1])
    axes[1,1].set_title('IC95 Msg BW (bytes)')
    plt.tight_layout()
    plt.savefig(plots_dir / 'intervalos_confianca.png', dpi=300)
    plt.close()

def grafico_correlacao_kem_bw(df, plots_dir):
    """Gráfico de correlação entre tempo de KEM e largura de banda KEM"""
    plt.figure(figsize=(8,6))
    sns.scatterplot(data=df, x='kem_ms_mean', y='kem_bw_mean', hue='acordo')
    plt.title('Correlação entre Tempo de KEM e Largura de Banda')
    plt.xlabel('Tempo KEM (ms)')
    plt.ylabel('Largura de Banda KEM (bytes)')
    plt.tight_layout()
    plt.savefig(plots_dir / 'correlacao_kem_bw.png', dpi=300)
    plt.close()

def grafico_tamanho_amostras(df, plots_dir):
    """Gráfico da distribuição do tamanho das amostras KEM por cenário"""
    plt.figure(figsize=(10,6))
    sns.boxplot(data=df, x='cenario', y='kem_sample_size')
    plt.title('Distribuição do Tamanho das Amostras KEM por Cenário')
    plt.ylabel('Tamanho da Amostra')
    plt.xlabel('Cenário')
    plt.tight_layout()
    plt.savefig(plots_dir / 'tamanho_amostras.png', dpi=300)
    plt.close()

def grafico_proporcao_tipos_mensagem(df, plots_dir):
    """Gráfico da proporção de tipos de mensagem por cenário"""
    tipos = ['text_msgs', 'image_msgs', 'file_msgs', 'system_msgs']
    df_tipos = df.groupby('cenario')[tipos].sum()
    df_tipos_pct = df_tipos.div(df_tipos.sum(axis=1), axis=0)
    df_tipos_pct.plot(kind='bar', stacked=True, figsize=(12,7), colormap='tab20')
    plt.title('Proporção de Tipos de Mensagem por Cenário')
    plt.ylabel('Proporção')
    plt.xlabel('Cenário')
    plt.legend(title='Tipo de Mensagem')
    plt.tight_layout()
    plt.savefig(plots_dir / 'proporcao_tipos_mensagem.png', dpi=300)
    plt.close()

def grafico_heatmap_correlacao(df, plots_dir):
    """Gráfico de heatmap de correlação das métricas"""
    cols = ['kem_ms_mean', 'kem_bw_mean', 'cipher_ms_mean', 'msg_bw_mean', 'rotacoes']
    corr = df[cols].corr()
    plt.figure(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
    plt.title('Heatmap de Correlação das Métricas')
    plt.tight_layout()
    plt.savefig(plots_dir / 'heatmap_correlacao.png', dpi=300)
    plt.close()

def grafico_impacto_rotacao_kem(df, plots_subdir):
    """
    Gráfico do impacto da frequência de rotação no tempo médio de KEM
    (Olm-Híbrido, AES-GCM, 1000 msgs)
    """
    # Filtrar dados específicos do cenário do gráfico
    filtro = (df['acordo'] == 'Olm-Híbrido') & (df['cifra'] == 'AES-GCM') & (df['num_msgs'] == 1000)
    dados = df[filtro].sort_values('msgs_por_rotacao')
    x = dados['msgs_por_rotacao']
    y = dados['kem_ms_mean'] * 1000  # ms para µs

    plt.figure(figsize=(12,7))
    plt.plot(x, y, marker='o', label='Tempo Médio de KEM')
    for xi, yi in zip(x, y):
        plt.text(xi, yi+100, f"{yi:.1f} µs", ha='center', fontsize=11)
    plt.title('Impacto da Frequência de Rotação no Tempo de KEM (Olm-Híbrido, AES-GCM, 1000 msgs)')
    plt.xlabel('Mensagens por Rotação de Chave')
    plt.ylabel('Tempo Médio de KEM (µs)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_subdir / 'impacto_rotacao_kem.png', dpi=300)
    plt.close()

def grafico_impacto_rotacao_kem_por_cenario(df, plots_subdir):
    """
    Gráfico do impacto da rotação (por cenário) no tempo médio de KEM.
    O eixo X mostra os cenários, o Y mostra o tempo médio de KEM (µs),
    e cada ponto é anotado com o número de mensagens por rotação.
    """
    dados = df[(df['acordo'] == 'Olm-Híbrido') & (df['cifra'] == 'AES-GCM')]
    dados = dados.sort_values('msgs_por_rotacao')
    x = dados['cenario']
    y = dados['kem_ms_mean'] * 1000  # ms para µs
    rotacao = dados['msgs_por_rotacao']

    plt.figure(figsize=(12,7))
    plt.plot(x, y, marker='o', label='Tempo Médio de KEM')
    for xi, yi, ri in zip(x, y, rotacao):
        plt.text(xi, yi+100, f"{yi:.1f} µs\n({ri:.0f} msgs/rot)", ha='center', fontsize=11)
    plt.title('Impacto da Rotação (por Cenário) no Tempo de KEM (Olm-Híbrido, AES-GCM)')
    plt.xlabel('Cenário')
    plt.ylabel('Tempo Médio de KEM (µs)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_subdir / 'impacto_rotacao_kem_por_cenario.png', dpi=300)
    plt.close()

def grafico_largura_banda_kem_por_rotacao(df, plots_subdir):
    """
    Gráfico da largura de banda média do KEM por política de rotação (por cenário),
    comparando Olm-Clássico e Olm-Híbrido.
    """
    # Filtra apenas experimentos com 1000 mensagens (ajuste se necessário)
    dados = df[df['num_msgs'] == 1000]
    cenarios_ord = sorted(dados['cenario'].unique(), key=lambda c: dados[dados['cenario'] == c]['msgs_por_rotacao'].mean())

    plt.figure(figsize=(14,8))
    protocolos = ['Olm-Clássico', 'Olm-Híbrido']
    cores = ['#1f77b4', '#ff7f0e']

    for protocolo, cor in zip(protocolos, cores):
        sub = dados[dados['acordo'] == protocolo].sort_values('msgs_por_rotacao')
        x = sub['msgs_por_rotacao']
        y = sub['kem_bw_mean'] / (1024*1024)  # bytes para MB
        cenarios = sub['cenario']
        plt.plot(x, y, marker='o', label=protocolo, color=cor)
        for xi, yi, cenario in zip(x, y, cenarios):
            plt.text(xi, yi, f"{cenario}", fontsize=10, va='bottom', ha='left')

    plt.title('Largura de Banda do KEM por Tipo de Acordo, Rotação e Cenário (1000 Mensagens)')
    plt.xlabel('Mensagens por Rotação de Chave')
    plt.ylabel('Largura de Banda Média (MB)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_subdir / 'largura_banda_kem_por_rotacao.png', dpi=300)
    plt.close()

def grafico_largura_banda_kem_vs_rotacoes(df, plots_subdir):
    """
    Gráfico de linha/curva do consumo de largura de banda do KEM (KB) por número de rotações,
    para cada tipo de acordo e cenário, usando o dataset do experimento.
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12,7))
    protocolos = ['Olm-Clássico', 'Olm-Híbrido']
    cores = ['#1f77b4', '#ff7f0e']
    cenarios = df['cenario'].unique()
    jitter = {'Olm-Clássico': -1, 'Olm-Híbrido': 1}

    for protocolo, cor in zip(protocolos, cores):
        sub = df[df['acordo'] == protocolo]
        x = []
        y = []
        labels = []
        for c in cenarios:
            sub_c = sub[sub['cenario'] == c]
            if not sub_c.empty:
                xi = sub_c['rotacoes'].values[0] + jitter[protocolo]
                yi = sub_c['kem_bw_mean'].values[0] / 1024  # bytes para KB
                x.append(xi)
                y.append(yi)
                labels.append(c)
        plt.plot(x, y, marker='o', color=cor, label=protocolo)
        for xi, yi, c in zip(x, y, labels):
            plt.text(xi, yi, f"{c}\n{yi:.2f} KB", fontsize=10, va='bottom', ha='center')

    plt.title('Largura de Banda do KEM por Número de Rotações e Cenário')
    plt.xlabel('Número de Rotações')
    plt.ylabel('Largura de Banda Média do KEM (KB)')
    plt.yscale('log')
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_subdir / 'largura_banda_kem_vs_rotacoes.png', dpi=300)
    plt.close()

def grafico_overhead_temporal_por_cenario(df, plots_dir):
    # Versão boxplot do overhead temporal por cenário
    plt.figure(figsize=(10,6))
    sns.boxplot(data=df, x='cenario', y='kem_ms_mean', hue='acordo', palette=['#1f77b4', '#ff7f0e'])
    plt.ylabel('Tempo Médio de KEM (ms)')
    plt.title('Overhead Temporal por Cenário (Boxplot)')
    plt.legend(title='Protocolo')
    plt.tight_layout()
    plt.savefig(plots_dir / 'overhead_temporal_por_cenario_boxplot.png', dpi=300)
    plt.close()
    """Gráfico de barras agrupadas do overhead temporal por cenário"""
    cenarios = df['cenario'].unique()
    protocolos = ['Olm-Clássico', 'Olm-Híbrido']
    x = np.arange(len(cenarios))
    width = 0.35
    means = {p: [df[(df['cenario'] == c) & (df['acordo'] == p)]['kem_ms_mean'].mean() for c in cenarios] for p in protocolos}
    cis = {p: [df[(df['cenario'] == c) & (df['acordo'] == p)]['kem_ms_ci95'].mean() for c in cenarios] for p in protocolos}
    plt.figure(figsize=(10,6))
    bars1 = plt.bar(x - width/2, means['Olm-Clássico'], width, yerr=cis['Olm-Clássico'], capsize=8, label='Olm-Clássico')
    bars2 = plt.bar(x + width/2, means['Olm-Híbrido'], width, yerr=cis['Olm-Híbrido'], capsize=8, label='Olm-Híbrido')
    plt.xticks(x, cenarios, rotation=30)
    plt.ylabel('Tempo Médio de KEM (ms)')
    plt.title('Overhead Temporal por Cenário (com IC95)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / 'overhead_temporal_por_cenario.png', dpi=300)
    plt.close()

def grafico_overhead_largura_banda_por_cenario(df, plots_dir):
    """Gráfico de barras empilhadas do overhead de largura de banda por cenário"""
    import matplotlib.pyplot as plt
    cenarios = df['cenario'].unique()
    protocolos = ['Olm-Clássico', 'Olm-Híbrido']
    x = np.arange(len(cenarios))
    width = 0.35
    means = {p: [df[(df['cenario'] == c) & (df['acordo'] == p)]['kem_bw_mean'].mean()/1024 for c in cenarios] for p in protocolos}
    plt.figure(figsize=(10,6))
    plt.bar(x - width/2, means['Olm-Clássico'], width, label='Olm-Clássico')
    plt.bar(x + width/2, means['Olm-Híbrido'], width, label='Olm-Híbrido')
    plt.xticks(x, cenarios, rotation=30)
    plt.ylabel('Largura de Banda Média do KEM (KB)')
    plt.title('Overhead de Largura de Banda por Cenário')
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / 'overhead_largura_banda_por_cenario.png', dpi=300)
    plt.close()

def grafico_eficiencia_pcs_fs_radar(df, plots_dir):
    """Gráfico radar de eficiência PCS/FS por cenário"""
    import matplotlib.pyplot as plt
    from math import pi
    cenarios = df['cenario'].unique()
    pcs_eff = []
    fs_eff = []
    for c in cenarios:
        sub = df[df['cenario'] == c]
        msgs_protegidas = sub['msgs_por_rotacao'].mean()
        overhead_temporal = sub['kem_ms_mean'].mean() * sub['rotacoes'].mean()
        pcs_eff.append(msgs_protegidas / overhead_temporal if overhead_temporal else 0)
        fs_eff.append(sub['fs_qualidade'].mean() if 'fs_qualidade' in sub.columns else 0)
    # Radar plot
    labels = list(cenarios)
    stats = pcs_eff + [pcs_eff[0]]
    angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
    angles += angles[:1]
    plt.figure(figsize=(8,8))
    ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:-1], labels)
    ax.plot(angles, stats, linewidth=2, linestyle='solid', label='Eficiência PCS')
    ax.fill(angles, stats, 'b', alpha=0.1)
    plt.title('Eficiência PCS por Cenário (Radar)')
    plt.tight_layout()
    plt.savefig(plots_dir / 'eficiencia_pcs_radar.png', dpi=300)
    plt.close()

def grafico_janelas_comprometimento(df, plots_dir):
    """Gráfico de barras do número máximo de mensagens comprometidas por rotação"""
    import matplotlib.pyplot as plt
    cenarios = df['cenario'].unique()
    comprometidas = [df[df['cenario'] == c]['msgs_por_rotacao'].mean() for c in cenarios]
    plt.figure(figsize=(10,6))
    plt.bar(cenarios, comprometidas, color='tomato')
    plt.ylabel('Mensagens Comprometidas por Rotação')
    plt.title('Janelas de Comprometimento por Cenário')
    plt.tight_layout()
    plt.savefig(plots_dir / 'janelas_comprometimento.png', dpi=300)
    plt.close()

def grafico_tradeoff_custo_beneficio(df, plots_dir):
    """Gráfico de dispersão do trade-off entre overhead temporal e proteção temporal"""
    import matplotlib.pyplot as plt
    cenarios = df['cenario'].unique()
    overhead = []
    protecao = []
    for c in cenarios:
        sub = df[df['cenario'] == c]
        overhead_temporal = sub['kem_ms_mean'].mean() * sub['rotacoes'].mean()
        protecao_temporal = sub['fs_qualidade'].mean() if 'fs_qualidade' in sub.columns else 0
        overhead.append(overhead_temporal)
        protecao.append(protecao_temporal)
    plt.figure(figsize=(10,6))
    plt.scatter(overhead, protecao, color='purple')
    for i, c in enumerate(cenarios):
        plt.text(overhead[i], protecao[i], c, fontsize=10)
    plt.xlabel('Overhead Temporal (ms)')
    plt.ylabel('Proteção Temporal (FS)')
    plt.title('Trade-off: Overhead vs Proteção Temporal')
    plt.tight_layout()
    plt.savefig(plots_dir / 'tradeoff_custo_beneficio.png', dpi=300)
    plt.close()

def grafico_sensibilidade_rotacao(df, plots_dir):
    """Gráfico de linhas do overhead por frequência de rotação"""
    import matplotlib.pyplot as plt
    cenarios = df['cenario'].unique()
    for c in cenarios:
        sub = df[df['cenario'] == c].sort_values('msgs_por_rotacao')
        plt.plot(sub['msgs_por_rotacao'], sub['kem_ms_mean']*sub['rotacoes'], marker='o', label=c)
    plt.xlabel('Mensagens por Rotação')
    plt.ylabel('Overhead Temporal Total (ms)')
    plt.title('Sensibilidade do Overhead à Frequência de Rotação')
    plt.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / 'sensibilidade_rotacao.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    # Carrega os dados
    df, timestamp = carregar_dados()
    if df is None:
        sys.exit(1)  

    # Debug: mostra info dos dados carregados
    print(f"\nDados carregados: {len(df)} amostras")
    print("\nColunas de normalidade disponíveis:")
    for col in ['kem_normal', 'cipher_normal', 'kem_bw_normal', 'msg_bw_normal']:
        if col in df.columns:
            counts = df[col].value_counts()
            print(f"  {col}: {dict(counts)}")
        else:
            print(f"  {col}: COLUNA NÃO ENCONTRADA")
    
    print("\nColunas de tipo estatístico disponíveis:")
    for col in ['kem_stat_type', 'cipher_stat_type', 'kem_bw_stat_type', 'msg_bw_stat_type']:
        if col in df.columns:
            counts = df[col].value_counts()
            print(f"  {col}: {dict(counts)}")
        else:
            print(f"  {col}: COLUNA NÃO ENCONTRADA")
    
    # Debug adicional: mostra resumo das métricas numéricas
    print(f"\nResumo das métricas de outliers:")
    outlier_cols = ['kem_outliers_pct', 'cipher_outliers_pct', 'kem_bw_outliers_pct', 'msg_bw_outliers_pct']
    for col in outlier_cols:
        if col in df.columns:
            print(f"  {col}: min={df[col].min():.1f}%, max={df[col].max():.1f}%, média={df[col].mean():.1f}%")
        else:
            print(f"  {col}: COLUNA NÃO ENCONTRADA")
    
    # Cria pasta de plots se não existir
    plots_dir = Path("../plots")
    plots_dir.mkdir(exist_ok=True)
    
    # Cria subdiretório com timestamp do experimento
    plots_subdir = plots_dir / f"graficos_normality_check_{timestamp}"
    plots_subdir.mkdir(exist_ok=True)
    
    print(f"\nSalvando gráficos em: {plots_subdir}")
    
    # Gera gráficos específicos de análise estatística
    try:
        
        print("Gerando gráfico de análise de normalidade...")
        grafico_analise_normalidade(df, plots_subdir)
        
        print("Gerando gráfico de distribuição de outliers...")
        grafico_distribuicao_outliers(df, plots_subdir)
        
        print("Gerando gráfico de comparação de estatísticas...")
        grafico_comparacao_estatisticas(df, plots_subdir)
        
        print("Gerando gráfico de qualidade das amostras...")
        grafico_qualidade_amostras(df, plots_subdir)
        
        print("Gerando gráfico de outliers extremos...")
        grafico_outliers_extremos(df, plots_subdir)
        
        print("Gerando gráfico de desempenho com normalidade...")
        grafico_desempenho_com_normalidade(df, plots_subdir)
        
        print("Gerando gráfico de correlação entre métricas...")
        grafico_correlacao_metricas(df, plots_subdir)
        
        # Gera gráficos tradicionais adaptados
        print("Gerando gráfico de desempenho por cenário...")
        grafico_desempenho_por_cenario(df, plots_subdir)
        
        print("Gerando gráfico comparativo de algoritmos...")
        grafico_comparacao_algoritmos(df, plots_subdir)
        
        print("Gerando gráfico de análise de acordos de chave...")
        grafico_analise_acordos_chave(df, plots_subdir)

        print("Gerando gráfico de overhead dos protocolos...")
        grafico_overhead_protocolos(df, plots_subdir)
        
        print("Gerando gráfico de eficiência PCS e overhead temporal...")
        grafico_eficiencia_pcs_fs(df, plots_subdir)
        
        print("Gerando gráfico de throughput e eficiência por cifra...")
        grafico_throughput_eficiencia_cifra(df, plots_subdir)
        
        print("Gerando gráfico de rotação por cenário...")
        grafico_rotacao_por_cenario(df, plots_subdir)
        
        print("Gerando gráfico de outliers e normalidade...")
        grafico_outliers_normalidade(df, plots_subdir)

        print("Gerando gráfico de trade-off PCS vs eficiência computacional...")
        grafico_tradeoff_pcs(df, plots_subdir)
        
        print("Gerando gráfico de distribuição de cifragem...")
        grafico_distribuicao_cifragem(df, plots_subdir)
        
        print("Gerando gráfico de intervalos de confiança das métricas...")
        grafico_intervalos_confianca(df, plots_subdir)
        
        print("Gerando gráfico de correlação entre tempo de KEM e largura de banda KEM...") 
        grafico_correlacao_kem_bw(df, plots_subdir)
        
        print("Gerando gráfico do tamanho das amostras KEM por cenário...")
        grafico_tamanho_amostras(df, plots_subdir)

        print("Gerando gráfico da proporção de tipos de mensagem por cenário...")   
        grafico_proporcao_tipos_mensagem(df, plots_subdir)
        
        print("Gerando gráfico de heatmap de correlação das métricas...")   
        grafico_heatmap_correlacao(df, plots_subdir)
        
        print("Gerando gráfico do impacto da frequência de rotação no tempo médio de KEM...")
        grafico_impacto_rotacao_kem(df, plots_subdir)
        
        print("Gerando gráfico do impacto da rotação (por cenário) no tempo médio de KEM...")
        grafico_impacto_rotacao_kem_por_cenario(df, plots_subdir)
        
        print("Gerando gráfico da largura de banda média do KEM por política de rotação...")
        grafico_largura_banda_kem_por_rotacao(df, plots_subdir)

        print("Gerando gráfico da largura de banda do KEM por número de rotações...")
        grafico_largura_banda_kem_vs_rotacoes(df, plots_subdir)
        
        print("Gerando gráfico do overhead temporal por cenário...")    
        grafico_overhead_temporal_por_cenario(df, plots_subdir)
        
        print("Gerando gráfico do overhead de largura de banda por cenário...")
        grafico_overhead_largura_banda_por_cenario(df, plots_subdir)
        
        print("Gerando gráfico radar de eficiência PCS/FS por cenário...")
        grafico_eficiencia_pcs_fs_radar(df, plots_subdir)
        
        print("Gerando gráfico do número máximo de mensagens comprometidas por rotação...") 
        grafico_janelas_comprometimento(df, plots_subdir)
        
        print("Gerando gráfico do trade-off entre overhead temporal e proteção temporal...")    
        grafico_tradeoff_custo_beneficio(df, plots_subdir)
        
        print("Gerando gráfico de sensibilidade do overhead à frequência de rotação...")    
        grafico_sensibilidade_rotacao(df, plots_subdir)
        
        print(f"Arquivos salvos em: {plots_subdir}")

        print("Todos os gráficos foram gerados com sucesso!")
        
    except Exception as e:
        print(f"\nERRO ao gerar gráficos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Exibe resumo dos resultados do experimento
    print("\n" + "="*60)
    print("RESUMO DO EXPERIMENTO:")
    print(f"  • Total de configurações testadas: {len(df)}")
    print(f"  • Cenários: {df['cenario'].nunique()} tipos")
    print(f"  • Padrões de tráfego: {df['padrao_trafego'].nunique()} tipos")
    print(f"  • Algoritmos de acordo: {df['acordo'].nunique()} tipos")
    print(f"  • Algoritmos de cifragem: {df['cifra'].nunique()} tipos")
    
    print("\nANÁLISE ESTATÍSTICA:")
    normal_count = sum([df['kem_normal'].sum(), df['cipher_normal'].sum(), 
                       df['kem_bw_normal'].sum(), df['msg_bw_normal'].sum()])
    total_tests = len(df) * 4  # 4 métricas por linha
    print(f"  • Testes de normalidade: {normal_count}/{total_tests} passaram ({100*normal_count/total_tests:.1f}%)")
    
    parametric_count = sum([
        (df['kem_stat_type'] == 'parametric').sum(),
        (df['cipher_stat_type'] == 'parametric').sum(),
        (df['kem_bw_stat_type'] == 'parametric').sum(),
        (df['msg_bw_stat_type'] == 'parametric').sum()
    ])
    print(f"  • Estatísticas paramétricas: {parametric_count}/{total_tests} aplicadas ({100*parametric_count/total_tests:.1f}%)")
    
    print("\nOUTLIERS DETECTADOS:")
    for col in ['kem_outliers', 'cipher_outliers', 'kem_bw_outliers', 'msg_bw_outliers']:
        if col in df.columns:
            total_outliers = df[col].sum()
            print(f"  • {col.replace('_', ' ').title()}: {total_outliers} no total")
    
    print("\nNovos gráficos específicos para análise estatística:")
    print("  • Análise de normalidade das métricas")
    print("  • Distribuição de outliers")
    print("  • Comparação de estatísticas paramétricas vs robustas")
    print("  • Qualidade das amostras após limpeza")
    print("  • Análise de outliers extremos")
    print("  • Desempenho considerando normalidade")
    print("  • Correlação entre métricas estatísticas")
    print(f"\nTodos os gráficos salvos em: {plots_subdir}")