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
from xena_anlt_lib import preset_performance

#---------------------------
# GLOBAL PARAMS
#---------------------------
CHASSIS_IP = "10.165.136.60"
TEST_PORT = "3/0"
PRESET = 1 # allowed values = 1, 2, 3, 4, 5
INCLUDE_AUTONEG = False # Do you want autoneg? (Some vendor's equipment cannot separate AN from LT. But since Xena is test equipment, you can choose if you want to include autoneg or not.)
USE_PAM4PRE = False # Do you want the trainer to request the DUT port to use PAM4 with Precoding? If not, it will only request PAM4.

#---------------------------
# xena_lt_preset_performance
#---------------------------
async def xena_lt_preset_performance(chassis: str, test_port_str: str, preset: int, include_an: bool, use_pam4pre: bool):
    # configure basic logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(asctime)s  %(message)s",
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(filename="lt_preset_performance_test.log", mode="a"),
            logging.StreamHandler()]
        )

    _mid_test = int(test_port_str.split("/")[0])
    _pid_test = int(test_port_str.split("/")[1])

    await preset_performance(
        chassis_ip=chassis,
        module_id=_mid_test,
        port_id=_pid_test,
        username="trainer",
        should_link_recovery=False,
        should_an=include_an,
        preset=preset,
        logger=logger,
        an_good_check_retries=20,
        frame_lock_retries=10,
        should_pam4pre=use_pam4pre
    )

if __name__ == "__main__":
    asyncio.run(xena_lt_preset_performance(
        chassis=CHASSIS_IP,
        test_port_str=TEST_PORT,
        preset=PRESET,
        include_an=INCLUDE_AUTONEG,
        use_pam4pre = USE_PAM4PRE
    ))
