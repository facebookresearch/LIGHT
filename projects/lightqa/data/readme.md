## Generate the data
1.  Use `generate_data.py` to generate the detailed dialogue data required to later build the individual  datasets. To speed up the construction of this dataset use SLURM. Using the provided `generate_data.sh` script, it can be scheduled using `sbatch generate_data.sh`.
2. Use `merge_data.py` to merge the individual data files produced by the actors.
3. Use `generate_parlai_dataset.py` to generate the final parlai compatible datasets.