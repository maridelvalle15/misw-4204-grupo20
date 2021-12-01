sudo apt update
sudo apt install nfs-common

sudo mkdir -p /nfs/general
sudo mount 172.31.18.123:/var/nfs/files /nfs/general