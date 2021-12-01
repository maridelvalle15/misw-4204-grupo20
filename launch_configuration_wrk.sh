   
#!/bin/bash

rm /var/lib/apt/lists/lock
rm /var/cache/apt/archives/lock
rm /var/lib/dpkg/lock
rm -f /var/lib/dpkg/lock-frontend
systemctl stop unattended-upgrades
apt-get purge -y unattended-upgrades
apt-get update

apt-get -y install git
apt-get -y install curl
curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# stop apache
/etc/init.d/apache2 stop
# git clone with access token
git clone https://<token>:x-oauth-basic@github.com/MISW-4204-ComputacionEnNube/Proyecto-Grupo20-202120.git
cd Proyecto-Grupo20-202120
git checkout feature/aws_autoscaling_api

bash run_docker_wkr.sh
