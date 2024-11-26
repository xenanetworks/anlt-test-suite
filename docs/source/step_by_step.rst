Step-by-Step
=============================

Prerequisite
-------------

1. Install xoa-driver. Read `install xoa-driver <https://docs.xenanetworks.com/projects/xoa-python-api/en/latest/getting_started/index.html>`_ for details.
2. Prepare your DUT port. It is recommended that you turn off the ANLT timeout on the DUT port, if possible. This is to make sure that the timeout won't interrupt the automated test.


Run Test
---------

There are 5 test scripts in /scripts/ directory:

* ``xena_lt_preset_frame_lock.py``
* ``xena_lt_preset_performance.py``
* ``xena_lt_coeff_max_limit.py``
* ``xena_lt_coeff_min_limit.py``
* ``xena_lt_coeff_eq_limit.py``

In each script, you should set the following the parameter to match your test.

.. code-block:: python

    #---------------------------
    # GLOBAL PARAMS
    #---------------------------
    CHASSIS_IP = "10.165.136.60"
    TEST_PORT = "3/0"
    PRESET = 1 # allowed values = 1, 2, 3, 4, 5
    INCLUDE_AUTONEG = False # Do you want autoneg? (Some vendor's equipment cannot separate AN from LT. But since Xena is test equipment, you can choose if you want to include autoneg or not.)
    USE_PAM4PRE = False # Do you want the trainer to request the DUT port to use PAM4 with Precoding? If not, it will only request PAM4.

1. ``CHASSIS_IP``: the test equipment IP address.
2. ``TEST_PORT``: the test port on the test chassis that you will use to exercise your DUT port.
3. ``PRESET``: the preset (from 1 to 5) you want the DUT port to use.
4. ``INCLUDE_AUTONEG``: if your DUT port requires autoneg before link training.
5. ``USE_PAM4PRE``: the modulation, PAM4 or PAM with Precoding, you want the DUT port to use when doing link training.

After setting the parameters, you can execute the script.