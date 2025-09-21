import os
import time
import subprocess
import glob

def watch_and_process():
    """Watch for processing requests and handle them"""
    print("Starting processing watcher...")
    
    while True:
        try:
            # Check for Real-ESRGAN only processing requests
            esrgan_files = glob.glob('/app/inputs/*.process_esrgan')
            for process_file in esrgan_files:
                try:
                    # Extract filename
                    base_process_file = os.path.basename(process_file)
                    input_filename = base_process_file.replace('.process_esrgan', '')
                    output_filename = f"esrgan_{input_filename}"
                    
                    print(f"Processing Real-ESRGAN for: {input_filename}")
                    
                    # Run Real-ESRGAN processing
                    result = subprocess.run([
                        'python', '/app/process_realesrgan_only.py', 
                        input_filename, 
                        output_filename
                    ], capture_output=True, text=True, timeout=600)
                    
                    if result.returncode == 0:
                        print(f"Real-ESRGAN processing successful: {output_filename}")
                    else:
                        print(f"Real-ESRGAN processing failed: {result.stderr}")
                    
                    # Remove the process file to signal completion
                    os.remove(process_file)
                    print(f"Removed process file: {process_file}")
                    
                except Exception as e:
                    print(f"Error processing {process_file}: {e}")
                    # Remove process file even if processing failed
                    try:
                        os.remove(process_file)
                    except:
                        pass

            # Check for GFPGAN processing requests
            gfpgan_files = glob.glob('/app/outputs/*.process_gfpgan')
            for process_file in gfpgan_files:
                try:
                    # Extract filename
                    base_process_file = os.path.basename(process_file)
                    input_filename = base_process_file.replace('.process_gfpgan', '')
                    
                    # Generate output filename
                    if input_filename.startswith('esrgan_'):
                        base_name = input_filename.replace('esrgan_', '')
                        output_filename = f"final_enhanced_{base_name}"
                    else:
                        output_filename = f"final_enhanced_{input_filename}"
                    
                    print(f"Processing GFPGAN for: {input_filename}")
                    
                    # Run GFPGAN processing
                    result = subprocess.run([
                        'python', '/app/process_gfpgan_only.py', 
                        input_filename, 
                        output_filename
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print(f"GFPGAN processing successful: {output_filename}")
                    else:
                        print(f"GFPGAN processing failed: {result.stderr}")
                    
                    # Remove the process file to signal completion
                    os.remove(process_file)
                    print(f"Removed process file: {process_file}")
                    
                except Exception as e:
                    print(f"Error processing {process_file}: {e}")
                    # Remove process file even if processing failed
                    try:
                        os.remove(process_file)
                    except:
                        pass
            
            # Sleep before checking again
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("Processing watcher stopped")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('/app/inputs', exist_ok=True)
    os.makedirs('/app/outputs', exist_ok=True)
    os.makedirs('/app/outputs/frontend', exist_ok=True)
    
    watch_and_process()