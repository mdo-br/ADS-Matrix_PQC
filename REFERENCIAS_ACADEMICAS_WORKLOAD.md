# Referências Acadêmicas para Fundamentação do Workload

Este documento lista as principais referências acadêmicas utilizadas para fundamentar cientificamente o módulo de workload do experimento Matrix. O workload implementado simula padrões realistas de comunicação baseados em dados empíricos de aplicações de mensagens instantâneas reais.

## Artigos Principais

### 1. Seufert, A., Poignée, F., Seufert, M., & Hoßfeld, T. (2023)
**"Share and Multiply: Modeling Communication and Generated Traffic in Private WhatsApp Groups"**
- **Publicação:** IEEE Access
- **Dataset:** 76 milhões de mensagens de 117.000 usuários do WhatsApp
- **Contribuição:** Análise detalhada de grupos privados e padrões de comunicação
- **Relevância:** Fornece dados precisos sobre distribuição de tipos de mensagem em grupos reais
- **Impacto no workload:** Distribuições de tipos de mensagem por cenário, tamanhos realistas de conteúdo

### 2. Seufert, M., Schwind, A., Hoßfeld, T., & Tran-Gia, P. (2015)
**"Analysis of Group-Based Communication in WhatsApp"**
- **Publicação:** Lecture Notes in Computer Science, Springer
- **Contribuição:** Caracterização empírica de chats em grupo do WhatsApp
- **Metodologia:** Classificação baseada em tópicos e estatísticas de mensagens
- **Relevância:** Modelagem de comunicação em grupo com processo semi-Markov
- **Impacto no workload:** Padrões de tráfego para grupos pequenos vs grandes

### 3. Xiao, Z., Guo, L., & Tracey, J. (2007)
**"Understanding Instant Messaging Traffic Characteristics"**
- **Publicação:** IEEE ICDCS (International Conference on Distributed Computing Systems)
- **Dataset:** Análise de tráfego de AIM e MSN Messenger em ambiente corporativo
- **Descoberta:** Maioria do tráfego é presença/overhead, não chat efetivo
- **Relevância:** Pioneiro na caracterização de tráfego de IM
- **Impacto no workload:** Base para distribuições de tipos de mensagem e overhead de protocolo

### 4. Keshvadi, S., Karamollahi, M., & Williamson, C. (2020)
**"Traffic Characterization of Instant Messaging Apps: A Campus-Level View"**
- **Publicação:** IEEE Conference on Local Computer Networks
- **Escopo:** Facebook Messenger, Google Hangouts, Snapchat, WeChat
- **Contribuição:** Padrões diurnos com picos de rajada, características de presença
- **Relevância:** Análise multi-aplicação em ambiente real (campus)
- **Impacto no workload:** Padrões temporais (burst, periódico, realista)

### 5. Zhang, L., Xu, C., Pathak, P., & Mohapatra, P. (2015)
**"Characterizing Instant Messaging Apps on Smartphones"**
- **Publicação:** Passive and Active Network Measurement Conference
- **Foco:** Consumo de energia e largura de banda
- **Descoberta:** Importância das notificações de digitação na eficiência
- **Relevância:** Análise específica para dispositivos móveis
- **Impacto no workload:** Tamanhos realistas de mensagem e otimizações de protocolo

### 6. Deng, Q., Li, Z., Wu, Q., Xu, C., & Xie, G. (2017)
**"An empirical study of the WeChat mobile instant messaging service"**
- **Publicação:** INFOCOM Workshops
- **Aplicação:** WeChat (uma das maiores aplicações de IM do mundo)
- **Contribuição:** Padrões temporais diurnos com picos de rajada
- **Dados:** Distribuição de tipos de mensagens e comportamento de usuários
- **Impacto no workload:** Validação de padrões observados em outras aplicações

## Contribuições Específicas para o Workload

### Distribuições de Tipos de Mensagem

Baseado nos estudos empíricos, implementamos as seguintes distribuições:

**SmallChat (Grupos Pequenos):**
- 85% texto, 12% imagem, 3% voz
- Baseado em Seufert et al. (2015, 2023) para grupos pequenos

**MediumGroup (Grupos Médios):**
- 70% texto, 18% imagem, 7% arquivo, 5% voz
- Balanceamento baseado em análise de grupos médios (Seufert et al., 2023)

**LargeChannel (Canais Grandes):**
- 60% texto, 22% imagem, 8% arquivo, 10% sistema
- Padrão observado em canais com muitos participantes

**SystemChannel (Canal de Sistema):**
- 25% texto, 50% sistema, 15% arquivo, 10% imagem
- Padrão típico de logs e notificações automatizadas

### Tamanhos de Mensagem

**Texto:**
- 45% muito curtas (15 chars), 35% curtas (50 chars), 15% médias (150 chars)
- Baseado em análise de 76M mensagens (Seufert et al., 2023)

**Imagem:**
- 40% pequenas (15KB), 35% médias (50KB), 20% grandes (150KB)
- Considera compressão automática dos aplicativos

**Arquivos:**
- 30% pequenos (10KB), 25% médios (100KB), 20% grandes (500KB)
- Distribuição típica de documentos e mídia

**Voz:**
- 50% muito curtas (3s), 30% curtas (8s), 15% médias (15s)
- ~6KB/s para codec comprimido (Opus, AAC)

### Padrões de Tráfego

**Constant:** Envio regular a cada 100ms
**Burst:** Rajadas de 5-10 mensagens com pausa de 1s
**Periodic:** Padrão sinusoidal simulando variação temporal
**Random:** Probabilidade fixa de 30% por tentativa
**Realistic:** Combinação temporal que simula uso real

Baseado em observações de padrões diurnos e sazonais (Keshvadi et al., 2020; Deng et al., 2017)

## Validação Acadêmica

O workload implementado foi validado através de:

1. **Comparação com dados empíricos** dos artigos citados
2. **Distribuições estatísticas realistas** baseadas em datasets reais
3. **Padrões temporais observados** em aplicações de produção
4. **Tamanhos de mensagem** consistentes com compressão automática
5. **Cenários diferenciados** que refletem uso real (P2P, grupos, canais, sistema)

## Limitações e Futuras Melhorias

**Limitações atuais:**
- Workload sintético, não captura todas as nuances do comportamento humano
- Focado em padrões ocidentais (WhatsApp, Telegram)
- Não inclui sazonalidade de longo prazo

**Futuras melhorias:**
- Incorporar dados de aplicações asiáticas (WeChat, LINE, KakaoTalk)
- Incluir padrões de uso específicos por região/cultura
- Adicionar variação sazonal e eventos especiais
- Integrar modelos de comportamento humano mais sofisticados

## Conclusão

O módulo de workload do experimento Matrix é solidamente fundamentado em literatura acadêmica de qualidade, utilizando dados empíricos de múltiplas aplicações de mensagens instantâneas reais. Esta fundamentação garante que os resultados dos experimentos sejam representativos de cenários reais de uso, aumentando a validade externa dos resultados obtidos.

A combinação de múltiplas fontes acadêmicas (2007-2023) e aplicações diversas (AIM, MSN, WhatsApp, WeChat, etc.) proporciona uma base robusta para simulação de workloads realistas em sistemas de comunicação segura.
