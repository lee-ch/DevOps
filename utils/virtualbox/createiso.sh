#!/usr/bin/env bash

# Creates a new Ubuntu unattended install ISO image and sets a static IP address if static_ip
# is set to true
tmp=/data/vms/ubuntu
enable_ssh=true
static_ip=true
ipaddress="%system.ipaddress%"
netmask="%system.netmask%"
broadcast="%system.broadcast%"
network="%system.network%"
gateway="%system.gateway%"
nameserver="%system.nameserver%"

# Download function
function download() {
	local url=$1
	echo -n "	"
	wget --progress=dot $url 2>&1 | grep --line-buffered "%" | \
		sed -u -e "s,\.,,g" | awk '{printf("\b\b\b\b%4s", $2)}'
	echo -ne "\b\b\b\b"
	echo " DONE"
}

# Check if program is installed
function program_installed() {
	local ret=1
	type $1 > /dev/null 2>&1 || { local ret=0; }
	echo $ret
}

echo
echo " +---------------------------------------------------+"
echo " |            Creating Ubuntu ISO Image              |"
echo " +---------------------------------------------------+"
echo

# Check if we're using Ubuntu 16.04
fgrep "16.04" /etc/os-release > /dev/null 2>&1
if [ $? -eq 0 ]; then
	ub1604="yes"
fi

# Get latest version of Ubuntu LTS
tmphtml=$tmp/tmphtml
rm $tmphtml > /dev/null 2>&1
wget -O $tmphtml 'http://releases.ubuntu.com/' > /dev/null 2>&1

prec=$(fgrep Precise $tmphtml | head -1 | awk '{print $3}')
trus=$(fgrep Trusty $tmphtml | head -1 | awk '{print $3}')
xenn=$(fgrep Xenial $tmphtml | head -1 | awk '{print $3}')


download_file="ubuntu-$xenn-server-amd64.iso"
download_location="http://releases.ubuntu.com/$xenn/"
new_iso_name="ubuntu-$xenn-server-amd64-unattended.iso"

if [ -f /etc/timezone ]; then
	timezone=$(cat /etc/timezone)
elif [ -h /etc/localtime]; then
	timezone=$(readlink /etc/localtime | sed "s/\/usr\/share\/zoneinfo\///")
else
	checksum=$(md5sum /etc/localtime | cut -d' ' -f1)
	timezone=$(find /usr/share/zoneinfo/ -type f -exec md5sum {} \; | grep "^$checksum" | sed "s/.*\/usr\/share\/zoneinfo\///" | head -n 1)
fi


# ISO Variables for TeamCity to process
hostname="%system.hostname%"
timezone="%timezone%"
username="%username%"
password="%password%"
bootable="%bootable%"

cd $tmp
if [[ ! -f $tmp/$download_file ]]; then
	echo -n "Downloading ${download_file}..."
	download "$download_location$download_file"
fi

if [[ ! -f $tmp/download_file ]]; then\
	echo -e "Error: Failed to download ISO: $download_location$download_file"
	echo -e "This file may have moved or may no longer exist.\n"
	echo -e "You can download it manually and move it to $tmp/$download_file"
	echo -e "Then re-run this build again.\n"
fi


# Download preseed file
seed_file="netson.seed"
if [[ ! -f $tmp/$seed_file ]]; then
	echo -n "Downloading ${seed_file}..."
	download "https://raw.githubusercontent.com/lee-ch/ubuntu-auto-install/master/$seed_file"
fi


# Install required packages
echo -e "Installing required packages"
if [ $(program_installed "mkpasswd") -eq 0 ] || [ $(program_installed "mkisofs") -eq 0 ]; then
	apt-get -y update > /dev/null 2>&1
	apt-get -y install whois genisoimage > /dev/null 2>&1
fi

if [[ $bootable == "yes" ]] || [[ $bootable == "y" ]]; then
	if [ $(program_installed "isohybrid") -eq 0 ]; then
		#16.04
		if [[ $ub1604 == "yes" || $(lsb_release -cs) == "artful" ]]; then
			apt-get -y install syslinux syslinux-utils > /dev/null 2>&1
		else
			apt-get -y install syslinux > /dev/null 2>&1
		fi
	fi
fi

echo -e "Remastering iso file $tmp/$download_file"
mkdir -p $tmp
mkdir -p $tmp/iso_org
mkdir -p $tmp/iso_new

# Mount the image
if grep -qs $tmp/iso_org /proc/mounts; then
	echo "Image already mounted, continuing..."
else
	(mount -o loop $tmp/$download_file $tmp/iso_org > /dev/null 2>&1)
fi

# Copy iso contents to directory
cp -rT $tmp/iso_org $tmp/iso_new > /dev/null 2>&1


