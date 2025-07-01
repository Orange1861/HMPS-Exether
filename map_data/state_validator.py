import os

def check_states_in_files(folder_path, output_file, verbose=True):
    errors = []
    files_ok = []
    province_conflicts = {}

    with open(output_file, "w", encoding="utf-8") as log_file:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                if verbose:
                    log_file.write(f"\nProcessing file: {filename}\n")
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as file:
                    content = file.read()

                state_blocks = content.split("STATE_")[1:]

                file_has_error = False
                all_states_provinces = {}

                # First pass: Parse all states and their provinces
                for state_block in state_blocks:
                    state_block = "STATE_" + state_block.strip()
                    state_name = state_block.split(" ")[0].strip()

                    start_provinces = state_block.find("provinces = {")
                    end_provinces = state_block.find("}", start_provinces)

                    # Skip states without provinces
                    if start_provinces == -1 or end_provinces == -1:
                        continue

                    provinces_str = state_block[start_provinces + len("provinces = {"):end_provinces].strip()
                    provinces = provinces_str.replace("\"", "").split()
                    all_states_provinces[state_name] = [p.lower() for p in provinces]

                    # Record provinces for conflict detection
                    for province in provinces:
                        province = province.lower()
                        if province not in province_conflicts:
                            province_conflicts[province] = []
                        province_conflicts[province].append((state_name, filename))

                # Second pass: Validate each state's elements
                for state_block in state_blocks:
                    state_block = "STATE_" + state_block.strip()
                    state_name = state_block.split(" ")[0].strip()

                    if verbose:
                        log_file.write(f"\n--- Processing {state_name} ---\n")
                        provinces = all_states_provinces.get(state_name, [])
                        log_file.write(f"Provinces extracted for {state_name}: {provinces}\n")

                    required_elements = {
                        "city": None,
                        "farm": None,
                        "mine": None,
                        "wood": None,
                        "port": None
                    }

                    for element in required_elements.keys():
                        start_element = state_block.find(f"{element} = \"")
                        if start_element != -1:
                            end_element = state_block.find("\"", start_element + len(f"{element} = \""))
                            required_elements[element] = state_block[start_element + len(f"{element} = \""):end_element]
                            required_elements[element] = required_elements[element].lower()

                    for element_name, element_value in required_elements.items():
                        if element_value:
                            if verbose:
                                log_file.write(f"Checking {element_name} ({element_value}) against provinces...\n")
                            if element_value not in all_states_provinces.get(state_name, []):
                                found_in_other_state = None
                                for other_state, other_provinces in all_states_provinces.items():
                                    if element_value in other_provinces:
                                        found_in_other_state = other_state
                                        break

                                if found_in_other_state:
                                    error_message = (
                                        f"{state_name} in {filename} has a {element_name} ({element_value}) not listed in its provinces. "
                                        f"Found in {found_in_other_state}."
                                    )
                                else:
                                    error_message = (
                                        f"{state_name} in {filename} has a {element_name} ({element_value}) not listed in its provinces. "
                                        f"No other state contains this province."
                                    )

                                errors.append(error_message)
                                file_has_error = True
                                if verbose:
                                    log_file.write(f"Error: {error_message}\n")
                            else:
                                if verbose:
                                    log_file.write(f"{element_name} ({element_value}) is valid.\n")
                        else:
                            if verbose:
                                log_file.write(f"No {element_name} found for {state_name}.\n")

                if not file_has_error:
                    files_ok.append(filename)

        # Detect conflicts over provinces across all files
        log_file.write("\nProvince Conflicts Across Files\n")
        conflict_found = False

        for province, claims in province_conflicts.items():
            if len(claims) > 1:
                conflict_found = True
                conflicting_states = ", ".join(f"{state} (file: {file})" for state, file in claims)
                conflict_message = f"Province '{province}' is claimed by multiple states: {conflicting_states}"
                errors.append(conflict_message)
                log_file.write(f"{conflict_message}\n")

        if not conflict_found:
            log_file.write("No shared province conflicts detected.\n")



        # Final report
        log_file.write("\nValidation Complete.\n")

        if errors:
            log_file.write("Validation errors found:\n")
            for error in errors:
                log_file.write(f"{error}\n")
        else:
            log_file.write("All files passed validation.\n")

        if files_ok:
            log_file.write("\nThe following files are OK:\n")
            for file in files_ok:
                log_file.write(f"{file}\n")


# Example usage, set verbose to True for province by province logging
folder_path = "C:/Users/zandr//OneDrive/Documents/Paradox Interactive/Victoria 3/mod/realms-gitlab/map_data/state_regions"
output_file = "validation_output.txt"
check_states_in_files(folder_path, output_file, verbose=False)
