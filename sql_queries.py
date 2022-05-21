symbols_query = """
    SELECT distinct symbol FROM symbol_list
"""

columns_query = """
    SELECT name FROM pragma_table_info('stocks')
"""

times_query = """
    SELECT distinct date FROM stocks
"""

insert_query = """
    INSERT INTO stocks(symbol, date, close)
    VALUES(:symbol, :date, :close)
"""