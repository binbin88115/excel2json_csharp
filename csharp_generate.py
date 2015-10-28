# -*- coding: utf-8 -*-

from base import *

TEMPLATE_CSHARP_MANAGER = 'ConfigManager.cs'
TEMPLATE_ITEM           = 'ConfigItem.cs'
TEMPLATE_SUB_ITEM       = 'ConfigSubItem.cs' 

TEMPLATE_DIRECTORY = 'csharp_template'
WIRTE_DIRECTORY    = 'csharp'

CSHARP_UNKNOWN_TYPE = 'unknown'
CSHARP_INT_TYPE     = 'int'
CSHARP_FLOAT_TYPE   = 'float'
CSHARP_STRING_TYPE  = 'string'
CSHARP_DOUBLE_TYPE  = 'double'
CSHARP_BOOL_TYPE    = 'bool'

LEFT_BRACE  = '{'
RIGHT_BRACE = '}'

CONFIG_MANAGER_FIELD_DECLARE = '\n\t\tprivate ConfigTable<{name}> {instance} = new ConfigTable<{name}>();'
CONFIG_MANAGER_PROPERTY_CLAUSE = '\n\t\tpublic ConfigTable<{name}> {property} {left} get {left} return {instance}; {right} {right}'
CONFIG_MANAGER_LOAD_CLAUSE = '\n\t\t\tLoadFromFile<{class_name}>("{table_name}");'

