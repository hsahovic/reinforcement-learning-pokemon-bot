import asyncio
from players.policy_network import PolicyNetwork


async def main():
    model_manager = PolicyNetwork()
    # Load model
    model_manager.load()

    print(f"{'-'*10} Testing {'-'*10}")
    perf = await model_manager.test(number_of_battles=20)
    print(f"\n{'*'*15} Performance: {perf*100:2.1f}% {'*'*15}\n")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())