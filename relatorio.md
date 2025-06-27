# Relatório Técnico - Tech UniSenac Server

**Data do Relatório:** 27 de Junho de 2025  
**Versão do Sistema:** 1.0 - Versão Básica  
**Ambiente:** Python 3.x com suporte a bibliotecas Rich e Questionary

---

## 1. Resumo Executivo

O Tech UniSenac Server é um sistema educacional que implementa um servidor Telnet básico com cliente rico em Python. O projeto demonstra conceitos fundamentais de programação em rede, incluindo sockets, threading, protocolos de comunicação e interfaces de usuário avançadas.

### 1.1 Objetivos Alcançados

- ✅ Servidor multi-cliente funcional
- ✅ Interface de cliente rica e interativa
- ✅ Sistema de comandos robusto
- ✅ Estatísticas em tempo real
- ✅ Tratamento de erros abrangente
- ✅ Documentação completa

### 1.2 Métricas do Projeto

- **Linhas de código:** ~1500+ linhas
- **Arquivos principais:** 4
- **Comandos implementados:** 8
- **Funcionalidades:** 15+

---

## 2. Arquitetura Técnica

### 2.1 Visão Geral da Arquitetura

```
┌─────────────────┐    TCP/Socket    ┌─────────────────┐
│   Cliente Rich  │ ◄──────────────► │     Servidor    │
│  (cliente_rich) │                  │ (tech_unisenac) │
└─────────────────┘                  └─────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────┐                  ┌─────────────────┐
│  Interface UI   │                  │   Threading     │
│  (Rich/Panel)   │                  │   (Multi-user)  │
└─────────────────┘                  └─────────────────┘
```

### 2.2 Componentes do Servidor (`tech_unisenac.py`)

#### 2.2.1 Classes e Estruturas

```python
class Colors:
    # Sistema de cores para terminal
    RESET, GREEN, YELLOW, BLUE, RED, CYAN
```

#### 2.2.2 Estruturas de Dados Globais

```python
connected_clients = {}  # Dicionário de clientes conectados
server_stats = {        # Estatísticas do servidor
    'total_connections': 0,
    'commands_executed': 0
}
```

#### 2.2.3 Funções Principais

| Função                  | Responsabilidade             | Parâmetros      |
| ----------------------- | ---------------------------- | --------------- |
| `start_server()`        | Inicializa o servidor socket | host, port      |
| `handle_client()`       | Gerencia sessão do cliente   | socket, address |
| `process_command()`     | Processa comandos recebidos  | data, address   |
| `print_server_banner()` | Exibe banner do servidor     | -               |

#### 2.2.4 Sistema de Comandos

| Comando  | Função         | Descrição Técnica                            |
| -------- | -------------- | -------------------------------------------- |
| `help`   | `cmd_help()`   | Lista comandos com formatação colorida       |
| `status` | `cmd_status()` | Retorna métricas do servidor em tempo real   |
| `users`  | `cmd_users()`  | Enumera clientes conectados com estatísticas |
| `ping`   | `cmd_ping()`   | Simula teste de conectividade com latência   |
| `time`   | `cmd_time()`   | Retorna timestamp formatado                  |
| `whoami` | `cmd_whoami()` | Informações da sessão atual                  |
| `uptime` | `cmd_uptime()` | Calcula tempo de atividade do servidor       |

### 2.3 Componentes do Cliente (`cliente_rich.py`)

#### 2.3.1 Classe Principal

```python
class TechUnisenacClient:
    def __init__(self):
        self.console = Console()  # Rich console
        self.socket = None        # Socket de conexão
        self.connected = False    # Status de conexão
        # ... outros atributos
```

#### 2.3.2 Funcionalidades Avançadas

##### Interface Rica

- **Painéis:** Layout organizado com bordas
- **Tabelas:** Dados estruturados
- **Cores:** Sistema de highlight
- **Alinhamento:** Centralização automática

##### Sistema de Notas

```python
self.session_notes = []  # Lista de notas da sessão
```

##### Estatísticas de Sessão

```python
self.session_stats = {
    'commands_sent': 0,
    'messages_received': 0,
    'bytes_sent': 0,
    'bytes_received': 0
}
```

---

## 3. Protocolo de Comunicação

### 3.1 Fluxo de Conexão

```
Cliente                          Servidor
   │                                │
   │─────── TCP Connect ──────────►│
   │◄────── Welcome Message ──────│
   │◄───── "Digite um comando:" ───│
   │                                │
   │────── Comando + \r\n ────────►│
   │◄───── Resposta + Prompt ─────│
   │                                │
   │────── "quit" ─────────────────►│
   │◄────── Goodbye Message ──────│
   │◄────── Connection Close ─────│
```

### 3.2 Formato de Mensagens

