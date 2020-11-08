def confirm(question):
    check = str(input(f"{question} (Y/N): ")).lower().strip()
    try:
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return confirm(question)
    except Exception as error:
        print("Please enter valid inputs")
        print(f"{error} (Error Code:C_001)")
        return confirm(question)