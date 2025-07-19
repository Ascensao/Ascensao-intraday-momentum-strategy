def calculate_annual_return():
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    returns = []

    print("Enter monthly returns in % (e.g., 3.5 for 3.5%):\n")
    
    for month in months:
        while True:
            try:
                r = float(input(f"{month}: ").replace(",", "."))
                returns.append(r)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number (e.g., 1.5, -2.3).")

    # Calculate compound annual return
    factors = [(1 + r / 100) for r in returns]
    annual_return = (__import__('math').prod(factors)) - 1
    print("\n=== Result ===")
    print(f"Compound annual return: {round(annual_return * 100, 2)}%")

# Run the function
calculate_annual_return()
