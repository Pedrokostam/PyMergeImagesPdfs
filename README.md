# PyMergeImagesPdfs

## What it is

This is a Python script, which takes given documents and merges them into a single PDF.

The script can handle various file formats:

- PDF files
- Image files (one image per page)
  - JPG/JPEG, PNG, BMP, GIF, TIFF, PNM, PGM, PBM, PPM, PAM, JXR, JPX/JP2, PSD
- Office documents (if LibreOffice is installed on the system)
  - Microsoft Office formats (.doc, .docx, .xlsx, .pptx ...)
  - OpenDocument formats (.sxw, .odt, .ods, .odp ...)
  - Text files (.txt, .rtf ...)

The script is customizable with command line parameters as well as a configuration files (TOML format).

The repository also contains a Python script that generates an standalone executable, which makes it easier to use the app (dragging files or folder onto the exe merges their contents).

## Input data

You can specify both files and directories to merge. Directories will be traversed recursively to find all files with supported extension, until `recursion-limit` is exceeded.
> [!WARNING]
> Be careful when setting recursion limit. If there directory tree is complex it may take some time to go through every subfolder (or you may find out, that the tree contains many more documents than you expected)

## Command line usage

Simply execute the script `merge_documents.py`. Using it with no arguemnts displays help, which should explain everything well enough.

While you can specify options like `--output-directory` as an argument, you can also use a configuration file.

The script will generate a default configuration file, if it is missing. The file has every option explained. When running the script first takes arguments from the configuration file, then from the command line (command line arguments have priority).

## *Drag&Drop* usage

While you can always drag and drop elements onto the script/executable, it is recommened to first tweak the configuration file. There should be a configuration file named `config_dragdrop.toml` near the app - it's been tweaked to provide better *drag&drop* usage. For example, the output folder is set to **~/Desktop** and the app will not close the console until the user presses Enter.

If you plan on using the app this way, rename that file to `config.toml` (or see the [next section](#shortcuts)). Of course, you can edit the file to your liking.

### Shortcuts

On Windows it may be convenient to create a shortcut to the executable. With a shortcut you can specify arguments in the target field - those will be recognized by the app when opening the shortcut. If you want to use the executable both from the command line and with *drag&drop* you can specify the config for *drag&drop* in the shortcut (path relative to the `Start in:` field).

This way the configuration from `config.toml` is used when in command line (without the need to use `--config`) but *drag&drop* uses its own configuration file.

## Language

The app will attempt to load a language file if one is present in its folder. First file matching the pattern `language*.json` will be used. 

To control which language is used you can either rename your preferred file so that it is the first alphabetically (or the only one) or use the argument `language (-l)`.

If that argument was specified (in configuration or command line) the app will attempt to load the language file with the spcified identifier. Failure to load will make it use the default language.

Setting the argument to an empty string will return to loading the first available file.

### Language files

Language files can be edited freely, with 2 caveats:

- a language file should contain all the keys that were present in the original English file. If a key is not present, the default English message will be used.
- every string should have the same number of matching placeholders as the default English string.
  - fewer placeholders are permitted - the intended part will simply not be inserted
  - more placeholders are not permitted - English version will be used instead
  - named placeholders are not permitted - English version will be used instead

## Remarks

### LibreOffice

Office documents formats can only be processed if LibreOffice is isntalled on the computer. It leverages its functionality to convert documents to PDFs. If LibreOffice is not installed (or otherwise cannot be found) those documents will be skipped.

It may be possible to use different descendants of StarOffice (like OpenOffirce) since they should have the same console interface. This however has not been tested.
