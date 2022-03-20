def build_employee_type_query(search: str) -> str:
    employeeTypeQuery = """
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
    return employeeTypeQuery


def build_employee_query(search: str) -> str:
    employeeQuery = """
    select
        e.id,
        e.firstname,
        e.lastname,
        e.referenceValue,
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
    return employeeQuery
