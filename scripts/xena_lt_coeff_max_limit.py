import asyncio
import logging
from xena_anlt_lib import coeff_boundary_max_min_limit_test, start_anlt_on_dut, stop_anlt_on_dut
from xoa_driver import enums

CHASSIS_IP = "10.165.136.60"

async def main():
    # create logger
    logger = logging.getLogger('lt_coeff_max_limit_test')
    logging.basicConfig(level=logging.DEBUG)

    # await start_anlt_on_dut(
    #     chassis_ip=CHASSIS_IP,
    #     module_id=6,
    #     port_id=0,
    #     username="sim_dut",
    #     should_link_recovery=False,
    #     should_an=False,
    #     logger=logger
    # )

    await coeff_boundary_max_min_limit_test(
        chassis_ip=CHASSIS_IP,
        module_id=3,
        port_id=0,
        username="xoa_exerciser",
        should_link_recovery=False,
        should_an=False,
        preset=2,
        coeff=enums.LinkTrainCoeffs.MAIN,
        type="max",
        serdes=0,
        logger=logger,
        an_good_check_retries=20,
        frame_lock_retries=10
    )

    # await stop_anlt_on_dut(
    #     chassis_ip=CHASSIS_IP,
    #     module_id=6,
    #     port_id=0,
    #     username="sim_dut",
    #     logger=logger
    # )


if __name__ == "__main__":
    asyncio.run(main())
