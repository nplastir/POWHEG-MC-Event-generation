# Instructions for the ttb-jets MC event production with POWHEG-BOX-RES

Setup
-------------
First set up a directory into the AFS space where everything will be installed
```
mkdir MCProduction ; cd MCProduction
base=$PWD
```
All commands are given relative to this `$base`

Set up a CMSSW_10_2_14 environment:
```
cd $base
scram project CMSSW_10_2_14
cd $base/CMSSW_10_2_14/src
cmsenv
cd $base
```
Install `yaml` package for python3:
```
pip3 install --user pyyaml
```

Install POWHEG-BOX-RES:
```
cd $base
svn checkout --revision 3604 --username anonymous --password anonymous svn://powhegbox.mib.infn.it/trunk/POWHEG-BOX-RES
```
We are using revision 3604, which is the stable release version. More recent revisions have not been tested yet.

Get the code for the ttbb process:
```
cd $base/POWHEG-BOX-RES
git clone ssh://git@gitlab.cern.ch:7999/tjezo/powheg-box-res_ttbb.git ttbb
```
Enter the ttbb directory and check out the appropriate commit that fits to r3604 of the POWHEG-BOX-RES code:
```
cd $base/POWHEG-BOX-RES/ttbb
git checkout 128aefb6061b72714d34e5f1d4798967f76f9585
```
Then compile the fortran code of POWHEG:
```
cd $base/POWHEG-BOX-RES/ttbb
make pwhg_main
make lhef_decay
```

The ttbb POWHEG code is now in principle ready to run. We can now also install this repository to ease the event generation and submit to HTCondor:
```
cd $base
git clone https://github.com/nplastir/POWHEG-MC-Event-generation.git
```

For a new production it is recommended to create a new directory now in which you can store everything needed for that production, e.g.
```
cd $base
mkdir production_test
cd production_test
production=$PWD
```

In `$base/POWHEG-MC-Event-generation/ttbb_powheg_inputs/` a few `powheg.input` files are stored which can be used as examples for event production. The settings of course can be adjusted based on what configuration is supposed to be generated.


Setting up a run
-------------
In `POWHEG-MC-Event-generation` three stages are supported for running all of the powheg parallel stages. 
To start a run from scratch, first an intialization has to be performed where a working directory is created and settings are determined.
Then, parallelstages can be run (i.e. submitted to HTCondor).
After one stage has finished, the output of the previous stage can be validated.

### Initialization

Initialize a new run via:
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py --init -p ../POWHEG-BOX-RES/ttbb -i ../POWHEG-MC-Event-generation/ttbb_powheg_inputs/powheg.input_nominal -t [NAME] (--mur [MUR])(--muf [MUF])(--mass [MASS])(--pdf [PDF])
```
Use the help function of `POWHEG-MC-Event-generation/run.py` for more details on the options.
In summary:
- `-p` the path to the process directory in your `POWHEG-BOX-RES` has to be given.
- `-i` specifies a `powheg.input` file to use for this production. Make sure that you are using the correct one. Options:
   - `powheg.input_nominal`
   - `powheg.input_hdampUP`
   - `powheg.input_hdampDOWN`
- `-t` specifies a name tag for the run to differentiate it from other productions.

In addition, in this initialization step, the following factors can be changed:
- `--mur` specifies the renormaliation scale.
- `--muf` specifies the factorization scale.
- `--mass` specifies the mass of the top quark.
- `--pdf` specifies the pdf of the proton.

If these factors are not explicitly set, then, the run will initialize with the default values: `--muf 1.0 --mur 1.0 --pdf 320900 --mass 172.5`.

**Example:**
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py --init -p ../POWHEG-BOX-RES/ttbb -i ../POWHEG-MC-Event-generation/ttbb_powheg_inputs/powheg.input_nominal -t test
```
where this command will create a work directory called `test__r1.0_f1.0_m172.5_p320900` 

