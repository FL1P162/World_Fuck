def phone_variables(phone_number: str) -> list:
    phone_number_variables = [phone_number[1:]]
    if len(phone_number) == 12:
        phone_number_variables.append(phone_number[2:])
        phone_number_variables.append(f'{phone_number[1:]}.0')
    elif len(phone_number) == 13:
        phone_number_variables.append(phone_number[3:])
        phone_number_variables.append(f'{phone_number[1:]}.0')
    elif len(phone_number) == 14:
        phone_number_variables.append(phone_number[4:])
        phone_number_variables.append(f'{phone_number[1:]}.0')
    return phone_number_variables