#### 3.2.1 Comandos do Cliente

```
FORMATO: comando [argumentos]\r\n
EXEMPLO: ping google.com\r\n
```

#### 3.2.2 Respostas do Servidor

```
FORMATO: [CATEGORIA] CONTEÚDO\n\nDigite um comando:
EXEMPLO: [PING] TESTE DE CONECTIVIDADE\nHost: google.com\n\nDigite um comando:
```

### 3.3 Parsing de Comandos

O servidor implementa um sistema robusto de parsing:

```python
buffer = ""
while True:
    data = client_socket.recv(256).decode('utf-8', errors='ignore')
    buffer += data

    while '\n' in buffer or '\r' in buffer:
        if '\r\n' in buffer:
            command, buffer = buffer.split('\r\n', 1)
        elif '\n' in buffer:
            command, buffer = buffer.split('\n', 1)
        else:
            command, buffer = buffer.split('\r', 1)
```

---

## 4. Análise de Segurança

### 4.1 Vulnerabilidades Identificadas

#### 4.1.1 Críticas

- **Sem Autenticação:** Qualquer usuário pode conectar
- **Protocolo em Texto Plano:** Dados não criptografados
- **Sem Autorização:** Todos os comandos disponíveis para todos

#### 4.1.2 Moderadas

- **Buffer Overflow Potencial:** Recv limitado a 256 bytes
- **DoS por Conexões:** Limite de 10 conexões simultâneas
- **Logs Expostos:** Informações sensíveis em logs

### 4.2 Mitigações Implementadas

#### 4.2.1 Tratamento de Erros

```python
try:
    # Operação de rede
except socket.timeout:
    continue
except Exception as e:
    error_msg = f"{Colors.RED}[ERRO]{Colors.RESET} {e}\n\n"
```

#### 4.2.2 Validação de Entrada

```python
command = command.strip()
if not command:
    continue
```

#### 4.2.3 Limpeza de Recursos

```python
finally:
    if client_address in connected_clients:
        del connected_clients[client_address]
    client_socket.close()
```

---

## 5. Performance e Escalabilidade

### 5.1 Métricas de Performance

#### 5.1.1 Servidor

- **Conexões Simultâneas:** Até 10 clientes
- **Threading:** 1 thread por cliente
- **Latência:** < 100ms para comandos simples
- **Throughput:** Limitado pela rede local

#### 5.1.2 Cliente

- **Responsividade:** Interface em tempo real
- **Memória:** ~50 mensagens em buffer
- **Histórico:** 100 comandos armazenados

### 5.2 Limitações de Escalabilidade

#### 5.2.1 Servidor

- **Threading Model:** Não adequado para alta concorrência
- **Memória:** Crescimento linear com número de clientes
- **CPU:** Processamento síncrono de comandos

#### 5.2.2 Possíveis Melhorias

- **Async/Await:** Para maior concorrência
- **Pool de Threads:** Limite fixo de threads
- **Cache:** Para comandos frequentes
- **Load Balancing:** Para múltiplas instâncias

---

## 6. Qualidade do Código

### 6.1 Métricas de Qualidade

#### 6.1.1 Estrutura

- **Modularidade:** ✅ Funções bem definidas
- **Reutilização:** ✅ Funções utilitárias
- **Organização:** ✅ Separação clara de responsabilidades

#### 6.1.2 Padrões de Codificação

- **PEP 8:** ✅ Majoritariamente seguido
- **Documentação:** ⚠️ Comentários básicos
- **Type Hints:** ❌ Não implementado

#### 6.1.3 Tratamento de Erros

- **Exception Handling:** ✅ Abrangente
- **Graceful Degradation:** ✅ Implementado
- **Error Messages:** ✅ Informativos

### 6.2 Pontos de Melhoria

#### 6.2.1 Documentação

```python
# ATUAL
def cmd_ping(args):
    host = args[0] if args else 'google.com'

# MELHORADO
def cmd_ping(args: List[str]) -> str:
    """
    Executa teste de ping simulado.

    Args:
        args: Lista de argumentos, onde args[0] é o host

    Returns:
        String formatada com resultado do ping
    """
```

#### 6.2.2 Configurabilidade

```python
# ATUAL: Valores hard-coded
server_socket.listen(10)

# MELHORADO: Configurável
MAX_CONNECTIONS = config.get('max_connections', 10)
server_socket.listen(MAX_CONNECTIONS)
```

---

## 7. Testes e Validação

### 7.1 Cenários de Teste Executados

#### 7.1.1 Testes Funcionais

- ✅ Conexão única cliente-servidor
- ✅ Múltiplos clientes simultâneos
- ✅ Todos os comandos funcionais
- ✅ Desconexão graceful

#### 7.1.2 Testes de Stress

