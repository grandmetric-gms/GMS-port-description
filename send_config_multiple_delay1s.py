import paramiko
import time

switches = [
    {"ip": "172.16.1.19"},# {"ip": "172.16.1.4"},
    #{"ip": "10.254.48.101"}
]

username = "admin"
password = "admin"

for switch in switches:
    ip = switch['ip']
    input_file = f"commands_{ip}.txt"

    try:
        # Inicjalizacja klienta SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        print(f"Połączono z urządzeniem {ip}")

        # Otwieranie sesji shell
        channel = ssh.invoke_shell()
        time.sleep(1)  # Małe opóźnienie, aby sesja shell była gotowa

        # Wejście w tryb enable, jeśli potrzebne
        channel.send('enable\n')
        time.sleep(1)
        channel.send(f'{password}\n')
        time.sleep(1)

        # Wejście w tryb konfiguracji terminala
        channel.send('configure terminal\n')
        time.sleep(1)

        # Wysyłanie komend jedna po jednej co 1 sekundę
        with open(input_file, 'r') as file:
            commands = file.readlines()

        for command in commands:
            command = command.strip()
            if command:
                channel.send(command + '\n')
                print(f"Wykonano komendę: {command} na urządzeniu {ip}")
                time.sleep(1)  # Opóźnienie 1 sekundy

        # Zakończenie trybu konfiguracji
        channel.send('end\n')
        time.sleep(1)

        # Zamknięcie sesji SSH
        ssh.close()
        print(f"Rozłączono z urządzeniem {ip}")

    except Exception as e:
        print(f"Wystąpił błąd podczas łączenia lub wysyłania konfiguracji do urządzenia {ip}: {e}")
