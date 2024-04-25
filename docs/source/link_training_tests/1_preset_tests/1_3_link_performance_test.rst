
Link Performance Test
======================

Objective
-----------

To measure the link training BER performances of the remote transmitter using the specified preset.

Configurations
-----------------

* Number of ``repetitions``, default to 1
* ANLT Configuration
    * AN enabled/disabled.
    * ``presets`` the remote transmitter should use.
    * ``Serdes to test``
* Port configuration
    * Interface type, e.g. QSFPDD 100G CR
    * Serdes speed
    * Number of Serdes (read-only)

Procedure
-----------
If AN is enabled, test port starts AN + interactive LT.

AN Phase:

1. If AN result is ``AN_GOOD_CHECK``, continue to LT Phase.
2. If AN result is not ``AN_GOOD_CHECK``, quit the test and report AN failure with the AN status.

LT Phase:

3. Request the remote transmitter to use a ``preset`` on each specified Serdes.
4. Read frame lock status of each specified Serdes.
5. Read ``LT BER`` each specified Serdes.
6. Announce trained on all Serdes to close LT.

Statistics
---------------

* Timestamp
* Repetition #
* AN status
* For each Serdes
    * Preset
    * LT PRBS total bits 
    * LT PRBS errored bits 
    * LT PRBS BER
