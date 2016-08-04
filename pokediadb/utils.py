import sqlite3


def max_sql_variables():
    """Get the maximum number of arguments allowed in a query by the current
    sqlite3 implementation.

    Returns:
        int: SQLITE_MAX_VARIABLE_NUMBER

    """
    db = sqlite3.connect(':memory:')
    cur = db.cursor()
    cur.execute('CREATE TABLE t (test)')
    low, high = 0, 100000

    while (high - 1) > low:
        guess = (high + low) // 2
        query = 'INSERT INTO t VALUES ' + ','.join(['(?)' for _ in
                                                    range(guess)])
        args = [str(i) for i in range(guess)]
        try:
            cur.execute(query, args)
        except sqlite3.OperationalError as e:
            if "too many SQL variables" in str(e):
                high = guess
            else:
                return 999
        else:
            low = guess

    cur.close()
    db.close()

    return low
