import PySimpleGUI as sg
import os
from zipfile import ZipFile, ZIP_DEFLATED
from ordered_set import OrderedSet


class ZipTool:

    TITLE = 'zip_tool'
    THEME = 'Dark Amber'

    def __init__(self, path='/Users/wes/zip_tool'):
        self._path = path
        self._files = OrderedSet()
        self._selected = None
        self._original_path = None
        sg.theme(self.THEME)

    def __read_zip(self, path):
        """Get all filenames in a zip file.
        """
        self._original_path = path
        self._files.clear()
        with ZipFile(path, 'r') as zip_file:
            self._files = [file for file in zip_file.namelist() if not file.endswith('/')]

    def __write_zip(self, path):
        """Write files into new zip file.
        """
        if os.path.isfile(path):
            os.remove(path)
        path_temp = path + '.tmp'
        with ZipFile(self._original_path, 'r') as original:
            with ZipFile(path_temp, 'w', compression=ZIP_DEFLATED, compresslevel=9) as new:
                for filename in self._files:
                    print('adding {}'.format(filename))
                    with original.open(filename) as in_original:
                        with new.open(filename, 'w') as in_new:
                            in_new.write(in_original.read())

        os.rename(path_temp, path)

    def __update_tree(self):
        """Recreate the tree with current list of files.
        """
        treedata = sg.TreeData()

        for filename in self._files:
            treedata.Insert('', filename, filename, values=[])

        if len(self._files) > 0:
            self._window['Save'].update(disabled=False)
            self._window['numFiles'].update(f'{len(self._files)} files')

        self._window['-TREE-'].Update(treedata)

    def __move_up(self):
        """Move selected file up.
        """
        index = self._files.index(self._selected)
        files = OrderedSet()
        if index == 0:
            return

        if index > 1:
            files = self._files[:index - 1]
        files = list(files) + [self._files[index], self._files[index - 1]] + self._files[index + 1:]

        self._files = files
        self.__update_tree()

    def __move_down(self):
        """Move selected file down.
        """
        index = self._files.index(self._selected)
        files = OrderedSet()
        if index == len(self._files) - 1:
            return

        if index > 0:
            files = self._files[:index]

        files = list(files) + [self._files[index + 1], self._files[index]] + self._files[index + 2:]

        self._files = files
        self.__update_tree()

    def run(self):
        layout = [
            [
                sg.Input(key='_FILEBROWSE_', enable_events=True, visible=False),
                sg.FileBrowse(
                    key='_FILEBROWSE_',
                    button_text='Open',
                    file_types=(('Zip Archive', '*.zip')),
                ),
                sg.Button('Save', disabled=True, key='Save'),
                sg.Text('', size=(32, 1), key='numFiles', auto_size_text=True, justification='right')
            ],
            [
                sg.Tree(
                    data=sg.TreeData(),
                    headings=[],
                    auto_size_columns=True,
                    num_rows=20,
                    col0_width=40,
                    key='-TREE-',
                    show_expanded=False,
                    enable_events=True
                )
            ],
            [sg.Button('Move Up'), sg.Button('Move Down')]
        ]

        self._window = sg.Window(self.TITLE, layout)

        while True:
            event, values = self._window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            elif event == '_FILEBROWSE_':
                self.__read_zip(values['_FILEBROWSE_0'])
                self.__update_tree()
            elif event == '-TREE-':
                self._selected = values['-TREE-'][0]
            elif event == 'Save':
                path = sg.popup_get_file('Save zip file', save_as=True)
                self.__write_zip(path)
            elif event == 'Move Up':
                self.__move_up()
            elif event == 'Move Down':
                self.__move_down()

        self._window.close()

z = ZipTool()
z.run()