# Tech UniSenac Server 🚀

Um sistema simples de servidor Telnet desenvolvido em Python para fins educacionais, com cliente rico usando Rich library para interface aprimorada.

## 📋 Visão Geral

O Tech UniSenac Server é um projeto educacional que demonstra os conceitos básicos de programação em rede, sockets, threading e comunicação cliente-servidor. O sistema inclui um servidor telnet robusto e um cliente com interface rica e colorida.

## 🏗️ Arquitetura do Projeto

```
Servidor/
├── tech_unisenac.py         # Servidor principal
├── cliente_rich.py          # Cliente com interface Rich
├── cliente_rich.bat         # Script de inicialização do cliente (Windows)
├── requirements.txt         # Dependências principais
├── requirements-dev.txt     # Dependências de desenvolvimento
├── instalar_dependencias.bat # Instalador automático (Windows)
├── instalar_dependencias.sh  # Instalador automático (Linux/macOS)
├── notas_sessao_*.txt       # Arquivos de notas de sessão
├── README.md                # Este arquivo
└── relatorio.md             # Relatório técnico detalhado
```

## ✨ Funcionalidades

### 🖥️ Servidor (tech_unisenac.py)

- **Servidor multi-threaded**: Suporta múltiplos clientes simultaneamente
- **Sistema de comandos**: Interface de linha de comando intuitiva
- **Estatísticas em tempo real**: Monitora conexões e comandos
- **Sistema de usuários**: Gerenciamento básico de sessões
- **Interface colorida**: Logs coloridos para melhor visualização

### 🎨 Cliente Rich (cliente_rich.py)

- **Interface moderna**: Usando a biblioteca Rich para UI avançada
- **Painel de controle**: Dashboard interativo
- **Histórico de comandos**: Armazena comandos executados
- **Notas de sessão**: Sistema de anotações
- **Estatísticas**: Métricas de conexão e uso

## 🚀 Como Usar

### Pré-requisitos

- Python 3.7+
- Biblioteca Rich (para o cliente)
- Biblioteca Questionary (para o cliente)

### Instalação das Dependências

#### Método 1: Usando requirements.txt (Recomendado)

```bash
pip install -r requirements.txt
```

#### Método 2: Usando scripts de instalação

**Windows:**

```bash
instalar_dependencias.bat
```

**Linux/macOS:**

```bash
chmod +x instalar_dependencias.sh
./instalar_dependencias.sh
```

#### Método 3: Instalação manual

```bash
pip install rich questionary
```

#### Para Desenvolvimento

```bash
pip install -r requirements-dev.txt
```

### Iniciando o Servidor

#### Método 1: Execução Direta

```bash
python tech_unisenac.py
```

#### Método 2: Com Parâmetros

```bash
python tech_unisenac.py [host] [porta]
```

Exemplo:

```bash
python tech_unisenac.py 0.0.0.0 2323
```

### Iniciando o Cliente

#### Método 1: Cliente Rich (Recomendado)

```bash
python cliente_rich.py
```

#### Método 2: Usando o Batch (Windows)

```bash
cliente_rich.bat
```

#### Método 3: Telnet Padrão

```bash
telnet 127.0.0.1 2323
```

## 📝 Comandos Disponíveis

| Comando              | Descrição                           |
| -------------------- | ----------------------------------- |
| `help`               | Lista todos os comandos disponíveis |
| `status`             | Mostra o status do servidor         |
| `users`              | Lista usuários conectados           |
| `ping [host]`        | Teste de conectividade              |
| `time`               | Mostra data e hora atual            |
| `whoami`             | Informações do usuário atual        |
| `uptime`             | Tempo de atividade do servidor      |
| `quit/exit/sair/bye` | Desconectar do servidor             |

## 🛠️ Configuração

### Servidor

O servidor pode ser configurado através de:

- **Host padrão**: 127.0.0.1
- **Porta padrão**: 2323
- **Máximo de conexões**: 10
- **Timeout de socket**: Configurável

### Cliente Rich

- **Auto-reconexão**: Disponível
- **Histórico de comandos**: Até 100 comandos
- **Buffer de mensagens**: Até 50 mensagens
- **Notas de sessão**: Salvamento automático

## 🔧 Estrutura Técnica

### Classes Principais

#### Servidor (tech_unisenac.py)

- `Colors`: Classe para cores no terminal
- Funções de comando: `cmd_help()`, `cmd_status()`, etc.
- Sistema de threading para múltiplos clientes
- Buffer de comandos com parsing linha por linha

#### Cliente (cliente_rich.py)

- `TechUnisenacClient`: Classe principal do cliente
- Interface Rich com painéis e tabelas
- Sistema de notas e histórico
- Estatísticas de sessão

## 📊 Funcionalidades Avançadas

### Sistema de Estatísticas

- Total de conexões
- Comandos executados
- Tempo de uptime
- Usuários ativos

### Sistema de Logs

- Logs coloridos por categoria
- Timestamps automáticos
- Histórico de conexões
- Rastreamento de erros

### Recursos de Rede

- Socket reutilizável
- Handling de desconexões
- Buffer inteligente para comandos
- Suporte a diferentes terminadores de linha

## 🐛 Tratamento de Erros

O sistema inclui tratamento robusto de erros para:

- Conexões perdidas
- Comandos inválidos
- Problemas de rede
- Erros de encoding
- Timeouts de socket

## 📚 Casos de Uso Educacionais

### Para Estudantes

- Aprender conceitos de rede
- Entender programação com sockets
- Praticar threading em Python
- Estudar protocolos de comunicação

### Para Professores

- Demonstrar cliente-servidor
- Ensinar sobre protocolos
- Mostrar boas práticas de programação
- Exemplificar tratamento de erros

## 🔒 Segurança e Limitações

### Limitações Conhecidas

- Sem autenticação
- Sem criptografia
- Protocolo em texto plano
- Limitado a rede local

### Uso Recomendado

- Apenas para fins educacionais
- Em ambiente controlado
- Para demonstrações acadêmicas
- Em redes confiáveis

## 🤝 Contribuindo

Este é um projeto educacional. Sugestões e melhorias são bem-vindas:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Faça push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é desenvolvido para fins educacionais no âmbito do UniSenac.

## 👥 Autores

Desenvolvido como projeto educacional para demonstração de conceitos de programação em rede.

## 📞 Suporte

Para dúvidas ou problemas:

- Verifique o arquivo `relatorio.md` para detalhes técnicos
- Consulte os logs do servidor
- Verifique as dependências instaladas

---

_Tech UniSenac Server - Sistema educacional de servidor Telnet_
