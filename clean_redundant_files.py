import shutil
from pathlib import Path

def clean_redundant_files():
    base_path = Path(__file__).parent  # Project root directory
    
    # Files and directories to delete
    targets = [
        "data.pkl",
        ".pytest_cache",
        "__pycache__",
        ".hypothesis"
    ]
    
    # First, clean the base directory
    for target_name in targets:
        target_path = base_path / target_name
        if target_path.is_file():
            target_path.unlink()
        elif target_path.is_dir():
            shutil.rmtree(target_path)
    
    # Directories to process
    test_dirs = [
        base_path / "blackbox_test",
        base_path / "whitebox_test",
    ]
    
    for test_dir in test_dirs:
        if not test_dir.exists():
            continue
            
        
        # Find all test method directories (like boundary_test, ECP, etc.)
        for method_dir in test_dir.iterdir():
            if method_dir.is_dir():
                
                for target_name in targets:
                    target_path = method_dir / target_name
                    
                    if target_path.is_file():
                        target_path.unlink()  # delete file
                    elif target_path.is_dir():
                        shutil.rmtree(target_path)  # delete folder

if __name__ == "__main__":
    clean_redundant_files()