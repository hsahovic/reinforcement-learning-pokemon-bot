import asyncio

from threading import Thread

from environnement.player_network import PlayerNetwork


class Player(PlayerNetwork):
    def __init__(
        self,
        username: str,
        password: str,
        server_adress: str,
        mode="wait",
        *,
        target_battles=10,
        to_target=None,
        format=None,
    ) -> None:
        super(Player, self).__init__(username, password, server_adress)
        self.current_battles = 0
        self.format = format
        self.mode = mode
        self.target_battles = target_battles
        self.to_target = to_target
        self.total_battles = 0

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

    async def run(self) -> None:
        if self.mode == "challenge":
            while self.total_battles < self.target_battles:
                print(self.username)
                await self.challenge()
                await asyncio.sleep(10)
        else:
            pass
