import asyncio
from players.fully_connected_random_model import FullyConnectedRandomModel


async def main():
    model_manager = FullyConnectedRandomModel()

    # Start from scratch
    # await model_manager.initial_training(
    # number_of_battles=100, concurrent_battles=20, log_messages=False
    # )

    # Load latest model
    # model_manager.load()
    await model_manager.self_training(
        number_of_battles=3, concurrent_battles=3, log_messages=False, iterations=2
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
