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
[Additional Link][https://www.wireguard.com/install/]
