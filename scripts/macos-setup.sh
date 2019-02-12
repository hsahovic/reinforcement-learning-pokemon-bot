# Installing dependencies
git clone https://github.com/Synedh/showdown-battle-bot
git clone https://github.com/Zarel/Pokemon-Showdown

git submodule init 
git submodule update

# Showdown requieres node.js
brew install nodejs

# Installing the server
cd Pokemon-Showdown
npm install
cd ..

# Installing the base bot
cd showdown-battle-bot
pip3 install -r requirement.txt
cd ..
