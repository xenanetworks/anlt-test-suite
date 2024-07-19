import asyncio
import logging
from xena_anlt_lib import change_module_media
from xoa_driver import enums, testers, modules


async def main():
    # create logger
    logger = logging.getLogger('module_media')
    logging.basicConfig(level=logging.DEBUG)

    async with testers.L23Tester("10.165.136.60", "xoa") as tester:
        module = tester.modules.obtain(3)

        await change_module_media(
            tester=tester,
            module=module,
            username="xoa",
            module_media=enums.MediaConfigurationType.QSFPDD800_ANLT,
            port_count=8,
            port_speed=100,
            logger=logger
        )


if __name__ == "__main__":
    asyncio.run(main())
