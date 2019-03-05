import asyncio
from players.ml_random_battle import ModelManager

async def main():
    model_manager = ModelManager()

    await model_manager.initial_training()
    await model_manager.self_training()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
