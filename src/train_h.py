import asyncio
from players.ml_random_battle import ModelManager


async def main():


    model_manager = ModelManager()
    
    # Start from scratch
    # await model_manager.initial_training(
        # number_of_battles=100, concurrent_battles=20, log_messages=False
    # )

    # Load latest model
    model_manager.load()
    await model_manager.self_training(
        number_of_battles=10, concurrent_battles=10, log_messages=False, iterations=300
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