- ✅ 10 clientes simultâneos
- ✅ Comandos em sequência rápida
- ✅ Desconexões abruptas
- ✅ Restart do servidor

#### 7.1.3 Testes de Compatibilidade

- ✅ Windows 10/11
- ✅ Cliente Rich functional
- ✅ Telnet padrão
- ✅ Python 3.7+

### 7.2 Bugs Conhecidos

#### 7.2.1 Menores

- Interface pode "quebrar" com terminal muito pequeno
- Encoding issues em alguns sistemas
- Performance degradada com muitos comandos

#### 7.2.2 Workarounds

- Usar terminal com resolução adequada
- Configurar encoding UTF-8
- Restart periódico em uso intenso

---

## 8. Deployment e Operação

### 8.1 Requisitos de Sistema

#### 8.1.1 Servidor

- **SO:** Windows, Linux, macOS
- **Python:** 3.7 ou superior
- **RAM:** Mínimo 64MB
- **Rede:** Porta 2323 disponível

#### 8.1.2 Cliente

- **SO:** Windows, Linux, macOS
- **Python:** 3.7 ou superior
- **Dependências:** rich, questionary
- **Terminal:** Suporte a cores

### 8.2 Procedimentos de Instalação

#### 8.2.1 Setup Básico

```bash
# 1. Clonar/baixar arquivos
# 2. Instalar dependências
pip install rich questionary

# 3. Executar servidor
python tech_unisenac.py

# 4. Executar cliente
python cliente_rich.py
```

#### 8.2.2 Configuração de Rede

Para acesso externo:

```python
# Modificar em tech_unisenac.py
host = '0.0.0.0'  # Ao invés de '127.0.0.1'
```

### 8.3 Monitoramento

#### 8.3.1 Logs do Servidor

O servidor produz logs coloridos para:

- Novas conexões
- Desconexões
- Erros de rede
- Comandos executados

#### 8.3.2 Estatísticas

Disponíveis via comando `status`:

- Uptime do servidor
- Total de conexões
- Comandos executados
- Usuários ativos

---

## 9. Casos de Uso Educacionais

### 9.1 Para Disciplinas

#### 9.1.1 Redes de Computadores

- **Conceitos:** TCP/IP, Socket Programming
- **Prática:** Cliente-servidor, protocolos
- **Demonstração:** Handshake, conexão, dados

#### 9.1.2 Programação

- **Threading:** Múltiplas conexões
- **Exception Handling:** Robustez
- **Design Patterns:** Modularidade

#### 9.1.3 Sistemas Operacionais

- **Processos:** Threading vs. Forking
- **IPC:** Inter-process communication
- **I/O:** Non-blocking operations

### 9.2 Exercícios Propostos

#### 9.2.1 Básicos

1. Adicionar novo comando personalizado
2. Modificar mensagens do sistema
3. Alterar cores e formatação

#### 9.2.2 Intermediários

1. Implementar autenticação simples
2. Adicionar logging em arquivo
3. Criar comando de transferência de arquivo

#### 9.2.3 Avançados

1. Implementar criptografia básica
2. Adicionar banco de dados
3. Criar interface web para monitoramento

---

## 10. Conclusões e Recomendações

### 10.1 Objetivos Alcançados

O projeto Tech UniSenac Server cumpriu com sucesso seus objetivos educacionais:

1. **Demonstração Prática:** Implementou conceitos de rede de forma tangível
2. **Interface Rica:** Proporcionou experiência de usuário moderna
3. **Código Didático:** Estrutura clara e compreensível
4. **Funcionalidade Completa:** Sistema operacional e estável

### 10.2 Pontos Fortes

- **Simplicidade:** Fácil de entender e modificar
- **Robustez:** Tratamento adequado de erros
- **Documentação:** README e relatório completos
- **Flexibilidade:** Configurável e extensível

### 10.3 Áreas de Melhoria

#### 10.3.1 Curto Prazo

- Adicionar type hints
- Melhorar documentação inline
- Implementar testes automatizados
- Configuração via arquivo

#### 10.3.2 Longo Prazo

- Migrar para async/await
- Adicionar autenticação
- Implementar protocolo binário
- Interface web de administração

### 10.4 Aplicações Futuras

Este projeto serve como base sólida para:

- Projetos mais complexos de rede
- Estudos de protocolos avançados
- Implementação de serviços reais
- Demonstrações acadêmicas

### 10.5 Valor Educacional

O Tech UniSenac Server oferece:

- **Aprendizado Prático:** Experiência hands-on com sockets
- **Conceitos Fundamentais:** Base sólida em programação de rede
- **Boas Práticas:** Exemplos de código limpo e organizado
- **Extensibilidade:** Plataforma para experimentação

---

**Fim do Relatório Técnico**
