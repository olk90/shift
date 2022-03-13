def build_employee_query(search: str) -> str:
    employeeQuery = """
    select
        e.firstname,
        e.lastname,
        e.email,
        e.id
    from Employee e
    where 
        e.firstname like '%{search}%'
        or e.lastname like '%{search}%'
    """.format(search=search)
    return employeeQuery
