# Showdown requieres node.js
curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
sudo apt-get install -y nodejs

# Installing the server
cd Pokemon-Showdown
npm install
cd ..

# Installing the base bot
cd showdown-battle-bot
pip3 install -r requierements.txt
cd ..
