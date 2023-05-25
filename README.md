# ssplz_device
Sample code of sensing plaza device

# setup

'''
echo "system update"

apt update
apt upgrade -y

sudo timedatectl set-timezone Asia/Tokyo

apt install -y python3-pip python3-flask python3-requests python3-pandas
pip3 install OPi.GPIO

cd
git clone https://github.com/shinob/ssplz_device.git
cd ssplz_device/client
cp config_org.py config.py
'''