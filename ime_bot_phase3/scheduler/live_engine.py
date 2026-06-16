import asyncio
import aiohttp

def start_engine():

    asyncio.run(main())


from collectors.cdc_collector import (
    run as fetch_cdc
)

from collectors.option_collector import (
    run as fetch_option
)

from collectors.etf_collector import (
    run as fetch_etf
)


async def cdc_loop():

    while True:

        try:

            fetch_cdc()

        except Exception as ex:

            print(ex)

        await asyncio.sleep(1)


async def option_loop():

    while True:

        try:

            fetch_option()

        except Exception as ex:

            print(ex)

        await asyncio.sleep(1)


async def etf_loop():

    while True:

        try:

            fetch_etf()

        except Exception as ex:

            print(ex)

        await asyncio.sleep(1)


async def main():

    await asyncio.gather(

        cdc_loop(),

        option_loop(),

        etf_loop()
    )


if __name__ == "__main__":

    asyncio.run(main())