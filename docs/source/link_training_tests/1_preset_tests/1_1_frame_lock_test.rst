
Frame Lock Test
=================

Objective
----------

To measure the frame lock status of the remote transmitter using the specified preset.

Configurations
--------------

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

3.	Request the remote transmitter to use a ``preset`` on each specified Serdes.
4.	Read frame lock status of each specified Serdes.
5.	Repeat 3-4 until all specified presets are tested.
6.	Announce trained on all Serdes to close LT.

Repeat until all ``repetitions`` are done.

Statistics
-----------
* Timestamp
* Repetition #
* AN status
* For each Serdes
    * Preset
    * Local frame lock status 
    * Remote frame lock status
