# CDCT Experiment Summary

Total Experiments: 56

## Summary by Model

| Model | N | Mean CSI | Std CSI | Mean Score | Domains |
|-------|---|----------|---------|------------|----------|
| DeepSeek-V3-0324 | 8 | 0.1395 | 0.1345 | 0.828 | 8 |
| Phi-4-mini-instruct | 8 | 0.1616 | 0.0542 | 0.815 | 8 |
| gpt-4.1 | 8 | 0.1671 | 0.1259 | 0.822 | 8 |
| gpt-5-mini | 8 | 0.0949 | 0.1028 | 0.810 | 8 |
| gpt-oss-120b | 8 | 0.1774 | 0.1080 | 0.784 | 8 |
| grok-4-fast-reasoning | 8 | 0.1048 | 0.0952 | 0.867 | 8 |
| mistral-medium-2505 | 8 | 0.1610 | 0.1971 | 0.818 | 8 |

## Summary by Domain

| Domain | N | Mean CSI | Std CSI | Models |
|--------|---|----------|---------|--------|
| art | 7 | 0.2202 | 0.1238 | 7 |
| biology | 7 | 0.1185 | 0.0818 | 7 |
| computer_science | 7 | 0.2640 | 0.2100 | 7 |
| ethics | 7 | 0.1588 | 0.0802 | 7 |
| linguistics | 7 | 0.1016 | 0.0767 | 7 |
| logic | 7 | 0.0852 | 0.0597 | 7 |
| mathematics | 7 | 0.1105 | 0.1073 | 7 |
| physics | 7 | 0.0912 | 0.0658 | 7 |

## Detailed Results

