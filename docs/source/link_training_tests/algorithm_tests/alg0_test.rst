
Algorithm-0 Test
================

Algorithm-0 is a heuristic that aims to provide a simple yet effective coefficient combination searching algorithm.

Objective
----------

To determine the BER performance of the algorithm.

Configurations
----------------

* Number of ``repetitions``, default to 1
* ANLT Configuration
    * AN enabled/disabled.
* PRBS BER configuration
    * ``PRBS polynomial`` for PRBS BER measurement
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

Test port runs the same or different searching algorithms on all Serdes simultaneously. Each Serdes follows the sequence below.

LT Phase 1:

To examine all Presets and find the one returns the best BER.

3.	Request the remote to use **preset 1**.
4.	Check frame lock status. If frame lock is not detected, go to Step 7.
5.	Wait a waiting time, to gather enough data for an accurate BER calculation. (If the remote end times out, quit the test.)
6.	Read BER of the Serdes.

Repeat Step 3-6 with ``preset 2``, ``preset 3``, ``preset 4`` and ``preset 5``.
Pick up the Preset value that returns the best BER.

LT Phase 2:

To tune the coefficients of the Preset to achieve the best BER within the allowed time. LT BER threshold is fixed to 10^-8.

7.	Request the remote to increase c(-1) by 1 and check the returned LT BER.
8.	If LT BER improves, repeat Step 6. Else, set it back to the previous Preset value.
9.	Request the remote to decrease c(-1) by 1 and check the returned LT BER.
10.	If LT BER improves, repeat Step 8. Else, set it back to the previous Preset value.
11.	Measure LT BER of the Serdes

Repeat Step 7-11, replacing c(-1) with c(-2).

Repeat Step 7-11, replacing c(-1) with c(1).

Repeat 1-11 until all repetitions are done.

3.4.1.1.4	Statistics
* Report the each “searching” step and the LT BER values
* Report the PRBS BER value

