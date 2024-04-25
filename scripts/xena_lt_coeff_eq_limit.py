import asyncio
import logging
from xena_anlt_lib import coeff_boundary_coeff_eq_limit_test, start_anlt_on_dut, stop_anlt_on_dut
from xoa_driver import enums


async def main():
    # create logger
    logger = logging.getLogger('lt_coeff_eq_limit_test')
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

    await coeff_boundary_coeff_eq_limit_test(
        logger=logger,
        chassis_ip="10.165.136.60",
        module_id=3,
        port_id=1,
        username="xoa_exerciser",
        should_link_recovery=False,
        should_an=False,
        coeff=enums.LinkTrainCoeffs.MAIN,
        serdes=0,
        preset=1,
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
