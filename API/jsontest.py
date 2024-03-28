import json

def json_to_txt(json_data, file_path):
    try:
        with open(file_path, 'w') as txt_file:
            json.dump(json_data, txt_file, indent=4)
        print(f"JSON data has been successfully converted and saved to {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")