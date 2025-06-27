#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import sys
import time
import os
from datetime import datetime
import random

class Colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    CYAN = '\033[96m'

connected_clients = {}
server_start_time = datetime.now()
server_stats = {
    'total_connections': 0,
    'commands_executed': 0
}

def start_server(host='127.0.0.1', port=2323):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(10)
        
        print_server_banner()
        print(f"Servidor rodando em: {Colors.CYAN}{host}:{port}{Colors.RESET}")
        print(f"Iniciado em: {Colors.GREEN}{server_start_time.strftime('%d/%m/%Y %H:%M:%S')}{Colors.RESET}")
        print("=" * 50)
        print("Pressione Ctrl+C para parar o servidor")
        print("=" * 50)
        
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                server_stats['total_connections'] += 1
                
                print(f"{Colors.GREEN}[NOVA CONEXAO]{Colors.RESET} {client_address[0]}:{client_address[1]}")
                
                connected_clients[client_address] = {
                    'socket': client_socket,
                    'connected_at': datetime.now(),
                    'username': f"user_{server_stats['total_connections']}",
                    'commands_count': 0
                }
                
                client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                print(f"{Colors.RED}[ERRO]{Colors.RESET} Erro ao aceitar conexão: {e}")
    
    except Exception as e:
        print(f"{Colors.RED}[ERRO CRITICO]{Colors.RESET} Erro no servidor: {e}")
    finally:
        server_socket.close()

def print_server_banner():
    banner = f"""
{Colors.CYAN}+================================================+
|  TECH UNISENAC SERVER - VERSÃO BÁSICA         |
|  Sistema Simples de Servidor Telnet           |
+================================================+{Colors.RESET}
"""
    print(banner)

def handle_client(client_socket, client_address):
    try:
        client_info = connected_clients[client_address]
        
        welcome = get_welcome_message(client_info)
        client_socket.send(welcome.encode('utf-8'))
        
        client_socket.send("Digite um comando: ".encode('utf-8'))
        
        buffer = ""
        while True:
            try:
                data = client_socket.recv(256).decode('utf-8', errors='ignore')
                
                if not data:
                    break
                
                buffer += data
                
                while '\n' in buffer or '\r' in buffer:
                    if '\r\n' in buffer:
                        command, buffer = buffer.split('\r\n', 1)
                    elif '\n' in buffer:
                        command, buffer = buffer.split('\n', 1)
                    else:
                        command, buffer = buffer.split('\r', 1)
                    
                    command = command.strip()
                    
                    if not command:
                        continue
                    
                    server_stats['commands_executed'] += 1
                    client_info['commands_count'] += 1
                    
                    if command.lower() in ['quit', 'exit', 'sair', 'bye']:
                        goodbye_msg = get_goodbye_message(client_info)
                        client_socket.send(goodbye_msg.encode('utf-8'))
                        return
                    
                    response = process_command(command, client_address)
                    response += "Digite um comando: "
                    client_socket.send(response.encode('utf-8'))
                
            except socket.timeout:
                continue
            except Exception as e:
                error_msg = f"{Colors.RED}[ERRO]{Colors.RESET} {e}\n\nDigite um comando: "
                try:
                    client_socket.send(error_msg.encode('utf-8'))
                except:
                    break
                
    except Exception as e:
        print(f"{Colors.YELLOW}[CLIENTE]{Colors.RESET} Erro com {client_address}: {e}")
    finally:
        if client_address in connected_clients:
            del connected_clients[client_address]
        try:
            client_socket.close()
        except:
            pass
        print(f"{Colors.YELLOW}[DESCONEXAO]{Colors.RESET} {client_address[0]}:{client_address[1]}")

def get_welcome_message(client_info):
    username = client_info['username']
    current_time = datetime.now().strftime('%H:%M:%S')
    
    return f"""
{Colors.CYAN}+================================================+
|            *** BEM-VINDO(A)! ***               |
+================================================+
|  Usuario: {username:<15}                       |
|  Conectado as: {current_time:<10}              |
|                                                |
|  TECH UNISENAC SERVER - VERSÃO BÁSICA         |
|                                                |
|  COMANDOS DISPONÍVEIS:                         |
|  > help    - Lista de comandos                 |
|  > status  - Status do servidor                |
|  > users   - Usuários conectados               |
|  > ping    - Teste de conectividade            |
|  > time    - Data e hora                       |
|  > quit    - Sair                              |
+================================================+{Colors.RESET}

Digite 'help' para ver todos os comandos disponíveis.

"""

def process_command(data, client_address):
    command = data.strip()
    parts = command.split()
    
    if not parts:
        return "Digite um comando. Use 'help' para ver opções.\n\n"
    
    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    if cmd == 'help':
        return cmd_help()
    elif cmd == 'status':
        return cmd_status()
    elif cmd == 'users':
        return cmd_users()
    elif cmd == 'ping':
        return cmd_ping(args)
    elif cmd == 'time':
        return cmd_time()
    elif cmd == 'whoami':
        return cmd_whoami(client_address)
    elif cmd == 'uptime':
        return cmd_uptime()
    else:
        return f"Comando '{cmd}' não reconhecido. Digite 'help' para ver comandos disponíveis.\n\n"

