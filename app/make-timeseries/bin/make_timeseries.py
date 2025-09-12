#!/usr/bin/env python3
"""
Create per-variable timeseries from shards

This script converts the original shell-based make-timeseries workflow to Python,
reducing Rose dependencies while maintaining the same functionality.
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from typing import Tuple


def parse_date(date_str: str) -> str:
    """Parse a date string and convert to ISO8601 format.

    Accepts date in YYYYMMDDHHmm or less precision.
    Outputs date in standard ISO8601 (YYYYMMDDTHHmm) format.
    """
    date_len = len(date_str)

    if date_len == 4:
        input_date = date_str
    elif date_len == 6:
        input_date = date_str + "01"
    elif date_len == 8:
        input_date = date_str
    elif date_len == 10:
        input_date = re.sub(r'(..)$', r'T\1', date_str)
    elif date_len == 12:
        input_date = re.sub(r'(....)$', r'T\1', date_str)
    else:
        raise ValueError(f"ERROR: unexpected date input '{date_str}'")

    # Use cylc cycle-point for date formatting
    try:
        result = subprocess.run(
            ["cylc", "cycle-point", "--template", "CCYYMMDDThhmm", input_date],
            check=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to parse date {date_str}: {e}") from e


def calculate_expected_chunks(input_chunk: str, output_chunk: str,
                            begin: str, pp_stop: str) -> Tuple[int, str]:
    """Calculate expected number of chunks and end date."""
    # Handle P12M -> P1Y conversion
    if input_chunk == "P12M":
        input_chunk = "P1Y"

    try:
        # Get chunk durations in hours
        input_hours_result = subprocess.run(
            ["isodatetime", "--as-total=H", input_chunk],
            check=True, capture_output=True, text=True
        )
        input_chunk_hrs = int(float(input_hours_result.stdout.strip().rstrip('.0')))

        output_hours_result = subprocess.run(
            ["isodatetime", "--as-total=H", output_chunk],
            check=True, capture_output=True, text=True
        )
        output_chunk_hrs = int(float(output_hours_result.stdout.strip().rstrip('.0')))

        expected_chunks = output_chunk_hrs // input_chunk_hrs

        # Calculate available chunks
        avail_hours_result = subprocess.run(
            ["isodatetime", "--as-total=H", begin, pp_stop, f"--offset2={input_chunk}"],
            check=True, capture_output=True, text=True
        )
        avail_chunk_hrs = int(float(avail_hours_result.stdout.strip().rstrip('.0')))
        avail_chunks = avail_chunk_hrs // input_chunk_hrs

        if avail_chunks >= expected_chunks:
            end_result = subprocess.run(
                ["isodatetime", begin, "--offset", output_chunk],
                check=True, capture_output=True, text=True
            )
            end = end_result.stdout.strip()
        else:
            expected_chunks = avail_chunks
            end_result = subprocess.run(
                ["isodatetime", pp_stop, "--offset", input_chunk],
                check=True, capture_output=True, text=True
            )
            end = end_result.stdout.strip()

        return expected_chunks, end

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to calculate chunks: {e}") from e


def hash_file_for_lineage(file_path: str) -> str:
    """Generate hash for data lineage tracking."""
    try:
        result = subprocess.run([
            "/home/Cole.Harvey/.conda/envs/bloom-filter-env/bin/python",
            "-m", "data_lineage.bloomfilter.HashGen", file_path
        ], check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        # Return empty string if lineage tool fails
        return ""


def process_variable_files(args, var: str, files: list, freq: str, chunk: str,
                          data_lineage_in_dir: str, data_lineage_out_dir: str,
                          newdir: Path, is_tiled: bool) -> bool:
    """Process files for a single variable."""
    if not files:
        return False

    # Sort files by date
    files.sort()

    # Form new filename
    d1 = files[0].split(".")[1].split("-")[0]
    d2 = files[-1].split(".")[1].split("-")[1]

    # Create output directory
    newdir.mkdir(parents=True, exist_ok=True)

    # Process tiled files
    if is_tiled:
        for tile in range(1, 7):  # tiles 1-6
            newfile = f"{args.component}.{d1}-{d2}.{var}.tile{tile}.nc"
            tiled_files = [f.replace("tile1", f"tile{tile}") for f in files]

            # Data lineage for input files
            if os.environ.get("EPMT_DATA_LINEAGE") == "1":
                for input_file in tiled_files:
                    input_path = Path(args.inputDir) / data_lineage_in_dir / input_file
                    hash_val = hash_file_for_lineage(str(input_path))
                    if hash_val:
                        current_list = os.environ.get("input_file_list", "")
                        env_var = f"{current_list}{data_lineage_in_dir}/{input_file} {hash_val},"
                        os.environ["input_file_list"] = env_var
                        print(f"[DATA LINEAGE] Added {data_lineage_in_dir}/{input_file}"
                              f" to input list with hash_val: {hash_val}")

            # Run CDO mergetime
            try:
                subprocess.run([
                    "cdo", "--history", "-O", "mergetime"
                ] + tiled_files + [str(newdir / newfile)], check=True)

                # Run fre pp ppval
                subprocess.run([
                    "fre", "-v", "pp", "ppval", "--path", str(newdir / newfile)
                ], check=True)

            except subprocess.CalledProcessError as e:
                print(f"ERROR: Failed to process {newfile}: {e}")
                continue

    else:
        # Non-tiled processing
        if os.environ.get("EPMT_DATA_LINEAGE") == "1":
            for input_file in files:
                input_path = Path(args.inputDir) / data_lineage_in_dir / input_file
                hash_val = hash_file_for_lineage(str(input_path))
                if hash_val:
                    current_list = os.environ.get("input_file_list", "")
                    env_var = f"{current_list}{data_lineage_in_dir}/{input_file} {hash_val},"
                    os.environ["input_file_list"] = env_var
                    print(f"[DATA LINEAGE] Added {data_lineage_in_dir}/{input_file}"
                          f" to input list with hash_val: {hash_val}")

        newfile = f"{args.component}.{d1}-{d2}.{var}.nc"

        try:
            subprocess.run([
                "cdo", "--history", "-O", "mergetime"
            ] + files + [str(newdir / newfile)], check=True)

            subprocess.run([
                "fre", "-v", "pp", "ppval", "--path", str(newdir / newfile)
            ], check=True)

        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to process {newfile}: {e}")
            return False

    # Data lineage for output file
    if os.environ.get("EPMT_DATA_LINEAGE") == "1":
        output_path = newdir / newfile
        hash_val = hash_file_for_lineage(str(output_path))
        if hash_val:
            current_list = os.environ.get("output_file_list", "")
            env_var = f"{current_list}{data_lineage_out_dir}/{newfile} {hash_val},"
            os.environ["output_file_list"] = env_var
            print(f"[DATA LINEAGE] Added {data_lineage_out_dir}/{newfile}"
                  f" to output list with hash_val: {hash_val}")

    return True


def process_timeseries(args, expected_chunks: int, begin: str, end: str) -> bool:
    """Process timeseries for given source directory location."""
    did_something = False

    # Find leaf directories containing datetime info (equivalent to find . -mindepth 2 -type d)
    dirs = []
    for root, _, _ in os.walk("."):
        # Convert to relative path and count parts
        rel_path = os.path.relpath(root, ".")
        if rel_path == ".":
            continue  # Skip current directory
        path_parts = rel_path.split(os.sep)
        if len(path_parts) >= 2:  # mindepth 2 equivalent
            dirs.append(rel_path)

    if not dirs:
        print("ERROR: No input directories found!")
        return False

    for directory in dirs:
        path_parts = directory.split(os.sep)
        if len(path_parts) < 2:
            continue

        freq = path_parts[0]
        chunk = path_parts[1]

        # Skip if chunk doesn't match input chunk
        input_chunk = args.inputChunk
        if input_chunk == "P12M":
            input_chunk = "P1Y"

        if chunk != input_chunk:
            continue

        original_dir = os.getcwd()
        os.chdir(directory)

        try:
            # Get unique variables in this directory
            variables = set()
            nc_files = [f for f in os.listdir(".") if f.endswith(".nc")]

            for filename in nc_files:
                parts = filename.split(".")
                if len(parts) >= 3:
                    variables.add(parts[2])  # Variable is 3rd part

            for var in sorted(variables):
                print(f"Evaluating variable {var}")

                # Check if tiled or non-tiled
                tile1_files = [f for f in nc_files
                              if f"{args.component}" in f and f".{var}.tile1.nc" in f]
                is_tiled = len(tile1_files) > 0

                # Find files for this variable
                files = []

                for filename in nc_files:
                    if ((not is_tiled and filename.endswith(f".{var}.nc")) or
                            (is_tiled and filename.endswith(f".{var}.tile1.nc"))):
                        # Extract date from filename
                        parts = filename.split(".")
                        if len(parts) >= 2:
                            date_part = parts[1].split("-")[0]
                            try:
                                date1 = parse_date(date_part)
                                if begin <= date1 < end:
                                    files.append(filename)
                            except (ValueError, RuntimeError) as e:
                                print(f"WARNING: Failed to parse date from {filename}: {e}")
                                continue

                if len(files) != expected_chunks:
                    print(f"WARNING: Skipping {var} as unexpected number of chunks;"
                          f" expected '{expected_chunks}', got '{len(files)}'")
                    continue

                # Set up directory paths
                if args.use_subdirs:
                    subdir = Path(original_dir).name  # Get parent directory name
                    data_lineage_in_dir = f"{subdir}/{args.component}/{freq}/{chunk}"
                    data_lineage_out_dir = f"{subdir}/{args.component}/{freq}/{args.outputChunk}"
                    newdir = (Path(args.outputDir) / subdir / args.component /
                             freq / args.outputChunk)
                else:
                    data_lineage_in_dir = f"{args.component}/{freq}/{chunk}"
                    data_lineage_out_dir = f"{args.component}/{freq}/{args.outputChunk}"
                    newdir = Path(args.outputDir) / args.component / freq / args.outputChunk

                # Process the variable files
                result = process_variable_files(
                    args, var, files, freq, chunk, data_lineage_in_dir,
                    data_lineage_out_dir, newdir, is_tiled
                )
                if result:
                    did_something = True

        finally:
            os.chdir(original_dir)

    return did_something


def setup_data_lineage():
    """Set up data lineage environment variables."""
    if os.environ.get("EPMT_DATA_LINEAGE") == "1":
        cylc_suite_path = os.environ.get("CYLC_SUITE_DEF_PATH", "")
        current_pythonpath = os.environ.get("PYTHONPATH", "")
        if cylc_suite_path:
            os.environ["PYTHONPATH"] = f"{cylc_suite_path}:{current_pythonpath}"
        os.environ["input_file_list"] = ""
        os.environ["output_file_list"] = ""
        print("Set PYTHONPATH and created i/o lists")


def finalize_data_lineage(args):
    """Finalize data lineage annotations."""
    if os.environ.get("EPMT_DATA_LINEAGE") != "1":
        return

    try:
        # Annotate paths
        subprocess.run(["epmt", "annotate",
                       f"EPMT_DATA_LINEAGE_IN_PATH={args.inputDir}/"], check=True)
        print(f"\n[COLE] annotated {args.inputDir} to EPMT_DATA_LINEAGE_IN_PATH")

        subprocess.run(["epmt", "annotate",
                       f"EPMT_DATA_LINEAGE_OUT_PATH={args.outputDir}/"], check=True)
        print(f"\n[COLE] annotated {args.outputDir} to EPMT_DATA_LINEAGE_OUT_PATH")

        # Annotate file lists
        input_file_list = os.environ.get("input_file_list", "")
        if input_file_list:
            result = subprocess.run([
                "/home/Cole.Harvey/.conda/envs/bloom-filter-env/bin/python",
                "-m", "data_lineage.bloomfilter.StringCompression", input_file_list
            ], check=True, capture_output=True, text=True)
            compressed_bytes = result.stdout.strip().rstrip(",")
            subprocess.run(["epmt", "-v", "annotate",
                           f"EPMT_DATA_LINEAGE_IN={compressed_bytes}"], check=True)
            print("[DATA LINEAGE] Annotated input files to EPMT_LINEAGE_IN")

        output_file_list = os.environ.get("output_file_list", "")
        if output_file_list:
            result = subprocess.run([
                "/home/Cole.Harvey/.conda/envs/bloom-filter-env/bin/python",
                "-m", "data_lineage.bloomfilter.StringCompression", output_file_list
            ], check=True, capture_output=True, text=True)
            compressed_bytes = result.stdout.strip().rstrip(",")
            subprocess.run(["epmt", "-v", "annotate",
                           f"EPMT_DATA_LINEAGE_OUT={compressed_bytes}"], check=True)
            print("[DATA LINEAGE] Annotated output files to EPMT_LINEAGE_OUT")

    except subprocess.CalledProcessError as e:
        print(f"WARNING: Data lineage annotation failed: {e}")


class Args:
    """Argument container for compatibility with original interface."""

    def __init__(self):
        """Initialize arguments from environment variables."""
        self.inputDir = os.environ.get("inputDir")
        self.outputDir = os.environ.get("outputDir")
        self.begin = os.environ.get("begin")
        self.inputChunk = os.environ.get("inputChunk")
        self.outputChunk = os.environ.get("outputChunk")
        self.pp_stop = os.environ.get("pp_stop")
        self.component = os.environ.get("component")
        self.fail_ok_components = os.environ.get("fail_ok_components", "")
        self.use_subdirs = os.environ.get("use_subdirs") is not None


def main():
    """Main function to run the timeseries generation."""
    # Create argument object for compatibility
    args = Args()

    # Validate required arguments
    required_vars = [args.inputDir, args.outputDir, args.begin, args.inputChunk,
                    args.outputChunk, args.pp_stop, args.component]
    if not all(required_vars):
        print("ERROR: Missing required environment variables")
        print("Required: inputDir, outputDir, begin, inputChunk, outputChunk, pp_stop, component")
        sys.exit(1)

    print("Arguments:")
    print(f"    input dir: {args.inputDir}")
    print(f"    output dir: {args.outputDir}")
    print(f"    begin: {args.begin}")
    print(f"    input chunk: {args.inputChunk}")
    print(f"    output chunk: {args.outputChunk}")
    print(f"    pp stop: {args.pp_stop}")
    print(f"    component: {args.component}")
    print(f"    components allowed to fail: {args.fail_ok_components}")
    print(f"    use subdirs: {args.use_subdirs}")

    print("Utilities:")
    try:
        # Check for required utilities
        subprocess.run(["cdo", "--version"], capture_output=True, check=True)
        print("cdo")
        subprocess.run(["isodatetime", "--version"], capture_output=True, check=True)
        print("isodatetime")
    except subprocess.CalledProcessError:
        print("ERROR: Required utilities not found")
        sys.exit(1)

    # Calculate expected chunks and end date
    try:
        expected_chunks, end = calculate_expected_chunks(
            args.inputChunk, args.outputChunk, args.begin, args.pp_stop
        )
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if expected_chunks > 0:
        print(f"NOTE: Expect to concatenate {expected_chunks} subchunks")
    else:
        print(f"ERROR: Could not calculate number of expected chunks from"
              f" input chunk '{args.inputChunk}' and output chunk '{args.outputChunk}'")
        sys.exit(1)

    # Verify directories
    if not os.path.isdir(args.inputDir):
        print(f"Error: Input directory '{args.inputDir}' does not exist or isn't a directory")
        sys.exit(1)

    if not os.path.isdir(args.outputDir):
        print(f"Error: Output directory '{args.outputDir}' does not exist or isn't a directory")
        sys.exit(1)

    # Setup data lineage
    setup_data_lineage()

    # Remove trailing Z from dates
    begin_clean = args.begin.rstrip('Z')
    end_clean = end.rstrip('Z')
    print(f"NOTE: Expect output date range to be [{begin_clean}, {end_clean})")

    # Change to input directory
    original_cwd = os.getcwd()
    os.chdir(args.inputDir)

    try:
        did_something = False

        # Process based on subdirs setting
        if args.use_subdirs:
            for subdir in os.listdir("."):
                subdir_path = Path(subdir) / args.component
                if subdir_path.is_dir():
                    os.chdir(subdir_path)
                    result = process_timeseries(args, expected_chunks, begin_clean, end_clean)
                    if result:
                        did_something = True
                    os.chdir(args.inputDir)
        else:
            component_path = Path(args.component)
            if component_path.is_dir():
                os.chdir(component_path)
                did_something = process_timeseries(args, expected_chunks, begin_clean, end_clean)
                os.chdir(args.inputDir)

        # Finalize data lineage
        finalize_data_lineage(args)

        # Exit based on results
        if did_something:
            print("Natural end of the timeseries generation")
            sys.exit(0)
        elif args.component in args.fail_ok_components.split():
            print("No input files were found, but this is allowed")
            sys.exit(0)
        else:
            print("No input files were found")
            sys.exit(1)

    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    main()
