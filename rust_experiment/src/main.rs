/*
=============================================================================================
EXPERIMENTO DE AVALIAÇÃO DE IMPACTO DA CRIPTOGRAFIA PÓS-QUÂNTICA: MATRIX-LIKE
=============================================================================================

OBJETIVO PRINCIPAL:
------------------
Este experimento avalia o impacto de desempenho da transição para criptografia pós-quântica
em sistemas de mensagens seguras, comparando especificamente:

1. **ACORDOS DE CHAVE CLÁSSICOS vs PÓS-QUÂNTICOS:**
   - Olm-Clássico: X25519 ECDH (32 bytes de largura de banda)
   - Olm-Híbrido: X25519 ECDH + Kyber768 KEM (~2304 bytes de largura de banda)
   - Análise de overhead computacional e de largura de banda

2. **ALGORITMOS DE CIFRAGEM SIMÉTRICA:**
   - AES-GCM: Padrão atual amplamente adotado
   - ChaCha20-Poly1305: Alternativa moderna resistente a ataques de canal lateral
   - Megolm-Like (AES-CTR): Implementação similar ao protocolo Matrix
   - Comparação de desempenho e adequação para diferentes cenários

3. **CENÁRIOS DE USO REALISTAS:**
   - SmallChat: Conversas pequenas (100 mensagens, rotação a cada 100)
   - MediumGroup: Grupos médios (250 mensagens, rotação a cada 50)
   - LargeChannel: Canais grandes (500 mensagens, rotação a cada 25)
   - SystemChannel: Canais de sistema (1000 mensagens, rotação a cada 10)

4. **PADRÕES DE TRÁFEGO DIVERSOS:**
   - Constant, Burst, Periodic, Random, Realistic
   - Simulação de condições reais de comunicação

MÉTRICAS AVALIADAS:
------------------
- Tempo de acordo de chaves (KEM): impacto dos algoritmos pós-quânticos
- Tempo de cifragem simétrica: comparação entre algoritmos
- Largura de banda: overhead da criptografia pós-quântica
- Throughput e latência: impacto na experiência do usuário
- Distribuição de tipos de mensagens: texto, imagem, arquivo, sistema

ANÁLISE ESTATÍSTICA:
-----------------------------
Para garantir resultados confiáveis, o experimento implementa:

1. **DETECÇÃO DE OUTLIERS (método IQR):**
   - Outliers moderados: valores além de 1.5 × IQR dos quartis
   - Outliers extremos: valores além de 3.0 × IQR dos quartis
   - Remoção automática de outliers extremos para análise

2. **VERIFICAÇÃO DE NORMALIDADE:**
   - Análise de assimetria (skewness) e curtose (kurtosis)
   - Critérios: |skewness| < 2.0 e |kurtosis| < 7.0

3. **ESTATÍSTICAS ADAPTATIVAS:**
   - Dados normais: média, desvio padrão, IC95 (z-score)
   - Dados não-normais: mediana, MAD, IC95 (percentis)

4. **ANÁLISE ESTATÍSTICA EM PYTHON:**
   - Testes de normalidade: Shapiro-Wilk, Kolmogorov-Smirnov, Anderson-Darling
   - Comparações: t-test, Mann-Whitney U, Welch's t-test
   - Múltiplos grupos: ANOVA, Kruskal-Wallis
   - Testes post-hoc: Tukey HSD
   - Equivalência: TOST (Two One-Sided Tests)
   - Tamanho do efeito: Cohen's d, Cliff's delta, Eta-squared
   - Correlações: Pearson, Spearman, Kendall

5. **LOGGING DETALHADO:**
   - Decisões sobre outliers e normalidade
   - Justificativas para escolha de estatísticas
   - Tamanhos amostrais após limpeza

SEQUÊNCIA DE EXECUÇÃO:
---------------------
1. Configuração experimental: 50 repetições por combinação de parâmetros
2. Simulação de workload realista com diferentes tipos de mensagens
3. Medição de tempos de execução e largura de banda
4. Detecção de outliers usando método IQR
5. Remoção de outliers extremos
6. Verificação de normalidade nos dados limpos
7. Aplicação de estatísticas apropriadas
8. Cálculo de intervalos de confiança
9. Análise estatística em Python
10. Geração de gráficos e relatórios

PARÂMETROS EXPERIMENTAIS:
-------------------------
- Repetições por configuração: 50 execuções
- Algoritmos de acordo de chaves: 
  * Olm-Clássico: X25519 ECDH
  * Olm-Híbrido: X25519 ECDH + Kyber768 KEM
- Algoritmos de cifragem simétrica: AES-GCM, ChaCha20-Poly1305, Megolm-Like
- Cenários de uso: SmallChat, MediumGroup, LargeChannel, SystemChannel
- Padrões de tráfego: Constant, Burst, Periodic, Random, Realistic
- Tipos de mensagens: texto, imagem, arquivo, sistema, voz

RESULTADOS GERADOS:
------------------
Os resultados são salvos em arquivos CSV na pasta "results/" com timestamp único.
As colunas incluem:
- Métricas de desempenho: tempos de KEM e cifragem, largura de banda
- Estatísticas descritivas: média/mediana, desvio padrão/MAD, IC95
- Metadados estatísticos: flags de normalidade, contadores de outliers
- Informações de amostra: tamanhos após limpeza, tipos de estatísticas aplicadas
- Distribuição de tipos de mensagens processadas

IMPORTÂNCIA DO ESTUDO:
---------------------
Este experimento fornece evidências empíricas fundamentais para:
- Avaliar a viabilidade da transição para criptografia pós-quântica
- Comparar algoritmos de cifragem simétrica em cenários realistas
- Quantificar o overhead computacional e de largura de banda
- Orientar decisões arquiteturais em sistemas de comunicação segura
- Estabelecer benchmarks para futuras implementações

A análise estatística garante que os resultados sejam confiáveis,
reproduzíveis e adequados para publicação científica e tomada de decisões
técnicas em ambientes de produção.

Autor: Marcos Dantas Ortiz
Data: Julho de 2025
=============================================================================================
*/