def cmd_help():
    return f"""
{Colors.GREEN}[HELP] COMANDOS DISPONÍVEIS{Colors.RESET}

{Colors.YELLOW}COMANDOS BÁSICOS:{Colors.RESET}
* help     - Esta lista de comandos
* status   - Status do servidor
* users    - Lista usuários conectados
* ping     - Teste de conectividade
* time     - Data e hora atual
* whoami   - Suas informações
* uptime   - Tempo de atividade do servidor
* quit     - Sair do servidor

"""

def cmd_status():
    uptime = calculate_uptime()
    users = len(connected_clients)
    
    return f"""
{Colors.GREEN}[STATUS] SERVIDOR{Colors.RESET}
Sistema: TECH UNISENAC - Versão Básica
Status: OPERACIONAL
Uptime: {uptime}
Usuários Conectados: {users}
Conexões Totais: {server_stats['total_connections']}
Comandos Executados: {server_stats['commands_executed']}

"""

def cmd_users():
    if not connected_clients:
        return f"{Colors.YELLOW}[USERS] Nenhum usuário conectado.{Colors.RESET}\n\n"
    
    result = f"{Colors.CYAN}[USERS] USUÁRIOS CONECTADOS{Colors.RESET}\n\n"
    
    for i, (addr, info) in enumerate(connected_clients.items(), 1):
        username = info['username']
        connect_time = info['connected_at']
        duration = datetime.now() - connect_time
        commands = info.get('commands_count', 0)
        
        result += f"{i}. {username} - {addr[0]} - {format_duration(duration)} - {commands} cmds\n"
    
    result += f"\nTotal: {len(connected_clients)} usuários\n\n"
    return result

def cmd_ping(args):
    host = args[0] if args else 'google.com'
    latency = random.randint(10, 100)
    
    return f"""
{Colors.CYAN}[PING] TESTE DE CONECTIVIDADE{Colors.RESET}
Host: {host}
Latência: {latency}ms
Status: OK

"""

def cmd_time():
    now = datetime.now()
    return f"""
{Colors.BLUE}[TIME] DATA E HORA{Colors.RESET}
Data: {now.strftime('%d/%m/%Y')}
Hora: {now.strftime('%H:%M:%S')}

"""

def cmd_whoami(client_address):
    client_info = connected_clients[client_address]
    return f"""
{Colors.BLUE}[WHOAMI] SUAS INFORMAÇÕES{Colors.RESET}
Usuário: {client_info['username']}
IP: {client_address[0]}:{client_address[1]}
Conectado há: {format_duration(datetime.now() - client_info['connected_at'])}
Comandos executados: {client_info['commands_count']}

"""

def cmd_uptime():
    return f"{Colors.CYAN}[UPTIME] Servidor ativo há: {calculate_uptime()}{Colors.RESET}\n\n"

def get_goodbye_message(client_info):
    session_time = datetime.now() - client_info['connected_at']
    username = client_info['username']
    commands = client_info['commands_count']
    
    return f"""
{Colors.YELLOW}+================================================+
|                 ATE LOGO!                      |
+================================================+
|  Obrigado por usar o Tech UniSenac Server!    |
|                                                |
|  Usuário: {username:<15}                       |
|  Tempo conectado: {format_duration(session_time):<20}          |
|  Comandos executados: {commands:<10}                  |
+================================================+{Colors.RESET}

Desconectando...
"""

def calculate_uptime():
    uptime = datetime.now() - server_start_time
    return format_duration(uptime)

def format_duration(duration):
    total_seconds = int(duration.total_seconds())
    
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def show_main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.CYAN}╔" + "═" * 50 + "╗")
    print(f"{Colors.CYAN}║" + " " * 8 + f"{Colors.YELLOW}TECH UNISENAC SERVER{Colors.CYAN}" + " " * 13 + "║")
    print(f"{Colors.CYAN}║" + " " * 8 + "Sistema Servidor Telnet" + " " * 12 + "║")
    print(f"{Colors.CYAN}╚" + "═" * 50 + "╝{Colors.RESET}")
    print()

def main():
    if len(sys.argv) >= 2:
        host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
        port = 2323
        
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print("ERRO: Porta deve ser um número.")
                return
        
        print("INICIANDO TECH UNISENAC SERVER...")
        print()
        
        try:
            start_server(host, port)
        except KeyboardInterrupt:
            print(f"\n\nServidor parado pelo usuário.")
            print("Até logo!")
        except Exception as e:
            print(f"\nERRO CRÍTICO: {e}")
        finally:
            print("Programa finalizado.")
    else:
        show_main_menu()
        print(f"{Colors.CYAN}=== CONFIGURAÇÃO DO SERVIDOR ==={Colors.RESET}")
        host = input("Host (padrão: 127.0.0.1): ").strip() or '127.0.0.1'
        port_input = input("Porta (padrão: 2323): ").strip() or '2323'
        
        try:
            port = int(port_input)
        except ValueError:
            print(f"{Colors.RED}Porta inválida!{Colors.RESET}")
            return
        
        print(f"\n{Colors.GREEN}Iniciando servidor...{Colors.RESET}")
        time.sleep(1)
        
        try:
            start_server(host, port)
        except KeyboardInterrupt:
            print(f"\n\nServidor parado pelo usuário.")
            print("Até logo!")
        except Exception as e:
            print(f"\nERRO: {e}")

if __name__ == "__main__":
    main()
