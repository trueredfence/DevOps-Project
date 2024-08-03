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
