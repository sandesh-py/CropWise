import sys
sys.path.append('C:\\Users\\sande\\OneDrive\\Desktop\\cropwise\\backend\\.venv\\Lib\\site-packages')

import subprocess
import os

def run_script(script_name):
    """Run a Python script and return success status"""
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {script_name} failed with return code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {str(e)}")
        return False

def main():
    """Seed all databases"""
    print("🌱 Starting database seeding process...")
    print("=" * 50)
    
    scripts = [
        "seed_mongo.py",
        "seed_vector_db.py"
    ]
    
    success_count = 0
    total_scripts = len(scripts)
    
    for script in scripts:
        print(f"\n📋 Running {script}...")
        if run_script(script):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Database seeding completed: {success_count}/{total_scripts} scripts successful")
    
    if success_count == total_scripts:
        print("🎉 All databases have been seeded successfully!")
        print("\n📊 Summary:")
        print("- MongoDB: Farmers collection seeded with sample data")
        print("- Vector Database: Agricultural knowledge base enhanced with additional documents")
    else:
        print("⚠️  Some scripts failed. Please check the error messages above.")

if __name__ == "__main__":
    main()