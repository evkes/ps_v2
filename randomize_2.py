import random
import json
import math

def clone_previous_quarter(data, growth_type="linear"):
    """
    Clones the previous quarter and adds employees to categories and countries.
    Growth can be linear, quadratic, exponential, bell_curve, logistic, cyclic, 
    stagnation-growth, decline, acquisition, failure, piecewise_funding, 
    linear_to_exponential, or exponential_to_decline.
    
    Capital is only added once every 4-7 quarters to simulate funding rounds.
    
    Prioritizes growth in the USA, India, Sales, and Software Engineering,
    with more realistic B2B SaaS company progression.
    """
    num_quarters = len(data)
    
    # Determine funding rounds (typically series A, B, C, etc.)
    capital_increase_intervals = sorted(random.sample(range(4, min(num_quarters, 20)), k=min(num_quarters // 5, 4)))
    
    for i in range(1, num_quarters):
        previous_entry = json.loads(json.dumps(data[i - 1]))  # Deep copy
        current_quarter = i + 1
        
        # Calculate total headcount from previous quarter
        total_employees = sum(previous_entry['Countries'].values())
        
        # Determine if this quarter should have a capital increase (funding round)
        capital_raised = False
        if i in capital_increase_intervals:
            # Simulate funding rounds increasing in size
            round_size = round(random.uniform(2.0, 5.0) * (1 + (i / num_quarters)), 2)
            previous_entry['Capital'] = round(previous_entry['Capital'] + round_size, 2)
            capital_raised = True
            
            # After funding, growth accelerates
            growth_multiplier = 2.0
        else:
            growth_multiplier = 1.0
        
        new_hires = 0 
        
        # Determine employee growth based on type and current company size
        if growth_type == "linear":
            # Steady predictable growth
            new_hires = random.randint(1, 3) * growth_multiplier
        
        elif growth_type == "quadratic":
            # Growth accelerates over time
            new_hires = (total_employees // 10 + 1) * growth_multiplier
        
        elif growth_type == "exponential":
            # Rapid scaling
            new_hires = max(1, int(total_employees * random.uniform(0.1, 0.3) * growth_multiplier))
        
        elif growth_type == "bell_curve":
            # Fast growth then slowdown
            midpoint = num_quarters // 2
            variance = max(1, int((midpoint - abs(midpoint - i)) * growth_multiplier))
            new_hires = random.randint(1, variance)
        
        elif growth_type == "logistic":
            # S-curve growth (slow, fast, plateau)
            k = 100  # Carrying capacity
            r = 0.2   # Growth rate
            new_hires = int(r * total_employees * (1 - total_employees / k) * growth_multiplier)
            new_hires = max(1, new_hires)
        
        elif growth_type == "cyclic":
            # Seasonal hiring patterns
            base = max(1, total_employees // 10)
            new_hires = int(base + base * math.sin(i * math.pi / 6) * growth_multiplier)
        
        elif growth_type == "stagnation-growth":
            # Periods of little growth followed by spurts
            if i % 3 != 0:
                new_hires = random.randint(0, max(1, total_employees // 20))
            else:
                new_hires = random.randint(max(1, total_employees // 10), max(2, total_employees // 5))
            new_hires = int(new_hires * growth_multiplier)
        
        elif growth_type == "decline":
            # Company that's gradually losing employees (but not catastrophically)
            quarter_percentage = i / num_quarters
            
            if quarter_percentage < 0.3:
                # Initial growth phase
                new_hires = random.randint(1, 3)
            elif quarter_percentage < 0.5:
                # Slowdown phase
                new_hires = random.randint(0, 1)
            else:
                # Decline phase - losing employees but not collapsing
                decline_rate = min(0.05, (quarter_percentage - 0.5) * 0.1)  # 5% max quarterly decline
                loss = max(1, int(total_employees * decline_rate))
                new_hires = -loss
                
                # Occasional small recovery quarters
                if random.random() < 0.2:  # 20% chance of a small recovery quarter
                    new_hires = random.randint(1, max(2, abs(new_hires) // 2))
        
        elif growth_type == "acquisition":
            # Normal growth with a major acquisition spike
            quarter_percentage = i / num_quarters
            
            # Base growth
            new_hires = random.randint(1, max(2, total_employees // 15))
            
            # Acquisition event
            if 0.4 < quarter_percentage < 0.6:
                if abs(quarter_percentage - 0.5) < 0.05:  # The acquisition quarter
                    # Major spike - acquire another company
                    acquired_size = random.randint(10, max(20, total_employees))
                    new_hires += acquired_size
                    print(f"Acquisition event: +{acquired_size} employees in Q{i+1}")
                elif abs(quarter_percentage - 0.5) < 0.1:  # Quarters around acquisition
                    # Pre/post acquisition hiring
                    new_hires += random.randint(3, 8)
            
            new_hires = int(new_hires * growth_multiplier)
        
        elif growth_type == "piecewise_funding":
            # Linear growth that switches to exponential after funding rounds
            
            # Check if this is a funding quarter
            if i in capital_increase_intervals:
                # Remember that we got funding this quarter for future growth
                previous_entry['JustFunded'] = True
                new_hires = random.randint(3, 6)  # Immediately hire a few people post-funding
            elif previous_entry.get('JustFunded', False):
                # First quarter after funding - exponential growth kicks in
                growth_rate = random.uniform(0.15, 0.3)  # 15-30% growth
                new_hires = max(2, int(total_employees * growth_rate))
                previous_entry['JustFunded'] = False  # Reset the flag
                previous_entry['PostFunding'] = 3  # Track 3 quarters of post-funding growth
            elif previous_entry.get('PostFunding', 0) > 0:
                # We're in the post-funding growth phase
                growth_rate = random.uniform(0.1, 0.2)  # 10-20% growth
                new_hires = max(2, int(total_employees * growth_rate))
                previous_entry['PostFunding'] -= 1  # Decrement the counter
            else:
                # Back to linear growth until next funding
                new_hires = random.randint(1, 3)
            
            new_hires = int(new_hires * growth_multiplier)
        
        elif growth_type == "linear_to_exponential":
            # Company that starts with linear growth, then hits product-market fit
            # and transitions to exponential growth regardless of funding
            
            quarter_percentage = i / num_quarters
            transition_point = 0.4  # Transition at 40% of the timeline
            
            if quarter_percentage < transition_point:
                # Linear growth phase (pre product-market fit)
                new_hires = random.randint(1, 3)
            else:
                # After product-market fit, exponential growth
                time_since_transition = quarter_percentage - transition_point
                growth_accelerator = min(0.3, 0.1 + time_since_transition)  # Growth rate increases over time
                new_hires = max(2, int(total_employees * growth_accelerator))
            
            new_hires = int(new_hires * growth_multiplier)
        
        elif growth_type == "exponential_to_decline":
            # Hot company that grows exponentially then hits a market ceiling or competition
            # and begins a slow decline
            
            quarter_percentage = i / num_quarters
            peak_point = 0.5  # Peak at halfway point
            decline_point = 0.7  # Begin decline at 70% of the timeline
            
            if quarter_percentage < peak_point:
                # Strong exponential growth phase
                growth_rate = 0.2 + (quarter_percentage * 0.4)  # Growth rate increases over time (20-40%)
                new_hires = max(2, int(total_employees * growth_rate))
            elif quarter_percentage < decline_point:
                # Plateau phase - growth slows dramatically
                new_hires = random.randint(1, max(2, int(total_employees * 0.05)))
            else:
                # Decline phase - losing employees gradually
                time_since_decline = quarter_percentage - decline_point
                decline_rate = min(0.1, 0.03 + (time_since_decline * 0.2))  # Gradually increasing decline
                loss = max(1, int(total_employees * decline_rate))
                new_hires = -loss
                
                # Occasional stability quarters
                if random.random() < 0.3:  # 30% chance of a stable quarter
                    new_hires = 0
            
            new_hires = int(new_hires * growth_multiplier)
        
        # Process employee changes
        country_keys = list(previous_entry['Countries'].keys())
        occupation_keys = list(previous_entry['Occupations'].keys())
        
        # Define weights based on company size and stage
        # Limited to US, UK, India, Brazil, and France
        # Heavily weighted toward US growth
        country_weights = []
        for c in country_keys:
            if c == 'USA':
                country_weights.append(0.8)  # Significantly increased US weight
            elif c == 'India':
                country_weights.append(0.1)  # Reduced India weight
            elif c == 'UK':
                country_weights.append(0.05)
            elif c == 'France':
                country_weights.append(0.03)
            elif c == 'Brazil':
                country_weights.append(0.02)
            else:
                country_weights.append(0.05)
        
        occupation_weights = []
        for o in occupation_keys:
            if o == 'Software Engineering':
                occupation_weights.append(0.4)
            elif o == 'Sales':
                occupation_weights.append(0.3)
            elif o in ['Customer Success', 'Product Management']:
                occupation_weights.append(0.15)
            else:
                occupation_weights.append(0.15 / (len(occupation_keys) - 4) if len(occupation_keys) > 4 else 0.15)
        
        # Add or remove employees while keeping country and occupation totals equal
        if new_hires != 0:
            country_additions = {}
            occupation_additions = {}
            
            # Initialize additions counters
            for country in country_keys:
                country_additions[country] = 0
            for occupation in occupation_keys:
                occupation_additions[occupation] = 0
            
            # Distribute additions/removals
            for _ in range(int(abs(new_hires))):
                # Select country based on weights
                selected_country = random.choices(country_keys, weights=country_weights)[0]
                country_additions[selected_country] += 1 if new_hires > 0 else -1
                
                # Select occupation based on weights
                selected_occupation = random.choices(occupation_keys, weights=occupation_weights)[0]
                occupation_additions[selected_occupation] += 1 if new_hires > 0 else -1
            
            # Apply changes with protection against negative values
            for country, change in country_additions.items():
                previous_entry['Countries'][country] = max(0, previous_entry['Countries'][country] + change)
            
            for occupation, change in occupation_additions.items():
                previous_entry['Occupations'][occupation] = max(0, previous_entry['Occupations'][occupation] + change)
            
            # Normalize to ensure country total equals occupation total
            country_total = sum(previous_entry['Countries'].values())
            occupation_total = sum(previous_entry['Occupations'].values())
            
            # Adjust if totals aren't equal
            if country_total != occupation_total:
                if country_total > occupation_total:
                    # Need to add employees to occupations
                    diff = country_total - occupation_total
                    for _ in range(diff):
                        selected_occupation = random.choices(occupation_keys, weights=occupation_weights)[0]
                        previous_entry['Occupations'][selected_occupation] += 1
                else:
                    # Need to add employees to countries
                    diff = occupation_total - country_total
                    for _ in range(diff):
                        selected_country = random.choices(country_keys, weights=country_weights)[0]
                        previous_entry['Countries'][selected_country] += 1
        
        # Update quarter label
        year = 2022 + (current_quarter - 1) // 4
        q_num = ((current_quarter - 1) % 4) + 1
        previous_entry['Quarter'] = f"Q{q_num}-{year}"
        
        # Store the updated entry
        data[i] = previous_entry
    
    return data

def generate_initial_conditions(num_conditions, growth_type="linear"):
    """
    Generates multiple initial conditions and saves each to a JSON file.
    
    Growth type can be "linear", "quadratic", "exponential", "bell_curve", "logistic", 
    "cyclic", "stagnation-growth", "decline", "acquisition", or "failure".
    
    For B2B SaaS companies, the initial conditions reflect early-stage startups
    with focus on engineering, sales, and admin, and typically concentrated in
    1-2 locations.
    """
    for i in range(num_conditions):
        # For early B2B SaaS, we'll start with a small team balanced between countries and roles
        initial_employees = random.randint(3, 8)
        
        # Initialize all countries with 0 employees
        countries = {
            "USA": 0,
            "UK": 0,
            "India": 0,
            "Brazil": 0,
            "France": 0
        }
        
        # Initialize all occupations with 0 employees
        occupations = {
            "Software Engineering": 0,
            "Sales": 0,
            "Administration": 0,
            "Product Management": 0,
            "Customer Success": 0,
            "Finance": 0,
            "Legal": 0
        }
        
        # Distribute initial employees with strong US preference
        for _ in range(initial_employees):
            # 90% chance of placing employees in USA for initial team
            if random.random() < 0.9:
                selected_country = "USA"
            else:
                # 10% chance of placing in India
                selected_country = "India"
            
            countries[selected_country] += 1
            
            # Distribute roles focusing on core functions
            role_chance = random.random()
            if role_chance < 0.6:
                # 60% chance of Software Engineering
                selected_occupation = "Software Engineering"
            elif role_chance < 0.9:
                # 30% chance of Sales
                selected_occupation = "Sales"
            else:
                # 10% chance of Administration
                selected_occupation = "Administration"
            
            occupations[selected_occupation] += 1
        
        # Ensure occupation total matches country total by adjusting as needed
        country_total = sum(countries.values())
        occupation_total = sum(occupations.values())
        
        if country_total > occupation_total:
            # Add to occupations (focused on core functions)
            for _ in range(country_total - occupation_total):
                if random.random() < 0.7:
                    occupations["Software Engineering"] += 1
                else:
                    occupations["Sales"] += 1
        elif occupation_total > country_total:
            # Add to countries (focused on US)
            for _ in range(occupation_total - country_total):
                countries["USA"] += 1
        
        # Initial capital (seed funding, typically $0.5M - $3M for early stage B2B SaaS)
        initial_capital = round(random.uniform(0.5, 3.0), 2)
        
        # Create initial data entry
        data = [
            {
                "Quarter": "Q1-2022", 
                "Countries": countries,
                "Occupations": occupations, 
                "Capital": initial_capital
            }
        ]
        
        # Create empty slots for additional quarters
        for _ in range(11):
            data.append({})
        
        # Generate growth data
        updated_data = clone_previous_quarter(data, growth_type)
        
        # Save to file
        with open(f'saas_growth_{growth_type}_{i+1}.json', 'w') as f:
            json.dump(updated_data, f, indent=4)

# Generate different growth types
growth_types = [
    ("linear", 3),
    ("quadratic", 3),
    ("exponential", 3),
    ("bell_curve", 3),
    ("logistic", 3),
    ("cyclic", 3),
    ("stagnation-growth", 3),
    ("decline", 3),
    ("acquisition", 3),
    ("failure", 3),
    ("piecewise_funding", 3),
    ("linear_to_exponential", 3),
    ("exponential_to_decline", 3)
]

# Generate all scenarios
for growth_type, count in growth_types:
    generate_initial_conditions(count, growth_type)
    print(f"Generated {count} scenarios with {growth_type} growth pattern")

print("All B2B SaaS growth scenarios generated successfully")