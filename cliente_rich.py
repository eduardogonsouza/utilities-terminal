#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import sys
import time
from datetime import datetime
import os
import random

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.text import Text
    from rich.align import Align
    from rich import box
    import questionary
except ImportError:
    print("ERRO: Bibliotecas necessárias não encontradas!")
    print("Instale com: pip install rich questionary")
    sys.exit(1)

class TechUnisenacClient:
    def __init__(self):
        self.console = Console()
        self.socket = None
        self.connected = False
        self.connection_time = None
        self.host = '127.0.0.1'
        self.port = 2323
        self.message_buffer = []
        self.max_messages = 50
        self.connection_history = []
        self.command_history = []
        self.session_notes = []
        self.session_stats = {
            'commands_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        }
        
    def clear_screen(self):
        self.console.clear()
    
    def print_banner(self):
        banner_content = "[bold cyan]TECH UNISENAC CLIENT[/bold cyan]\n[white]Cliente Telnet[/white]"
        
        panel = Panel(
            Align.center(banner_content),
            padding=(1, 2),
            border_style="cyan"
        )
        self.console.print(panel)
        self.console.print()
    
    def print_loading(self, message, duration=1):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            progress.add_task(f"{message}...", total=None)
            time.sleep(duration)
    
    def print_success(self, message):
        self.console.print(f"[bold green]OK[/bold green] {message}")
    
    def print_error(self, message):
        self.console.print(f"[bold red]ERRO[/bold red] {message}")
    
    def print_warning(self, message):
        self.console.print(f"[bold yellow]AVISO[/bold yellow] {message}")
    
    def show_status_panel(self):
        if self.connected:
            status_text = f"[bold green]CONECTADO[/bold green] - {self.host}:{self.port}"
        else:
            status_text = "[bold red]DESCONECTADO[/bold red]"
        
        panel = Panel(status_text, title="[bold]Status da Conexao[/bold]", border_style="blue")
        self.console.print(panel)
        self.console.print()
    
    def get_main_menu_choice(self):
        choices = []
        if not self.connected:
            choices.append({"name": "Conectar ao Servidor", "value": "connect"})
            choices.append({"name": "Configurar Servidor", "value": "config"})
            choices.append({"name": "Testar Conexao", "value": "test"})
        else:
            choices.append({"name": "Modo Terminal", "value": "terminal"})
            choices.append({"name": "Status da Conexao", "value": "status"})
            choices.append({"name": "Desconectar", "value": "disconnect"})

        if self.connected:
            choices.append({"name": "Calculadora", "value": "calculator"})
            choices.append({"name": "Info do Sistema", "value": "sysinfo"})
            choices.append({"name": "Cronômetro", "value": "timer"})
            choices.append({"name": "Bloco de Notas", "value": "notepad"})
            choices.append({"name": "Gerador de Senhas", "value": "password"})

        choices.append({"name": "Sair", "value": "exit"})
        
        return questionary.select(
            "Escolha uma opcao:",
            choices=choices
        ).ask()
    
    def configure_server(self):
        self.console.print(Panel("[bold cyan]Configuracao do Servidor[/bold cyan]", border_style="cyan"))
        self.console.print()
        
        try:
            new_host = questionary.text(
                "Host:",
                default=self.host
            ).ask()
            
            if new_host is None:
                self.print_warning("Configuracao cancelada")
            
            if new_host.strip():
                self.host = new_host.strip()
            
            while True:
                new_port = questionary.text(
                    "Porta:",
                    default=str(self.port)
                ).ask()
                
                if new_port is None:
                    self.print_warning("Configuracao cancelada")
                    return
                
                if new_port.strip():
                    try:
                        self.port = int(new_port.strip())
                        break
                    except ValueError:
                        self.print_error("Porta invalida! Digite um numero.")
                        continue
                else:
                    break
            
            self.print_success(f"Servidor configurado: {self.host}:{self.port}")
            
        except KeyboardInterrupt:
            self.print_warning("Configuracao cancelada")
    
    def connect_to_server(self):
        if self.connected:
            self.print_warning("Ja conectado!")
            return
        
        try:
            self.print_loading(f"Conectando a {self.host}:{self.port}", 1.5)
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            self.connected = True
            self.connection_time = time.time()
            
            self.connection_history.append({
                'host': self.host,
                'port': self.port,
                'time': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'status': 'Sucesso'
            })
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.print_success("Conectado com sucesso!")
            
        except Exception as e:
            self.connection_history.append({
                'host': self.host,
                'port': self.port,
                'time': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'status': f'Falha: {str(e)[:30]}...'
            })
            self.print_error(f"Erro na conexao: {e}")
    
    def disconnect_from_server(self):
        if not self.connected:
            self.print_warning("Nao ha conexao ativa.")
            return
        
        try:
            if self.socket:
                self.socket.send("quit\n".encode('utf-8'))
                time.sleep(0.5)
                self.socket.close()
            
            self.connected = False
            self.connection_time = None
            
            self.print_success("Desconectado com sucesso!")
            
        except Exception as e:
            self.print_error(f"Erro ao desconectar: {e}")
    
    def receive_messages(self):
        buffer = ""
        while self.connected:
            try:
                if self.socket:
                    data = self.socket.recv(4096)
                    if data:
                        message = data.decode('utf-8', errors='ignore')
                        buffer += message
                        
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            if line.strip():
                                self.add_message(line.rstrip('\r'), "server")
                        
                        if buffer and not buffer.endswith('Digite um comando: '):
                            self.add_message(buffer.strip(), "server")
                            buffer = ""
                        elif buffer.endswith('Digite um comando: '):
                            buffer = ""
                            
            except socket.timeout:
                continue
            except Exception as e:
                self.connected = False
                break
    
    def add_message(self, message, message_type="server"):
        if not message.strip():
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if message_type == "command":
            formatted_message = f"[dim]{timestamp}[/dim] [bold blue]>[/bold blue] [cyan]{message}[/cyan]"
            self.session_stats['commands_sent'] += 1
        else:
            formatted_message = f"[dim]{timestamp}[/dim] [bold green]<[/bold green] {message}"
            self.session_stats['messages_received'] += 1
            self.session_stats['bytes_received'] += len(message.encode('utf-8'))
        
        self.message_buffer.append(formatted_message)
        
        if len(self.message_buffer) > self.max_messages:
            self.message_buffer.pop(0)
    
    def format_conversation(self, limit=10):
        if not self.message_buffer:
            return "Nenhuma mensagem ainda..."
        
        recent_messages = self.message_buffer[-limit:]
        return "\n".join(recent_messages)
    
    def show_terminal_commands_banner(self):
        commands_table = Table(show_header=True, box=box.ROUNDED, border_style="cyan")
        commands_table.add_column("Comando", style="bold yellow", width=18)
        commands_table.add_column("Descricao", style="white")
        
        commands_table.add_row("[bold cyan]CLIENTE[/bold cyan]", "")
        commands_table.add_row(":quit", "Sair do programa")
        commands_table.add_row(":clear", "Limpar terminal")
        commands_table.add_row(":history", "Ver historico de comandos")
        commands_table.add_row(":info", "Info e estatisticas")
        commands_table.add_row(":note [msg]", "Adicionar anotacao")
        commands_table.add_row(":export", "Exportar dados da sessao")
        commands_table.add_row(":reconnect", "Reconectar ao servidor")
        
        commands_table.add_row("", "")
        
        commands_table.add_row("[bold green]SERVIDOR[/bold green]", "")
        commands_table.add_row("status", "Status do sistema")
        commands_table.add_row("users", "Usuarios conectados")
        commands_table.add_row("ping [host]", "Teste de conectividade")
        commands_table.add_row("time", "Data e hora")
        commands_table.add_row("whoami", "Suas informacoes")
        commands_table.add_row("uptime", "Tempo ativo do servidor")
        commands_table.add_row("quit", "Sair do servidor")
        
        self.console.print(Panel(
            commands_table,
            title="[bold]Comandos Disponiveis[/bold]",
            border_style="cyan"
        ))
        self.console.print()
    
    def show_session_notes_panel(self):
        if self.session_notes:
            notes_text = ""
            for note in self.session_notes[-3:]:
                notes_text += f"[dim]{note['time']}[/dim] [bold blue]NOTA:[/bold blue] [yellow]{note['note']}[/yellow]\n"
            
            self.console.print(Panel(
                notes_text.strip(),
                title="[bold]Anotacoes da Sessao[/bold]",
                border_style="yellow"
            ))
            self.console.print()

    def terminal_mode(self):
        if not self.connected:
            self.print_error("Voce precisa estar conectado!")
            return
        
        self.message_buffer = []
        self.print_loading("Iniciando terminal", 1.5)
        
        self.clear_screen()
        
        self.show_session_notes_panel()
        
        self.show_terminal_commands_banner()
        
        self.console.print(Panel(
            f"[bold cyan]Terminal Conectado - {self.host}:{self.port}[/bold cyan]\n"
            "[yellow]Digite comandos para interagir com o servidor[/yellow]\n"
            "[dim]Use os comandos da tabela acima[/dim]",
            border_style="cyan",
            title="Terminal Ativo"
        ))
        self.console.print()
        
        try:
            while self.connected:
                if self.message_buffer:
                    conversation = self.format_conversation(8)
                    self.console.print(Panel(
                        conversation,
                        title="[bold]Conversacao[/bold]",
                        border_style="green"
                    ))
                    self.console.print()
                
                try:
                    user_input = questionary.text(
                        "> Comando:",
                        qmark=""
                    ).ask()
                    
                    if user_input is None:
                        break
                    
                    user_input = user_input.strip()
                    
                    if user_input == ':quit':
                        break
                    elif user_input == ':clear':
                        self.message_buffer = []
                        self.clear_screen()
                        self.show_session_notes_panel()
                        self.show_terminal_commands_banner()
                        
                        self.console.print(Panel(
                            "[bold green]Terminal limpo![/bold green]",
                            border_style="green"
                        ))
                        continue
                    elif user_input.startswith(':'):
                        if self.handle_terminal_command(user_input):
                            continue
                        else:
                            self.console.print(f"[red]Comando desconhecido: {user_input}[/red]")
                            continue
                    elif user_input == '':
                        continue
                    
                    self.command_history.append({
                        'command': user_input,
                        'time': datetime.now().strftime('%H:%M:%S')
                    })
                    
                    self.add_message(user_input, "command")
                    
                    if user_input.lower() in ['quit', 'exit', 'bye', 'sair']:
                        if self.socket:
                            self.socket.send(f"{user_input}\n".encode('utf-8'))
                            time.sleep(1)
                        break
                    
                    if self.socket and self.connected:
                        command_bytes = f"{user_input}\n".encode('utf-8')
                        self.socket.send(command_bytes)
                        self.session_stats['bytes_sent'] += len(command_bytes)
                    
                    time.sleep(0.8)
                    
                    self.clear_screen()
                    self.show_session_notes_panel()
                    self.show_terminal_commands_banner()
                
                except (EOFError, KeyboardInterrupt):
                    break
                
        except Exception as e:
            self.print_error(f"Erro no terminal: {e}")
        
        self.console.print(Panel(
            "[bold yellow]Saindo do terminal...[/bold yellow]",
            border_style="yellow"
        ))
        
        if self.connected:
            self.disconnect_from_server()
        
        self.print_final_message()
        exit(0)
    
    def show_help(self):
        help_table = Table(show_header=True, box=box.ROUNDED, border_style="blue")
        help_table.add_column("Comando", style="bold cyan", width=15)
        help_table.add_column("Descricao", style="white")
        
        help_table.add_section()
        help_table.add_row("[bold yellow]COMANDOS DO CLIENTE[/bold yellow]", "")
        help_table.add_row(":quit", "Sair do terminal")
        help_table.add_row(":clear", "Limpar terminal")
        
        help_table.add_section()
        help_table.add_row("[bold yellow]COMANDOS DO SERVIDOR[/bold yellow]", "")
        help_table.add_row("help", "Lista de comandos do servidor")
        help_table.add_row("status", "Status do sistema")
        help_table.add_row("users", "Usuarios conectados")
        help_table.add_row("ping", "Teste de conectividade")
        help_table.add_row("time", "Data e hora")
        help_table.add_row("whoami", "Suas informacoes")
        help_table.add_row("quit", "Sair do servidor")
        
        self.console.print(Panel(
            help_table,
            title="[bold blue]Ajuda do Cliente[/bold blue]",
            border_style="blue"
        ))
        
        questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
    
    def test_connection(self):
        self.console.print(Panel("[bold cyan]Teste de Conexao[/bold cyan]", border_style="cyan"))
        self.console.print()
        
        try:
            self.print_loading(f"Testando conexao com {self.host}:{self.port}", 2)
            
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(5)
            test_socket.connect((self.host, self.port))
            test_socket.close()
            
            self.print_success(f"Conexao com {self.host}:{self.port} OK!")
            
        except Exception as e:
            self.print_error(f"Falha na conexao: {e}")
        
        questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
    
    def show_connection_history(self):
        if not self.connection_history:
            self.console.print(Panel(
                "[yellow]Nenhuma conexao registrada ainda[/yellow]",
                title="Historico de Conexoes",
                border_style="yellow"
            ))
        else:
            history_table = Table(show_header=True, box=box.ROUNDED, border_style="blue")
            history_table.add_column("Data/Hora", style="cyan", width=16)
            history_table.add_column("Host:Porta", style="white", width=20)
            history_table.add_column("Status", style="white")
            
            for entry in self.connection_history[-10:]:
                status_style = "green" if entry['status'] == 'Sucesso' else "red"
                history_table.add_row(
                    entry['time'],
                    f"{entry['host']}:{entry['port']}",
                    f"[{status_style}]{entry['status']}[/{status_style}]"
                )
            
            self.console.print(Panel(
                history_table,
                title="[bold]Historico de Conexoes (Ultimas 10)[/bold]",
                border_style="blue"
            ))
        
        questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
    
    def show_calculator(self):
        self.console.print(Panel("[bold cyan]Calculadora Simples[/bold cyan]", border_style="cyan"))
        self.console.print()
        
        try:
            while True:
                expression = questionary.text(
                    "Digite uma expressao matematica (ou 'sair' para voltar):",
                    qmark="🔢"
                ).ask()
                
                if expression is None or expression.lower() in ['sair', 'exit', 'quit']:
                    break
                
                if not expression.strip():
                    continue
                
                try:
                    # Permitir apenas operações matemáticas básicas
                    allowed_chars = set('0123456789+-*/().,e ')
                    if all(c in allowed_chars for c in expression.replace(' ', '')):
                        result = eval(expression)
                        self.console.print(f"[bold green]Resultado:[/bold green] [yellow]{result}[/yellow]")
                    else:
                        self.console.print("[red]Erro: Apenas operações matemáticas básicas são permitidas[/red]")
                
                except Exception as e:
                    self.console.print(f"[red]Erro na expressão: {e}[/red]")
                
                self.console.print()
        
        except (EOFError, KeyboardInterrupt):
            pass
    
    def show_system_info(self):
        import platform
        import psutil
        
        info_table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
        info_table.add_column("Item", style="bold cyan", width=20)
        info_table.add_column("Valor", style="white")
        
        info_table.add_row("Sistema", platform.system())
        info_table.add_row("Versao", platform.release())
        info_table.add_row("Arquitetura", platform.machine())
        info_table.add_row("Processador", platform.processor()[:50] + "..." if len(platform.processor()) > 50 else platform.processor())
        
        try:
            info_table.add_row("CPU Uso", f"{psutil.cpu_percent(interval=1):.1f}%")
            info_table.add_row("Memoria", f"{psutil.virtual_memory().percent:.1f}%")
            info_table.add_row("Disco", f"{psutil.disk_usage('/').percent:.1f}%")
        except:
            info_table.add_row("Recursos", "Informacao nao disponivel")
        
        info_table.add_row("Python", platform.python_version())
        info_table.add_row("Hostname", platform.node())
        
        self.console.print(Panel(
            info_table,
            title="[bold]Informacoes do Sistema[/bold]",
            border_style="blue"
        ))
        
        questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
    
    def show_timer(self):
        self.console.print(Panel("[bold cyan]Cronometro/Timer[/bold cyan]", border_style="cyan"))
        self.console.print()
        
        timer_choice = questionary.select(
            "Escolha uma opcao:",
            choices=[
                {"name": "Cronometro da Sessao", "value": "session"},
                {"name": "Timer Personalizado", "value": "custom"},
                {"name": "Voltar", "value": "back"}
            ]
        ).ask()
        
        if timer_choice == "session":
            self.show_session_timer()
            questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
        
        elif timer_choice == "custom":
            try:
                seconds = questionary.text(
                    "Digite o tempo em segundos:",
                    validate=lambda x: x.isdigit() and int(x) > 0
                ).ask()
                
                if seconds:
                    countdown_time = int(seconds)
                    self.console.print(f"[cyan]Iniciando timer de {countdown_time} segundos...[/cyan]")
                    
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=self.console
                    ) as progress:
                        task = progress.add_task(f"Timer: {countdown_time}s restantes", total=None)
                        
                        for i in range(countdown_time, 0, -1):
                            progress.update(task, description=f"Timer: {i}s restantes")
                            time.sleep(1)
                    
                    self.console.print("[bold green]Timer finalizado![/bold green] ⏰")
                    questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
            
            except (EOFError, KeyboardInterrupt):
                self.console.print("[yellow]Timer cancelado[/yellow]")
    
    def show_notepad(self):
        self.console.print(Panel("[bold cyan]Bloco de Notas da Sessao[/bold cyan]", border_style="cyan"))
        self.console.print()
        
        while True:
            notepad_choice = questionary.select(
                "Escolha uma opcao:",
                choices=[
                    {"name": "Ver Todas as Notas", "value": "view"},
                    {"name": "Adicionar Nova Nota", "value": "add"},
                    {"name": "Exportar Notas", "value": "export"},
                    {"name": "Limpar Notas", "value": "clear"},
                    {"name": "Voltar", "value": "back"}
                ]
            ).ask()
            
            if notepad_choice == "view":
                if not self.session_notes:
                    self.console.print("[yellow]Nenhuma nota registrada ainda[/yellow]")
                else:
                    notes_table = Table(show_header=True, box=box.ROUNDED, border_style="blue")
                    notes_table.add_column("#", style="dim", width=4)
                    notes_table.add_column("Hora", style="cyan", width=8)
                    notes_table.add_column("Nota", style="white")
                    
                    for i, note in enumerate(self.session_notes, 1):
                        notes_table.add_row(str(i), note['time'], note['note'][:60] + "..." if len(note['note']) > 60 else note['note'])
                    
                    self.console.print(Panel(
                        notes_table,
                        title=f"[bold]Notas da Sessao ({len(self.session_notes)})[/bold]",
                        border_style="blue"
                    ))
                
                questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
            
            elif notepad_choice == "add":
                note_text = questionary.text(
                    "Digite sua nota:",
                    multiline=True
                ).ask()
                
                if note_text and note_text.strip():
                    self.add_session_note(note_text.strip())
                else:
                    self.console.print("[yellow]Nota vazia, nao adicionada[/yellow]")
            
            elif notepad_choice == "export":
                if not self.session_notes:
                    self.console.print("[yellow]Nenhuma nota para exportar[/yellow]")
                else:
                    try:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"notas_sessao_{timestamp}.txt"
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(f"NOTAS DA SESSAO - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                            f.write("=" * 50 + "\n\n")
                            
                            for i, note in enumerate(self.session_notes, 1):
                                f.write(f"[{i:02d}] {note['time']} - {note['note']}\n\n")
                        
                        self.console.print(f"[green]Notas exportadas para: {filename}[/green]")
                    
                    except Exception as e:
                        self.console.print(f"[red]Erro ao exportar: {e}[/red]")
            
            elif notepad_choice == "clear":
                if self.session_notes:
                    confirm = questionary.confirm(
                        f"Tem certeza que deseja limpar todas as {len(self.session_notes)} notas?",
                        default=False
                    ).ask()
                    
                    if confirm:
                        self.session_notes.clear()
                        self.console.print("[green]Todas as notas foram removidas[/green]")
                else:
                    self.console.print("[yellow]Nenhuma nota para limpar[/yellow]")
            
            elif notepad_choice == "back":
                break
    
    def generate_password(self):
        self.console.print(Panel("[bold cyan]Gerador de Senhas[/bold cyan]", border_style="cyan"))
        self.console.print()
        
        try:
            length = questionary.text(
                "Comprimento da senha (default: 12):",
                default="12",
                validate=lambda x: x.isdigit() and 4 <= int(x) <= 128
            ).ask()
            
            if length is None:
                return
            
            length = int(length)
            
            include_options = questionary.checkbox(
                "Incluir:",
                choices=[
                    {"name": "Letras minusculas (a-z)", "value": "lower", "checked": True},
                    {"name": "Letras maiusculas (A-Z)", "value": "upper", "checked": True},
                    {"name": "Numeros (0-9)", "value": "digits", "checked": True},
                    {"name": "Simbolos (!@#$%^&*)", "value": "symbols", "checked": False}
                ]
            ).ask()
            
            if not include_options:
                self.console.print("[yellow]Nenhuma opcao selecionada[/yellow]")
                return
            
            import string
            
            chars = ""
            if "lower" in include_options:
                chars += string.ascii_lowercase
            if "upper" in include_options:
                chars += string.ascii_uppercase
            if "digits" in include_options:
                chars += string.digits
            if "symbols" in include_options:
                chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
            if not chars:
                self.console.print("[red]Erro: Nenhum caractere disponivel[/red]")
                return
            
            password = ''.join(random.choice(chars) for _ in range(length))
            
            password_table = Table(show_header=False, box=box.ROUNDED, border_style="green")
            password_table.add_column("Item", style="bold cyan", width=15)
            password_table.add_column("Valor", style="white")
            
            password_table.add_row("Senha Gerada", f"[bold yellow]{password}[/bold yellow]")
            password_table.add_row("Comprimento", str(length))
            password_table.add_row("Caracteres", ", ".join(include_options))
            
            self.console.print(Panel(
                password_table,
                title="[bold]Senha Gerada[/bold]",
                border_style="green"
            ))
            
            save_option = questionary.confirm(
                "Deseja salvar a senha em um arquivo?",
                default=False
            ).ask()
            
            if save_option:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"senha_{timestamp}.txt"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Senha gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                        f.write(f"Comprimento: {length}\n")
                        f.write(f"Opcoes: {', '.join(include_options)}\n")
                        f.write(f"Senha: {password}\n")
                    
                    self.console.print(f"[green]Senha salva em: {filename}[/green]")
                
                except Exception as e:
                    self.console.print(f"[red]Erro ao salvar: {e}[/red]")
        
        except (EOFError, KeyboardInterrupt):
            self.console.print("[yellow]Operacao cancelada[/yellow]")
        
        questionary.press_any_key_to_continue("Pressione qualquer tecla para continuar...").ask()
    
    def handle_terminal_command(self, command):
        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == ':history':
            self.show_command_history()
            return True
        elif cmd == ':info':
            self.show_unified_info()
            return True
        elif cmd == ':note':
            self.add_session_note(' '.join(args) if args else "Nota vazia")
            return True
        elif cmd == ':export':
            self.export_session_data()
            return True
        elif cmd == ':reconnect':
            self.quick_reconnect()
            return True
        
        return False
    
    def show_command_history(self):
        if not self.command_history:
            self.console.print(Panel(
                "[yellow]Nenhum comando executado ainda[/yellow]",
                title="Historico de Comandos",
                border_style="yellow"
            ))
        else:
            history_table = Table(show_header=True, box=box.ROUNDED, border_style="blue")
            history_table.add_column("#", style="dim", width=4)
            history_table.add_column("Comando", style="cyan")
            history_table.add_column("Hora", style="dim", width=8)
            
            for i, entry in enumerate(self.command_history[-15:], 1):
                history_table.add_row(
                    str(i),
                    entry['command'],
                    entry['time']
                )
            
            self.console.print(Panel(
                history_table,
                title="[bold]Historico de Comandos (Ultimos 15)[/bold]",
                border_style="blue"
            ))
        
        self.console.print()
    
    def quick_save_log(self):
        if not self.message_buffer:
            self.console.print("[yellow]Nenhuma mensagem para salvar![/yellow]")
            return
        
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"session_{timestamp}.log"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"SESSAO TERMINAL - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("=" * 40 + "\n")
                
                for message in self.message_buffer:
                    clean_message = message.replace('[dim]', '').replace('[/dim]', '')
                    clean_message = clean_message.replace('[bold blue]', '').replace('[/bold blue]', '')
                    clean_message = clean_message.replace('[bold green]', '').replace('[/bold green]', '')
                    clean_message = clean_message.replace('[cyan]', '').replace('[/cyan]', '')
                    f.write(clean_message + "\n")
            
            self.console.print(f"[green]Log salvo: {filename}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Erro ao salvar: {e}[/red]")
        
        self.console.print()
    
    def show_unified_info(self):
        info_table = Table(show_header=False, box=box.ROUNDED, border_style="blue")
        info_table.add_column("Item", style="bold cyan", width=20)
        info_table.add_column("Valor", style="white")
        
        if self.connected:
            uptime = time.time() - self.connection_time if self.connection_time else 0
            minutes, seconds = divmod(int(uptime), 60)
            
            info_table.add_row("Status", "[bold green]CONECTADO[/bold green]")
            info_table.add_row("Servidor", f"[cyan]{self.host}:{self.port}[/cyan]")
            info_table.add_row("Tempo Conectado", f"[yellow]{minutes:02d}m{seconds:02d}s[/yellow]")
        else:
            info_table.add_row("Status", "[bold red]DESCONECTADO[/bold red]")
            info_table.add_row("Servidor", f"{self.host}:{self.port}")
        
        info_table.add_row("", "")
        
        info_table.add_row("Comandos Enviados", str(self.session_stats['commands_sent']))
        info_table.add_row("Mensagens Recebidas", str(self.session_stats['messages_received']))
        info_table.add_row("Total de Mensagens", str(len(self.message_buffer)))
        info_table.add_row("Historico Comandos", str(len(self.command_history)))
        info_table.add_row("Anotacoes", str(len(self.session_notes)))
        info_table.add_row("Bytes Enviados", f"{self.session_stats['bytes_sent']} bytes")
        info_table.add_row("Bytes Recebidos", f"{self.session_stats['bytes_received']} bytes")
        
        self.console.print(Panel(
            info_table,
            title="[bold]Info da Conexao & Estatisticas[/bold]",
            border_style="blue"
        ))
        self.console.print()

    def show_connection_info(self):
        if self.connected:
            uptime = time.time() - self.connection_time if self.connection_time else 0
            minutes, seconds = divmod(int(uptime), 60)
            
            info_text = f"""[bold green]CONECTADO[/bold green]
Servidor: [cyan]{self.host}:{self.port}[/cyan]
Tempo: [yellow]{minutes:02d}m{seconds:02d}s[/yellow]
Mensagens: [blue]{len(self.message_buffer)}[/blue]
Comandos: [magenta]{len(self.command_history)}[/magenta]"""
        else:
            info_text = "[bold red]DESCONECTADO[/bold red]"
        
        self.console.print(Panel(
            info_text,
            title="[bold]Info da Conexao[/bold]",
            border_style="blue"
        ))
        self.console.print()
    
    def echo_message(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        echo_msg = f"[dim]{timestamp}[/dim] [bold magenta]ECHO[/bold magenta] {message}"
        
        self.console.print(Panel(
            echo_msg,
            border_style="magenta"
        ))
        self.console.print()
    

    
    def show_session_timer(self):
        if self.connected and self.connection_time:
            uptime = time.time() - self.connection_time
            hours, remainder = divmod(int(uptime), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            timer_text = f"""[bold green]CRONOMETRO DA SESSAO[/bold green]

[cyan]Conectado ha:[/cyan] [bold yellow]{hours:02d}h {minutes:02d}m {seconds:02d}s[/bold yellow]
[cyan]Inicio:[/cyan] {datetime.fromtimestamp(self.connection_time).strftime('%H:%M:%S')}
[cyan]Agora:[/cyan] {datetime.now().strftime('%H:%M:%S')}

[dim]Media de comandos/minuto:[/dim] {len(self.command_history) / max(uptime/60, 1):.1f}"""
        else:
            timer_text = "[bold red]Nao conectado - Cronometro indisponivel[/bold red]"
        
        self.console.print(Panel(
            timer_text,
            title="[bold]Cronometro[/bold]",
            border_style="yellow"
        ))
        self.console.print()
    
    def add_session_note(self, note):
        if not note.strip():
            self.console.print("[yellow]Anotacao vazia ignorada[/yellow]")
            return
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        note_entry = {
            'time': timestamp,
            'note': note.strip(),
            'context': f"{len(self.command_history)} comandos executados"
        }
        
        self.session_notes.append(note_entry)
        
        self.console.print(Panel(
            f"[bold blue]NOTA ADICIONADA[/bold blue]\n[yellow]{note.strip()}[/yellow]",
            title=f"[dim]{timestamp}[/dim]",
            border_style="blue"
        ))
        self.console.print()
    
    def search_in_history(self, search_term):
        if not search_term:
            self.console.print("[yellow]Digite um termo para buscar[/yellow]")
            return
        
        results = []
        search_lower = search_term.lower()
        
        for i, message in enumerate(self.message_buffer):
            if search_lower in message.lower():
                results.append(('Mensagem', i+1, message))
        
        for i, cmd in enumerate(self.command_history):
            if search_lower in cmd['command'].lower():
                results.append(('Comando', i+1, f"{cmd['time']} - {cmd['command']}"))
        
        for i, note in enumerate(self.session_notes):
            if search_lower in note['note'].lower():
                results.append(('Nota', i+1, f"{note['time']} - {note['note']}"))
        
        if not results:
            self.console.print(f"[yellow]Nenhum resultado encontrado para: '{search_term}'[/yellow]")
        else:
            search_table = Table(show_header=True, box=box.ROUNDED, border_style="blue")
            search_table.add_column("Tipo", style="cyan", width=10)
            search_table.add_column("#", style="dim", width=4)
            search_table.add_column("Conteudo", style="white")
            
            for result_type, index, content in results[:10]:
                clean_content = content.replace('[dim]', '').replace('[/dim]', '')
                clean_content = clean_content.replace('[bold blue]', '').replace('[/bold blue]', '')
                clean_content = clean_content.replace('[bold green]', '').replace('[/bold green]', '')
                clean_content = clean_content.replace('[cyan]', '').replace('[/cyan]', '')
                
                search_table.add_row(result_type, str(index), clean_content[:60] + "..." if len(clean_content) > 60 else clean_content)
            
            self.console.print(Panel(
                search_table,
                title=f"[bold]Resultados para '{search_term}' ({len(results)})[/bold]",
                border_style="blue"
            ))
        
        self.console.print()
    
    def export_session_data(self):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_export_{timestamp}.json"
            
            export_data = {
                'session_info': {
                    'host': self.host,
                    'port': self.port,
                    'connected': self.connected,
                    'start_time': datetime.fromtimestamp(self.connection_time).isoformat() if self.connection_time else None,
                    'export_time': datetime.now().isoformat()
                },
                'statistics': self.session_stats,
                'messages': [msg.replace('[dim]', '').replace('[/dim]', '').replace('[bold blue]', '').replace('[/bold blue]', '').replace('[bold green]', '').replace('[/bold green]', '').replace('[cyan]', '').replace('[/cyan]', '') for msg in self.message_buffer],
                'command_history': self.command_history,
                'notes': self.session_notes,
                'connection_history': self.connection_history[-5:]
            }
            
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]Dados exportados para: {filename}[/green]")
            self.console.print(f"[dim]Incluidos: {len(self.message_buffer)} mensagens, {len(self.command_history)} comandos, {len(self.session_notes)} notas[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]Erro ao exportar: {e}[/red]")
        
        self.console.print()
    
    def quick_reconnect(self):
        if self.connected:
            self.console.print("[yellow]Ja conectado! Use :info para ver status[/yellow]")
            return
        
        self.console.print("[cyan]Tentando reconectar...[/cyan]")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            
            self.connected = True
            self.connection_time = time.time()
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.console.print("[green]Reconectado com sucesso![/green]")
            
            self.connection_history.append({
                'host': self.host,
                'port': self.port,
                'time': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'status': 'Reconexao bem-sucedida'
            })
            
        except Exception as e:
            self.console.print(f"[red]Falha na reconexao: {e}[/red]")
            
            self.connection_history.append({
                'host': self.host,
                'port': self.port,
                'time': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'status': f'Falha reconexao: {str(e)[:20]}...'
            })
        
        self.console.print()
    
    def print_final_message(self):
        final_panel = Panel(
            Align.center("Obrigado por usar o Tech UniSenac Client!"),
            padding=(1, 2),
            border_style="green",
            title="[bold green]Ate Logo![/bold green]"
        )
        self.console.print(final_panel)
    
    def run(self):
        try:
            while True:
                self.clear_screen()
                self.print_banner()
                self.show_status_panel()
                
                choice = self.get_main_menu_choice()
                
                if choice is None or choice == 'exit':
                    if self.connected:
                        disconnect = questionary.confirm(
                            "Desconectar antes de sair?",
                            default=True
                        ).ask()
                        if disconnect:
                            self.disconnect_from_server()
                    
                    self.print_final_message()
                    break
                
                elif choice == 'connect':
                    self.connect_to_server()
                
                elif choice == 'config':
                    self.configure_server()
                
                elif choice == 'test':
                    self.test_connection()
                
                elif choice == 'disconnect':
                    self.disconnect_from_server()
                
                elif choice == 'history':
                    self.show_connection_history()
                
                elif choice == 'status':
                    self.show_detailed_status()
                
                elif choice == 'terminal':
                    self.terminal_mode()
                
                elif choice == 'help':
                    self.show_help()
                
                elif choice == 'calculator':
                    self.show_calculator()
                
                elif choice == 'sysinfo':
                    self.show_system_info()
                
                elif choice == 'timer':
                    self.show_timer()
                
                elif choice == 'notepad':
                    self.show_notepad()
                
                elif choice == 'password':
                    self.generate_password()
        except Exception as e:
            self.print_error(f"Erro inesperado: {e}")
                    
        except KeyboardInterrupt:
            self.console.print("\n")
            self.print_warning("Saindo...")
            if self.connected:
                self.disconnect_from_server()

def main():
    try:
        client = TechUnisenacClient()
        
        if len(sys.argv) >= 3:
            try:
                client.host = sys.argv[1]
                client.port = int(sys.argv[2])
            except ValueError:
                print("❌ Erro: Porta deve ser um número")
                return
        
        client.run()
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    main()