mod workload;

// --- BIBLIOTECAS DE CRIPTOGRAFIA SIMÉTRICA ---
use aes_gcm::{Aes256Gcm, Key, Nonce};
use aes_gcm::aead::{Aead, KeyInit};
use aes::Aes256;
use ctr::cipher::{KeyIvInit, StreamCipher};
use chacha20poly1305::{ChaCha20Poly1305, Key as ChaKey, Nonce as ChaNonce};

// --- BIBLIOTECAS DE CRIPTOGRAFIA ASSIMÉTRICA (KEMs) ---
use pqcrypto_kyber::kyber768::*;
use pqcrypto_traits::kem::{Ciphertext as KemCiphertext, SharedSecret as KemSharedSecret, PublicKey};

// --- CURVAS ELÍPTICAS CLÁSSICAS (X25519) ---
use x25519_dalek::{EphemeralSecret as StaticSecret, PublicKey as X255PublicKey};

// --- UTILITÁRIOS DO SISTEMA E TEMPO ---
use rand::RngCore;
use std::time::{Duration, Instant};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::Path;
use std::process::Command;
use chrono;

// --- WORKLOAD REALISTA ---
// Importa tipos de mensagens, padrões de tráfego e cenários de uso
use workload::{
    MessageType, TrafficPattern, UsageScenario,
    MessageGenerator, TrafficGenerator,
    get_rotation_config, get_message_count_config
};

// Número de repetições por configuração experimental
// Valor balanceado entre robustez estatística e tempo de execução
const REPETICOES: usize = 50;

// Estrutura para armazenar estatísticas descritivas de cada métrica
// Suporta tanto estatísticas paramétricas quanto robustas
#[derive(Debug, Clone)]
struct Stats {
    mean: f64,                    // Média (dados normais) ou mediana (dados não-normais)
    std_dev: f64,                 // Desvio padrão (normal) ou MAD escalado (não-normal)
    ci95: f64,                    // Intervalo de confiança 95%
    is_normal: bool,              // Flag indicando se os dados seguem distribuição normal
    outliers_count: usize,        // Número total de outliers detectados (moderados + extremos)
    extreme_outliers_count: usize, // Número específico de outliers extremos
    sample_size: usize,           // Tamanho da amostra final após remoção de outliers
}

/// Calcula estatísticas paramétricas para dados que seguem distribuição normal
///
/// Aplica estatísticas tradicionais baseadas na distribuição normal:
/// - Média aritmética como medida de tendência central
/// - Desvio padrão amostral (com correção de Bessel) para dispersão
/// - Intervalo de confiança 95% usando z-score (1.96)
///
/// Parâmetros:
/// - data: slice de valores f64 (tempos de execução, larguras de banda, etc.)
/// - outliers_count: número total de outliers detectados
/// - extreme_outliers_count: número específico de outliers extremos
/// - original_size: tamanho original da amostra antes da limpeza
///
/// Retorna:
/// - Stats com estatísticas paramétricas e flag is_normal = true
fn calculate_parametric_stats(data: &[f64], outliers_count: usize, extreme_outliers_count: usize, original_size: usize) -> Stats {
    let n = data.len();
    if n == 0 {
        return Stats { 
            mean: 0.0, 
            std_dev: 0.0, 
            ci95: 0.0, 
            is_normal: true,
            outliers_count,
            extreme_outliers_count,
            sample_size: n
        };
    }
    
    let mean = data.iter().sum::<f64>() / n as f64;
    
    if n < 2 {
        return Stats { 
            mean, 
            std_dev: 0.0, 
            ci95: 0.0, 
            is_normal: true,
            outliers_count,
            extreme_outliers_count,
            sample_size: n
        };
    }
    
    // Calcula a variância amostral (correção de Bessel)
    let variance = data.iter().map(|value| {
        let diff = mean - value;
        diff * diff
    }).sum::<f64>() / (n - 1) as f64;
    
    let std_dev = variance.sqrt();
    
    // Z-score para 95% de confiança (distribuição normal)
    let z_score = 1.96;
    let ci95 = z_score * (std_dev / (n as f64).sqrt());
    
    Stats { 
        mean, 
        std_dev, 
        ci95, 
        is_normal: true,
        outliers_count,
        extreme_outliers_count,
        sample_size: n
    }
}

