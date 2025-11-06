# CDCT Framework

This framework is designed to generate data for the Compression-Decay Comprehension Test (CDCT), as described in the paper "The Compression-Decay Comprehension Test (CDCT): An Information-Theoretic Benchmark for Measuring Machine Comprehension."

## Project Structure

- `concepts/`: Contains JSON definitions for each concept, including their compression levels.
- `results/`: Stores the raw and analyzed results from the experiments.
- `src/`: The source code for the framework, including modules for:
  - `agent.py`: Interacting with different language models.
  - `concept.py`: Loading and managing concept definitions.
  - `evaluation.py`: Evaluating model responses.
  - `experiment.py`: Running the CDCT experiments.
  - `analysis.py`: Analyzing the results and calculating metrics.
- `main.py`: The main script to run the entire data generation and analysis pipeline.
- `config.py`: Configuration file for API keys and other settings.
