import json
import requests
import websockets


class PlayerNetwork:
    """
    Network interface of a player.
    
    In charge of communicating with the pokemon showdown server.
    """

    def __init__(
        self, username: str, password: str, server_adress: str, avatar: int = None
    ) -> None:
        """
        Initialises interface.
        """
        self._avatar = avatar
        self._logged_in = False
        self._password = password
        self._server_adress = server_adress
        self._username = username

        self._auth_adress = "https://play.pokemonshowdown.com/action.php?"

    async def _log_in(self, conf_1: str, conf_2: str) -> None:
        """
        Log in player to specified username.
        conf_1 and conf_2 are confirmation strings received upon server access.
        They are needed to log in.
        """
        log_in_request = requests.post(
            self._auth_adress,
            data={
                "act": "login",
                "name": self._username,
                "pass": self._password,
                "challstr": conf_1 + "%7C" + conf_2,
            },
        )
        await self.send_message(
            f"/trn {self._username},0,{json.loads(log_in_request.text[1:])['assertion']}"
        )
        self._logged_in = True

        # If there is an avatar to select, let's select it !
        if self._avatar:
            await self.send_message(f"/avatar {self._avatar}")

    async def accept_challenge(self, user:str) -> None:
        await self.send_message(f"/accept {user}")

    async def challenge(self, player=None, format=None):
        if not self.logged_in:
            return

        if player is None:
            player = self.to_target
        if format is None:
            format = self.format

        if player and format:
            await self.send_message(f"/challenge {player}, {format}")
        else:
            print(f"No player or format specified in call to 'challenge' from {self}\nplayer: {player}\nformat: {format}")
            raise ValueError(
                f"No player or format specified in call to 'challenge' from {self}\nplayer: {player}\nformat: {format}"
            )

    async def listen(self) -> None:
        async with websockets.connect(self.websocket_adress) as websocket:
            self._websocket = websocket
            while True:
                message = await websocket.recv()
                print(f"\n<< {message}")
                await self.manage_message(message)

    async def manage_message(self, message: str) -> None:
        """
        Parse and manage responses to incoming messages.
        """
        split_message = message.split("|")
        # challstr confirms that we are connected to the server
        # we can therefore login
        if split_message[1] == "challstr":
            conf_1, conf_2 = split_message[2], split_message[3]
            await self._log_in(conf_1, conf_2)

        # updatechallenges means that we received a challenge
        elif "updatechallenges" in split_message[1]:
            response = json.loads(split_message[2])
            print(response)
            for user, format in json.loads(split_message[2]).get('challengesFrom', {}).items():
                if format == self.format:
                    await self.accept_challenge(user)

        elif "battle" in split_message:
            pass

    async def send_message(
        self, message: str, room: str = "", message_2: str = None
    ) -> None:
        if message_2:
            to_send = "|".join([room, message, message_2])
        else:
            to_send = "|".join([room, message])
        print(f"\n>> {to_send}")
        await self._websocket.send(to_send)

    @property
    def logged_in(self) -> bool:
        return self._logged_in

    @property
    def username(self) -> str:
        return self._username

    @property
    def websocket_adress(self) -> str:
        return f"ws://{self._server_adress}/showdown/websocket"
