sudo apt update
sudo apt install nfs-kernel-server

sudo mkdir /var/nfs/general -p
sudo chown nobody:nogroup /var/nfs/general

#vi /etc/exports
#/var/nfs/general    client_ip(rw,sync,no_subtree_check)
#/var/nfs/general    client_ip(rw,sync,no_subtree_check)

#/var/nfs/files      172.31.87.133(rw,sync,no_subtree_check)
#/var/nfs/files      172.31.25.241(rw,sync,no_subtree_check)

sudo systemctl restart nfs-kernel-server
