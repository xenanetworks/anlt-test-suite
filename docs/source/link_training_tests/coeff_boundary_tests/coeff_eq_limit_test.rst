
Coefficient and Equalization Limit Test
========================================

Objective
----------

To make the test port to respond ``COEFF AND EQ AT LIMIT`` or ``COEFF AT LIMIT`` or ``EQ AT LIMIT``.

Configurations
---------------

* Number of ``repetitions``, default to 1
* ANLT Configuration
    * AN enabled/disabled.
    * ``preset`` the remote transmitter should start.
    * ``coefficients`` of the remote transmitter.
    * LT control action: **decrease**
    * ``Serdes to test``
* Port configuration
    * Interface type, e.g. QSFPDD 100G CR
    * Serdes speed
    * Number of Serdes (read-only)

Procedure
-----------

AN Phase:

1.	If AN result is ``AN_GOOD_CHECK``, continue to LT Phase.
2.	If AN result is not ``AN_GOOD_CHECK``, quit the test and report AN failure with the AN status.

LT Phase:

3.	Request the remote transmitter to use preset on each ``specified`` Serdes.
4.	Request the remote transmitter to **increase coefficient** on each specified Serdes.
5.	Repeat this step until the response is ``COEFF EQ AT LIMIT`` or ``COEFF AT LIMIT`` or ``EQ AT LIMIT`` or ``COEFF NOT SUPPORTED``.
6.	Report the response on each specified Serdes.
7.	Repeat 3-6 until all coefficients are tested.

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

