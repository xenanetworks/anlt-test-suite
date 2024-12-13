
Frame Lock Test
=================

Filename
---------

``xena_lt_preset_frame_lock.py``

Objective
----------

To measure the frame lock status of the remote transmitter using the specified preset.

Configurations
--------------

* Number of ``<repetitions>``, default to 1
* AN/LT Configuration
    * AN enabled/disabled.
    * ``<preset>`` the remote transmitter should use.
    * ``<serdes>`` the serdes lane(s) to test
* Port configuration
    * Interface type, e.g. QSFPDD 100G CR
    * Serdes speed
    * Number of Serdes (read-only)

Procedure
-----------

1. If AN is enabled, test port starts AN + interactive LT. Else, start interactive LT on the port.

2. AN Phase

    * 2.1. If AN result is ``AN_GOOD_CHECK``, continue to LT Phase.
    * 2.2. If AN result is not ``AN_GOOD_CHECK``, quit the test and report AN failure with the AN status.

3. LT Phase:

    * 3.1. Request the remote transmitter to use ``PAM4`` or ``PAM with Precoding`` modulation.
    * 3.2. Request the remote transmitter to use a ``<preset>`` on each specified Serdes.
    * 3.3. Read frame lock status of each specified Serdes.
    * 3.4. Announce trained on ``<serdes>`` to close LT.

4. Stop AN and LT on the test port.
5. Repeat 1-4 until all ``<repetitions>`` are done.

Statistics
-----------
* Timestamp
* Repetition #
* AN status
* For each Serdes
    * Preset
    * Local frame lock status 
    * Remote frame lock status
