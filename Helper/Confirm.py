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
        print(error)
        return confirm(question)