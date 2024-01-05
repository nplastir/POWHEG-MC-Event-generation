import os
import sys
import glob

def lhe_postprocess(settings, out_dir):
    print(f"Moving LHE stage output to {out_dir}")
    run_dir = settings["run_dir"]
    
    # get all lhe files in directory
    lhe_files = glob.glob(os.path.join(run_dir, "pwgevents-*.lhe"))
    stat_files = glob.glob(os.path.join(run_dir, "pwg-*-st4-stat.dat"))
    cnt_files = glob.glob(os.path.join(run_dir, "pwgcounters-st4-*.dat"))
    bound_files = glob.glob(os.path.join(run_dir, "pwgboundviolations-*.dat"))

    cmd = f"mv {run_dir}/pwg-*-st4-stat.dat {out_dir}"
    os.system(cmd)
    cmd = f"mv {run_dir}/pwgcounters-st4-*.dat {out_dir}"
    os.system(cmd)
    cmd = f"mv {run_dir}/pwgboundviolations-*.dat {out_dir}"
    os.system(cmd)
    cmd = f"mv {run_dir}/powheg.input {out_dir}"
    os.system(cmd)

    # extract ttbar decay channel from powheg input file
    pwg_input = os.path.join(out_dir, "powheg.input")
    mode = None
    with open(pwg_input, "r") as f:
        lines = f.readlines()
        for l in lines:
            if l.startswith("topdecaymode"):
                mode = l.split(" ")[1].strip()

    if mode is None:
        print(f"WARNING: could not extract top decay mode from powheg.input file. Make sure to label your lhe files according to your chosen settings yourself")
        ttdecay_tag = "ttdecay-UNKNOWN"
    elif mode == "22222":
        ttdecay_tag = "ttdecay-incl"
    elif mode == "11111":
        ttdecay_tag = "ttdecay-1L"
    elif mode == "00022":
        ttdecay_tag = "ttdecay-0L"
    elif mode == "22200":
        ttdecay_tag = "ttdecay-2L"
    else: 
        print(f"Invalid ttdecay extracted from config ({mode})")
        ttdecay_tag = "ttdecay-INVALID"
    
    # loop over lhe files
    n_tot = 0
    for f in list(sorted(lhe_files)):
        '''
        f_name = os.path.basename(f)
        print(f"Moving and unzipping file {f_name}...")
        new_f = f"{out_dir}/{f_name}"
        cmd = f"cp {f} {new_f}"
        os.system(cmd)
        '''
        f_name = os.path.basename(f)
        new_f = f"{out_dir}/{f_name}.gz"
        
        print(f"Moving and unzipping file {f_name}...")
        # move file
        cmd = f"mv {f} {new_f}"
        os.system(cmd)
        
        # unzip file
        cmd = f"gzip -d {new_f}"
        os.system(cmd)

        # get nevents per file
        cmd = f'grep /event {new_f[:-3]} | wc -l > .n'
        os.system(cmd)
        # get the number of events from that file
        with open('.n', "r") as sf:
            nevt = int(sf.readlines()[0].strip())
        os.system("rm .n")
        
        if nevt > 0:
            n_tot += nevt
        else:
            print(f"\tNo events found in LHE file -- skipping")
            # TODO delete file
        
    # get current location
    local_dir = os.path.dirname(os.path.abspath(__file__))
    # check if cpp script exists
    merge_script = os.path.join(local_dir, "mergeLHEfiles")
    cpp_script = os.path.join(local_dir, "mergeLHEfiles.cc")
    if not os.path.exists(merge_script):
        print(f"compiling lhe merging file...")
        cmd = f"g++ -Wall -o {merge_script} {cpp_script}"
        os.system(cmd)

    # merging files
    print(f"Merging LHE files (this will take a few minutes)...")
    os.chdir(out_dir)
    cmd = f"{merge_script} pwgevents-*.lhe"
    os.system(cmd)
    '''
    # finalize merged file
    cmd = f'echo "</LesHouchesEvents>" >> {merged_file}'
    os.system(cmd)
    '''
    print(f"Extracted {n_tot} events from all LHE files")

    comb_file = f"{out_dir}-events-{n_tot}-{ttdecay_tag}.lhe" 
    cmd = f"mv {out_dir}/out.lhe {comb_file}"
    os.system(cmd)
    print(f"Moved combined LHE file to\n\t{comb_file}")
     
    
        
    # TODO validate integrity
    # xmllint --stream --noout ${file}.lhe > /dev/null 2>&1; test $? -eq 0 || fail_exit "xmllint integrity check failed on ${file}.lhe"
        
    
