from textwrap import dedent

queries_dict = {
        'searches': dedent('''
                SELECT COUNT(str.str_id)/60 AS searcher_dates_per_day
                FROM standard_reports.search_to_request str
                WHERE str.dates BETWEEN dateadd('day', -61, current_date) AND dateadd('day', -1, current_date)'''
        ),
        'requests': dedent('''
                SELECT SUM(str.converted)/60 AS requests_per_day
                FROM standard_reports.search_to_request str
                WHERE str.dates BETWEEN dateadd('day', -61, current_date) AND dateadd('day', -1, current_date)'''
        ),
        'needs': dedent('''
                SELECT COUNT(n.need_id)/60 AS needs_per_day
                FROM standard_reports.needs n
                WHERE n.need_added BETWEEN dateadd('day', -61, current_date) AND dateadd('day', -1, current_date)'''
        ),
        'need_to_book_lagged': dedent('''
                SELECT COUNT(n.need_id)/60 AS needs_per_day, SUM(ntb.booked)/60 AS bookings_per_day
                FROM standard_reports.needs n  
                JOIN standard_reports.need_to_book ntb ON n.need_id = ntb.need_id AND lag = {lag} AND lagged = TRUE
                WHERE n.need_added BETWEEN dateadd('day', -(61+{lag}), current_date) AND dateadd('day', -(1+{lag}), current_date)'''
        ),
        'search_to_book_lagged': dedent('''
                SELECT COUNT(stb.str_id)/60 AS search_events_per_day, SUM(stb.booked)/60 AS bookings_per_day
                FROM standard_reports.search_to_request str
                JOIN standard_reports.search_to_book stb ON str.str_id = stb.str_id AND stb.lagged = 1 AND stb.lag = {lag}
                JOIN standard_reports.searches s ON s.search_event_id = str.min_search 
                        AND s.search_event_added BETWEEN dateadd('day', -(61+{lag}), current_date) 
                        AND dateadd('day', -(1+{lag}), current_date)
                WHERE str.dates BETWEEN dateadd('day', -(61+{lag})-1, current_date) 
                        AND dateadd('day', -(1+{lag})+1, current_date)'''
        ),
        'need_to_book': dedent('''
                WITH unlagged_needs AS (
                        SELECT n.need_id, MAX(ntb.booked) AS booked 
                        FROM standard_reports.needs n  
                        JOIN standard_reports.need_to_book ntb ON n.need_id = ntb.need_id 
                        WHERE n.need_added BETWEEN dateadd('day', -(61), current_date) AND dateadd('day', -(1), current_date)
                        GROUP BY 1
                ) 
                SELECT COUNT(need_id)/60 AS needs_per_day, SUM(booked)/60 AS booked_per_day
                FROM unlagged_needs'''
        ),
        'search_to_request': dedent('''
                SELECT COUNT(str.str_id)/60 AS searches_per_day, SUM(str.converted)/60 AS requests_per_day
                FROM standard_reports.search_to_request str
                JOIN standard_reports.searches s ON s.search_event_id = str.min_search
                WHERE s.search_event_added BETWEEN dateadd('day', -(61), current_date) AND dateadd('day', -(1), current_date)'''
        ),
        'search_to_book': dedent('''
                WITH unlagged_searches AS (
                        SELECT str.str_id, max(stb.booked) AS booked
                        FROM standard_reports.search_to_request str
                        JOIN standard_reports.searches s ON s.search_event_id = str.min_search
                                AND s.search_event_added BETWEEN dateadd('day', -61, current_date)
                                AND dateadd('day', -1, current_date)
                        JOIN standard_reports.search_to_book stb ON stb.str_id = str.str_id
                        WHERE str.dates BETWEEN dateadd('day', -(61+1), current_date)
                                AND dateadd('day', -(1-1), current_date)
                        GROUP BY 1
                )
                SELECT COUNT(str_id)/60 AS searches_per_day, SUM(booked)/60 AS books_per_day
                FROM unlagged_searches'''
        )
        }
