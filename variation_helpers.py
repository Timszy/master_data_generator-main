import random
import copy
import re
from datetime import datetime, timedelta

# Variation rate
variation_rate_default = 0.2

# Dictionary to track all introduced duplicates across all entities
duplicate_registry = {}

def register_duplicate(original_id, duplicate_id, entity_type, variation_type, field_name):
    """Register a duplicate relationship in the global registry"""
    if original_id not in duplicate_registry:
        duplicate_registry[original_id] = []
    
    duplicate_registry[original_id].append({
        'duplicate_id': duplicate_id,
        'entity_type': entity_type,
        'variation_type': variation_type,
        'field_name': field_name
    })

# Helper functions for generating variations
def introduce_variations(data_list, variation_function, variation_rate=variation_rate_default, entity_type=None):
    # Generate variations for only a subset of the items based on the variation_rate
    selected_indices = random.sample(range(len(data_list)), int(len(data_list) * variation_rate))
    variations = []
    for index in selected_indices:
        varied_item, variation_info = variation_function(data_list[index])
        variations.append(varied_item)
        register_duplicate(
            original_id=data_list[index]["identifier"],
            duplicate_id=varied_item["identifier"], 
            entity_type=entity_type or variation_function.__name__.replace("_variation", ""),
            variation_type=variation_info["variation_type"],
            field_name=variation_info["field_name"]
        )
    return data_list + variations

# Enhanced address variations
def address_variation(address):
    """Generate variations of an address"""
    # Original simple variation (missing postal code)
    var1 = copy.deepcopy(address)
    if var1.get("postalCode"):
        var1["postalCode"] = ''  # Simulate missing postal code
        var1["identifier"] = var1["identifier"] + "_var1"  # Add variant identifier
        # Return the modified address and variation info
        return var1, {"variation_type": "missing_field", "field_name": "postalCode"}
    
    # Variation with typo in city name
    var2 = copy.deepcopy(address)
    if var2.get("city") and len(var2["city"]) > 3:
        city = list(var2["city"])
        pos = random.randint(1, len(city) - 2)
        # Random typo operations
        typo_type = random.choice(["swap", "duplicate", "missing", "extra"])
        
        if typo_type == "swap":
            city[pos], city[pos+1] = city[pos+1], city[pos]
        elif typo_type == "duplicate":
            city.insert(pos, city[pos])
        elif typo_type == "missing":
            city.pop(pos)
        elif typo_type == "extra":
            city.insert(pos, random.choice("abcdefghijklmnopqrstuvwxyz"))
        
        var2["city"] = "".join(city)
        var2["text"] = re.sub(r'[^,]+, ([^,]+) ([^,]+)', f'{var2["city"]}, \\1 \\2', var2["text"])
        var2["identifier"] = var2["identifier"] + "_var2"
        return var2, {"variation_type": "typo", "field_name": "city"}
    
    # Default variation - format change
    var3 = copy.deepcopy(address)
    if all(key in var3 for key in ["city", "postalCode", "country"]):
        street_part = var3["text"].split(',')[0]
        var3["text"] = f"{var3['postalCode']} {var3['city']}, {street_part}, {var3['country']}"
        var3["identifier"] = var3["identifier"] + "_var3"
        return var3, {"variation_type": "format_change", "field_name": "text"}
    
    # If nothing else worked, return a simple copy with minimal change
    var4 = copy.deepcopy(address)
    var4["identifier"] = var4["identifier"] + "_var4"
    return var4, {"variation_type": "minor_change", "field_name": "text"}

# Enhanced person name variations
def person_names_variation(person):
    """Generate variations of a person's name"""
    var1 = copy.deepcopy(person)
    names = var1["personName"].split()
    if len(names) > 1:
        var1["personName"] = ' '.join(names[::-1])
        var1["identifier"] = var1["identifier"] + "_var1"
        return var1, {"variation_type": "name_swap", "field_name": "personName"}
    
    var2 = copy.deepcopy(person)
    names = var2["personName"].split()
    if len(names) >= 2:
        if len(names) == 2:  # Add middle initial if none exists
            middle_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            var2["personName"] = f"{names[0]} {middle_initial}. {names[1]}"
            var2["identifier"] = var2["identifier"] + "_var2"
            return var2, {"variation_type": "middle_initial_added", "field_name": "personName"}
    
    # Default minimal change
    var3 = copy.deepcopy(person)
    var3["identifier"] = var3["identifier"] + "_var3"
    return var3, {"variation_type": "minor_change", "field_name": "personName"}

def replace_day_or_month(date_string, new_value, is_day=True):
    """
    Replace the day or month in a date string.

    Parameters:
        date_string (str): Original date string in 'YYYY-MM-DD' format.
        new_value (str): New value for the day or month.
        is_day (bool): If True, replace the day, otherwise replace the month.

    Returns:
        str: Modified date string.
    """
    parts = date_string.split('-')
    if is_day:
        parts[2] = new_value.zfill(2)
    else:
        parts[1] = new_value.zfill(2)
    return '-'.join(parts)

