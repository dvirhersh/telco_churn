# Prompts for your coding agent (S4)

Copy, paste, adapt. Read what the agent does before you accept it.

## Step 0 — Set up

> I'm in the telco_churn repo on branch s4. Create a Python 3.12 virtual
> environment in .venv, install requirements.txt, and copy .env.example to .env.
> Do not write my password anywhere; I will fill .env myself.

> Run `python earth/check_connection.py` and explain the output.

## Step 1 — Run the search as is

> Run `python earth/run_search.py --name run1` and tell me what each stage of the
> output means while it runs.

> Open work/runs/run1/earth_ids.json and champion_chromosome.json. Was
> test_ids.csv uploaded? Which model won, which features did it keep, and how
> stable are the per-fold hit rates?

## Step 2 — Read the search space and fitness

> Explain earth/chromosome.yaml gene by gene. For each gene, say which model
> family uses it and what range of real values it maps to.

> Walk me through FitnessClass in earth/fitness.py for one chromosome, from
> loading the CSV to the hit@400 score. Why are the folds fixed once?

> Using earth/WALKTHROUGH.md, quiz me on the search space one question at a time.
> Don't give the answer until I try.

## Step 3 — One change in the chromosome

> I want to change one thing in the search space: <your idea>. Copy
> earth/chromosome.yaml to work/runs/run2/chromosome.yaml, make only that change,
> and show me the diff. Then run `python earth/check_local.py --chromosome
> work/runs/run2/chromosome.yaml`.

> Run `python earth/run_search.py --name run2 --chromosome
> work/runs/run2/chromosome.yaml`, then `python earth/compare_runs.py run1 run2`,
> and help me decide whether the change helped or was just noise.

## Step 4 — One change in the fitness (if time)

> Copy earth/fitness.py to work/runs/run3/fitness.py and change only <your idea>.
> Show me the diff and explain how it changes what the score means. Then run
> `python earth/check_local.py --fitness work/runs/run3/fitness.py`.
