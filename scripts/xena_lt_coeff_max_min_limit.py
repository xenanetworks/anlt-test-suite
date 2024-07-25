###############################################################
#                                                             #
#       COEFFICIENT BOUNDARY TEST - MAX/MIN LIMIT TEST        #
#                                                             #
# Objective                                                   #
# To measure the frame lock status of the remote transmitter  #
# using the specified preset.                                 #
#                                                             #
###############################################################
import asyncio
import logging
from xena_anlt_lib import coeff_boundary_max_min_limit_test, start_anlt_on_dut, stop_anlt_on_dut
from xoa_driver import enums

CHASSIS_IP = "10.165.136.60"
TEST_PORT = "3/0"
DUT_PORT = "6/0"
SERDES = 1
COEFF = "main"
PRESET = 3
SIMULATED_DUT = False
TYPE = "max"

async def main(chassis: str, test_port_str: str, dut_port_str: str, serdes: int, preset: int, coeff: str, simulate_dut: bool, test_type: str):
    # configure basic logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(asctime)s  %(message)s",
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(filename="lt_coeff_max_min_limit_test.log", mode="a"),
            logging.StreamHandler()]
        )

    _mid_test = int(test_port_str.split("/")[0])
    _pid_test = int(test_port_str.split("/")[1])
    _mid_dut = int(dut_port_str.split("/")[0])
    _pid_dut = int(dut_port_str.split("/")[1])

    if simulate_dut:
        await start_anlt_on_dut(chassis_ip=chassis, module_id=_mid_dut, port_id=_pid_dut, username="sim_dut", should_link_recovery=False, should_an=False, logger=logger)

    await coeff_boundary_max_min_limit_test(
        chassis_ip=chassis,
        module_id=_mid_test,
        port_id=_pid_test,
        username="xoa_exerciser",
        should_link_recovery=False,
        should_an=False,
        preset=preset,
        coeff=enums.LinkTrainCoeffs[coeff.upper()],
        type=test_type,
        serdes=serdes,
        logger=logger,
        an_good_check_retries=20,
        frame_lock_retries=10
    )

    if simulate_dut:
        await stop_anlt_on_dut(chassis_ip=chassis, module_id=_mid_dut, port_id=_pid_dut, username="sim_dut", logger=logger)


if __name__ == "__main__":
    asyncio.run(main(
        chassis=CHASSIS_IP,
        test_port_str=TEST_PORT,
        dut_port_str=DUT_PORT,
        serdes = SERDES,
        preset = PRESET,
        coeff = COEFF,
        simulate_dut=SIMULATED_DUT,
        test_type = TYPE
        ))
