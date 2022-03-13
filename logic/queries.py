def build_employee_query(search: str) -> str:
    employeeQuery = """
    select
        e.id,
        e.firstname,
        e.lastname,
        e.referenceValue,
        e.e_type
    from Employee e
    where 
        e.firstname like '%{search}%'
        or e.lastname like '%{search}%'
        or e.e_type like '%{search}%'
    """.format(search=search)
    return employeeQuery
