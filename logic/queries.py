def employee_fullname_query() -> str:
    query = """
        select
            e.firstname || ' ' || e.lastname as name,
            e.id 
        from Employee e
        order by e.lastname, e.firstname
        """
    return query


def employee_type_designation_query() -> str:
    query = """
        select
            e.designation,
            e.id
        from EmployeeType e
        order by e.designation
    """
    return query


def off_period_query(year: int, month: int, search: str) -> str:
    query = """
    select
        p.id,
        p.start,
        p.end,
        e.firstname || ' ' || e.lastname as e_fullname
    from OffPeriod p
    inner join Employee e 
    on p.e_id = e.id
    where 
        (strftime('%m', p.start) = '{month}' and strftime('%Y', p.start) = '{year}'
        or strftime('%m', p.end) = '{month}' and strftime('%Y', p.end) = '{year}')
    
    """.format(year=year, month=str(month).zfill(2))
    if len(search) > 0:
        query += """
            and (e.firstname like '%{search}%'
            or e.lastname like '%{search}%')
            
        """.format(search=search)
    query += """
        order by e.lastname, e.firstname
    """
    return query


def schedule_query(year: int, month: int, search: str) -> str:
    query = """
            select 
                s.id,
                s.date,
                d.firstname || ' ' || d.lastname as d_fullname,
                n.firstname || ' ' || n.lastname as n_fullname,
                s.comment
            from Schedule s
            left join Employee d
            on d.id = s.day_id
            left join Employee n 
            on n.id = s.night_id
            where 
                strftime('%m', s.date) = '{month}' and strftime('%Y', s.date) = '{year}'
                
        """.format(year=year, month=str(month).zfill(2))
    if len(search) > 0:
        query += """
            and (d.firstname like '%{search}%'
            or d.lastname like '%{search}%'
            or n.firstname like '%{search}%'
            or n.lastname like '%{search}%'
            or s.comment like '%{search}%')
    """.format(search=search)
    return query


def schedule_id_query(year: int, month: int) -> str:
    query = """
    select 
        s.id
    from Schedule s
    where 
        strftime('%m', s.date) = '{month}' and strftime('%Y', s.date) = '{year}'
    """.format(year=year, month=str(month).zfill(2))
    return query


def day_shift_replacement_query() -> str:
    query = """
        select
            e.firstname || ' ' || e.lastname || ' (' || e.score || ')' as name,
            e.id 
        from Employee e
        order by e.score asc 
        """
    return query


def night_shift_replacement_query() -> str:
    query = """
        select
            e.firstname || ' ' || e.lastname || ' (' || e.score || ')' as name,
            e.id 
        from Employee e
        where e.night_shifts = 1
        order by e.score asc 
        """
    return query


def employee_id_by_name_and_score_query(nas: str) -> str:
    query = """
        select e.id from Employee e
        where e.firstname || ' ' || e.lastname || ' (' || e.score || ')' = '{nas}'
    """.format(nas=nas)
    return query
