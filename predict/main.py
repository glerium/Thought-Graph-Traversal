import subprocess
import os
import sys

num_loops = 1
script_to_run = "evaluate.py"
output_dir = "logs"
bot_type = 'huatuo'
openai_api_key = 'your-api-key-here'
aliyun_api_key = 'your-api-key-here'
# data_path = '/data2/tianxy/got/GPT-GoT/mimic_images'
data_path = '/home/ps/got/R2Gen/data/iu_xray/images'
gts_path = 'gts_iuxray.csv'

try:
    os.makedirs(output_dir, exist_ok=True)
    print(f"Log files will be saved to directory: '{output_dir}'")
except OSError as e:
    print(f"Error: Could not create log directory '{output_dir}': {e}", file=sys.stderr)
    sys.exit(1)


print(f"Starting {num_loops} rounds of experiments.")
print(f"Script to be executed: {script_to_run}")

for loop_idx in range(num_loops):
    print(f"\n{'-'*80}")
    print(f"=== Starting experiment round {loop_idx + 1}/{num_loops} (setting environment variable LOOP={loop_idx}) ===")
    print(f"{'-'*80}")

    script_not_found = False

    stdout_filename = os.path.join(output_dir, f"loop_{loop_idx}_stdout.log")
    stderr_filename = os.path.join(output_dir, f"loop_{loop_idx}_stderr.log")

    print(f"\n{'-'*60}")
    print(f"Calling script (LOOP={loop_idx})")
    print(f"stdout will be written to: {stdout_filename}")
    print(f"stderr will be written to: {stderr_filename}")
    print(f"{'-'*60}")

    env = os.environ.copy()
    env['LOOP'] = str(loop_idx)
    env['BOT_TYPE'] = bot_type
    env['OPENAI_API_KEY'] = openai_api_key
    env['ALIYUN_API_KEY'] = aliyun_api_key
    env['DATA_PATH'] = data_path
    env['GTS_PATH'] = gts_path

    stdout_file = None
    stderr_file = None

    try:
        stdout_file = open(stdout_filename, 'w', encoding='utf-8')
        stderr_file = open(stderr_filename, 'w', encoding='utf-8')

        result = subprocess.run(
            ['python', script_to_run],
            env=env,
            stdout=stdout_file,
            stderr=stderr_file,
            check=True
        )
        print(f"\nScript {script_to_run} (LOOP={loop_idx}) ran successfully. Exit code {result.returncode}. Output saved to log files.")

    except FileNotFoundError:
        print(f"\nError: File {script_to_run} not found. Please ensure the file exists and is in the current directory or system's PATH.", file=sys.stderr)
        script_not_found = True
        break

    except subprocess.CalledProcessError as e:
        print(f"\nError: Script {script_to_run} (LOOP={loop_idx}) failed with exit code {e.returncode}.", file=sys.stderr)
        print(f"Please check log files {stdout_filename} and {stderr_filename} for more details.", file=sys.stderr)
        pass

    except Exception as e:
        print(f"\nAn unknown error occurred when calling LOOP={loop_idx}: {e}", file=sys.stderr)
        print(f"Please check log files {stdout_filename} and {stderr_filename} for possible error output.", file=sys.stderr)
        pass

    finally:
        if stdout_file and not stdout_file.closed:
            stdout_file.close()
        if stderr_file and not stderr_file.closed:
            stderr_file.close()

    if script_not_found:
        break

print(f"\n{'-'*80}")
print(f"=== All {num_loops} experiment rounds completed ===")
print(f"{'-'*80}")