# Quantum Amplitude Estimation without Phase Estimation

This was my group's final project for BWSI 2021, where we implemented QAE as outlined in [this](https://arxiv.org/abs/2008.02102) paper using the methods from [Suzuki et al](https://link.springer.com/article/10.1007%2Fs11128-019-2565-2).

This algorithm can be run either with Mircosoft's [QDK](https://docs.microsoft.com/en-us/azure/quantum/user-guide/) or IBM's [Qiskit](https://qiskit.org/).

Please note that when using Qiskit, you must first add your API token, like so:
```python
>>> import IBMQ
>>> IBMQ.save_account("YOUR_TOKEN")
```