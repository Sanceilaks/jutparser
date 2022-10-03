### Пример
```python
async def main():
    for i in await get_animes('Две звезды'):
        async for j in i.get_episodes():
            print(j.name)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
```