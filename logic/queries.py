def employee_type_query(search: str) -> str:
    query = """
        select
            t.id,
            t.designation,
            t.rotation_period
        from EmployeeType t 
        where 
            t.designation like '%{search}%'
            or t.rotation_period like '%{search}%'
        order by t.designation
        """.format(search=search)
    return query


def employee_query(search: str) -> str:
    query = """
    select
        e.id,
        e.firstname,
        e.lastname,
        e.referenceValue,
        e.night_shifts,
        e.global_score,
        t.designation
    from Employee e
    inner join EmployeeType t 
    on e.e_type_id = t.id
    where 
        e.firstname like '%{search}%'
        or e.lastname like '%{search}%'
        or t.designation like '%{search}%'
    order by e.global_score desc, e.lastname, e.firstname
    """.format(search=search)
    return query


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


def off_period_query(search: str) -> str:
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
        e.firstname like '%{search}%'
        or e.lastname like '%{search}%'
    order by e.lastname, e.firstname
    """.format(search=search)
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
        and (d.firstname like '%{search}%'
        or d.lastname like '%{search}%'
        or n.firstname like '%{search}%'
        or n.lastname like '%{search}%'
        or s.comment like '%{search}%')
    """.format(year=year, month=str(month).zfill(2), search=search)
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
            e.firstname || ' ' || e.lastname as name,
            e.id 
        from Employee e
        order by e.global_score
        """
    return query


def night_shift_replacement_query() -> str:
    query = """
        select
            e.firstname || ' ' || e.lastname as name,
            e.id 
        from Employee e
        where e.night_shifts = 1
        order by e.global_score
        """
    return query
