import asyncio
from players.policy_network import PolicyNetwork


async def main():
    model_manager = PolicyNetwork()

    # Start from scratch
    # await model_manager.initial_training(
    # number_of_battles=100, concurrent_battles=20, log_messages=False
    # )

    # Load latest model
    # model_manager.load()
    await model_manager.self_training(
        number_of_battles=1, concurrent_battles=1, log_messages=False, iterations=20
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
