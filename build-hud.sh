#!/bin/sh

# To build:
# Make sure Kivy is installed in your /Applications folder
# Clone the kivy-sdk repo from:
#    https://github.com/kivy/kivy-sdk-packager
# put this script in kivy-sdk-packager/osx
# run sh build-hud.sh ~/path/to/SteakRazor

sudo echo "removing .app"
sudo rm -rf SteakRazor.app

echo "removing Kivy.app"
sudo rm -rf Kivy.app

echo "removing .dmg"
sudo rm SteakRazor.dmg

echo "removing -temp.dmg"
sudo rm SteakRazor-temp.dmg

echo "copying Kivy to this directory"
sudo cp -a /Applications/Kivy.app ./Kivy.app

# $1 is path to HUD directory
echo "packaging app..."
sudo ./package_app.py $1 --appname="SteakRazor" --with-gstreamer=no

echo "removing .git"
sudo rm -rf ./SteakRazor.app/Contents/Resources/yourapp/.git

echo "removing QuartzCore"
sudo rm -rf ./SteakRazor.app/Contents/Frameworks/QuartzCore.framework

echo "removing Quartz"
sudo rm -rf ./SteakRazor.app/Contents/Frameworks/Quartz.framework

echo "removing cython fragments"
sudo rm ./SteakRazor.app/Contents/Resources/yourapp/*.c
sudo rm ./SteakRazor.app/Contents/Resources/yourapp/*.pyc
sudo rm ./SteakRazor.app/Contents/Resources/yourapp/dbs.py
sudo rm ./SteakRazor.app/Contents/Resources/yourapp/proc_hands.py
sudo rm ./SteakRazor.app/Contents/Resources/yourapp/os_tools.py

echo "building dmg"
sudo ./create-osx-dmg.sh SteakRazor.app
