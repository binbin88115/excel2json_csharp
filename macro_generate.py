# -*- coding: utf-8 -*-

from base import *

CONFIG_TABLE_NAME = '_config_'

CPP_HEADER_BEGIN = '#ifndef _CONFIG_MACRO_{upper_name}_H\n#define _CONFIG_MACRO_{upper_name}_H\n\n'
CPP_HEADER_MACRO = '#define {macro} \t{id}\t // {desc}\n'
CPP_HEADER_END = '\n#endif // _CONFIG_MACRO_{upper_name}_H'

JS_HEADER_BEGIN = 'module.exports = {\n\n'
JS_HEADER_MACRO = '\t{macro}: {id},\t // {desc}\n'
JS_HEADER_END = '\n};'

TEMPLATE_DIRECTORY = 'csharp_template'
WRITE_DIRECTORY    = 'csharp/Constant'

TEMPLATE_CSHARP_MARCO = 'Macro.cs'

CSHARP_MACRO_DEFINE = '\n\t\tpublic const int {macro} = {id};'

class MACROGenerate(Base):

    _marco_template = ''

    def __init__(self):
        Base.__init__(self)

    def load_xls_file(self, xls_file):
        self._load_xls_file(xls_file)

    # 判断文件是否存在
    def template_directory_exists(self):
        return self._directory_exists(os.path.abspath(TEMPLATE_DIRECTORY))

    def change_to_code_name(self, name):
        return name.replace('_', ' ').title().replace(' ','')

    def get_marco_template(self):
        if self._marco_template == '':
            self._marco_template = self.try_open_file(TEMPLATE_CSHARP_MARCO)
        return self._marco_template

    def try_open_file(self, file_name):
        if self.template_directory_exists():
            file_path = os.path.abspath(os.path.join(TEMPLATE_DIRECTORY, file_name))
            if os.path.exists(file_path) and os.path.isfile(file_path):
                f = file(file_path, 'r')
                value = f.read()
                f.close()
                return value
            else:
                self._error(str.format('"{}"文件不存在', file_name))
                sys.exit()
        else:
            self._error(str.format('"{}"文件夹不存在', TEMPLATE_DIRECTORY))
            sys.exit()

    def table_to_json(self, sheet_name, output_name):
        table = self._try_get_sheet_by_name(sheet_name)
        column_names = table.row_values(TABLE_COLUMN_NAME_ROW_INDEX)
        column_types = table.row_values(TABLE_COLUMN_TYPE_ROW_INDEX)
        if (COLUMN_MACRO_TYPE not in column_types):
            return '';

        table_json = []
        for row_index in range(TABLE_OFFSET_ROW_NUM, table.nrows):
            row_json = {}
            for column_index in range(table.ncols):
                cell = table.cell(row_index, column_index)
                column_name = column_names[column_index]
                if column_name == '':
                    continue

                column_type = column_types[column_index]
                if column_type == '':
                    continue

                if column_index != 0 and column_type != COLUMN_MACRO_TYPE:
                    continue
                    
                if column_type == COLUMN_INT_TYPE:
                    row_json['id'] = (0 if cell.value == '' else int(cell.value))
                elif column_type == COLUMN_MACRO_TYPE:
                    row_json['macro'] = str(cell.value)

                if len(row_json) == 2:
                    break

            if row_json['id'] == 0 or row_json['macro'] == '':
                continue
            table_json.append(row_json)
        return table_json

    def get_macro_define(self, id, macro):
        return CSHARP_MACRO_DEFINE.format(macro = macro, id = id)

    def export_macro(self):
        for table in self._output_config_table:
            sheet_name = table[CONFIG_SHEET_NAME_COLUMN_INDEX]
            output_name = table[CONFIG_OUTPUT_NAME_COLUMN_INDEX]

            table_json = self.table_to_json(sheet_name, output_name)
            if (len(table_json) == 0):
                continue

            macro_items = ''
            for row in table_json:
                macro_items += self.get_macro_define(row['id'], row['macro'])

            macro_class_name = self.change_to_code_name(output_name)
            macro = self.get_marco_template()
            macro = macro.format(macro_class_name = macro_class_name, macro_items = macro_items, left = '{', right = '}')

            self._write(WRITE_DIRECTORY, macro_class_name + '.cs', macro)

