
Algorithm Tests (WIP)
=====================

The major part of link training is that the link partners exchange Training Sequences (TS) to tune the channels for optimal signal transmission. Training became necessary with 25GbE NRZ signaling and has only increased in complexity and necessity with high-speed PAM4 signals.

For different signal transmission channels, e.g. cables by different vendors, or temperature, the coefficient combination that gives the most optimal signal quality varies. To efficiently search for the ideal coefficient combination, a transmitter requires an algorithm. Different from throughput binary searching algorithm, where only one variable (traffic rate) impacts the result, there are at least three coefficients to tune (for PAM4, five coefficients), resulting in a multi-dimensional searching algorithm. Apparently, the complexity of the algorithm increases with the increase of the number of coefficients. Unfortunately, there hasn't been a standardized algorithm for finding the coefficient combination for a specified signal transmission channel.

Because link training process requires stricter timing between the protocol message exchanges, the searching algorithm must be implemented and executed at Layer-1 (hardware level). Otherwise, a sporadic delay on the software level will result in a reset in the link training process, causing the test to fail to complete.


.. toctree::
    :glob:
    :maxdepth: 1
    
    *