| Model | Concept | Domain | CSI | C_h | Mean Score | Direction |
|-------|---------|--------|-----|-----|------------|------------|
| DeepSeek-V3-0324 | impressionism | art | 0.4127 | 0.020689655172413793 | 0.680 | improvement |
| DeepSeek-V3-0324 | natural_selection | biology | 0.1296 | 0.01694915254237288 | 0.893 | decay |
| DeepSeek-V3-0324 | recursion | computer_science | 0.2504 | 0.05454545454545454 | 0.727 | decay |
| DeepSeek-V3-0324 | harm_principle | ethics | 0.1493 | 0.10948905109489052 | 0.760 | decay |
| DeepSeek-V3-0324 | phoneme | linguistics | 0.0492 | 0.013986013986013986 | 0.747 | decay |
| DeepSeek-V3-0324 | modus_ponens | logic | 0.0682 | 0.014388489208633094 | 0.910 | decay |
| DeepSeek-V3-0324 | derivative | mathematics | 0.0000 | 0.047619047619047616 | 1.000 | decay |
| DeepSeek-V3-0324 | f_equals_ma | physics | 0.0568 | 0.02 | 0.910 | decay |
| Phi-4-mini-instruct | impressionism | art | 0.2303 | 0.020689655172413793 | 0.753 | improvement |
| Phi-4-mini-instruct | natural_selection | biology | 0.1296 | 0.01694915254237288 | 0.893 | decay |
| Phi-4-mini-instruct | recursion | computer_science | 0.0735 | 0.05454545454545454 | 0.693 | decay |
| Phi-4-mini-instruct | harm_principle | ethics | 0.2233 | 0.021897810218978103 | 0.787 | improvement |
| Phi-4-mini-instruct | phoneme | linguistics | 0.1538 | 0.013986013986013986 | 0.663 | improvement |
| Phi-4-mini-instruct | modus_ponens | logic | 0.1929 | 0.014388489208633094 | 0.850 | decay |
| Phi-4-mini-instruct | derivative | mathematics | 0.1731 | 0.047619047619047616 | 0.967 | improvement |
| Phi-4-mini-instruct | f_equals_ma | physics | 0.1160 | 0.02 | 0.917 | improvement |
| gpt-4.1 | impressionism | art | 0.0562 | 0.020689655172413793 | 0.787 | decay |
| gpt-4.1 | natural_selection | biology | 0.1727 | 0.01694915254237288 | 0.927 | improvement |
| gpt-4.1 | recursion | computer_science | 0.4365 | 0.12727272727272726 | 0.587 | decay |
| gpt-4.1 | harm_principle | ethics | 0.2233 | 0.021897810218978103 | 0.787 | improvement |
| gpt-4.1 | phoneme | linguistics | 0.1538 | 0.013986013986013986 | 0.663 | improvement |
| gpt-4.1 | modus_ponens | logic | 0.0643 | 0.014388489208633094 | 0.950 | decay |
| gpt-4.1 | derivative | mathematics | 0.1731 | 0.047619047619047616 | 0.967 | improvement |
| gpt-4.1 | f_equals_ma | physics | 0.0568 | 0.02 | 0.910 | decay |
| gpt-5-mini | impressionism | art | 0.1234 | 0.020689655172413793 | 0.837 | improvement |
| gpt-5-mini | natural_selection | biology | 0.0400 | 0.01694915254237288 | 0.780 | decay |
| gpt-5-mini | recursion | computer_science | 0.0000 | 0.01818181818181818 | 0.920 | decay |
| gpt-5-mini | harm_principle | ethics | 0.2651 | 0.021897810218978103 | 0.653 | improvement |
| gpt-5-mini | phoneme | linguistics | 0.0583 | 0.013986013986013986 | 0.667 | decay |
| gpt-5-mini | modus_ponens | logic | 0.0405 | 0.014388489208633094 | 0.787 | decay |
| gpt-5-mini | derivative | mathematics | 0.0000 | 0.047619047619047616 | 1.000 | decay |
| gpt-5-mini | f_equals_ma | physics | 0.2321 | 0.02 | 0.833 | improvement |
| gpt-oss-120b | impressionism | art | 0.2893 | 0.020689655172413793 | 0.843 | improvement |
| gpt-oss-120b | natural_selection | biology | 0.2623 | 0.01694915254237288 | 0.747 | decay |
| gpt-oss-120b | recursion | computer_science | 0.2883 | 0.01818181818181818 | 0.803 | improvement |
| gpt-oss-120b | harm_principle | ethics | 0.1141 | 0.10948905109489052 | 0.523 | improvement |
| gpt-oss-120b | phoneme | linguistics | 0.2272 | 0.013986013986013986 | 0.673 | improvement |
| gpt-oss-120b | modus_ponens | logic | 0.0092 | 0.014388489208633094 | 0.850 | decay |
| gpt-oss-120b | derivative | mathematics | 0.1731 | 0.047619047619047616 | 0.967 | improvement |
| gpt-oss-120b | f_equals_ma | physics | 0.0556 | 0.02 | 0.867 | decay |
| grok-4-fast-reasoning | impressionism | art | 0.2976 | 0.020689655172413793 | 0.803 | improvement |
| grok-4-fast-reasoning | natural_selection | biology | 0.0491 | 0.01694915254237288 | 0.900 | decay |
| grok-4-fast-reasoning | recursion | computer_science | 0.1861 | 0.01818181818181818 | 0.860 | decay |
| grok-4-fast-reasoning | harm_principle | ethics | 0.0832 | 0.021897810218978103 | 0.760 | decay |
| grok-4-fast-reasoning | phoneme | linguistics | 0.0492 | 0.013986013986013986 | 0.747 | decay |
| grok-4-fast-reasoning | modus_ponens | logic | 0.1126 | 0.014388489208633094 | 0.917 | improvement |
| grok-4-fast-reasoning | derivative | mathematics | 0.0000 | 0.047619047619047616 | 1.000 | decay |
| grok-4-fast-reasoning | f_equals_ma | physics | 0.0604 | 0.02 | 0.950 | decay |
| mistral-medium-2505 | impressionism | art | 0.1317 | 0.020689655172413793 | 0.797 | improvement |
| mistral-medium-2505 | natural_selection | biology | 0.0460 | 0.01694915254237288 | 0.860 | decay |
| mistral-medium-2505 | recursion | computer_science | 0.6134 | 0.12727272727272726 | 0.660 | decay |
| mistral-medium-2505 | harm_principle | ethics | 0.0533 | 0.021897810218978103 | 0.860 | decay |
| mistral-medium-2505 | phoneme | linguistics | 0.0197 | 0.013986013986013986 | 0.697 | decay |
| mistral-medium-2505 | modus_ponens | logic | 0.1087 | 0.014388489208633094 | 0.877 | improvement |
| mistral-medium-2505 | derivative | mathematics | 0.2544 | 0.047619047619047616 | 0.847 | improvement |
| mistral-medium-2505 | f_equals_ma | physics | 0.0604 | 0.02 | 0.950 | decay |
