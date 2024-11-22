
Equalization Limit Test
===================================

Objective
------------

To make the test port to respond ``COEFF_AND_EQ_AT_LIMIT``.

Configurations
---------------

* Number of ``repetitions``, default to 1
* ANLT Configuration
    * AN enabled/disabled.
    * ``preset`` the remote transmitter should start.
    * ``Serdes to test``
* Port configuration
    * Interface type, e.g. QSFPDD 100G CR
    * Serdes speed
    * Number of Serdes (read-only)

Procedure
-----------

AN Phase:

1. If AN result is ``AN_GOOD_CHECK``, continue to LT Phase.
2. If AN result is not ``AN_GOOD_CHECK``, quit the test and report AN failure with the AN status.

LT Phase:

3. Request the remote transmitter to use ``preset`` on each specified Serdes.
4. Request the remote transmitter to **increase each coefficient by 1** in a **round robin fashion on each specified Serdes**.
5. If any coefficient's response is ``COEFF_AT_LIMIT`` or ``COEFF_EQ_AT_LIMIT`` or ``EQ_AT_LIMIT``, the coefficient should not be incremented any further.
6. Report the last response of each coefficient on each specified Serdes.

.. note::
    
    This test may cause the local port to lose frame lock to the remote port.

Statistics
-------------

* Timestamp
* Repetition #
* AN status
* For each Serdes
    * Starting preset
    * For each coefficient
        * Last response


