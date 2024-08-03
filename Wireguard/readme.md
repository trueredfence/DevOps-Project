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
Table = 123
PreUp = sysctl -w net.ipv4.ip_forward=1
PreUp = ip rule add iif wg0 table 123 priority 456
PostDown = ip rule del iif wg0 table 123 priority 456

# Masquerade traffic for outgoing internet access
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

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
```
