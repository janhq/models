import argparse
from huggingface_hub import hf_hub_download
import os
from ruamel.yaml import YAML
import ast

def download_yaml_from_huggingface(repo_id, filename, save_path, branch=None):
    try:
        # Download the file from the Hugging Face Hub
        try:
            downloaded_path = hf_hub_download(repo_id=repo_id, filename=filename, revision=branch)
        except:
            downloaded_path = hf_hub_download(repo_id=repo_id, filename=filename)
        
        # Ensure the directory for save_path exists
        os.makedirs(save_path, exist_ok=True)
        full_save_path = os.path.join(save_path, "model.yml")
        # Copy the downloaded file to the desired save location
        with open(downloaded_path, 'rb') as src_file, open(full_save_path, 'wb') as dst_file:
            dst_file.write(src_file.read())
        
        print(f"File downloaded successfully and saved to {full_save_path}")
        return full_save_path
    except Exception as e:
        print(f"An error occurred during download: {str(e)}")
        return None

def modify_nested_dict(data, keys, new_value):
    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = new_value

def modify_yaml(file_path, key_value_pairs):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    try:
        with open(file_path, 'r') as file:
            data = yaml.load(file)

        # Modify the specified fields
        for field, new_value in key_value_pairs:
            keys = field.split('.')
            modify_nested_dict(data, keys, new_value)
            print(f"Modified field '{field}' to '{new_value}'")

        # Write the modified data back to the file
        with open(file_path, 'w') as file:
            yaml.dump(data, file)

        print(f"Successfully modified all specified fields in {file_path}")
    except Exception as e:
        print(f"An error occurred while modifying the YAML file: {str(e)}")

def parse_value(value):
    try:
        # Try to evaluate the string as a Python literal
        parsed_value = ast.literal_eval(value)
        
        # If it's a list, parse each element
        if isinstance(parsed_value, list):
            return [parse_value(item) for item in parsed_value]
        
        return parsed_value
    except (ValueError, SyntaxError):
        # If it's not a valid Python literal, return it as a string
        return value

def parse_key_value_pair(pair):
    try:
        field, value = pair.split('=', 1)  # Split on first '=' only
        parsed_value = parse_value(value)
        return field, parsed_value
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid field-value pair: {pair}. Use format 'field=value'")

def main():
    parser = argparse.ArgumentParser(description="Download a YAML file from Hugging Face, modify multiple fields, and save it")
    parser.add_argument("--repo_id", required=True, help="The ID of the Hugging Face repository")
    parser.add_argument("--filename", required=True, help="The name of the YAML file to download")
    parser.add_argument("--branch", default=None, help="The branch to download from (default is main)")
    parser.add_argument("--save_path", required=True, help="The local path where the file should be saved")
    parser.add_argument("--key_value_pairs", required=True, nargs='+', type=parse_key_value_pair,
                        help="Field-value pairs to modify. Format: field1=value1 field2=value2 ...")
    
    args = parser.parse_args()
    
    # Download the file
    downloaded_file = download_yaml_from_huggingface(
        repo_id=args.repo_id,
        filename=args.filename,
        save_path=args.save_path,
        branch=args.branch
    )
    
    if downloaded_file:
        # Modify the YAML file
        modify_yaml(
            file_path=downloaded_file,
            key_value_pairs=args.key_value_pairs
        )

if __name__ == "__main__":
    main()