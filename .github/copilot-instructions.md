# GitHub Copilot Instructions for `fre-postprocess-workflow`

## Project Context
- This repository holds GFDL's next-generation FRE (FMS Runtime Environment) workflow configuration templates.
- The primary workflow engine used is **Cylc**, alongside **Rose** and **Jinja2**.
- Execution environments include bare-metal HPC systems (like PPAN and Gaea) via Slurm, as well as portable containerized setups (Podman/Apptainer) running locally or in the cloud.

## Workflow Configuration Rules
- **Configuration Hierarchy:** Understand that Cylc configurations are hierarchical. `global.cylc` is loaded first, followed by the central `flow.cylc`, and finally site-specific configurations from the `site/` directory (e.g., `site/ppan.cylc`). 
- **Platform-Specific vs. Independent:** 
  - Place platform-independent changes in `flow.cylc`. 
  - Place platform-specific changes (e.g., Slurm directives, HPC module loads) in the appropriate `site/*.cylc` files.
- **Precedence:** Keep in mind that configurations defined closer to the bottom of the workflow template take precedence.
- **NEVER Edit Runtime Directories:** Never suggest changes or edits to code located in `~/cylc-run` or `~/cylc-src`. All development must happen within a local clone of the repository.

## Repository Structure & Code Guidelines
- **`flow.cylc` & `site/`**: Use these for Cylc workflow definitions, scheduling, and task dependencies.
- **`bin/`**: When generating shell scripts for the `bin/` directory, ensure they properly wrap `fre-cli` calls to keep `flow.cylc` readable. Use strict error handling (`set -euo pipefail`).
- **`Jinja2Filters/`**: Use Python modules here to preprocess `flow.cylc` Jinja templates.
- **`lib/python/`**: This directory handles custom job runner handlers (e.g., `PPANHandler`) and EPMT (Exascale Performance Management Tool) integration. Ensure Python code here relies on standard libraries where possible, uses type hints, and handles Slurm job script parsing carefully (e.g., injecting `papiex` tags).
- **Environment Management:** Tasks submitted by Cylc run in bare environments. When generating task scripts, ensure required tools are explicitly loaded via LMOD (`module load ...`) or a Conda environment activation within the task's `init-script` or `pre-script`.

## Containerization & Portability
- When dealing with the portable post-processing workflow (`site/ppp-container.cylc`), ensure jobs are configured to run with `platform=localhost` (in the background) rather than relying on Slurm.
- Assume the presence of a Conda environment built via a Dockerfile for containerized tasks.

## General Coding Standards
- **Clarity over Cleverness:** Add inline comments explaining *why* complex logic or specific system workarounds are necessary, especially when dealing with Cylc task definitions or Slurm handlers.
- **Security:** Never generate code that embeds secrets, tokens, or personal paths (avoid hardcoding `/home/username/`).
