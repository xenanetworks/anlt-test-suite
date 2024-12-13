
Maximum Limit Tests
====================

Filename
---------

``xena_lt_coeff_max_limit.py``

Objective
-----------

To make the test port to respond ``COEFF_AT_LIMIT`` when incrementing a coefficient on the remote transmitter.

Configurations
-----------------

* Number of ``<repetitions>``, default to 1
* AN/LT Configuration
    * AN enabled/disabled.
    * ``<preset>`` the remote transmitter should start.
    * ``<coefficients>`` of the remote transmitter.
    * LT control action: **INCREMENT**
    * ``<serdes>`` the serdes lane(s) to test
* Port configuration
    * Interface type, e.g. QSFPDD 100G CR
    * Serdes speed
    * Number of Serdes (read-only)

Procedure
-----------------

1. If AN is enabled, test port starts AN + interactive LT. Else, start interactive LT on the port.

2. AN Phase

    * 2.1. If AN result is ``AN_GOOD_CHECK``, continue to LT Phase.
    * 2.2. If AN result is not ``AN_GOOD_CHECK``, quit the test and report AN failure with the AN status.

3. LT Phase:

    * 3.1. Request the remote transmitter to use ``PAM4`` or ``PAM with Precoding`` modulation.
    * 3.2. Request the remote transmitter to use ``<preset>`` on each specified Serdes.
    * 3.3. Request the remote transmitter to **INCREMENT** coefficient on each specified Serdes.
    * 3.4. If the response is ``COEFF_AT_LIMIT`` or ``COEFF_NOT_SUPPORTED``, then test is OK.
    * 3.5. If the response is  ``EQ_AT_LIMIT`` or ``COEFF_EQ_AT_LIMIT`` or frame lock is lost, then the test is failed.
    * 3.6. Report the response on each specified Serdes.

4. Stop AN and LT on the test port.
5. Repeat 1-4 until all ``<coefficients>`` are tested.
6. Repeat 1-5 until all ``<repetitions>`` are tested.

.. note::
    
    This test may cause the local port to lose frame lock to the remote port.

Statistics
-----------------
* Timestamp
* Repetition #
* AN status
* For each Serdes
    * Starting preset
    * For each coefficient
        * Last response
