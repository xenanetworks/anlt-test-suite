import asyncio
import logging
from xena_anlt_lib import start_anlt_on_dut, preset_frame_lock, stop_anlt_on_dut


async def main():
    # create logger
    logger = logging.getLogger('lt_preset_link_up_test')
    logging.basicConfig(level=logging.DEBUG)

    await start_anlt_on_dut(
        chassis_ip="10.165.136.60",
        module_id=6,
        port_id=1,
        username="sim_dut",
        should_link_recovery=False,
        should_an=False,
        logger=logger
    )

    await preset_frame_lock(
        logger=logger,
        chassis_ip="10.165.136.60",
        module_id=3,
        port_id=1,
        username="xoa_exerciser",
        should_link_recovery=False,
        should_an=False,
        preset=1,
        serdes=0,
        an_good_check_retries=20,
        frame_lock_retries=10
    )

    await stop_anlt_on_dut(
        chassis_ip="10.165.136.60",
        module_id=6,
        port_id=1,
        username="sim_dut",
        logger=logger
    )


if __name__ == "__main__":
    asyncio.run(main())
