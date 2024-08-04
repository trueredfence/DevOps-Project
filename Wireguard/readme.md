# Wireguard Centos 7
## Install in Cento 7
` change vault repo in CentosBase`
```bash
yum update -y
yum install yum-utils vim wget -y
reboot

yum install epel-release elrepo-release -y
yum install kmod-wireguard wireguard-tools -y

yum-config-manager --setopt=centosplus.includepkgs=kernel-plus --enablerepo=centosplus --save
sed -e 's/^DEFAULTKERNEL=kernel$/DEFAULTKERNEL=kernel-plus/' -i /etc/sysconfig/kernel
yum install kernel-plus wireguard-tools
reboot
```
[Additional Link](https://www.wireguard.com/install/)

### Create pair of keys
```
# Manually
sudo mkdir -p /etc/wireguard/
cd /etc/wireguard
wg genkey | sudo tee /etc/wireguard/server_private.key | wg pubkey | sudo tee /etc/wireguard/server_public.key
```
```bash
#!/bin/bash

# Check if the number of key pairs to generate is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <number_of_key_pairs>"
    exit 1
fi
# Number of key pairs to generate
NUM_KEYS=$1

# Directory where the keys will be stored
KEY_DIR="."

# Generate the key pairs
for i in $(seq 1 $NUM_KEYS); do
    # Generate the private key
    wg genkey | sudo tee "${KEY_DIR}/private_${i}.key" | wg pubkey | sudo tee "${KEY_DIR}/public_${i}.key"
    echo "Generated key pair $i: private_${i}.key and public_${i}.key"
done

echo "All key pairs have been generated and saved in $KEY_DIR."
```
### Conf file Host A VPS `/etc/wireguard/wg0.conf`
```ini
# Host A
[Interface]
Address = 10.10.10.1/24
SaveConfig = true
PrivateKey = YCc2sgK/jpJJBdBiw4LQLPjE8Fh0xE4HuITKy1QQ0lY= # Host A Private key
ListenPort = 51820
Table = 123

PreUp = sysctl -w net.ipv4.ip_forward=1
PreUp = ip rule add iif wg0 table 123 priority 456
PostDown = ip rule del iif wg0 table 123 priority 456

# Remote setting for 2nd hope
[Peer] 
PublicKey = Fol97yuanQrUr68wU+faRIp4gXOMCyBXa9oSwppZGCI= #Host B Public key
AllowedIPs = 0.0.0.0/0 # to allow untunneled traffic, use `0.0.0.0/1, 128.0.0.0/1` instead
Endpoint = <host-B ip>:51820
PersistentKeepalive = 25

```
### Host B Conf `/etc/wireguard/wg0.conf`
```ini
# Host B
[Interface]
Address = 10.10.10.2/24
PrivateKey = 2LO30hRtR3Ul0C35/nzlO//dX9pdQZ4o4Qk4f6wimFU= # Host B Private key
ListenPort = 51820
Table = 123

PreUp = sysctl -w net.ipv4.ip_forward=1
PreUp = ip rule add iif wg0 table 123 priority 456
PostDown = ip rule del iif wg0 table 123 priority 456

[Peer]
PublicKey = 0fzuxRTjhV7tpaU575fYXxBe0KxFpZiyyxDA0w+EH0I= Host A Public Key
AllowedIPs = 10.10.10.1/32

# Remote setting for 3nd hope
[Peer] 
PublicKey = hlIchsikADC7Y9VAYDgUexcC9D7YiUI0nLCWFCxEEHY= #Host C Public key
AllowedIPs = 0.0.0.0/0 # to allow untunneled traffic, use `0.0.0.0/1, 128.0.0.0/1` instead
Endpoint = <host-C ip>:51820
PersistentKeepalive = 25

```

### Host C config or End point host where we have internet exit point `/etc/wireguard/wg0.conf`

```ini
# Host -C
[Interface]
PrivateKey = 4N4EdSgB69soXBfsjHP/rgFPCdq5/NnUyXR3hdB21UU= # host c private key
Address = 10.10.10.3/24
ListenPort = 51820
#Table = 123
PreUp = sysctl -w net.ipv4.ip_forward=1
#PreUp = ip rule add iif wg0 table 123 priority 456
#PostDown = ip rule del iif wg0 table 123 priority 456

# Masquerade traffic for outgoing internet access
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer] # host -b PUblic key
PublicKey = Fol97yuanQrUr68wU+faRIp4gXOMCyBXa9oSwppZGCI= # host be public key
AllowedIPs = 10.10.10.2/32
# PersistentKeepalive = 25

```
### Firewall cmd for Hope
```bash
# Add WireGuard port
firewall-cmd --permanent --add-port=51820/udp

# Ensure SSH traffic uses the main routing table
ip rule add from <your_client_ip> to <HostC_IP> table main priority 100

# Reload firewalld
firewall-cmd --reload

```
### Firewall Cmd for Exit point
```bash
# Add WireGuard port
firewall-cmd --permanent --add-port=51820/udp

# Exclude SSH traffic from masquerading
iptables -t nat -A POSTROUTING -p tcp --dport 22 -j ACCEPT

# Apply masquerading for other traffic
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Ensure SSH traffic uses the main routing table
ip rule add from <your_client_ip> to <HostD_IP> table main priority 100

# Reload firewalld
firewall-cmd --reload

# More
sudo firewall-cmd --zone=public --permanent --add-masquerade
sudo systemctl reload firewalld
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf

```
### Create conf file auto with bash
```bash
#!/bin/bash

# Function to generate keys and save them
generate_keys() {
    private_key=$(wg genkey)
    public_key=$(echo $private_key | wg pubkey)
    echo $private_key > "$1_private.key"
    echo $public_key > "$1_public.key"
}

# Function to create client configuration
create_client_config() {
    private_key=$1
    peer_public_key=$2
    endpoint=$3
    config_file="client_${index}.conf"

    echo "[Interface]" > $config_file
    echo "Address = 10.10.10.${address_suffix}/24" >> $config_file
    echo "PrivateKey = $private_key" >> $config_file
    echo "ListenPort = 51820" >> $config_file
    echo "SaveConfig = true" >> $config_file

    echo "[Peer]" >> $config_file
    echo "PublicKey = $peer_public_key" >> $config_file
    echo "AllowedIPs = 0.0.0.0/0" >> $config_file
    echo "Endpoint = $endpoint:51820" >> $config_file
    echo "PersistentKeepalive = 25" >> $config_file

    echo "Client configuration saved to $config_file"
}

# Function to create server configuration
create_server_config() {
    private_key=$1
    previous_peer_public_key=$2
    next_peer_public_key=$3
    next_peer_ip=$4
    config_file="server_${index}.conf"

    echo "[Interface]" > $config_file
    echo "Address = 10.10.10.${address_suffix}/24" >> $config_file
    echo "PrivateKey = $private_key" >> $config_file
    echo "ListenPort = 51820" >> $config_file
    echo "Table = 123" >> $config_file

    echo "PreUp = sysctl -w net.ipv4.ip_forward=1" >> $config_file
    echo "PreUp = ip rule add iif wg0 table 123 priority 456" >> $config_file
    echo "PostDown = ip rule del iif wg0 table 123 priority 456" >> $config_file

    echo "[Peer]" >> $config_file
    echo "PublicKey = $previous_peer_public_key" >> $config_file
    echo "AllowedIPs = 10.10.10.${previous_suffix}/32" >> $config_file

    if [ -n "$next_peer_public_key" ]; then
        echo "[Peer]" >> $config_file
        echo "PublicKey = $next_peer_public_key" >> $config_file
        echo "AllowedIPs = 0.0.0.0/0" >> $config_file
        echo "Endpoint = $next_peer_ip:51820" >> $config_file
        echo "PersistentKeepalive = 25" >> $config_file
    fi

    echo "Server configuration saved to $config_file"
}

# Function to create gateway configuration
create_gateway_config() {
    private_key=$1
    previous_peer_public_key=$2
    config_file="gateway_${index}.conf"

    echo "[Interface]" > $config_file
    echo "Address = 10.10.10.${address_suffix}/24" >> $config_file
    echo "PrivateKey = $private_key" >> $config_file
    echo "ListenPort = 51820" >> $config_file

    echo "PreUp = sysctl -w net.ipv4.ip_forward=1" >> $config_file
    echo "PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE" >> $config_file
    echo "PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE" >> $config_file

    echo "[Peer]" >> $config_file
    echo "PublicKey = $previous_peer_public_key" >> $config_file
    echo "AllowedIPs = 10.10.10.${previous_suffix}/32" >> $config_file

    echo "Gateway configuration saved to $config_file"
}

# Validate arguments
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <role1> <role2> ... <roleN>"
    echo "Example: $0 client server gateway"
    exit 1
fi

# Initialize variables
index=1
address_suffix=1
previous_suffix=1
previous_private_key=""
previous_public_key=""
public_keys=()

# Create keys for each role
for role in "$@"; do
    generate_keys "role${index}"
    public_keys+=($(cat "role${index}_public.key"))
    index=$((index + 1))
done

# Reset index and address_suffix for configuration generation
index=1
address_suffix=1

# Create configurations based on roles
for role in "$@"; do
    private_key=$(cat "role${index}_private.key")
    public_key=$(cat "role${index}_public.key")

    case $role in
        "client")
            if [ $index -eq 1 ]; then
                next_peer_public_key=${public_keys[$index]}
                create_client_config $private_key $next_peer_public_key "<next-hop-ip>"
            else
                previous_peer_public_key=${public_keys[$((index - 2))]}
                create_client_config $private_key $previous_peer_public_key "<next-hop-ip>"
            fi
            ;;
        "server")
            previous_peer_public_key=${public_keys[$((index - 2))]}
            if [ $index -lt $# ]; then
                next_peer_public_key=${public_keys[$index]}
                next_peer_ip="<next-hop-ip>"
                create_server_config $private_key $previous_peer_public_key $next_peer_public_key $next_peer_ip
            else
                create_server_config $private_key $previous_peer_public_key "" ""
            fi
            ;;
        "gateway")
            previous_peer_public_key=${public_keys[$((index - 2))]}
            create_gateway_config $private_key $previous_peer_public_key
            ;;
        *)
            echo "Unknown role: $role"
            exit 1
            ;;
    esac

    previous_private_key=$private_key
    previous_public_key=$public_key
    previous_suffix=$address_suffix
    index=$((index + 1))
    address_suffix=$((address_suffix + 1))
done

# Clean up key files if needed
rm role*_private.key role*_public.key

echo "WireGuard configuration files created successfully."
```
