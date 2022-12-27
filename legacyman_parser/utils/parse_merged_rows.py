class MergedRowsExtractor:
    def __init__(self, number_of_columns: int):
        self.number_of_columns = number_of_columns
        self._content_of_current_merged_row_of_column = {}
        self._no_of_rows_for_which_current_merged_row_of_column_is_applicable_now = {}

    def decrement_and_possibly_reset_current_merged_row_of_column_flags(self, column: int):
        # Decrement the applicable rows by one each time we consume the row
        self._no_of_rows_for_which_current_merged_row_of_column_is_applicable_now[column] -= 1

        if self._no_of_rows_for_which_current_merged_row_of_column_is_applicable_now[column] == 0:
            self._content_of_current_merged_row_of_column.pop(column, None)
            self._no_of_rows_for_which_current_merged_row_of_column_is_applicable_now.pop(column, None)

    def set_current_merged_row_of_column_flags(self, column: int, applicable_rows: int, content: str):
        self._no_of_rows_for_which_current_merged_row_of_column_is_applicable_now[column] = applicable_rows
        self._content_of_current_merged_row_of_column[column] = content

    def effective_length_of(self, columns):
        return len(columns) + len(self._no_of_rows_for_which_current_merged_row_of_column_is_applicable_now)

    def retrieve_row(self, columns):
        list_of_row_data = []
        if len(columns) == self.number_of_columns:
            for index in range(0, self.number_of_columns):
                list_of_row_data.append(columns[index].text)
                if 'rowspan' in columns[index].attrs:
                    self.set_current_merged_row_of_column_flags(index,
                                                                int(columns[index]['rowspan']) - 1,
                                                                columns[index].text)
        else:
            tracked_index = 0
            for index in range(0, self.number_of_columns):
                if self._content_of_current_merged_row_of_column.get(index, None) is not None:
                    list_of_row_data.append(self._content_of_current_merged_row_of_column.get(index))
                    self.decrement_and_possibly_reset_current_merged_row_of_column_flags(index)
                else:
                    list_of_row_data.append(columns[tracked_index].text)
                    if 'rowspan' in columns[tracked_index].attrs:
                        self.set_current_merged_row_of_column_flags(index,
                                                                    int(columns[tracked_index]['rowspan']) - 1,
                                                                    columns[index].text)
                    tracked_index += 1
        return list_of_row_data
