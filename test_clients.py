#!/usr/bin/env python3
import asyncio
import aiohttp
import random
import string
import datetime
import signal
from typing import List, Set
import argparse

class EmojiClient:
    def __init__(self, server_url: str, client_id: str):
        self.server_url = server_url
        self.client_id = client_id
        self.running = True
        self.emoji_types = ['😊', '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣']
        
    async def send_emoji(self, session: aiohttp.ClientSession) -> int:
        """Send a random emoji for this client to the emoji service."""
        data = {
            "user_id": self.client_id,
            "emoji_type": random.choice(self.emoji_types),
            "timestamp": datetime.datetime.now().isoformat(),
            "client_id": self.client_id
        }
        
        try:
            async with session.post(f'{self.server_url}/emoji', json=data) as response:
                return response.status
        except aiohttp.ClientError as e:
            print(f"Error sending emoji for client {self.client_id}: {e}")
            return 500
            
    async def run(self, session: aiohttp.ClientSession, delay_range: tuple[float, float]):
        """Continuously send emojis with random delays."""
        while self.running:
            status = await self.send_emoji(session)
            print(f"Client {self.client_id}: Sent emoji, status: {status}")
            # Random delay between requests to simulate realistic usage
            delay = random.uniform(*delay_range)
            await asyncio.sleep(delay)

async def main():
    parser = argparse.ArgumentParser(description='Emoji Client Simulator')
    parser.add_argument('--num-clients', type=int, default=5, help='Number of concurrent clients')
    parser.add_argument('--server-url', type=str, default='http://localhost:5000', help='Server URL')
    parser.add_argument('--min-delay', type=float, default=0.5, help='Minimum delay between requests (seconds)')
    parser.add_argument('--max-delay', type=float, default=2.0, help='Maximum delay between requests (seconds)')
    args = parser.parse_args()

    # Create clients
    clients: List[EmojiClient] = []
    for _ in range(args.num_clients):
        client_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        clients.append(EmojiClient(args.server_url, client_id))
    
    # Handle graceful shutdown
    shutdown_event = asyncio.Event()
    
    def signal_handler():
        print("\nShutdown signal received. Stopping clients...")
        for client in clients:
            client.running = False
        shutdown_event.set()
        
    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, signal_handler)
    
    # Statistics tracking
    request_count = 0
    start_time = datetime.datetime.now()
    
    async def print_stats():
        nonlocal request_count
        while not shutdown_event.is_set():
            await asyncio.sleep(5)
            duration = (datetime.datetime.now() - start_time).total_seconds()
            rate = request_count / duration if duration > 0 else 0
            
           
    
    # Create a single session for all clients
    async with aiohttp.ClientSession() as session:
        # Start all clients
        tasks: Set[asyncio.Task] = set()
        
        # Add client tasks
        for client in clients:
            task = asyncio.create_task(
                client.run(session, (args.min_delay, args.max_delay))
            )
            tasks.add(task)
        
        # Add statistics task
        stats_task = asyncio.create_task(print_stats())
        tasks.add(stats_task)
        
        try:
            # Wait for shutdown signal
            await shutdown_event.wait()
        finally:
            # Cancel all tasks
            for task in tasks:
                task.cancel()
            
            # Wait for tasks to finish
            await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
