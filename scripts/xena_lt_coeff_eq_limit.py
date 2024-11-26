###############################################################
#                                                             #
#     COEFFICIENT BOUNDARY TEST - COEFF & EQ LIMIT TEST       #
#                                                             #
# Objective                                                   #
# To make the test port to respond COEFF_EQ_AT_LIMIT or       #
# COEFF_AT_LIMIT or EQ_AT_LIMIT when keep incrementing        #
# a coefficient on the remote transmitter.                    #
#                                                             #
###############################################################

import asyncio
import logging
from xena_anlt_lib import coeff_boundary_coeff_eq_limit_test
from xoa_driver import enums

#---------------------------
# GLOBAL PARAMS
#---------------------------
CHASSIS_IP = "10.165.136.60"
TEST_PORT = "3/0"
COEFF = "main" # allowed values = "pre3 | pre2 | pre | main | post"
PRESET = 1 # allowed values = 1, 2, 3, 4, 5
INCLUDE_AUTONEG = False # Do you want autoneg? (Some vendor's equipment cannot separate AN from LT. But since Xena is test equipment, you can choose if you want to include autoneg or not.)
USE_PAM4PRE = False # Do you want the trainer to request the DUT port to use PAM4 with Precoding? If not, it will only request PAM4.

#---------------------------
# xena_lt_coeff_eq_limit
#---------------------------
async def xena_lt_coeff_eq_limit(chassis: str, test_port_str: str, preset: int, coeff: str, include_an: bool, use_pam4pre: bool):
    # configure basic logger
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format="%(asctime)s  %(message)s",
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(filename="lt_coeff_eq_limit_test.log", mode="a"),
            logging.StreamHandler()]
        )

    _mid_test = int(test_port_str.split("/")[0])
    _pid_test = int(test_port_str.split("/")[1])

    await coeff_boundary_coeff_eq_limit_test(
        logger=logger,
        chassis_ip=chassis,
        module_id=_mid_test,
        port_id=_pid_test,
        username="trainer",
        should_link_recovery=False,
        should_an=include_an,
        coeff=enums.LinkTrainCoeffs[coeff.upper()],
        preset=preset,
        an_good_check_retries=20,
        frame_lock_retries=10,
        should_pam4pre=use_pam4pre
    )

if __name__ == "__main__":
    asyncio.run(xena_lt_coeff_eq_limit(
        chassis=CHASSIS_IP,
        test_port_str=TEST_PORT,
        preset=PRESET,
        coeff=COEFF,
        include_an=INCLUDE_AUTONEG,
        use_pam4pre = USE_PAM4PRE
    ))
