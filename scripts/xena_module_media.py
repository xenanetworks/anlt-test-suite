import asyncio
import logging
from xena_anlt_lib import change_module_media
from xoa_driver import enums, testers, modules

CHASSIS_IP = "10.165.136.60"
MODULE_INDEX = 3
MODULE_MEDIA = "QSFPDD800_ANLT" # "OSFP800_ANLT", "QSFP112_ANLT", "QSFPDD_ANLT", "OSFP_ANLT", "QSFP56_ANLT"
PORT_CONFIG = "8x100G"

async def main(chassis: str, module_index: int, module_media: str, port_config: str):
    # create logger
    logger = logging.getLogger('module_media')
    logging.basicConfig(level=logging.DEBUG)

    _module_media = enums.MediaConfigurationType[module_media.upper()]
    _port_count = int(port_config.split("x")[0])
    _port_speed = int(port_config.split("x")[1].replace("G", ""))

    async with testers.L23Tester(chassis, "xoa") as tester:
        module = tester.modules.obtain(module_index)

        if not isinstance(module, modules.Z800FreyaModule):
            return

        await change_module_media(
            tester=tester,
            module=module,
            username="xoa",
            module_media=_module_media,
            port_count=_port_count,
            port_speed=_port_speed,
            logger=logger
        )


if __name__ == "__main__":
    asyncio.run(main(chassis=CHASSIS_IP, module_index=MODULE_INDEX, module_media=MODULE_MEDIA, port_config=PORT_CONFIG))
