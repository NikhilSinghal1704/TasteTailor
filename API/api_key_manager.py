from Home.models import APIKey


def get_next_api_key():
    # Get the next API key based on the rotation_order
    next_api_key = APIKey.objects.filter(is_active=True)

    if not next_api_key:
        # If there are no active keys, reactivate all keys and try again
        APIKey.objects.update(is_active=True)
        next_api_key = APIKey.objects.filter(is_active=True)

    if next_api_key:
        n = len(next_api_key)

        fl = open("index_storage", "w+")

        i = fl.read()

        if i >= n:
            fl.write(0)
            i = 0
        
        next_api_key = next_api_key[i]   
        
        return next_api_key.key

    return None  # No keys available
