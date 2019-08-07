from textwrap import dedent

queries_dict = {
        'searches': dedent('''
            SELECT COUNT(str.str_id)/60 AS searcher_dates_per_day
            FROM standard_reports.search_to_request str
            WHERE str.dates BETWEEN dateadd('day', -61, current_date) AND dateadd('day', -1, current_date)
            '''),
        'requests': dedent('''
            SELECT SUM(str.converted)/60 AS requests_per_day
            FROM standard_reports.search_to_request str
            WHERE str.dates BETWEEN dateadd('day', -61, current_date) AND dateadd('day', -1, current_date)
            '''),
        'needs': dedent('''
            SELECT COUNT(n.need_id)/60 AS needs_per_day
            FROM standard_reports.needs n
            WHERE n.need_added BETWEEN dateadd('day', -61, current_date) AND dateadd('day', -1, current_date)
            '''),
        'bookings': dedent('''
            SELECT SUM(ntb.booked)/60 AS bookings_per_day
            FROM standard_reports.needs n  
            JOIN standard_reports.need_to_book ntb ON n.need_id = ntb.need_id AND lag = {lag} AND lagged = TRUE
            WHERE n.need_added BETWEEN dateadd('day', -(61+{lag}), current_date) AND dateadd('day', -(1+{lag}), current_date)
            ''')
        }
