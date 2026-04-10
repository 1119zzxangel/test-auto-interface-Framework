def print_table(two_dimension_list):
    """
    打印表格函数
    输入一个2维列表,格式参见:
    [
    ["123,"123,"123"],
    ["123,"123","123]
    ...
    ]
    空行表示方法:
    ["","",""]
    注意每行的元素数需要相等
    :param two_dimension_list:
    :return:
    """

    def sum_string_length(keys):
        """内部函数：计算字符串显示长度，中文/全角符号占2位，英文/数字占1位"""
        length = 0
        for key in str(keys):
            # 判断是否是中文字符
            if u'\u4e00' <= key <= u'\u9fff':
                length += 2
            # 判断是否是全角符号
            elif u'\uFF01' <= key <= u'\uFF5E':
                length += 2
            # 其他字符（英文、数字）
            else:
                length += 1
        return length

    four_space = "    "  # 定义4个空格，用于表格内边距

    # 存储每一列最长字符串长度的列表，用于对齐
    each_col_max_length_list = []
    # 一行有多少个元素（列数）
    row_element_count = len(two_dimension_list[0])

    # 遍历每一列，计算每一列最长的字符串长度
    for col in range(row_element_count):
        max_length = 0
        # 遍历每一行，对比当前列所有单元格的长度
        for i in range(len(two_dimension_list)):
            # 计算当前单元格的显示长度
            element_length = sum_string_length(two_dimension_list[i][col])
            # 更新最大值
            if max_length < element_length:
                max_length = element_length
        # 把本列最大长度存入列表
        each_col_max_length_list.append(max_length)

    # 计算表格顶部边框长度
    vertical_line_count = len(each_col_max_length_list)
    before_space_count = vertical_line_count * 4
    after_space_count = sum(each_col_max_length_list) + before_space_count
    line_count = before_space_count + after_space_count + vertical_line_count
    # 拼接顶部边框：+-------------------------+
    case_str = "+{0}+".format("-" * (line_count - 1))
    print(case_str)

    # 遍历每一行数据，开始打印表格内容
    for row_num in range(len(two_dimension_list)):
        output_str = "|"  # 每行以 | 开头
        # 遍历当前行的每一列
        for element in range(len(two_dimension_list[row_num])):
            # 计算当前单元格后面需要填充的空格数，实现对齐
            later_space_count = each_col_max_length_list[element] - sum_string_length(
                two_dimension_list[row_num][element]) + 4
            space1 = " " * (later_space_count)
            # 拼接单元格内容：四个空格 + 内容 + 填充空格 + |
            output_str += "{space0}{value}{space1}|".format(space0=four_space,
                                                            value=two_dimension_list[row_num][element],
                                                            space1=space1)
        # 判断当前行是否是空行（内容全为空）
        if output_str.replace("|", "").replace(" ", ""):
            # 不是空行，直接打印
            print(output_str)
        else:
            # 如果是空行，替换为分隔线行
            output_str = "|"
            for i in range(len(two_dimension_list[row_num])):
                output_str += "-" * (each_col_max_length_list[i] + 8) + "+"
            output_str = output_str[:-1] + "|"
            print(output_str)
    # 打印底部边框
    print(case_str)


# 测试数据
test_list = [
    ['id', 'vehicle_no', 'color', 'address'],
    ["", "", "", ""],
    ['1116016058541708528', '京GW0001', '蓝色', '北京海淀'],
    ['1146003998720578844', '冀F12343', '黄色', '成都锦江'],
    ['1148015232542564762', '冀F12370', '绿色', '广州花都'],
    ["", "", "", ""]
]

# 调用函数打印表格
# print_table(test_list)