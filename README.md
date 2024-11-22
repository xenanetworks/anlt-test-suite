# Automated ANLT Test Suite

## Introduction

### Auto-Negotiation in Link Training Test
In accordance with the IEEE standard, in the event of a failure during the ANLT procedure, the port should initiate the procedure anew.

Freya, functioning as a test port, possesses the capability to perform AN and LT as distinct and autonomous processes. Nevertheless, remote ports under test from different vendors may lack this capability. Consequently, when conducting LT tests, the testing port must activate or deactivate AN based on the settings configured on the remote port.

### PRBS BER Measurement
The LT phase involves the measurement of LT BER using the PRBS-13 pattern. The LT algorithm relies on these LT BER values as its criteria.

It’s essential to clarify that LT’s primary goal is to enhance the PRBS BER during the DATA phase. However, it’s important to note that the pattern employed during the DATA phase may not necessarily be PRBS-13.

Therefore, any LT algorithm should strive to IMPROVE the PRBS BER rather than degrade it. Any LT algorithm that has a detrimental impact on the PRBS BER must be categorized as a “poor” algorithm.

# Automated Link Training Tests

Instead of manually do the link training test. We also want a way to automate it, running through all the possible status returns, and all the possible presets and coefficients. We want to see where are the limits on each of those. Can we communicate effectively and not lose frame lock on a link? 

* **Preset Tests**
  * **Frame Lock Test & Consistent Frame Lock Tests**
    To measure the frame lock status of the remote transmitter using the specified preset.
  * **Link Performance Test**
    To measure the link training BER performances of the remote transmitter using the specified preset.
* **Coefficient Boundary Tests**
  * **Maximum Limit Tests**
    To make the test port to respond ``COEFF_AT_LIMIT`` when incrementing a coefficient on the remote transmitter.
  * **Minimum Limit Tests**
    To make the test port to respond ``COEFF_AT_LIMIT`` when decrementing a coefficient on the remote transmitter.
  * **Coefficient and Equalization Limit Test**
    To make the test port to respond ``COEFF_EQ_AT_LIMIT`` or ``COEFF_AT_LIMIT`` or ``EQ_AT_LIMIT`` when keep incrementing a coefficient on the remote transmitter.