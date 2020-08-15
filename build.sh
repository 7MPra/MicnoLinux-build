#!/bin/bash
rm *.iso
URL=https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/`curl -so- https://cdimage.debian.org/cdimage/unofficial/non-free/cd-including-firmware/ | grep live | grep nonfree | sed -e "s/.*href=\"\(.*\/\)\".*/\1/g"`
wget ${URL}amd64/iso-hybrid/`curl -so- ${URL}amd64/iso-hybrid/ | grep xfce | grep iso | sed -e "s/.*href=\"\(.*.iso\)\".*/\1/g"`
rm -r BaseDisk
mkdir BaseDisk
mount *.iso BaseDisk/
rm -rf Simply_Circles_Themes
git clone https://github.com/ju1464/Simply_Circles_Themes.git
rm -rf Tela-circle-red
rm -rf Tela-circle-red-dark
git clone https://github.com/vinceliuice/Tela-circle-icon-theme.git
./Tela-circle-icon-theme/install.sh -d ./ red
cp Tela-circle-icon-theme/COPYING ./Tela-circle-red
cp Tela-circle-icon-theme/AUTHORS ./Tela-circle-red
cp Tela-circle-icon-theme/COPYING ./Tela-circle-red-dark
cp Tela-circle-icon-theme/AUTHORS ./Tela-circle-red-dark
rm -rf Tela-circle-icon-theme
rm -rf deb
mkdir deb
cd deb
wget https://download.opensuse.org/repositories/home:/antergos/Debian_9.0/amd64/lightdm-webkit2-greeter_2.2.5-1+15.8_amd64.deb
git clone https://github.com/TMP-tenpura/MicnoSwitcher.git
cd MicnoSwitcher
dpkg -b MicnoSwitcher
mv MicnoSwitcher.deb ..
cd ..
rm -rf MicnoSwitcher
git clone https://github.com/TMP-tenpura/MicnoTheme.git
cd MicnoTheme
chmod 755 MicnoTheme/DEBIAN/postinst
dpkg -b MicnoTheme
mv MicnoTheme.deb ..
cd ..
rm -rf MicnoTheme
git clone https://github.com/TMP-tenpura/lightdm-theme-micno.git
cd lightdm-theme-micno
dpkg -b lightdm-theme-micno
mv lightdm-theme-micno.deb ..
cd ..
rm -rf  lightdm-theme-micno
git clone https://github.com/TMP-tenpura/MicnoStarter.git
cd MicnoStarter
dpkg -b MicnoStarter
mv MicnoStarter.deb ..
cd ..
rm -rf MicnoStarter
cd ..
rm -rf kernel
mkdir kernel
cd kernel
mkdir config
PACK_NAME=`apt-cache search linux-config | tail -n 1 | sed 's/ .*//1'`
echo $PACK_NAME
apt download $PACK_NAME
dpkg -x *.deb config
xz -dv config/usr/src/$PACK_NAME/config.amd64_none_amd64.xz
rm *.deb
git clone -b `echo $PACK_NAME | sed 's/.*-//g'`/master https://github.com/zen-kernel/zen-kernel.git
mv config/usr/src/$PACK_NAME/config.amd64_none_amd64 ./zen-kernel/.config
cd zen-kernel
yes '' | make oldconfig
make -j 4 bindeb-pkg
cd ../../
find `pwd`/kernel -mindepth 1 -maxdepth 1 -name "linux*deb" | sed "s/^/deb /" > micno.Mflow
cat << EOF >> micno.Mflow
run sudo apt purge --autoremove \`dpkg -l | grep linux | grep "\\\`ls -1 /boot/ | grep vmlinuz | grep -v zen | sed "s/vmlinuz-\(.*\)-amd64/\1/"\\\`" | sed "s/^ii *\(linux[^ ]*\).*/\1/"\`
apt wget
apt curl
apt plank
apt grub-customizer
apt rhythmbox
apt vlc
apt fcitx-mozc
apt python3-distutils
add ./.config /etc/skel/
deb ./deb/MicnoStarter.deb
deb ./deb/MicnoSwitcher.deb
deb ./deb/MicnoTheme.deb
deb ./deb/lightdm-theme-micno.deb
deb ./deb/lightdm-webkit2-greeter_2.2.5-1+15.8_amd64.deb
add ./Simply_Circles_Themes/GTK-Gnome/Red/Simply_Circles_Red_Dark_Envolved/ /usr/share/themes/
add ./Tela-circle-red /usr/share/icons/
add ./Tela-circle-red-dark /usr/share/icons/
pge uim
pge xterm*
pge ibus*
pge anthy*
pge xiterm+thai
pge mlterm*
pge atril
pge exfalso
pge parole
pge firefox-esr
pge goldendict
pge khmerconverter
EOF
sudo python3 build.py \
	-f ./micno.Mflow\
	-s ./BaseDisk/live/filesystem.squashfs