# Set language for the installation menu
cd $tmp/iso_new
# Doesn't work for 16.04
echo en > $tmp/iso_new/isolinux/lang

sed -i -r 's/timeout\s+[0-9]+/timeout 1/g' $tmp/iso_new/isolinux/isolinux.cfg

# Set late command
if [[ $ub1604 == "yes" ]]; then
	late_command="apt-install wget; in-target wget --no-check-certificate -O /home/$username/start.sh https://github.com/netson/ubuntu-unattended/raw/master/start.sh ;\
		in-target chmod +x /home/$username/start.sh ;"
fi

if [ $enable_ssh ]; then
	# Install openssh-server, open port 22 and configure static IP
	late_command="in-target apt-get install openssh-server -y; in-target cp -p /etc/ssh/sshd_config{,.backup}; in-target sed -Ei 's/\#.*(Port 22)/\1/g' /etc/ssh/sshd_config; in-target service ssh restart; "
	if [ $static_ip ]; then
		late_command=$late_command"in-target sed -Ei 's/(iface enp0s3 inet) dhcp/\1 static/g' /etc/network/interfaces; "
		late_command=$late_command"in-target sed -i '/iface enp0s3 inet static/a address $ipaddress' /etc/network/interfaces; "
		late_command=$late_command"in-target sed -i '/address $ipaddress/a netmask $netmask' /etc/network/interfaces; "
		late_command=$late_command"in-target sed -i '/netmask $netmask/a broadcast $broadcast' /etc/network/interfaces; "
		late_command=$late_command"in-target sed -i '/broadcast $broadcast/a network $network' /etc/network/interfaces; "
		late_command=$late_command"in-target sed -i '/network $network/a gateway $gateway' /etc/network/interfaces; "
		late_command=$late_command"in-target sed -i 's/.*/nameserver $nameserver/g /etc/resolv.conf; '
	fi
	# Configure user to run sudo without password
	late_command=$late_command"in-target sed -i '/\# User privilege specification/a $username	ALL=(ALL) NOPASSWD: ALL' /etc/sudoers; "
	late_command=$late_command"in-target sed -i '/\%sudo.*ALL=(ALL:ALL).*ALL/a %${username}	ALL=(ALL:ALL) NOPASSWD: ALL' /etc/sudoers"
	echo "
	# Setup first run script
	d-i preseed/late_command					string		$late_command" >> $tmp/iso_new/preseed/$seed_file
fi


# Copy preseed file to iso
cp -rT $tmp/$seed_file $tmp/iso_new/preseed/$seed_file


# Include firstrun script
echo "
# Setup first run script
d-i preseed/late_command					string		$late_command" >> $tmp/iso_new/preseed/$seed_file


# Generate password hash
pwhash=$(echo $password | mkpasswd -s -m sha-512)

# Update seed file
sed -i "s@{{username}}@$username@g" $tmp/iso_new/preseed/$seed_file
sed -i "s@{{pwhash}}@$pwhash@g" $tmp/iso_new/preseed/$seed_file
sed -i "s@{{hostname}}@$hostname@g" $tmp/iso_new/preseed/$seed_file
sed -i "s@{{timezone}}@$timezone@g" $tmp/iso_new/preseed/$seed_file

# Calculate checksum of seed file
seed_checksum=$(md5sum $tmp/iso_new/preseed/$seed_file)

# add the autoinstall option to the menu
sed -i "/label install/ilabel autoinstall\n\
  menu label ^Autoinstall NETSON Ubuntu Server\n\
  kernel /install/vmlinuz\n\
  append file=/cdrom/preseed/ubuntu-server.seed initrd=/install/initrd.gz auto=true priority=high preseed/file=/cdrom/preseed/netson.seed preseed/file/checksum=$seed_checksum --" $tmp/iso_new/isolinux/txt.cfg


echo -e "Creating new ISO Image"
cd $tmp/iso_new
mkisofs -D -r -V "NETSON_UBUNTU" -cache-inodes -J -l -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -o $tmp/$new_iso_name . > /dev/null 2>&1

# Make iso bootable
if [[ $bootable == "yes" ]] || [[ $bootable == "y" ]]; then
	isohybrid $tmp/$new_iso_name
fi

# Cleanup
umount $tmp/iso_org
rm -rf $tmp/iso_new
rm -rf $tmp/iso_org
rm -rf $tmphtml

# Print info
echo -e "-----"
echo -e "ISO File created successfully"
echo -e "Username: $username"
echo -e "Password: $pwhash"
echo -e "Hostname: $hostname"
echo -e "Timezone: $timezone"
echo -e "-----\n"


# Unset variables
unset username
unset password
unset hostname
unset timezone
unset pwhash
unset download_file
unset download_location
unset new_iso_name
unset tmp
unset seed_file