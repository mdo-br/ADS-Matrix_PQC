# Estrutura do Arquivo CSV de Resultados

Este repositório contém o arquivo `resultados_normality_check_20250716_202824.csv`, que armazena os dados brutos dos experimentos estatísticos realizados no projeto Matrix.

## Descrição das Colunas

O arquivo CSV possui as seguintes colunas principais:

- **acordo**: Tipo de protocolo de acordo de chaves utilizado (`Olm-Clássico`, `Olm-Híbrido`).
- **cenario**: Cenário de uso simulado (`SmallChat`, `MediumGroup`, `LargeChannel`, `SystemChannel`).
- **padrao_trafego**: Padrão de tráfego aplicado (`Constant`, `Burst`, `Periodic`, `Random`, `Realistic`).
- **cifra**: Algoritmo de cifra simétrica utilizado (`AES-GCM`, `ChaCha20`, `Megolm-Like`).
- **num_msgs**: Número de mensagens processadas na sessão.
- **rotacoes**: Número de rotações de chave realizadas.
- **kem_ms_mean**: Latência média (em milissegundos) do acordo de chaves (KEM).
- **kem_ms_ci95**: Intervalo de confiança de 95% para a latência média do KEM.
- **kem_bw_mean**: Largura de banda média (em bytes) do acordo de chaves.
- **cipher_ms_mean**: Latência média (em milissegundos) da cifragem simétrica.
- **cipher_ms_ci95**: Intervalo de confiança de 95% para a latência média da cifragem.
- **msg_bw_mean**: Largura de banda média (em bytes) das mensagens cifradas.
- **outlier_kem_ms_mean**: Indicador de outlier para latência KEM.
- **outlier_cipher_ms_mean**: Indicador de outlier para latência de cifragem.
- **outlier_kem_bw_mean**: Indicador de outlier para largura de banda KEM.
- **outlier_msg_bw_mean**: Indicador de outlier para largura de banda das mensagens.

## Exemplo de Linha

```
acordo,cenario,padrao_trafego,cifra,num_msgs,rotacoes,kem_ms_mean,kem_ms_ci95,kem_bw_mean,cipher_ms_mean,cipher_ms_ci95,msg_bw_mean,outlier_kem_ms_mean,outlier_cipher_ms_mean,outlier_kem_bw_mean,outlier_msg_bw_mean
Olm-Clássico,SmallChat,Constant,AES-GCM,100,1,0.23,0.02,32,0.15,0.01,1200,0,0,0,0
```

## Observações

- Cada linha representa uma configuração experimental única.
- Os valores de latência e largura de banda são médias calculadas sobre múltiplas repetições.
- Os campos de intervalo de confiança permitem avaliar a variabilidade dos resultados.
- Os indicadores de outlier auxiliam na análise estatística e validação dos dados.

## Utilização

O arquivo pode ser utilizado para análises estatísticas, geração de gráficos, validação de hipóteses e replicação dos experimentos descritos no artigo acadêmico do projeto.

Para dúvidas sobre os campos ou para replicar os experimentos, consulte o artigo ou os scripts de análise disponíveis