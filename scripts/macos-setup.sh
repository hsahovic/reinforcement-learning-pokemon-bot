# Installing dependencies
git clone https://github.com/Zarel/Pokemon-Showdown

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

# Updating some showdown files
sh scripts/update-showdown.sh