/// Calcula estatísticas robustas para dados que não seguem distribuição normal
/// 
/// Aplica estatísticas não-paramétricas resistentes a outliers:
/// - Mediana como medida de tendência central (mais robusta que média)
/// - MAD (Median Absolute Deviation) escalado para dispersão
/// - Intervalo de confiança baseado em percentis (2.5% e 97.5%)
///
/// O fator de escala 1.4826 é aplicado ao MAD para torná-lo equivalente
/// ao desvio padrão em distribuições normais, mantendo interpretabilidade.
///
/// Parâmetros:
/// - data: slice de valores f64
/// - outliers_count: número total de outliers detectados
/// - extreme_outliers_count: número específico de outliers extremos
/// - original_size: tamanho original da amostra antes da limpeza
///
/// Retorna:
/// - Stats com estatísticas robustas e flag is_normal = false
fn calculate_robust_stats(data: &[f64], outliers_count: usize, extreme_outliers_count: usize, original_size: usize) -> Stats {
    let n = data.len();
    if n == 0 {
        return Stats { 
            mean: 0.0, 
            std_dev: 0.0, 
            ci95: 0.0, 
            is_normal: false,
            outliers_count,
            extreme_outliers_count,
            sample_size: n
        };
    }
    
    // Ordena os dados para cálculo de percentis
    let mut sorted_data = data.to_vec();
    sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    // Calcula mediana
    let median = if n % 2 == 0 {
        (sorted_data[n / 2 - 1] + sorted_data[n / 2]) / 2.0
    } else {
        sorted_data[n / 2]
    };
    
    // Calcula MAD (Median Absolute Deviation)
    let mut abs_deviations: Vec<f64> = data.iter()
        .map(|x| (x - median).abs())
        .collect();
    abs_deviations.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let mad = if n % 2 == 0 {
        (abs_deviations[n / 2 - 1] + abs_deviations[n / 2]) / 2.0
    } else {
        abs_deviations[n / 2]
    };
    
    // Fator de escala para tornar MAD equivalente ao desvio padrão em distribuições normais
    let mad_scaled = mad * 1.4826;
    
    // Intervalo de confiança baseado em percentis (mais robusto)
    let p2_5_idx = ((n as f64 * 0.025) as usize).min(n - 1);
    let p97_5_idx = ((n as f64 * 0.975) as usize).min(n - 1);
    let p2_5 = sorted_data[p2_5_idx];
    let p97_5 = sorted_data[p97_5_idx];
    let ci95_robust = (p97_5 - p2_5) / 2.0;
    
    Stats { 
        mean: median,        // Usa mediana como medida central
        std_dev: mad_scaled, // Usa MAD escalado como dispersão
        ci95: ci95_robust,   // Usa diferença de percentis
        is_normal: false,
        outliers_count,
        extreme_outliers_count,
        sample_size: n
    }
}

/// Detecta outliers usando método IQR (Interquartile Range)
/// 
/// Implementa o método estatístico padrão para detecção de outliers:
/// - Outliers moderados: valores além de 1.5 × IQR dos quartis Q1 e Q3
/// - Outliers extremos: valores além de 3.0 × IQR dos quartis Q1 e Q3
/// 
/// O método IQR é robusto e amplamente aceito na literatura estatística.
/// Outliers moderados são identificados mas mantidos na análise.
/// Outliers extremos são candidatos à remoção da amostra.
///
/// Parâmetros:
/// - data: slice de valores f64 para análise
/// - label: nome da métrica para logging detalhado
///
/// Retorna:
/// - Tupla contendo: (índices_outliers_moderados, índices_outliers_extremos, dados_limpos)
fn detect_outliers(data: &[f64], label: &str) -> (Vec<usize>, Vec<usize>, Vec<f64>) {
    let n = data.len();
    if n < 4 {
        println!("  [OUTLIERS] {}: Amostra muito pequena (n={}), sem detecção de outliers", label, n);
        return (vec![], vec![], data.to_vec());
    }
    
    // Ordena os dados para calcular quartis
    let mut sorted_data = data.to_vec();
    sorted_data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    // Calcula quartis
    let q1_idx = (n as f64 * 0.25) as usize;
    let q3_idx = (n as f64 * 0.75) as usize;
    let q1 = sorted_data[q1_idx];
    let q3 = sorted_data[q3_idx];
    let iqr = q3 - q1;
    
    // Limites para outliers
    // Outliers moderados: 1.5 × IQR
    let lower_bound = q1 - 1.5 * iqr;
    let upper_bound = q3 + 1.5 * iqr;

    // Outliers extremos: 3.0 × IQR
    let extreme_lower = q1 - 3.0 * iqr;
    let extreme_upper = q3 + 3.0 * iqr;
    
    // Detecta outliers
    let mut outliers = Vec::new();
    let mut extreme_outliers = Vec::new();
    let mut cleaned_data = Vec::new();
    
    // Itera sobre os dados e classifica os valores
    for (i, &value) in data.iter().enumerate() {
        // Verifica se o valor é um outlier moderado ou extremo
        if value < extreme_lower || value > extreme_upper {
            // Adiciona a lista de outliers extremos
            extreme_outliers.push(i);
        } else if value < lower_bound || value > upper_bound {
            // Adiciona a lista de outliers moderados
            outliers.push(i);
        } else {
            // Adiciona à lista de dados limpos
            cleaned_data.push(value);
        }
    }
    
    // Log dos resultados
    if !outliers.is_empty() || !extreme_outliers.is_empty() {
        println!("  [OUTLIERS] {}: Q1={:.3}, Q3={:.3}, IQR={:.3}", label, q1, q3, iqr);
        println!("  [OUTLIERS] {}: Outliers moderados: {} | Extremos: {}", 
                 label, outliers.len(), extreme_outliers.len());
        
        // Mostra alguns exemplos de outliers
        if !extreme_outliers.is_empty() {
            let extreme_values: Vec<f64> = extreme_outliers.iter().take(3)
                .map(|&i| data[i]).collect();
            println!("  [OUTLIERS] {}: Valores extremos: {:?}", label, extreme_values);
        }
    } else {
        println!("  [OUTLIERS] {}: Nenhum outlier detectado", label);
    }
    
    (outliers, extreme_outliers, cleaned_data)
}

