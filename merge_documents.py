from pathlib import Path
import sys
from implementation.merge import merge_documents
from implementation.files import generate_name, recurse_files
from implementation.logger import printline, set_language_from_file, printlog
from implementation.commandline import regenerate_default_config, parse_arguments, load_config, wait_for_confirm

# if main script is in a folder called _internal, it means it's part of a generated exe
# it means that langueage and config files should be one level above, where the .exe is.
PROGRAM_DIR = Path(__file__).parent.parent.parent if getattr(sys, "frozen", False) else Path(__file__).parent

if __name__ == "__main__":
    # print(PROGRAM_DIR)
    # REGENERATE CONFIG
    default_config_path = PROGRAM_DIR.joinpath("config.toml")
    regenerate_default_config(default_config_path)
    # PARSE ARGS
    args = parse_arguments()
    # LOAD LANGUAGE FROM ARGS
    set_language_from_file(PROGRAM_DIR, args.language)
    # LOAD CONFIG
    config = load_config(args, default_config_path)
    # RELOAD LANGUAGE IF NEEDED
    if config.language != args.language:
        set_language_from_file(PROGRAM_DIR, config.language)

    # MAYBE SAVE CONFIG
    if args.save_config:
        config.save_config(args.save_config)
    # GET FILES
    files_to_process = recurse_files(args.files, config.alphabetic_file_sorting, config.recursion_limit)
    if not files_to_process:
        printlog("NoFilesToProcess")
        sys.exit()
    # GET OUTPUT PATH
    if args.output_file:  # Output_file has precedence if specified
        output = Path(args.output_file)
    else:
        output = generate_name(config.output_directory_expanded(PROGRAM_DIR))
    # MERGE
    merge_documents(files_to_process, output, config)
    if config.whatif:
        printline()
        printlog("WhatIfMode")
    # WAIT FOR CONFIRM
    wait_for_confirm(wait=config.confirm_exit and not config.quiet)
