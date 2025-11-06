# CDCT Analysis Script: Findings & Corrections

This document outlines the process of identifying and correcting a discrepancy between the CDCT implementation in `src/analysis.py` and the formal definitions in the accompanying research paper.

## 1. Initial Problem: Contradictory `C_h` Definition

We initially discovered that the script's calculation of the **Comprehension Horizon (`C_h`)** was contradictory to the paper's definition.

-   **Paper's Definition**: `C_h` is the *minimum continuous compression value* `c` (from 0.0 to 1.0) where the model's performance **passes** a set threshold (e.g., score >= 0.7). According to this definition, a **lower `C_h` is better**, indicating comprehension resilience at high levels of compression.

-   **Initial Code Logic**: The script calculated `C_h` as the first *discrete compression level* `L` (from 0 to 4) where the model's performance **failed** (score < 0.7). This logic meant a **higher `C_h` was better**.

This fundamental contradiction was the source of our initial confusion.

## 2. The Deeper Issue: Discrete vs. Continuous Scaling

Our first attempt to fix this was to simply invert the logic to find the first level that *passed*. However, we quickly realized a deeper issue: the script was treating the compression scale as a set of discrete, linear integer levels (0, 1, 2, 3, 4), whereas the paper defines it as a continuous value `c` representing the "fraction of information retained."

A simple linear mapping (`c = L/4`) was an oversimplification, as the information difference between Level 0 and 1 is not necessarily the same as between Level 3 and 4.

## 3. The Solution: Non-Linear, Information-Based Scaling

To create a more accurate mapping that honors the paper's definition, we implemented a non-linear scaling solution.

1.  **Information Proxy**: We used the `context_length` (word count) of the text at each compression level as a proxy for its "information content."

2.  **Calculating `c`**: The continuous value `c` for each level `L` was calculated as a fraction of the maximum information content:
    ```
    c(L) = word_count(L) / word_count(L_max)
    ```

3.  **Implementation**: The `src/analysis.py` script was updated to perform this calculation. It now generates a non-linear, continuous `c_value` for each compression level before calculating the final metrics.

## 4. Final Outcome

By implementing this more rigorous scaling, the script now calculates both `C_h` and `CSI` using a continuous scale that is faithful to the paper's information-theoretic framework.

The final, corrected metrics for the `art_impressionism` concept were:

-   **`C_h` ≈ 0.021**
-   **`CSI` ≈ 0.042**

These results are now directly comparable to the paper's classification thresholds (e.g., `CSI < 0.4` and `C_h < 0.4` for "Strong Comprehension") and confirm that the model demonstrates a strong comprehension profile. This fix ensures all future analyses will be consistent with the formal theory.