/// Verifica se os dados seguem distribuição normal
/// 
/// Utiliza análise de momentos estatísticos para avaliar normalidade:
/// - Assimetria (skewness): mede simetria da distribuição
/// - Curtose (kurtosis): mede "peso" das caudas da distribuição
/// 
/// Critérios conservadores aplicados:
/// - |skewness| < 2.0: assimetria aceitável para normalidade
/// - |kurtosis| < 7.0: curtose aceitável para normalidade
/// 
/// Estes critérios são mais rigorosos que alguns métodos tradicionais,
/// garantindo maior confiabilidade na classificação de normalidade.
///
/// Parâmetros:
/// - data: slice de valores f64 para análise
/// - label: nome da métrica para logging detalhado
///
/// Retorna:
/// - bool: true se os dados seguem distribuição normal
fn check_normality(data: &[f64], label: &str) -> bool {
    let n = data.len();
    if n < 3 {
        println!("  [NORMALIDADE] {}: Amostra muito pequena (n={}), assumindo normalidade", label, n);
        return true;
    }
    
    // Calcula estatísticas básicas
    let mean = data.iter().sum::<f64>() / n as f64;
    let variance = data.iter().map(|x| (x - mean).powi(2)).sum::<f64>() / (n - 1) as f64;
    let std_dev = variance.sqrt();
    
    if std_dev == 0.0 {
        println!("  [NORMALIDADE] {}: Variância zero, assumindo normalidade", label);
        return true;
    }
    
    // Calcula assimetria (skewness) e curtose (kurtosis)
    let skewness = data.iter()
        .map(|x| ((x - mean) / std_dev).powi(3))
        .sum::<f64>() / n as f64;
    
    let kurtosis = data.iter()
        .map(|x| ((x - mean) / std_dev).powi(4))
        .sum::<f64>() / n as f64 - 3.0;
    
    // Critérios conservadores para normalidade
    let skew_ok = skewness.abs() < 2.0;  // Assimetria aceitável
    let kurt_ok = kurtosis.abs() < 7.0;  // Curtose aceitável
    
    let is_normal = skew_ok && kurt_ok;
    
    println!("  [NORMALIDADE] {}: Assimetria={:.3}, Curtose={:.3}, Normal={}", 
             label, skewness, kurtosis, is_normal);
    
    is_normal
}

/// Calcula estatísticas apropriadas baseadas na normalidade dos dados
/// 
/// Implementa pipeline completo de análise estatística adaptativa:
/// 1. Detecção de outliers usando método IQR
/// 2. Remoção seletiva de outliers extremos (mantém moderados)
/// 3. Verificação de normalidade nos dados tratados
/// 4. Aplicação de estatísticas paramétricas ou robustas conforme apropriado
/// 
/// Estratégia de tratamento de outliers:
/// - Outliers moderados: mantidos na análise (podem ser variação natural)
/// - Outliers extremos: removidos da análise (provavelmente erros de medição)
/// 
/// Seleção de estatísticas:
/// - Dados normais: média, desvio padrão, IC95 via z-score
/// - Dados não-normais: mediana, MAD, IC95 via percentis
///
/// Parâmetros:
/// - data: slice de valores f64 para análise
/// - label: nome da métrica para logging detalhado
///
/// Retorna:
/// - Stats com estatísticas apropriadas e metadados da análise
fn calculate_adaptive_stats(data: &[f64], label: &str) -> Stats {
    let original_size = data.len();
    
    // Passo 1: Detecta outliers usando método IQR
    let (outliers, extreme_outliers, cleaned_data) = detect_outliers(data, label);
    
    // Passo 2: Decide se usar dados limpos ou originais
    // Estratégia: remove apenas outliers EXTREMOS, mantém outliers moderados
    let data_for_analysis = if extreme_outliers.is_empty() {
        data.to_vec()
    } else {
        println!("  [DECISÃO] {}: Removendo {} outliers extremos para análise", label, extreme_outliers.len());
        cleaned_data.clone()
    };
    
    // Passo 3: Verifica normalidade nos dados tratados
    let is_normal = check_normality(&data_for_analysis, label);
    
    // Log dos outliers detectados
    let total_outliers = outliers.len() + extreme_outliers.len();
    
    // Passo 4: Calcula estatísticas apropriadas baseadas na normalidade
    if is_normal {
        println!("  [ESTATÍSTICAS] {}: Usando estatísticas paramétricas (média, desvio padrão)", label);
        let mut stats = calculate_parametric_stats(&data_for_analysis, total_outliers, extreme_outliers.len(), original_size);
        stats.is_normal = true;
        stats
    } else {
        println!("  [ESTATÍSTICAS] {}: Usando estatísticas robustas (mediana, MAD)", label);
        calculate_robust_stats(&data_for_analysis, total_outliers, extreme_outliers.len(), original_size)
    }
}

