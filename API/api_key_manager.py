from Home.models import APIKey


def get_next_api_key():
    # Get all active API keys
    active_api_keys = list(APIKey.objects.filter(is_active=True))

    if not active_api_keys:
        # If there are no active keys, reactivate all keys and try again
        APIKey.objects.update(is_active=True)
        active_api_keys = list(APIKey.objects.filter(is_active=True))

    if active_api_keys:
        # Read the current index from the storage file or initialize it to 0
        try:
            with open("index_storage", "r") as fl:
                current_index = int(fl.read())
        except (FileNotFoundError, ValueError):
            current_index = 0  # Handle the case where the file is empty or contains an invalid value

        # Get the next API key based on the current index
        next_api_key = active_api_keys[current_index]
        
        # Increment the index and loop it if it exceeds the list length
        current_index = (current_index + 1) % len(active_api_keys)
        
        #Update the usage count of the API Key
        next_api_key.update_usage_count()

        # Update the index in the storage file
        with open("index_storage", "w") as fl:
            fl.write(str(current_index))

        return next_api_key.key

    return None  # No keys available

