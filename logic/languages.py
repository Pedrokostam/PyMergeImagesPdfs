from dataclasses import dataclass


@dataclass
class Language:
    id: str
    msg_merged_prefix: str
    msg_exit: str
    msg_post_merge_listing: str
    msg_empty_input: str
    msg_appended: str
    msg_saved_in: str
    msg_config_saved: str
    msg_file_count: str
    msg_gather_header: str
    msg_file_converting: str
    msg_file_copying: str
    msg_pdf_merging: str
    msg_pdf_2_pdf: str
    msg_img_2_pdf: str
    msg_conversion_error:str


en = Language(
    "en",
    msg_merged_prefix="merged",
    msg_exit="Press ENTER to exit",
    msg_post_merge_listing="Merged following files:",
    msg_empty_input="No files to merge!",
    msg_appended="Appended: ",
    msg_saved_in="Merged file saved in: ",
    msg_config_saved="Saved config to: ",
    msg_file_count=" file(s) to process",
    msg_file_converting="Converting to PDF: ",
    msg_file_copying="Copying: ",
    msg_gather_header="Gathering files...",
    msg_pdf_merging="Merging file: ",
    msg_pdf_2_pdf="",
    msg_img_2_pdf=" (image -> PDF)",
    msg_conversion_error="Cannot convert to PDF: ",
)
pl = Language(
    "pl",
    msg_merged_prefix="scalony",
    msg_exit="Wciśnij ENTER, aby wyjść",
    msg_post_merge_listing="Scalono następujące pliki:",
    msg_empty_input="Brak plików do scalenia!",
    msg_appended="Dołączono: ",
    msg_saved_in="Zapisano scalony plik w: ",
    msg_config_saved="Zapisano plik konfiguracji w: ",
    msg_file_count=" plików do przetworzenia",
    msg_file_converting="Konwersja do PDF: ",
    msg_file_copying="Kopiowanie: ",
    msg_gather_header="Zbieranie plików...",
    msg_pdf_merging="Dołączanie pliku: ",
    msg_pdf_2_pdf="",
    msg_img_2_pdf=" (obraz -> PDF)",
    msg_conversion_error="Nie można przekonwertować do PDF: ",
)
