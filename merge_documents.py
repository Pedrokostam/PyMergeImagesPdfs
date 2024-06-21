from pathlib import Path
from implementation.merge import merge_documents
from implementation.files import generate_name, recurse_files
from implementation.logger import set_language_from_file
from implementation.commandline import regenerate_default_config, parse_arguments, load_config, wait_for_confirm

PROGRAM_DIR = Path(__file__).parent

if __name__ == "__main__":
    # REGENERATE CONFIG
    default_config_path = PROGRAM_DIR.joinpath("config.toml")
    regenerate_default_config(default_config_path)
    # LOAD LANGUAGE
    set_language_from_file(PROGRAM_DIR.joinpath("language.json"))
    # PARSE ARGS
    args = parse_arguments()
    # LOAD CONFIG
    config = load_config(args, default_config_path)
    # MAYBE SAVE CONFIG
    if args.save_config:
        config.save_config(args.save_config)
    # GET FILES
    files_to_process = recurse_files(args.files, config.alphabetic_file_sorting)
    # GET OUTPUT PATH
    if args.output_file:  # Output_file has precedence if specified
        output = Path(args.output_file)
    else:
        output = generate_name(config.output_directory_expanded(PROGRAM_DIR))
    # MERGE
    merge_documents(files_to_process, output, config)
    # WAIT FOR CONFIRM
    wait_for_confirm(wait=config.confirm_exit and not config.quiet)
