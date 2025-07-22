# Módulo de Workload Realista para Experimentos Matrix-PQC

Este módulo implementa a geração de workloads sintéticos e realistas para simulação de cenários, padrões de tráfego e tipos de mensagens em experimentos de desempenho criptográfico no contexto do protocolo Matrix.

## Fundamentação Acadêmica

O workload é fundamentado em estudos empíricos e acadêmicos sobre aplicações de mensagens instantâneas, incluindo:
- Seufert et al. (2023, 2015): Análise de 76 milhões de mensagens do WhatsApp
- Xiao et al. (2007): Caracterização de tráfego AIM/MSN
- Keshvadi et al. (2020): Tráfego de Facebook Messenger, Hangouts, Snapchat, WeChat
- Zhang et al. (2015): Consumo de energia e largura de banda
- Deng et al. (2017): Padrões temporais e tipos de mensagens no WeChat
- Rammos et al. (2021): Impacto energético de padrões burst/regular

## Funcionalidades

- **Cenários de Uso**: SmallChat, MediumGroup, LargeChannel, SystemChannel
- **Padrões de Tráfego**: Constant, Burst, Periodic, Random, Realistic
- **Tipos de Mensagem**: Texto, Imagem, Arquivo, Sistema, Voz
- **Distribuição Realista**: Proporções e tamanhos baseados em dados reais
- **Rotação de Chaves**: Intervalos adaptados ao cenário
- **Simulação de Energia**: Modo burst/regular para análise energética

## Estruturas Principais

- `MessageType`: Enum para tipos de mensagem (Text, Image, File, System, Voice)
- `TrafficPattern`: Enum para padrões de tráfego
- `UsageScenario`: Enum para cenários de uso
- `MessageGenerator`: Gera mensagens realistas conforme cenário
- `TrafficGenerator`: Simula ritmo de envio conforme padrão
- `get_rotation_config`: Retorna intervalo de rotação de chave por cenário
- `get_message_count_config`: Retorna número de mensagens por cenário

## Exemplos de Distribuição

- **SmallChat**: 85% texto, 12% imagem, 3% voz
- **MediumGroup**: 70% texto, 18% imagem, 7% arquivo, 5% voz
- **LargeChannel**: 60% texto, 22% imagem, 8% arquivo, 10% sistema
- **SystemChannel**: 25% texto, 50% sistema, 15% arquivo, 10% imagem

## Tamanhos Realistas
- Texto: 10-500 caracteres
- Imagem: 15KB-1MB
- Arquivo: 10KB-10MB
- Voz: 3-60s (~6KB/s)

## Padrões de Tráfego
- **Constant**: Mensagens a cada 100ms
- **Burst**: Rajadas rápidas com pausas (inspirado em testes energéticos)
- **Periodic**: Atividade cíclica (heartbeat)
- **Random**: Probabilidade fixa de envio
- **Realistic**: Combinação temporal para simular uso real

## Como Usar

1. Instancie um `MessageGenerator` com o cenário desejado:
   ```rust
   let mut gen = MessageGenerator::new(UsageScenario::MediumGroup);
   let msg = gen.generate_message();
   ```
2. Instancie um `TrafficGenerator` com o padrão desejado:
   ```rust
   let mut traffic = TrafficGenerator::new(TrafficPattern::Burst);
   let should_send = traffic.should_send_message(Instant::now());
   ```
3. Use `get_rotation_config` e `get_message_count_config` para definir parâmetros do experimento:
   ```rust
   let rot_interval = get_rotation_config(&UsageScenario::LargeChannel);
   let msg_count = get_message_count_config(&UsageScenario::LargeChannel);
   ```

## Extensibilidade

O módulo pode ser facilmente adaptado para novos cenários, padrões ou tipos de mensagem, bastando ajustar as distribuições e enums.

## Referências
Consulte os comentários do código para detalhes e citações acadêmicas.

---
**Autor:** Marcos Dantas Ortiz
**Data:** Julho de 2025
