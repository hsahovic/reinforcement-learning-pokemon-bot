import asyncio
from players.ml_random_battle import ModelManager


async def main():
    model_manager = ModelManager()
    await model_manager.initial_training(
        number_of_battles=1000, concurrent_battles=100, log_messages=False
    )
    await model_manager.self_training(
        number_of_battles=100, concurrent_battles=100, log_messages=True, iterations=300
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
