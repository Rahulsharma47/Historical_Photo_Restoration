import os
import time
import subprocess
import glob

def watch_and_process():
    """Watch for processing requests and handle them"""
    print("Starting processing watcher...")
    print("Watching directories:")
    print(f"  - Inputs: /app/inputs")
    print(f"  - Outputs: /app/outputs/frontend")
    
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
                    
                    print(f"[ESRGAN] Processing Real-ESRGAN for: {input_filename}")
                    
                    # Run Real-ESRGAN processing
                    result = subprocess.run([
                        'python', '/app/frontend/process_realesrgan_only.py', 
                        input_filename, 
                        output_filename
                    ], capture_output=True, text=True, timeout=600)
                    
                    if result.returncode == 0:
                        print(f"[ESRGAN] Real-ESRGAN processing successful: {output_filename}")
                        print(f"[ESRGAN] STDOUT:\n{result.stdout}")
                    else:
                        print(f"[ESRGAN] Real-ESRGAN processing failed: {result.stderr}")
                        print(f"[ESRGAN] STDOUT:\n{result.stdout}")
                    
                    # Remove the process file to signal completion
                    os.remove(process_file)
                    print(f"[ESRGAN] Removed process file: {process_file}")
                    
                except Exception as e:
                    print(f"[ESRGAN] Error processing {process_file}: {e}")
                    # Remove process file even if processing failed
                    try:
                        os.remove(process_file)
                    except:
                        pass

            # Check for GFPGAN processing requests - FIXED PATH
            gfpgan_files = glob.glob('/app/outputs/frontend/*.process_gfpgan')
            
            if gfpgan_files:
                print(f"[GFPGAN] Found {len(gfpgan_files)} GFPGAN processing requests")
            
            for process_file in gfpgan_files:
                try:
                    # Extract filename
                    base_process_file = os.path.basename(process_file)
                    input_filename = base_process_file.replace('.process_gfpgan', '')
                    
                    print(f"[GFPGAN] Found process file: {process_file}")
                    print(f"[GFPGAN] Input filename: {input_filename}")
                    
                    # Generate output filename
                    if input_filename.startswith('esrgan_'):
                        base_name = input_filename.replace('esrgan_', '')
                        output_filename = f"final_enhanced_{base_name}"
                    else:
                        output_filename = f"final_enhanced_{input_filename}"
                    
                    print(f"[GFPGAN] Processing GFPGAN for: {input_filename} -> {output_filename}")
                    
                    # Verify input file exists
                    input_path = f'/app/outputs/frontend/{input_filename}'
                    if not os.path.exists(input_path):
                        print(f"[GFPGAN] ERROR: Input file not found: {input_path}")
                        # List files in directory for debugging
                        print(f"[GFPGAN] Files in /app/outputs/frontend/:")
                        for f in os.listdir('/app/outputs/frontend'):
                            print(f"  - {f}")
                        os.remove(process_file)
                        continue
                    
                    print(f"[GFPGAN] Input file exists: {input_path}")
                    
                    # Run GFPGAN processing
                    result = subprocess.run([
                        'python', '/app/frontend/process_gfpgan_only.py', 
                        input_filename, 
                        output_filename
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print(f"[GFPGAN] GFPGAN processing successful: {output_filename}")
                        print(f"[GFPGAN] STDOUT:\n{result.stdout}")
                    else:
                        print(f"[GFPGAN] GFPGAN processing failed!")
                        print(f"[GFPGAN] STDERR:\n{result.stderr}")
                        print(f"[GFPGAN] STDOUT:\n{result.stdout}")
                    
                    # Remove the process file to signal completion
                    os.remove(process_file)
                    print(f"[GFPGAN] Removed process file: {process_file}")
                    
                except Exception as e:
                    print(f"[GFPGAN] Error processing {process_file}: {e}")
                    import traceback
                    traceback.print_exc()
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
            import traceback
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('/app/inputs', exist_ok=True)
    os.makedirs('/app/outputs', exist_ok=True)
    os.makedirs('/app/outputs/frontend', exist_ok=True)
    
    print("=" * 60)
    print("Image Processing Watcher Started")
    print("=" * 60)
    print("Monitoring:")
    print("  1. /app/inputs/*.process_esrgan -> Real-ESRGAN processing")
    print("  2. /app/outputs/frontend/*.process_gfpgan -> GFPGAN processing")
    print("=" * 60)
    
    watch_and_process()