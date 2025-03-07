import json
import os

def calculate_revenue(employee_data):
    """
    Calculate revenue based on employee distribution across countries and job roles
    using salary estimates with min and max ranges.
    
    Args:
        employee_data (dict): A dictionary containing employee distribution data.
        
    Returns:
        dict: Revenue calculations and related metrics.
    """
    # Country salary multipliers (normalized to USA = 1.0)
    country_multipliers = {
        "USA": 1.0,     # Base reference country
        "UK": 0.85,     # 85% of US salaries
        "India": 0.30,  # 30% of US salaries
        "France": 0.78, # 78% of US salaries
        "Brazil": 0.38  # 38% of US salaries
    }
    
    # Role revenue multipliers (min and max revenue per $1 of salary)
    role_multipliers = {
        "Sales": (2.5, 4),                    # Sales directly impacts revenue
        "Software Engineering": (2.0, 3.5),   # Engineering creates product value
        "Product Management": (2.0, 3.0),     # Product influences revenue significantly
        "Customer Success": (2.0, 3.0),       # Customer retention drives recurring revenue
        "Administration": (1.0, 2.0),         # Support function
        "Finance": (1.5, 2.5),                # Financial optimization
        "Legal": (1.0, 2.0)                   # Risk mitigation
    }
    
    # Base salary by role (in USD for USA)
    base_salaries = {
        "Sales": 110000,
        "Software Engineering": 130000,
        "Product Management": 125000,
        "Customer Success": 85000,
        "Administration": 65000,
        "Finance": 95000,
        "Legal": 120000
    }

    countries = employee_data.get("Countries", {})
    occupations = employee_data.get("Occupations", {})
    capital = employee_data.get("Capital", 0) * 1000000 
    
    total_employees = sum(countries.values())
    total_revenue_min = 0
    total_revenue_max = 0
    
    country_distribution = {}
    for country, count in countries.items():
        country_distribution[country] = count / total_employees if total_employees > 0 else 0
    
    role_distribution = {}
    role_total = sum(occupations.values())
    for role, count in occupations.items():
        role_distribution[role] = count / role_total if role_total > 0 else 0
    
    for country, country_percent in country_distribution.items():
        country_count = countries[country]
        country_factor = country_multipliers.get(country, 0.7) 
    
        for role, role_percent in role_distribution.items():
            role_count = country_count * role_percent
            base_salary = base_salaries.get(role, 90000) 
            role_multiplier_min, role_multiplier_max = role_multipliers.get(role, (1.5, 2.5))
            salary_cost = base_salary * country_factor * role_count
            role_revenue_min = salary_cost * role_multiplier_min
            role_revenue_max = salary_cost * role_multiplier_max
            total_revenue_min += role_revenue_min
            total_revenue_max += role_revenue_max
    
    total_revenue = (total_revenue_min + total_revenue_max) / 2
    total_revenue_min = round(total_revenue_min / 1000) * 1000
    total_revenue_max = round(total_revenue_max / 1000) * 1000
    total_revenue = round(total_revenue / 1000) * 1000
    
    revenue_per_employee = round(total_revenue / total_employees) if total_employees > 0 else 0
    capital_to_revenue_ratio = capital / total_revenue if total_revenue > 0 else 0
    
    return {
        "Revenue": total_revenue,
        "RevenueMin": total_revenue_min,
        "RevenueMax": total_revenue_max,
        "RevenuePerEmployee": revenue_per_employee,
        "CapitalToRevenueRatio": capital_to_revenue_ratio
    }

def update_json_files(json_files):
    """
    Update the specified JSON files with revenue information.
    
    Args:
        json_files (list): List of JSON filenames to update.
    """
    for filename in json_files:
        try:
            with open(filename, 'r') as file:
                company_data = json.load(file)
            
            for quarter in company_data:
                revenue_info = calculate_revenue(quarter)
                quarter["Revenue"] = revenue_info["Revenue"]
                quarter["RevenueMin"] = revenue_info["RevenueMin"]
                quarter["RevenueMax"] = revenue_info["RevenueMax"]
                quarter["RevenuePerEmployee"] = revenue_info["RevenuePerEmployee"]
                quarter["CapitalToRevenueRatio"] = revenue_info["CapitalToRevenueRatio"]
            
            with open(filename, 'w') as file:
                json.dump(company_data, file, indent=4)
            
            print(f"Updated {filename} with revenue information.")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

def process_directory(directory_path="."):
    """
    Process all JSON files in the specified directory.
    
    Args:
        directory_path (str): Path to directory containing JSON files.
    """
    json_files = []
    
    try:
        json_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
                     if f.endswith('.json')]
    except Exception as e:
        print(f"Error reading directory {directory_path}: {e}")
        return
    
    if not json_files:
        print(f"No JSON files found in {directory_path}")
        return
    
    update_json_files(json_files)
    print(f"Processed {len(json_files)} JSON files with revenue data.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        directory_path = sys.argv[1]
        if not os.path.isdir(directory_path):
            print(f"Error: {directory_path} is not a valid directory.")
            sys.exit(1)
    else:
        directory_path = "."
    
    process_directory(directory_path)
    print("Revenue calculation completed.")