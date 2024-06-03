switches = [
    {"ip": "172.16.1.19"}, #{"ip": "10.254.16.15"},
]

def generate_commands(input_file):
    commands = []
    commands.append('configure terminal\n')
    with open(input_file, 'r', encoding="utf-8") as file:
        for line in file:
            if line.strip():  # Sprawdzenie, czy linia nie jest pusta
                parts = line.strip().split(',')
                port = parts[0].split(':')[1].strip()
                neighbor = parts[1].split(':')[1].strip()
                commands.append(f'interface {port}\n')
                commands.append(f'description {neighbor}\n')
                commands.append('exit\n')
    return commands

def save_commands(commands, output_file):
    with open(output_file, 'w', encoding="utf-8") as file:
        file.writelines(commands)

if __name__ == "__main__":
    for switch in switches:
        ip = switch['ip']
        input_file = f"{ip}.txt"
        output_file = f"commands_{ip}.txt"
        commands = generate_commands(input_file)
        save_commands(commands, output_file)
        print(f"Lista komend została wygenerowana i zapisana w pliku {output_file}.")
