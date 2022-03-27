def build_employee_type_query(search: str) -> str:
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


def build_employee_query(search: str) -> str:
    query = """
    select
        e.id,
        e.firstname,
        e.lastname,
        e.referenceValue,
        e.night_shifts,
        t.designation
    from Employee e
    inner join EmployeeType t 
    on e.e_type_id = t.id
    where 
        e.firstname like '%{search}%'
        or e.lastname like '%{search}%'
        or t.designation like '%{search}%'
    order by e.lastname, e.firstname
    """.format(search=search)
    return query


def build_employee_combo_query() -> str:
    query = """
        select
            e.id,
            e.firstname,
            e.lastname,
        from Employee e
        order by e.lastname, e.firstname
        """
    return query


def build_off_period_query(search: str) -> str:
    query = """
    select
        p.id,
        p.start,
        p.end,
        e.firstname,
        e.lastname
    from OffPeriod p
    inner join Employee e 
    on p.e_id = e.id
    where 
        e.firstname like '%{search}%'
        or e.lastname like '%{search}%'
    order by e.lastname, e.firstname
    """.format(search=search)
    return query


def build_schedule_query(search: str) -> str:
    query = """
    select 
        s.id,
        s.date,
        d.firstname || ' ' || d.lastname as d_fullname,
        n.firstname || ' ' || n.lastname as n_fullname,
        s.comment
    from Schedule s
    inner join Employee d
    on d.id = s.day_id
    inner join Employee n 
    on n.id = s.night_id
    where 
        d.firstname like '%{search}%'
        or d.lastname like '%{search}%'
        or n.firstname like '%{search}%'
        or n.lastname like '%{search}%'
        or s.comment like '%{search}%'
    """.format(search=search)
    return query
