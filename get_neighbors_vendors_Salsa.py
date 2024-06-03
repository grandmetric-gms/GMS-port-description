import time
import paramiko
import re

switches = [
    {"ip": "172.16.1.19"}#, {"ip": "10.254.8.12"} #{"ip": "172.16.1.4"},
    #{"ip": "10.254.48.111"}, {"ip": "10.254.48.121"},
    #{"ip": "10.254.48.131"}, {"ip": "10.254.48.141"}, {"ip": "10.254.48.151"}, {"ip": "10.254.48.161"},
    #{"ip": "10.254.48.171"}
]

def connect_to_switch(ip, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(ip, username=username, password=password, look_for_keys=False)
        print(f"Successfully connected to the switch at {ip}.")
        return ssh_client
    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your credentials.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"Error: {e}")

    return None

def get_lldp_neighbors(ssh_client):
    command = "show lldp neighbors"
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode()
    print(output)
    return output

def parse_lldp_neighbors(output):
    neighbors = {}
    lines = output.split("\n")
    for line in lines:
        match = re.match(r'^\s*(\S+)\s+(\S+)\s+\d+\s+\S+\s+(\S+)', line)
        if match:
            neighbor_name = match.group(1)
            port = match.group(2)
            mac_address = match.group(3).split(";")[0]  # extract MAC address from the string
            neighbors[port] = {"neighbor": neighbor_name, "mac_address": mac_address}
    return neighbors

def load_vendor_data():
    vendor_data = {}
    with open("vendors.txt", "r", encoding='utf-8') as file:
        for line in file:
            mac_prefix, vendor = line.strip().split(" ", 1)
            vendor_data[mac_prefix] = vendor
    return vendor_data

def get_vendor(mac_address):
    vendor_data = load_vendor_data()
    mac_prefix = mac_address[:7]#.upper()  # Get the first 7 characters and convert to uppercase
    return vendor_data.get(mac_prefix, "Unknown")

def save_to_file(ip, data):
    filename = f"{ip}.txt"
    with open(filename, "w") as f:
        f.write(data)

def main():
    username = "admin"
    password = "admin"

    neighbor_starts = "Salsa"

    for switch in switches:
        ip = switch["ip"]
        ssh_client = connect_to_switch(ip, username, password)
        if ssh_client:
            lldp_output = get_lldp_neighbors(ssh_client)
            neighbors = parse_lldp_neighbors(lldp_output)
            print(f"\nLLDP neighbors and MAC addresses for switch at {ip}:")
            output_data = f""
            for port, info in neighbors.items():
                neighbor_name = info["neighbor"]
                mac_address = info["mac_address"]
                if neighbor_name.startswith(neighbor_starts):
                    vendor = get_vendor(mac_address)
                    time.sleep(1)
                    line = f"Port: {port}, Neighbor: {neighbor_name}, MAC Address: {mac_address}, Vendor: {vendor}\n"
                    print(line)
                    output_data += line
            ssh_client.close()
            if neighbor_starts in output_data:
                save_to_file(ip, output_data)
                print(f"Data saved to {ip}.txt")
            else:
                print(f"No {neighbor_starts} neighbors found for switch at {ip}.")
        else:
            print(f"\nFailed to connect to the switch at {ip}.")

if __name__ == "__main__":
    main()
