import PySimpleGUI as sg
import functions

sg.theme("Black")

# This section is for the main application window.
file_choice_label = sg.Text("Select the text file containing the spell description:")
file_choice_input = sg.Input(key="file_choice",
                             enable_events=True,
                             visible=True)
file_choice_button = sg.FileBrowse("Choose",
                                   key="filepath",
                                   target="file_choice")

output_dir_label = sg.Text("Pick the desired destination directory:")
output_dir_input = sg.Input(key="folder_choice",
                            enable_events=True,
                            visible=True)
output_dir_button = sg.FolderBrowse("Choose",
                                    key="dest_folder",
                                    target="folder_choice")

preamble_choice_label = sg.Text("How many lines in preamble, including name?")
preamble_choice_input = sg.Input(key="preamble_length",
                                 enable_events=True,
                                 visible=True)
preamble_help_text = """
The preamble includes all lines before
the spell descriptive text begins. This
includes Name, Level, Classes, etc.
Include broken lines as well, since these
change the preamble length.
"""
preamble_help_label = sg.Text(preamble_help_text)

extra_elements_checkbox = sg.Checkbox("Are there any extra elements?",
                                      key="extra_elements",
                                      enable_events=True,
                                      visible=True)
extra_elements_help_text = """
Extra elements include any items bulleted
in the spell descriptive text, bold or
bold-italicized text denoting special
descriptions.
"""
extra_elements_help_label = sg.Text(extra_elements_help_text)

result_label = sg.Text(key="results", text_color="white")

convert_button = sg.Button("Convert File")
quit_button = sg.Button("Quit", key="quit")

layout_col1 = [[file_choice_label],
               [file_choice_input],
               [file_choice_button]]

layout_col2 = [[output_dir_label],
               [output_dir_input],
               [output_dir_button]]

layout_col3 = [[preamble_choice_label],
               [preamble_choice_input],
               [preamble_help_label]]

layout_col4 = [[extra_elements_checkbox],
               [extra_elements_help_label]]

col1 = sg.Column(layout=layout_col1)
col2 = sg.Column(layout=layout_col2)
col3 = sg.Column(layout=layout_col3)
col4 = sg.Column(layout=layout_col4)

main_window = sg.Window("Spell Converter",
                        layout=[[col1, col2],
                                [col3, col4],
                                [convert_button, quit_button, result_label]])

# This section is for the presentation window that allows the user to see the
# changes made to the final version before writing the output to disk.

while True:
    event, values = main_window.read()
    print(event, values)
    match event:
        case "Convert File":
            filepath = values["filepath"]
            dest_folder = values["dest_folder"]
            preamble_length_text = values["preamble_length"]
            extra_elements = values["extra_elements"]
            lines = functions.load_file(filepath)
            print(f"lines type: {type(lines)}")
            elements = functions.load_elements()
            if not isinstance(lines, list):
                # An error occurred trying to load the file.
                main_window["results"].update(value=lines)
            else:
                try:
                    preamble_length = int(preamble_length_text)
                    # First remove the break lines.
                    lines = [line.strip("\n") for line in lines]
                    finished_lines = functions.convert_preamble(
                        lines[0:preamble_length], preamble_length, elements["preamble"])

                    # The next step is to convert the remaining text into paragraphs.
                    paragraphs = functions.find_paragraphs(lines[preamble_length:],
                                                           elements["extras"],
                                                           extra_elements)
                    finished_lines.extend(paragraphs)
                    error_msg = functions.write_new_file(finished_lines, filepath, dest_folder)
                    if error_msg:
                        main_window["results"].update(value=error_msg)
                    else:
                        main_window["results"].update(
                            value="Conversion complete.")

                except ValueError:
                    main_window["results"].update(value="Preamble length must a number.")

        case sg.WIN_CLOSED:
            break
        case "quit":
            break

main_window.close()