# Enhanced date of birth variations
def person_dob_variation(person):
    """Generate variations of a person's date of birth"""
    var1 = copy.deepcopy(person)
    var1["birthDate"] = replace_day_or_month(var1["birthDate"], '01', is_day=True)
    var1["identifier"] = var1["identifier"] + "_var1"
    return var1, {"variation_type": "default_day", "field_name": "birthDate"}

# New variation function for organization names
def organization_name_variation(organization):
    """Generate variations of an organization name"""
    var1 = copy.deepcopy(organization)
    if "healthcareOrganizationName" in var1:
        name = var1["healthcareOrganizationName"]
        # Add/remove suffixes
        suffixes = [" Inc.", " LLC", " Ltd.", " Group", " Center", " Associates", " & Co."]
        if any(name.endswith(suffix) for suffix in suffixes):
            for suffix in suffixes:
                if name.endswith(suffix):
                    var1["healthcareOrganizationName"] = name.replace(suffix, "")
                    break
        else:
            var1["healthcareOrganizationName"] = name + random.choice(suffixes)
        var1["identifier"] = var1["identifier"] + "_var1"
        return var1, {"variation_type": "suffix_change", "field_name": "healthcareOrganizationName"}
    
    # Default minimal change if no name present
    var2 = copy.deepcopy(organization)
    var2["identifier"] = var2["identifier"] + "_var2"
    return var2, {"variation_type": "minor_change", "field_name": "healthcareOrganizationName"}
    


# New variation function for email addresses
def email_variation(personnel):
    """Generate variations of an email address"""
    var1 = copy.deepcopy(personnel)
    if "email" in var1:
        local_part, domain = var1["email"].split('@')
        alt_domains = {
            "healthcare.org": "health-care.org",
            "hospital.com": "hospitals.com",
            "clinic.org": "clinics.org",
            "medical.com": "med.com",
            "doctor.net": "dr.net",
            "health.org": "healthcare.org"
        }
        if domain in alt_domains:
            var1["email"] = f"{local_part}@{alt_domains[domain]}"
        else:
            # Add a location prefix to the domain
            locations = ["us", "eu", "uk", "ca", "au"]
            var1["email"] = f"{local_part}@{random.choice(locations)}.{domain}"
        var1["identifier"] = var1["identifier"] + "_var1"
        return var1, {"variation_type": "domain_change", "field_name": "email"}
    
    # Default minimal change if no email present
    var2 = copy.deepcopy(personnel)
    var2["identifier"] = var2["identifier"] + "_var2"
    return var2, {"variation_type": "minor_change", "field_name": "email"}

# New function for department name variations
def department_name_variation(department):
    """Generate variations of a department name"""
    var1 = copy.deepcopy(department)
    if "serviceDepartmentName" in var1:
        dept_name = var1["serviceDepartmentName"]
        abbreviations = {
            "Anesthesia": "Anesth Dept",
            "Cardiovascular": "Cardio",
            "Community Health": "Comm Health",
            "Dentistry": "Dental",
            "Dermatology": "Derm",
            "Emergency": "ER",
            "Endocrine": "Endo",
            "Gastroenterologic": "GI",
            "Gynecologic": "GYN",
            "Hematologic": "Hema",
            "Infectious": "ID",
            "Laboratory": "Lab",
            "Musculoskeletal": "MSK",
            "Neurologic": "Neuro",
            "Obstetric": "OB",
            "Oncologic": "Onc",
            "Optometric": "Opt",
            "Otolaryngologic": "ENT",
            "Pathology": "Path",
            "Pediatric": "Peds",
            "Psychiatric": "Psych",
            "Pulmonary": "Pulm",
            "Radiography": "Radiology",
            "Respiratory": "Resp",
            "Surgical": "Surgery"
        }
        
        for full, abbr in abbreviations.items():
            if full in dept_name:
                var1["serviceDepartmentName"] = dept_name.replace(full, abbr)
                var1["identifier"] = var1["identifier"] + "_var1"
                return var1, {"variation_type": "abbreviation", "field_name": "serviceDepartmentName"}
    
    # Default minimal change if no match
    var2 = copy.deepcopy(department)
    var2["identifier"] = var2["identifier"] + "_var2"
    return var2, {"variation_type": "minor_change", "field_name": "serviceDepartmentName"}
    

def export_duplicate_registry(filename='duplicate_registry.csv'):
    """
    Export the duplicate registry to a CSV file for reference
    """
    import csv
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['original_id', 'duplicate_id', 'entity_type', 'variation_type', 'field_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for original_id, duplicates in duplicate_registry.items():
            for dup in duplicates:
                writer.writerow({
                    'original_id': original_id,
                    'duplicate_id': dup['duplicate_id'],
                    'entity_type': dup['entity_type'],
                    'variation_type': dup['variation_type'],
                    'field_name': dup['field_name']
                })