class CSharpGenerate(Base):

    _sub_item_template = ''

    def __init__(self):
        Base.__init__(self)

    def load_xls_file(self, xls_file):
        self._load_xls_file(xls_file)

    def change_to_code_name(self, name):
        return name.replace('_', ' ').title().replace(' ','')

    # 获取每次表的字段类型及字段名称
    def get_table_structure(self, sheet_name):
        table = self._try_get_sheet_by_name(sheet_name)
        column_names = table.row_values(TABLE_COLUMN_NAME_ROW_INDEX)
        column_types = table.row_values(TABLE_COLUMN_TYPE_ROW_INDEX)

        ret_json = []
        index = 0
        for column_index in range(table.ncols):
            if column_index == 0:
                index += 1
                continue

            column = {}

            column_name = column_names[column_index]
            if column_name == '':
                continue

            column_type = column_types[column_index]
            if column_type == '':
                continue

            code_type = CSHARP_UNKNOWN_TYPE;
            if column_type == COLUMN_INT_TYPE:
                code_type = CSHARP_INT_TYPE
            elif column_type == COLUMN_FLOAT_TYPE:
                code_type = CSHARP_FLOAT_TYPE
            elif column_type == COLUMN_DOUBLE_TYPE:
                code_type = CSHARP_DOUBLE_TYPE
            elif column_type == COLUMN_BOOL_TYPE:
                code_type = CSHARP_BOOL_TYPE
            elif column_type == COLUMN_STRING_TYPE:
                code_type = CSHARP_STRING_TYPE

            if code_type == CSHARP_UNKNOWN_TYPE:
                continue

            column['type'] = code_type
            column['title'] = column_name
            column['index'] = index
            ret_json.append(column)

            index += 1
        return ret_json

    # 获取Config##Item中字段的声明
    def get_config_item_filed(self, column_type, column_title):
        return str.format('\n\t\tpublic {} {};', column_type, self.change_to_code_name(column_title))

    # 获取Config##Item.Init中的分配语句
    def get_config_item_assigment(self, column_type, column_title, column_index):
        assign_clause = str.format('\n\t\t\t{} = node[{}]', self.change_to_code_name(column_title), column_index)
        if column_type == CSHARP_INT_TYPE:
            assign_clause += ".AsInt;"
        elif column_type == CSHARP_FLOAT_TYPE:
            assign_clause += ".AsFloat;"
        elif column_type == CSHARP_DOUBLE_TYPE:
            assign_clause += ".AsDouble;"
        elif column_type == CSHARP_BOOL_TYPE:
            assign_clause += ".AsBool;"
        else:
            assign_clause += ";";
        return assign_clause;

    # 获取Config##Item类型名
    def get_config_item_class_name(self, output_name):
        return str.format('Config{}Item', self.change_to_code_name(output_name))

    def get_config_sub_item_template(self):
        if self._sub_item_template == '':
            self._sub_item_template = self.try_open_file(TEMPLATE_SUB_ITEM)
        return self._sub_item_template

    # 生成一个ConfigXXXItem
    def get_config_sub_item(self, output_name, column_array):
        fileds = ''
        assigments = ''
        for column in column_array:
            fileds += self.get_config_item_filed(column['type'], column['title'])
            assigments += self.get_config_item_assigment(column['type'], column['title'], column['index'])
        sub_item = self.get_config_sub_item_template()
        return sub_item.format(config_sub_class = self.get_config_item_class_name(output_name), 
            config_fields = fileds, config_fields_assigment = assigments, left = LEFT_BRACE, right = RIGHT_BRACE)

    # 获取ConfigManager中ConfigTable<T>的变量名
    def get_config_manager_field_name(self, output_name):
        return str.format('m_cfg{}', self.change_to_code_name(output_name))

    # 获取ConfigManager的属性名
    def get_config_manager_property_name(self, output_name):
        return self.change_to_code_name(output_name)

    # 获取ConfigManager字段声明语句
    def get_config_manager_file_clause(self, output_name):
        config_class_name = self.get_config_item_class_name(output_name)
        config_class_instance = self.get_config_manager_field_name(output_name)
        return CONFIG_MANAGER_FIELD_DECLARE.format(name = config_class_name, instance = config_class_instance);

    # 获取ConfigManager属性声明语句
    def get_config_manger_propery_clause(self, output_name):
        config_property = self.get_config_manager_property_name(output_name)
        config_class_name = self.get_config_item_class_name(output_name)
        config_class_instance = self.get_config_manager_field_name(output_name)
        return CONFIG_MANAGER_PROPERTY_CLAUSE.format(name = config_class_name, instance = config_class_instance,
            property = config_property, left = LEFT_BRACE, right = RIGHT_BRACE)

    # 获取ConfigManager.Load中的JSON文件加载语句
    def get_config_manager_load_clause(self, output_name):
        config_class_name = self.get_config_item_class_name(output_name)
        return CONFIG_MANAGER_LOAD_CLAUSE.format(class_name = config_class_name, table_name = output_name)

    # 生成ConfigManager所需的field, proerty, load
    def parse_config_manager(self, output_name_array):
        filed_clauses = ''
        property_clauses = ''
        load_clauses = ''
        for output_name in output_name_array:
            filed_clauses += self.get_config_manager_file_clause(output_name)
            property_clauses += self.get_config_manger_propery_clause(output_name)
            load_clauses += self.get_config_manager_load_clause(output_name)
        return filed_clauses, property_clauses, load_clauses

    # 判断文件是否存在
    def template_directory_exists(self):
        return self._directory_exists(os.path.abspath(TEMPLATE_DIRECTORY))

    # 打开文件
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

    # ========> 外部调用接口
    # 返回，ConfigManager(fiels, properties, loads), ConfigItems
    def get_config_info(self):
        config_items = ''
        output_name_array = []
        for row in self._output_config_table:
            column_array = self.get_table_structure(row[CONFIG_SHEET_NAME_COLUMN_INDEX])
            output_name = row[CONFIG_OUTPUT_NAME_COLUMN_INDEX]

            output_name_array.append(output_name)

            config_items += self.get_config_sub_item(output_name, column_array)
            config_items += '\n\n'

        fileds, properties, loads = self.parse_config_manager(output_name_array)
        return fileds, properties, loads, config_items

    # ========> 外部调用接口
    # 生成ConfigManager.cs文件
    def export_config_manager(self, fileds, properties, loads):
        config_manager = self.try_open_file(TEMPLATE_CSHARP_MANAGER)
        config_manager = config_manager.format(config_fields = fileds, config_properties = properties,
            load_data_from_json_files = loads, left = LEFT_BRACE, right = RIGHT_BRACE)
        self._write(WIRTE_DIRECTORY, TEMPLATE_CSHARP_MANAGER, config_manager)

    # ========> 外部调用接口
    # 生成ConfigItem.cs文件
    def export_config_item(self, config_items):
        config_item = self.try_open_file(TEMPLATE_ITEM)
        config_item = config_item.format(config_items = config_items, left = LEFT_BRACE, right = RIGHT_BRACE)
        self._write(WIRTE_DIRECTORY, TEMPLATE_ITEM, config_item)
