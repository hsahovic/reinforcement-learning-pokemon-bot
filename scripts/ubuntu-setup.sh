# Installing dependencies
git submodule add https://github.com/Synedh/showdown-battle-bot
git submodule add https://github.com/Zarel/Pokemon-Showdown

git submodule init 
git submodule update

# Showdown requieres node.js
curl -sL https://deb.nodesource.com/setup_11.x | sudo -E bash -
sudo apt-get install -y nodejs

# Installing the server
cd Pokemon-Showdown
npm install
cd ..

# Installing the base bot
cd showdown-battle-bot
pip3 install -r requierement.txt
cd ..
