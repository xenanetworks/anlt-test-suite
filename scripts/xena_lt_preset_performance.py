###############################################################
#                                                             #
#               PRESET TEST - LINK PERFORMANCE TEST           #
#                                                             #
# Objective                                                   #
# To measure the link training BER performances of the remote #
# transmitter using the specified preset.                     #
#                                                             #
###############################################################

import asyncio
import logging
from xena_anlt_lib import start_anlt_on_dut, preset_performance, stop_anlt_on_dut

CHASSIS_IP = "10.165.136.60"
TEST_PORT = "3/0"
DUT_PORT = "6/0"
SERDES = 1
PRESET = 1
SIMULATED_DUT = False

async def main(chassis: str, test_port_str: str, dut_port_str: str, serdes: int, preset: int, simulate_dut: bool):
    # configure basic logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(asctime)s  %(message)s",
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(filename="lt_preset_link_up_test.log", mode="a"),
            logging.StreamHandler()]
        )

    _mid_test = int(test_port_str.split("/")[0])
    _pid_test = int(test_port_str.split("/")[1])
    _mid_dut = int(dut_port_str.split("/")[0])
    _pid_dut = int(dut_port_str.split("/")[1])

    if simulate_dut:
        await start_anlt_on_dut(chassis_ip=chassis, module_id=_mid_dut, port_id=_pid_dut, username="sim_dut", should_link_recovery=False, should_an=False, logger=logger)

    await preset_performance(
        chassis_ip=chassis,
        module_id=_mid_test,
        port_id=_pid_test,
        username="xoa_exerciser",
        should_link_recovery=False,
        should_an=False,
        preset=preset,
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
        simulate_dut=SIMULATED_DUT
    ))
