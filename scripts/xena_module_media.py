import asyncio
import logging
from xena_anlt_lib import change_module_media
from xoa_driver import enums


async def main():
    # create logger
    logger = logging.getLogger('module_media')
    logging.basicConfig(level=logging.DEBUG)

    await change_module_media(
        chassis_ip="10.20.30.50",
        module_id=0,
        username="xoa",
        module_media=enums.MediaConfigurationType.OSFP800,
        port_count=1,
        port_speed=800,
        logger=logger
    )


if __name__ == "__main__":
    asyncio.run(main())