/// Função principal do experimento com verificação de normalidade
/// 
/// Esta função executa o experimento completo de desempenho criptográfico,
/// incluindo detecção de outliers, verificação de normalidade e aplicação
/// de estatísticas apropriadas para cada tipo de distribuição.
/// 
/// Retorna o nome do arquivo CSV com os resultados do experimento.
fn run_normality_aware_experiment() -> String {
    println!("=== EXPERIMENTO COM VERIFICAÇÃO DE NORMALIDADE ===");
    
    // Gera timestamp único para identificar o experimento
    let timestamp = chrono::Local::now().format("%Y%m%d_%H%M%S");
    let pasta_resultados = "../results";
    let filename = format!("{}/resultados_normality_check_{}.csv", pasta_resultados, timestamp);

    // Garante que a pasta de resultados existe
    if !Path::new(pasta_resultados).exists() {
        fs::create_dir_all(pasta_resultados).expect("Não foi possível criar a pasta de resultados");
    }

    // Abre arquivo CSV para escrita dos resultados
    let mut writer = OpenOptions::new()
        .create(true)
        .write(true)
        .truncate(true)
        .open(&filename)
        .expect("Não foi possível criar o arquivo de resultados");

    // Escreve cabeçalho do CSV com todas as métricas e informações estatísticas
    writeln!(
        writer,
        "cenario,padrao_trafego,acordo,cifra,num_msgs,msgs_por_rotacao,rotacoes,kem_ms_mean,kem_ms_std,kem_ms_ci95,cipher_ms_mean,cipher_ms_std,cipher_ms_ci95,kem_bw_mean,kem_bw_std,kem_bw_ci95,msg_bw_mean,msg_bw_std,msg_bw_ci95,text_msgs,image_msgs,file_msgs,system_msgs,kem_normal,cipher_normal,kem_bw_normal,msg_bw_normal,kem_stat_type,cipher_stat_type,kem_bw_stat_type,msg_bw_stat_type,kem_outliers,cipher_outliers,kem_bw_outliers,msg_bw_outliers,kem_extreme_outliers,cipher_extreme_outliers,kem_bw_extreme_outliers,msg_bw_extreme_outliers,kem_sample_size,cipher_sample_size,kem_bw_sample_size,msg_bw_sample_size"
    ).unwrap();

    // Define configurações experimentais
    let cenarios = vec![
        UsageScenario::SmallChat,
        UsageScenario::MediumGroup,
        UsageScenario::LargeChannel,
        UsageScenario::SystemChannel,
    ];
    
    let padroes_trafego = vec![
        TrafficPattern::Constant,
        TrafficPattern::Burst,
        TrafficPattern::Periodic,
        TrafficPattern::Random,
        TrafficPattern::Realistic,
    ];
    
    let acordos = vec!["Olm-Clássico", "Olm-Híbrido"];
    let cifragens = vec!["AES-GCM", "ChaCha20", "Megolm-Like"];

    let total_configs = cenarios.len() * padroes_trafego.len() * acordos.len() * cifragens.len();
    let mut config_count = 0;

    // Loop principal: executa todas as combinações experimentais
    // Itera sobre cenários, padrões de tráfego, acordos e cifragens
    // total_configs = 4 cenários * 5 padrões de tráfego * 2 acordos * 3 cifragens = 120 combinações
    for cenario in cenarios.iter() {
        for padrao in padroes_trafego.iter() {
            for acordo in acordos.iter() {
                for cipher_name in cifragens.iter() {
                    config_count += 1;
                    println!("\n{}/{}. Configuração: {:?} + {:?} + {} + {}", 
                             config_count, total_configs, cenario, padrao, acordo, cipher_name);
                    
                    // Obtém parâmetros específicos do cenário
                    // Define número de mensagens por rotação e total de mensagens
                    // Baseado na configuração do cenário
                    // Exemplo: SmallChat pode ter 10 mensagens por rotação, 100 no total
                    // MediumGroup pode ter 20 mensagens por rotação, 200 no total
                    // LargeChannel pode ter 50 mensagens por rotação, 500 no total
                    // SystemChannel pode ter 100 mensagens por rotação, 1000 no total
                    // Estes valores são configuráveis e podem ser ajustados conforme necessário
                    let msgs_por_rotacao = get_rotation_config(cenario); 
                    let num_messages = get_message_count_config(cenario);

                    // Inicializa vetores para coleta de métricas
                    let mut kem_times = Vec::with_capacity(REPETICOES);
                    let mut cipher_times = Vec::with_capacity(REPETICOES);
                    let mut kem_bws = Vec::with_capacity(REPETICOES);
                    let mut msg_bws = Vec::with_capacity(REPETICOES);
                    let mut total_rotations_per_run = 0;
                    let mut text_count = 0; 
                    let mut image_count = 0;
                    let mut file_count = 0;
                    let mut system_count = 0;

                    // Executa as repetições do experimento para esta configuração
                    for rep in 0..REPETICOES {
                        if rep % 10 == 0 {
                            println!("  Repetição {}/{}", rep + 1, REPETICOES);
                        }
                        
                        // Inicializa geradores de mensagens e tráfego
                        let mut message_gen = MessageGenerator::new(cenario.clone());
                        let mut traffic_gen = TrafficGenerator::new(padrao.clone());

                        // Gera chaves criptográficas baseadas no tipo de acordo
                        // Olm-Clássico usa apenas X25519, Olm-Híbrido usa Kyber768 + X25519
                        // Chaves são geradas aleatoriamente usando o gerador de números aleatórios do sistema
                        // Garante que as chaves sejam únicas e seguras para cada execução
                            
                        // Gera chaves Kyber para Bob, se necessário
                        // Olm-Híbrido usa Kyber768, então gera chaves públicas e secret
                        let (bob_pk_kyber, bob_sk_kyber) = if *acordo == "Olm-Híbrido" {
                            let (pk, sk) = keypair();
                            (Some(pk), Some(sk))
                        } 
                        // Olm-Clássico não usa Kyber, então chaves são None
                        else {
                            (None, None)
                        };
                        
                        // Gera chaves X25519 para Bob
                        let bob_x25519_secret = StaticSecret::random_from_rng(&mut rand::thread_rng());
                        let bob_x25519_public = X255PublicKey::from(&bob_x25519_secret);

                        // Inicializa estado do experimento
                        let mut current_key: [u8; 32] = [0u8; 32];
                        let mut last_rotation = Instant::now();
                        let mut total_kem_time = Duration::ZERO;
                        let mut total_kem_bandwidth = 0;
                        let mut total_msg_bandwidth = 0;
                        let mut total_rotations = 0;
                        let mut messages_processed = 0;

                        // Início do tempo de cifragem
                        let start_enc = Instant::now();  
                        
                        // Loop principal de processamento de mensagens
                        while messages_processed < num_messages {
                            let current_time = Instant::now();
                            
                            // Verifica se deve enviar mensagem baseado no padrão de tráfego
                            if traffic_gen.should_send_message(current_time) {
                                let time_since_last_rotation = current_time.duration_since(last_rotation);
                                
                                // Executa rotação de chave quando necessário
                                // Rotação ocorre se:
                                // - Número de mensagens processadas é múltiplo de msgs_por_rotacao
                                // - Ou se passaram 7 dias desde a última rotação
                                // Isso garante que as chaves sejam rotacionadas periodicamente
                                // e também após um número fixo de mensagens, dependendo do padrão de tráfego
                                if messages_processed % msgs_por_rotacao == 0 || 
                                    time_since_last_rotation >= Duration::from_secs(7 * 86400) {
                                    let start_kem = Instant::now();
                                    
                                    // Seleciona algoritmo de acordo de chaves
                                    let (shared_secret, kem_bandwidth) = if *acordo == "Olm-Clássico" {
                                        // Olm-Clássico: apenas X25519 ECDH
                                        let alice_secret = StaticSecret::random_from_rng(&mut rand::thread_rng());
                                        let shared_secret = alice_secret.diffie_hellman(&bob_x25519_public);
                                        let bandwidth = bob_x25519_public.as_bytes().len();
                                        (shared_secret.as_bytes().to_vec(), bandwidth)
                                    } else {
                                        // Olm-Híbrido: X25519 + Kyber768
                                        let alice_secret = StaticSecret::random_from_rng(&mut rand::thread_rng());
                                        let x25519_shared = alice_secret.diffie_hellman(&bob_x25519_public);
                                        
                                        let (kyber_shared, kyber_ct) = encapsulate(&bob_pk_kyber.as_ref().unwrap());
                                        let _kyber_decap = decapsulate(&kyber_ct, &bob_sk_kyber.as_ref().unwrap());
                                        
                                        let mut combined_secret = Vec::with_capacity(64);
                                        combined_secret.extend_from_slice(x25519_shared.as_bytes());
                                        combined_secret.extend_from_slice(kyber_shared.as_bytes());
                                        
                                        let bandwidth = bob_x25519_public.as_bytes().len() + 
                                                       kyber_ct.as_bytes().len() + 
                                                       bob_pk_kyber.as_ref().unwrap().as_bytes().len();
                                        (combined_secret, bandwidth)
                                    };
                                    
                                    // Atualiza chave e métricas
                                    current_key.copy_from_slice(&shared_secret[..32]);
                                    let elapsed_kem = start_kem.elapsed();
                                    total_kem_time += elapsed_kem;          // Tempo gasto na KEM
                                    total_rotations += 1;                   // Incrementa contador de rotações
                                    total_kem_bandwidth += kem_bandwidth;   // Atualiza largura de banda KEM
                                    last_rotation = current_time;           // Atualiza tempo da última rotação
                                }
                                
                                // Gera mensagem e executa cifragem
                                let message = message_gen.generate_message();
                                // Conta tipos de mensagens para estatísticas
                                match &message {
                                    MessageType::Text(_) => text_count += 1,
                                    MessageType::Image(_) => image_count += 1,
                                    MessageType::File(_) => file_count += 1,
                                    MessageType::System(_) => system_count += 1,
                                    MessageType::Voice(_) => text_count += 1,
                                }
                                
                                let plaintext = message_gen.get_message_bytes(&message);
                                // Baseado no nome da cifra, escolhe o algoritmo apropriado
                                // AES-GCM, ChaCha20 ou Megolm-Like (AES-CTR)
                                // Cada algoritmo é configurado com nonce/IV aleatório
                                // e a chave atual gerada pelo KEM
                                let (ciphertext, nonce_len, _): (Vec<u8>, usize, Vec<u8>) = match *cipher_name {
                                    "AES-GCM" => {
                                        let mut nonce = [0u8; 12];
                                        rand::thread_rng().fill_bytes(&mut nonce);
                                        let key = Key::<Aes256Gcm>::from_slice(&current_key);
                                        let cipher = Aes256Gcm::new(key);
                                        let ciphertext = cipher.encrypt(
                                            Nonce::from_slice(&nonce),
                                            aes_gcm::aead::Payload { msg: &plaintext, aad: b"" }
                                        ).expect("Erro na criptografia AES-GCM");
                                        (ciphertext, nonce.len(), nonce.to_vec())
                                    }
                                    "ChaCha20" => {
                                        let mut nonce = [0u8; 12];
                                        rand::thread_rng().fill_bytes(&mut nonce);
                                        let key = ChaKey::from_slice(&current_key);
                                        let cipher = ChaCha20Poly1305::new(key);
                                        let ciphertext = cipher.encrypt(
                                            ChaNonce::from_slice(&nonce),
                                            chacha20poly1305::aead::Payload { msg: &plaintext, aad: b"" }
                                        ).expect("Erro na criptografia ChaCha20");
                                        (ciphertext, nonce.len(), nonce.to_vec())
                                    }
                                    _ => {
                                        // Megolm-Like: AES-CTR
                                        let mut iv = [0u8; 16];
                                        rand::thread_rng().fill_bytes(&mut iv);
                                        let mut cipher = ctr::Ctr64BE::<Aes256>::new(&current_key.into(), &iv.into());
                                        let mut buffer = plaintext.clone();
                                        cipher.apply_keystream(&mut buffer);
                                        (buffer, iv.len(), iv.to_vec())
                                    }
                                };
                                
                                // Atualiza métricas de largura de banda
                                total_msg_bandwidth += ciphertext.len() + nonce_len;
                                messages_processed += 1;
                            }
                            
                            // Pequena pausa para simular processamento realista
                            //std::thread::sleep(Duration::from_millis(10));
                        }
                        
                        let total_enc_time = start_enc.elapsed();
                        
                        // Armazena resultados desta repetição
                        // Coleta tempos de KEM e cifragem, largura de banda e contadores de mensagens
                        kem_times.push(total_kem_time.as_secs_f64() * 1000.0);      // Tempo KEM em milissegundos
                        cipher_times.push(total_enc_time.as_secs_f64() * 1000.0);   // Tempo de cifragem em milissegundos
                        kem_bws.push(total_kem_bandwidth as f64);                   // Largura de banda KEM em bytes
                        msg_bws.push(total_msg_bandwidth as f64);                   // Largura de banda de mensagens em bytes
                        total_rotations_per_run = total_rotations;                  // Total de rotações nesta sessão
                    }
                    
                    // Executa análise estatística adaptativa nos dados coletados
                    println!("  Analisando normalidade e calculando estatísticas...");
                    let kem_time_stats = calculate_adaptive_stats(&kem_times, "KEM Times");
                    let cipher_time_stats = calculate_adaptive_stats(&cipher_times, "Cipher Times");
                    let kem_bw_stats = calculate_adaptive_stats(&kem_bws, "KEM Bandwidth");
                    let msg_bw_stats = calculate_adaptive_stats(&msg_bws, "Message Bandwidth");
                    
                    // Calcula médias dos contadores de tipos de mensagens
                    let total_repetitions = REPETICOES as f64;
                    let avg_text = text_count as f64 / total_repetitions;
                    let avg_image = image_count as f64 / total_repetitions;
                    let avg_file = file_count as f64 / total_repetitions;
                    let avg_system = system_count as f64 / total_repetitions;
                    
                    // Determina o tipo de estatística aplicado para cada métrica
                    let kem_stat_type = if kem_time_stats.is_normal { "parametric" } else { "robust" };
                    let cipher_stat_type = if cipher_time_stats.is_normal { "parametric" } else { "robust" };
                    let kem_bw_stat_type = if kem_bw_stats.is_normal { "parametric" } else { "robust" };
                    let msg_bw_stat_type = if msg_bw_stats.is_normal { "parametric" } else { "robust" };
                    
                    // Grava linha de resultados no arquivo CSV
                    writeln!(
                        writer,
                        "{:?},{:?},{},{},{},{},{},{:.4},{:.4},{:.4},{:.4},{:.4},{:.4},{:.2},{:.2},{:.2},{:.2},{:.2},{:.2},{:.1},{:.1},{:.1},{:.1},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
                        cenario, padrao, acordo, cipher_name, num_messages, msgs_por_rotacao,
                        total_rotations_per_run,
                        kem_time_stats.mean, kem_time_stats.std_dev, kem_time_stats.ci95,
                        cipher_time_stats.mean, cipher_time_stats.std_dev, cipher_time_stats.ci95,
                        kem_bw_stats.mean, kem_bw_stats.std_dev, kem_bw_stats.ci95,
                        msg_bw_stats.mean, msg_bw_stats.std_dev, msg_bw_stats.ci95,
                        avg_text, avg_image, avg_file, avg_system,
                        kem_time_stats.is_normal, cipher_time_stats.is_normal, 
                        kem_bw_stats.is_normal, msg_bw_stats.is_normal,
                        kem_stat_type, cipher_stat_type, kem_bw_stat_type, msg_bw_stat_type,
                        kem_time_stats.outliers_count, cipher_time_stats.outliers_count,
                        kem_bw_stats.outliers_count, msg_bw_stats.outliers_count,
                        kem_time_stats.extreme_outliers_count, cipher_time_stats.extreme_outliers_count,
                        kem_bw_stats.extreme_outliers_count, msg_bw_stats.extreme_outliers_count,
                        kem_time_stats.sample_size, cipher_time_stats.sample_size,
                        kem_bw_stats.sample_size, msg_bw_stats.sample_size
                    ).unwrap();
                }
            }
        }
    }
    
    // Finaliza experimento e exibe resumo
    println!("\n=== EXPERIMENTO COM ANÁLISE DE OUTLIERS E NORMALIDADE CONCLUÍDO ===");
    println!("Resultados salvos em: {}", filename);
    println!("Arquivo inclui informações sobre:");
    println!("  - Detecção de outliers (moderados e extremos)");
    println!("  - Verificação de normalidade");
    println!("  - Tipo de estatística aplicada");
    println!("  - Tamanho das amostras após limpeza");
    println!("\nSequência de análise aplicada:");
    println!("  1. Detecção de outliers (método IQR)");
    println!("  2. Remoção de outliers extremos (opcional)");
    println!("  3. Verificação de normalidade");
    println!("  4. Aplicação de estatísticas apropriadas");
    
    filename
}

