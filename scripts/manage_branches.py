#!/usr/bin/env python3
from huggingface_hub import HfApi
import time

def manage_branches(repo_id, target_size, target_quant, new_branch_name):
    # Initialize the Hugging Face API
    api = HfApi()
    
    try:
        # Get all branches
        print(f"\nFetching current branches for {target_size}...")
        refs = api.list_repo_refs(repo_id)
        existing_branches = [branch.name for branch in refs.branches]
        
        print(f"Current branches: {existing_branches}")
        
        # Filter branches for current size (1.5b or 8b)
        size_branches = [b for b in existing_branches if b.startswith(target_size)]
        print(f"\nBranches for {target_size}: {size_branches}")
        
        # First delete the existing new_branch_name if it exists
        if new_branch_name in existing_branches:
            print(f"\nDeleting existing branch: {new_branch_name}")
            try:
                api.delete_branch(repo_id=repo_id, branch=new_branch_name)
                print(f"✓ Deleted existing {new_branch_name}")
                time.sleep(1)
            except Exception as e:
                print(f"Error deleting existing branch: {str(e)}")
                return
        
        # Then rename target quantization branch to new name
        if target_quant in existing_branches:
            print(f"\nRenaming '{target_quant}' branch to '{new_branch_name}'")
            try:
                api.create_branch(branch=new_branch_name, repo_id=repo_id, revision=target_quant)
                print(f"✓ Created new branch '{new_branch_name}'")
                time.sleep(1)  # Wait a bit before continuing
            except Exception as e:
                print(f"Error during rename: {str(e)}")
                return
        
        # Delete other quantization branches for this size
        for branch in size_branches:
            if branch != new_branch_name:  # Keep the newly created branch
                print(f"\nDeleting branch: {branch}")
                try:
                    api.delete_branch(repo_id=repo_id, branch=branch)
                    print(f"✓ Deleted {branch}")
                    time.sleep(1)
                except Exception as e:
                    print(f"Error deleting {branch}: {str(e)}")
        
        # Verify final state
        time.sleep(1)  # Wait before final check
        final_refs = api.list_repo_refs(repo_id)
        final_branches = [branch.name for branch in final_refs.branches]
        print(f"\nFinal branches after {target_size} cleanup: {final_branches}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Repository ID
    repo_id = "cortexso/yi-1.5"
    
    # First handle 1.5b branches
    print("\n=== Processing 34b branches ===")
    manage_branches(
        repo_id=repo_id,
        target_size="34b",
        target_quant="34b-gguf-q4-km",
        new_branch_name="34b"
    )
