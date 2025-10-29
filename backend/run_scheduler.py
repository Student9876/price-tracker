import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler import check_all_prices

async def main():
    scheduler = AsyncIOScheduler()
    # Run immediately on start, then every 24 hours
    scheduler.add_job(check_all_prices, "interval", hours=24, misfire_grace_time=900)
    scheduler.start()
    print("Scheduler started in background worker mode. Press Ctrl+C to exit.")

    # Keep the script running indefinitely
    while True:
        await asyncio.sleep(3600) # Sleep for an hour

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")