/// Função para executar o script de geração de gráficos
/// 
/// Esta função executa o script Python responsável por gerar gráficos
/// dos resultados experimentais, incluindo análise de normalidade e outliers.
/// Tenta usar o ambiente virtual primeiro, com fallback para execução direta.
fn generate_plots() {
    println!("\nGerando gráficos dos resultados...");
    
    let venv_path = "../venv";
    let venv_python = format!("{}/bin/python", venv_path);
    let plot_script = "../analysis/gerar_graficos.py";
    
    // Verifica se o script de geração de gráficos existe
    if !Path::new(plot_script).exists() {
        println!("ERRO: Script de gráficos não encontrado: {}", plot_script);
        return;
    }
    
    // Tenta usar o ambiente virtual primeiro
    if Path::new(&venv_python).exists() {
        println!("  Usando ambiente virtual Python...");
        
        // Instala dependências necessárias para geração de gráficos
        let venv_pip = format!("{}/bin/pip", venv_path);
        let install_plot_deps = Command::new(&venv_pip)
            .arg("install")
            .arg("--quiet")
            .arg("matplotlib")
            .arg("seaborn")
            .arg("pandas")
            .arg("numpy")
            .output();
        
        match install_plot_deps {
            Ok(output) => {
                if !output.status.success() {
                    let stderr = String::from_utf8_lossy(&output.stderr);
                    println!("  AVISO: Problemas na instalação de dependências de gráficos: {}", stderr);
                }
            }
            Err(e) => {
                println!("  AVISO: Erro ao instalar dependências de gráficos: {}", e);
            }
        }
        
        // Executa script de gráficos com ambiente virtual
        let result = Command::new(&venv_python)
            .arg(plot_script)
            .current_dir("../analysis")
            .output();
        
        match result {
            Ok(output) => {
                if output.status.success() {
                    println!("  SUCESSO: Gráficos gerados com sucesso!");
                    println!("  Arquivos salvos em: ../plots/");
                    
                    let stdout = String::from_utf8_lossy(&output.stdout);
                    if !stdout.is_empty() {
                        println!("  Saída do script:");
                        for line in stdout.lines() {
                            println!("    {}", line);
                        }
                    }
                    return;
                } else {
                    println!("  AVISO: Erro ao gerar gráficos com venv:");
                    let stderr = String::from_utf8_lossy(&output.stderr);
                    println!("    {}", stderr);
                }
            }
            Err(e) => {
                println!("  AVISO: Erro ao executar script com venv: {}", e);
            }
        }
    }
    
    // Fallback: tenta executar sem ambiente virtual
    println!("  Tentando executar sem ambiente virtual...");
    let fallback_result = Command::new("python3")
        .arg(plot_script)
        .current_dir("../analysis")
        .output();
    
    match fallback_result {
        Ok(fallback_output) => {
            if fallback_output.status.success() {
                println!("  SUCESSO: Gráficos gerados com sucesso (fallback)!");
                println!("  Arquivos salvos em: ../plots/");
                
                let stdout = String::from_utf8_lossy(&fallback_output.stdout);
                if !stdout.is_empty() {
                    println!("  Saída do script:");
                    for line in stdout.lines() {
                        println!("    {}", line);
                    }
                }
            } else {
                println!("  ERRO: Falha no fallback:");
                let fallback_stderr = String::from_utf8_lossy(&fallback_output.stderr);
                println!("    {}", fallback_stderr);
                println!("  INFO: Verifique se as dependências Python estão instaladas:");
                println!("    pip install matplotlib seaborn pandas numpy");
            }
        }
        Err(e) => {
            println!("  ERRO: Erro ao executar fallback: {}", e);
        }
    }
}

/// Função main
/// 
/// Função principal que coordena todo o experimento de desempenho criptográfico.
/// Executa o experimento, análise estatística e geração de gráficos em sequência.
fn main() {
    println!("=== EXPERIMENTO DE DESEMPENHO CRIPTOGRÁFICO COM ANÁLISE ESTATÍSTICA ===");
    println!("Inicializando experimento");
    
    // Executa o experimento principal e obtém o nome do arquivo de resultados
    let results_filename = run_normality_aware_experiment();
    
    println!("\nExperimento concluído com sucesso!");
    println!("Análise estatística aplicada:");
    println!("  - Detecção de outliers: método IQR (1.5x e 3.0x)");
    println!("  - Remoção de outliers extremos quando necessário");
    println!("  - Verificação de normalidade: assimetria e curtose");
    println!("  - Dados normais: média, desvio padrão, IC95 (z-score)");
    println!("  - Dados não-normais: mediana, MAD, IC95 (percentis)");
    
    // Lista arquivos gerados
    println!("\nArquivos gerados:");
    println!("  - CSV de resultados: {}", results_filename);
    
    // Executa geração de gráficos
    generate_plots();
}