----------
After the initialization of the run, [parallel stages 1-3](#parallel-stages-1-3) can be submitted in order to start a full production, or if the inputs for producing LHE files are already available, only [stage 4](#lhe-file-production) has to be run

----------


### Parallel Stages 1-3
After initialization of the run, parallel stages can be submitted:

1. **Stage 1**

```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 1 -X 1 -n [NBATCHES]
```
- Here, `-w` specifies the path to the previously created work directory (e.g. `-w ./test__r1.0_f1.0_m172.5_p320900`)
- With `-n` you can create the number of jobs to be submitted, e.g. `-n 1000` for 1000 submitted jobs.
- The parameters `-S` and `-X` specify the parallel stage (`-S`) and xgriditeration (`-X`) to run.

The number of jobs here will determine the number of ubound files we have in the end. (<ins>Recommended 100-200 jobs</ins>)
 
After the jobs of one parallel stage are done the output can be validated before the next step has to be run:
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 1 -X 1 -n [NBATCHES] --validate
```

If validation was successful then the next step is to run again stage 1 but with different xgriditeration in order to refine the grid integration:

```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 1 -X 2 -n [NBATCHES]
```
After these jobs are completed we validate them:
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 1 -X 2 -n [NBATCHES] --validate
```
and then run it again with `-X 3`:

```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 1 -X 3 -n [NBATCHES]
```
and again validation:

```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 1 -X 3 -n [NBATCHES] --validate
```

The first parallelstage has to be run at least three times as indicated above but can be continued with more xgridintegrations if needed. (<ins>Recommended 5 xgriditerations</ins>)

2. **Stage 2**

For this stage, it is only required to be run once and with the same number of jobs as in stage 1
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 2 -n [NBATCHES]
```
This stage will take a while to finish. When all jobs are completed, you need to validate them before moving to the next stage. 
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 2 -n [NBATCHES] --validate
```

3. **Stage 3**

After stage 2 has finished, submit again with the same number of jobs as in previous stages 
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 3 -n [NBATCHES]
```
----------

### LHE file production

For this stage, make sure that you have initialized the working directory with the appropriate generator settings (mur,muf,mass,pdf).

Then, proceed to copy all the grid files for the LHE run to the run directory `run__[NAME]__r[MUR]_f[MUF]_m[MASS]_p[PDF]` that has been created inside the `POWHEG-BOX-RES/ttbb/`. 
Availiable grids:
- muR=1.0, muF=1.0:
```
cp /afs/cern.ch/work/v/vanderli/public/ttbb-lhe-inputs/grids_nominal/muR1.0_muF1.0/*
```
- muR=1.0, muF=2.0:
```
cp /afs/cern.ch/work/v/vanderli/public/ttbb-lhe-inputs/grids_nominal/muR1.0_muF2.0_v2/*
```
- muR=1.0, muF=1.0 for hdampUp:
```
cp /afs/cern.ch/work/v/vanderli/public/ttbb-lhe-inputs/grids_hdampUP/muR1.0_muF1.0/*
```
- muR=1.0, muF=2.0 for hdampUp:
- muR=1.0, muF=1.0 for hdampDOWN:
```
cp /afs/cern.ch/work/v/vanderli/public/ttbb-lhe-inputs/grids_hdampDOWN/muR1.0_muF1.0/*
```
- muR=1.0, muF=2.0 for hdampDOWN:
```
cp /afs/cern.ch/user/n/nplastir/public/grids_hdampDOWN/muR1.0_muF2.0/*
```

(e.g. `cp /afs/cern.ch/work/v/vanderli/public/ttbb-lhe-inputs/grids_nominal/muR1.0_muF2.0/* $base/POWHEG-BOX-RES/ttbb/run__test__r1.0_f1.0_m172.5_p320900`).

After everything has been copied inside the run directory, the jobs for the LHE production can be submitted via 
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 4 -n [NBATCHES] -N [NEVENTSPERJOB] --decay [DECAYCHANNEL] -f
```
You have to append the option `-f` to force the submission of batch jobs as otherwise this is blocked as parallel stages 1-3 were skipped.
Two additional options are required for this step, `-N` and `--decay`. The first specifies the number of events per job (defaults to 1000), and the second specifies the ttbar decay channel.
This option is mandatory and has to be specified. The options are:
- `1L`: for semileptonic ttbar decays
- `0L`: for fully hadronic ttbar decays
- `2L`: for dileptonic ttbar decays
- `incl`: for inclusive ttbar decays

**Example:**
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w ./test__r1.0_f1.0_m172.5_p320900 -S 4 -n 1000 -N 1000 --decay 2L -f
```

Ater the jobs have finished, merge the LHE files that have been produced:
```
cd $production
python3 ../POWHEG-MC-Event-generation/run.py -w [PATH_TO_WORKDIR] -S 4 -n [NBATCHES] -N [NEVENTSPERJOB] --decay [DECAYCHANNEL] --lhe
```
(NOTE: This process takes several hours when the number of events is high. Run it in a tmux!)

